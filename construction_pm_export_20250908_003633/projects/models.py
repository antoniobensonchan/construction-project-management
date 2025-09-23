from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()
from django.utils import timezone
from datetime import date


class Project(models.Model):
    """项目模型 - 顶级容器"""

    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='项目所有者', related_name='owned_projects')
    name = models.CharField(max_length=200, verbose_name='项目名称')
    description = models.TextField(blank=True, verbose_name='项目描述')
    start_date = models.DateField(verbose_name='开始日期')
    end_date = models.DateField(verbose_name='结束日期')

    # 项目状态
    STATUS_CHOICES = [
        ('planning', '规划中'),
        ('active', '进行中'),
        ('completed', '已完成'),
        ('suspended', '暂停'),
        ('cancelled', '已取消'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='planning',
        verbose_name='项目状态'
    )

    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '项目'
        verbose_name_plural = '项目'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('projects:project_detail', kwargs={'pk': self.pk})

    @property
    def is_active(self):
        """项目是否进行中"""
        return self.status == 'active'

    @property
    def is_overdue(self):
        """项目是否已过期"""
        return self.end_date < date.today() and self.status not in ['completed', 'cancelled']

    @property
    def duration_days(self):
        """项目持续天数"""
        return (self.end_date - self.start_date).days

    @property
    def progress_percentage(self):
        """项目进度百分比（基于时间）"""
        if self.status == 'completed':
            return 100
        elif self.status in ['cancelled', 'suspended']:
            return 0

        today = date.today()
        if today < self.start_date:
            return 0
        elif today > self.end_date:
            return 100
        else:
            total_days = self.duration_days
            elapsed_days = (today - self.start_date).days
            return min(100, int((elapsed_days / total_days) * 100)) if total_days > 0 else 0

    def clean(self):
        """数据验证"""
        from django.core.exceptions import ValidationError

        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValidationError('开始日期不能晚于结束日期')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class WorkSite(models.Model):
    """工地模型 - 项目下的具体工地"""

    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name='所属项目', related_name='worksites')
    name = models.CharField(max_length=200, verbose_name='工地名称')
    description = models.TextField(blank=True, verbose_name='工地描述')
    location = models.CharField(max_length=200, blank=True, verbose_name='工地地址')
    site_manager = models.CharField(max_length=100, blank=True, verbose_name='工地负责人')
    contact_phone = models.CharField(max_length=20, blank=True, verbose_name='联系电话')

    # 工地时间计划
    start_date = models.DateField(verbose_name='开始日期')
    end_date = models.DateField(verbose_name='结束日期')

    # 工地状态
    STATUS_CHOICES = [
        ('preparing', '准备中'),
        ('active', '施工中'),
        ('completed', '已完成'),
        ('suspended', '暂停'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='preparing',
        verbose_name='工地状态'
    )

    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '工地'
        verbose_name_plural = '工地'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.project.name} - {self.name}"

    def get_absolute_url(self):
        return reverse('projects:worksite_detail', kwargs={'pk': self.pk})

    @property
    def duration_days(self):
        """工地持续天数"""
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days + 1
        return 0

    @property
    def progress_percentage(self):
        """工地进度百分比（基于时间）"""
        if self.status == 'completed':
            return 100
        elif self.status in ['suspended']:
            return 0

        today = date.today()
        if today < self.start_date:
            return 0
        elif today > self.end_date:
            return 100
        else:
            total_days = self.duration_days
            elapsed_days = (today - self.start_date).days
            return min(100, int((elapsed_days / total_days) * 100)) if total_days > 0 else 0

    def clean(self):
        """数据验证"""
        from django.core.exceptions import ValidationError

        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValidationError('开始日期不能晚于结束日期')

        # 验证工地日期是否在项目日期范围内
        if self.project:
            if self.start_date and self.project.start_date and self.start_date < self.project.start_date:
                raise ValidationError('工地开始日期不能早于项目开始日期')
            if self.end_date and self.project.end_date and self.end_date > self.project.end_date:
                raise ValidationError('工地结束日期不能晚于项目结束日期')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
