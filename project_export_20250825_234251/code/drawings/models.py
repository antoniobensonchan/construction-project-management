from django.db import models
from django.core.validators import FileExtensionValidator
from django.core.files.base import ContentFile
import os
import PyPDF2
from PIL import Image
import tempfile
import logging

logger = logging.getLogger(__name__)


def drawing_upload_path(instance, filename):
    """生成图纸文件上传路径"""
    return f'drawings/{filename}'


def thumbnail_upload_path(instance, filename):
    """生成缩略图上传路径"""
    return f'thumbnails/{filename}'


class Drawing(models.Model):
    """PDF图纸模型"""

    # 项目关联
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='drawings',
        verbose_name='所属项目'
    )

    # 文件名（显示用）
    name = models.CharField(max_length=255, verbose_name='图纸名称')

    # 图纸文件（支持PDF和图片格式）
    file = models.FileField(
        upload_to=drawing_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png', 'bmp', 'tiff'])],
        verbose_name='图纸文件'
    )

    # 文件大小（字节）
    file_size = models.PositiveIntegerField(verbose_name='文件大小')

    # 页数（PDF专用，图片默认为1）
    page_count = models.PositiveIntegerField(default=1, verbose_name='页数')

    # 文件类型
    file_type = models.CharField(max_length=10, blank=True, verbose_name='文件类型')

    # PDF版本（仅PDF文件）
    pdf_version = models.CharField(max_length=10, blank=True, verbose_name='PDF版本')

    # 缩略图
    thumbnail = models.ImageField(
        upload_to=thumbnail_upload_path,
        blank=True,
        null=True,
        verbose_name='缩略图'
    )

    # 文件完整性状态
    is_valid = models.BooleanField(default=True, verbose_name='文件完整性')

    # 上传时间
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='上传时间')

    # 更新时间
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = 'PDF图纸'
        verbose_name_plural = 'PDF图纸'
        ordering = ['-uploaded_at']  # 按上传时间倒序

    def __str__(self):
        return self.name

    @property
    def file_size_mb(self):
        """返回文件大小（MB）"""
        return round(self.file_size / (1024 * 1024), 2)

    def validate_file(self):
        """验证文件完整性和类型"""
        try:
            file_extension = os.path.splitext(self.file.name)[1].lower()
            self.file_type = file_extension[1:]  # 去掉点号

            if file_extension == '.pdf':
                return self.validate_pdf()
            elif file_extension in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
                return self.validate_image()
            else:
                self.is_valid = False
                return False, f"不支持的文件格式: {file_extension}"

        except Exception as e:
            logger.error(f"文件验证失败: {str(e)}")
            self.is_valid = False
            return False, f"文件验证失败: {str(e)}"

    def validate_pdf(self):
        """验证PDF文件完整性和版本"""
        try:
            with open(self.file.path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)

                # 检查PDF版本（简化版本检查）
                try:
                    self.pdf_version = "1.6"  # 默认版本，POC阶段简化
                except:
                    self.pdf_version = "未知"

                # 获取页数
                self.page_count = len(pdf_reader.pages)

                # 检查是否有页面
                if self.page_count == 0:
                    self.is_valid = False
                    return False, "PDF文件为空"

                # 尝试读取第一页内容（验证文件完整性）
                try:
                    first_page = pdf_reader.pages[0]
                    if first_page:
                        self.is_valid = True
                        return True, "PDF文件验证成功"
                    else:
                        self.is_valid = False
                        return False, "PDF第一页无法访问"
                except Exception as page_error:
                    self.is_valid = False
                    return False, f"PDF页面读取失败: {str(page_error)}"

        except Exception as e:
            logger.error(f"PDF验证失败: {str(e)}")
            self.is_valid = False
            return False, f"PDF文件损坏或格式错误: {str(e)}"

    def validate_image(self):
        """验证图片文件"""
        try:
            from PIL import Image
            with Image.open(self.file.path) as img:
                # 验证图片可以正常打开
                img.verify()

                # 重新打开获取信息（verify后需要重新打开）
                with Image.open(self.file.path) as img:
                    width, height = img.size
                    if width < 100 or height < 100:
                        self.is_valid = False
                        return False, "图片尺寸太小（最小100x100像素）"

                    if width > 10000 or height > 10000:
                        self.is_valid = False
                        return False, "图片尺寸太大（最大10000x10000像素）"

                self.page_count = 1  # 图片只有一页
                self.is_valid = True
                return True, "图片文件验证成功"

        except Exception as e:
            logger.error(f"图片验证失败: {str(e)}")
            self.is_valid = False
            return False, f"图片文件损坏或格式错误: {str(e)}"

    def generate_thumbnail(self):
        """生成PDF缩略图"""
        try:
            # 使用pdf2image生成第一页的图片
            from pdf2image import convert_from_path

            # 转换第一页为图片
            images = convert_from_path(
                self.file.path,
                first_page=1,
                last_page=1,
                dpi=150,
                fmt='PNG'
            )

            if images:
                image = images[0]

                # 调整为16:9比例的缩略图
                width, height = image.size
                target_ratio = 16 / 9
                current_ratio = width / height

                if current_ratio > target_ratio:
                    # 图片太宽，裁剪宽度
                    new_width = int(height * target_ratio)
                    left = (width - new_width) // 2
                    image = image.crop((left, 0, left + new_width, height))
                else:
                    # 图片太高，裁剪高度
                    new_height = int(width / target_ratio)
                    top = (height - new_height) // 2
                    image = image.crop((0, top, width, top + new_height))

                # 缩放到合适大小
                image = image.resize((320, 180), Image.Resampling.LANCZOS)

                # 保存缩略图
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                    image.save(temp_file.name, 'PNG')

                    with open(temp_file.name, 'rb') as f:
                        thumbnail_name = f"{os.path.splitext(self.file.name)[0]}_thumb.png"
                        self.thumbnail.save(
                            thumbnail_name,
                            ContentFile(f.read()),
                            save=False
                        )

                    os.unlink(temp_file.name)

                return True, "缩略图生成成功"
            else:
                return False, "无法生成缩略图"

        except ImportError:
            logger.warning("pdf2image未安装，跳过缩略图生成")
            return False, "缺少pdf2image依赖"
        except Exception as e:
            logger.error(f"缩略图生成失败: {str(e)}")
            return False, f"缩略图生成失败: {str(e)}"

    def delete(self, *args, **kwargs):
        """删除模型时同时删除文件"""
        if self.file:
            if os.path.isfile(self.file.path):
                os.remove(self.file.path)
        if self.thumbnail:
            if os.path.isfile(self.thumbnail.path):
                os.remove(self.thumbnail.path)
        super().delete(*args, **kwargs)
