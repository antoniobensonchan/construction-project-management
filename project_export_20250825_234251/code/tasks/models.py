from django.db import models
from django.urls import reverse
from django.utils import timezone


class Task(models.Model):
    """任务模型"""

    # 任务类型选择
    TASK_TYPE_CHOICES = [
        ('new_construction', '新建施工'),
        ('repair', '整改修复'),
        ('inspection', '检查验收'),
        ('maintenance', '维护保养'),
    ]

    # 任务状态
    STATUS_CHOICES = [
        ('pending', '待开始'),
        ('in_progress', '进行中'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    ]

    # 项目关联
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name='所属项目'
    )

    # 基本信息
    name = models.CharField(max_length=200, verbose_name='任务名称')
    description = models.TextField(blank=True, verbose_name='任务描述')

    task_type = models.CharField(
        max_length=20,
        choices=TASK_TYPE_CHOICES,
        default='new_construction',
        verbose_name='任务类型'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='任务状态'
    )

    responsible_person = models.CharField(max_length=100, verbose_name='负责人')
    deadline = models.DateField(verbose_name='截止时间')

    # 关联图纸（多对多关系，支持一个任务关联多张图纸）
    drawings = models.ManyToManyField(
        'drawings.Drawing',
        related_name='tasks',
        verbose_name='关联图纸',
        blank=True
    )

    # 创建时间
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    # 更新时间
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '任务'
        verbose_name_plural = '任务'
        ordering = ['-deadline']  # 按截止时间倒序

    def __str__(self):
        return f"{self.name} - {self.get_task_type_display()}"

    @property
    def task_type_display(self):
        """返回任务类型的中文显示"""
        return self.get_task_type_display()


class TaskAnnotation(models.Model):
    """任务标注模型"""

    ANNOTATION_TYPE_CHOICES = [
        ('point', '点标记'),
        ('rectangle', '矩形标记'),
        ('text', '文字标注'),
        ('line', '线条标注'),
    ]

    COLOR_CHOICES = [
        ('red', '红色'),
        ('blue', '蓝色'),
        ('green', '绿色'),
        ('yellow', '黄色'),
        ('orange', '橙色'),
        ('purple', '紫色'),
        ('black', '黑色'),
    ]

    # 关联任务
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='annotations',
        verbose_name='关联任务'
    )

    # 关联图纸（标注属于哪张图纸）
    drawing = models.ForeignKey(
        'drawings.Drawing',
        on_delete=models.CASCADE,
        related_name='annotations',
        verbose_name='关联图纸'
    )

    # 标注类型
    annotation_type = models.CharField(
        max_length=20,
        choices=ANNOTATION_TYPE_CHOICES,
        verbose_name='标注类型'
    )

    # 页码（标注所在的PDF页面）
    page_number = models.PositiveIntegerField(default=1, verbose_name='页码')

    # 坐标信息（相对于PDF页面的像素坐标）
    x_coordinate = models.FloatField(verbose_name='X坐标')
    y_coordinate = models.FloatField(verbose_name='Y坐标')

    # 矩形标注的宽度和高度（仅矩形标注使用）
    width = models.FloatField(null=True, blank=True, verbose_name='宽度')
    height = models.FloatField(null=True, blank=True, verbose_name='高度')

    # 线条标注的终点坐标（仅线条标注使用）
    end_x = models.FloatField(null=True, blank=True, verbose_name='终点X坐标')
    end_y = models.FloatField(null=True, blank=True, verbose_name='终点Y坐标')

    # 标注颜色
    color = models.CharField(
        max_length=20,
        choices=COLOR_CHOICES,
        default='red',
        verbose_name='标注颜色'
    )

    # 标注内容
    content = models.TextField(max_length=200, verbose_name='标注内容')

    # 创建时间
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '任务标注'
        verbose_name_plural = '任务标注'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.task.name} - {self.get_annotation_type_display()}"

    @property
    def is_point(self):
        """是否为点标记"""
        return self.annotation_type == 'point'

    @property
    def is_rectangle(self):
        """是否为矩形标记"""
        return self.annotation_type == 'rectangle'

    @property
    def is_text(self):
        """是否为文字标注"""
        return self.annotation_type == 'text'

    @property
    def is_line(self):
        """是否为线条标注"""
        return self.annotation_type == 'line'
