from django import forms
from .models import Drawing
from projects.models import Project


class DrawingUploadForm(forms.ModelForm):
    """PDF图纸上传表单"""

    project = forms.ModelChoiceField(
        queryset=Project.objects.all(),
        required=False,
        empty_label="选择项目（可选）",
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='所属项目'
    )

    class Meta:
        model = Drawing
        fields = ['name', 'project', 'file']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入图纸名称，如"3层东墙钢筋绑扎图"',
                'maxlength': 255
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png,.bmp,.tiff',
                'id': 'file-input'
            })
        }

    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)

        if project:
            # 如果指定了项目，隐藏项目选择字段并设置默认值
            self.fields['project'].widget = forms.HiddenInput()
            self.fields['project'].initial = project
            self.fields['project'].required = False
        labels = {
            'name': '图纸名称',
            'file': '图纸文件'
        }

    def clean_file(self):
        """验证上传的文件"""
        file = self.cleaned_data.get('file')

        if file:
            # 检查文件大小（10MB限制）
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError('文件大小不能超过10MB')

            # 检查文件扩展名
            allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.bmp', '.tiff']
            file_extension = file.name.lower().split('.')[-1]
            if f'.{file_extension}' not in allowed_extensions:
                raise forms.ValidationError('仅支持PDF、JPG、PNG、BMP、TIFF格式文件')

            # 检查MIME类型
            allowed_mime_types = [
                'application/pdf',
                'image/jpeg', 'image/jpg', 'image/png',
                'image/bmp', 'image/tiff'
            ]
            if file.content_type not in allowed_mime_types:
                raise forms.ValidationError('文件格式不正确，请重新选择')

        return file

    def save(self, commit=True):
        """保存时自动设置文件大小并验证PDF"""
        instance = super().save(commit=False)
        if instance.file:
            instance.file_size = instance.file.size

            if commit:
                instance.save()  # 先保存文件

                # 验证文件
                is_valid, message = instance.validate_file()
                if not is_valid:
                    instance.delete()  # 删除无效文件
                    raise forms.ValidationError(message)

                # 生成缩略图
                instance.generate_thumbnail()
                instance.save()  # 保存验证结果和缩略图
        elif commit:
            instance.save()
        return instance
