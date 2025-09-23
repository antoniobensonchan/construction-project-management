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
        ('open', '开放'),
        ('in_progress', '进行中'),
        ('pending', '待处理'),
        ('completed', '已完成'),
    ]

    # 工地关联（任务属于工地）
    worksite = models.ForeignKey(
        'projects.WorkSite',
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name='所属工地'
    )

    # 父任务关联（支持子任务）
    parent_task = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subtasks',
        verbose_name='父任务'
    )

    # 项目关联（通过工地间接关联，用于向后兼容）
    @property
    def project(self):
        return self.worksite.project if self.worksite else None

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
        default='open',
        verbose_name='任务状态'
    )

    responsible_person = models.CharField(max_length=100, verbose_name='负责人')

    # 任务时间计划
    start_date = models.DateField(verbose_name='开始日期')
    end_date = models.DateField(verbose_name='结束日期')
    deadline = models.DateField(verbose_name='截止时间')  # 保留向后兼容

    # 关联图纸（多对多关系，支持一个任务关联多张图纸）
    drawings = models.ManyToManyField(
        'drawings.Drawing',
        related_name='tasks',
        verbose_name='关联图纸',
        blank=True
    )

    # 任务依赖关系
    dependencies = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='dependent_tasks',
        verbose_name='依赖任务',
        blank=True,
        help_text='此任务依赖的其他任务（必须等待这些任务完成后才能开始）'
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
        parent_info = f" (子任务: {self.parent_task.name})" if self.parent_task else ""
        return f"{self.name} - {self.get_task_type_display()}{parent_info}"

    @property
    def task_type_display(self):
        """返回任务类型的中文显示"""
        return self.get_task_type_display()

    @property
    def is_subtask(self):
        """判断是否为子任务"""
        return self.parent_task is not None

    @property
    def is_parent_task(self):
        """判断是否为父任务"""
        return self.subtasks.exists()

    def get_all_subtasks(self):
        """获取所有子任务（递归）"""
        subtasks = []
        for subtask in self.subtasks.all():
            subtasks.append(subtask)
            subtasks.extend(subtask.get_all_subtasks())
        return subtasks

    def get_task_level(self):
        """获取任务层级（0为顶级任务）"""
        level = 0
        current_task = self
        while current_task.parent_task:
            level += 1
            current_task = current_task.parent_task
        return level

    def get_progress_percentage(self):
        """获取任务进度百分比（基于子任务完成情况）"""
        subtasks = self.subtasks.all()
        if not subtasks.exists():
            # 如果没有子任务，根据自身状态返回进度
            if self.status == 'completed':
                return 100
            elif self.status == 'in_progress':
                return 50
            else:
                return 0

        # 如果有子任务，基于子任务完成情况计算进度
        total_subtasks = subtasks.count()
        completed_subtasks = subtasks.filter(status='completed').count()

        if total_subtasks == 0:
            return 0

        return round((completed_subtasks / total_subtasks) * 100)

    def get_subtask_stats(self):
        """获取子任务统计信息"""
        subtasks = self.subtasks.all()
        return {
            'total': subtasks.count(),
            'open': subtasks.filter(status='open').count(),
            'in_progress': subtasks.filter(status='in_progress').count(),
            'pending': subtasks.filter(status='pending').count(),
            'completed': subtasks.filter(status='completed').count(),
        }

    def get_completed_subtasks_count(self):
        """获取已完成子任务数量"""
        return self.subtasks.filter(status='completed').count()

    def get_subtasks_count(self):
        """获取子任务总数"""
        return self.subtasks.count()

    def update_parent_progress(self):
        """更新父任务的进度（当子任务状态改变时调用）"""
        if self.parent_task:
            # 可以在这里添加自动更新父任务状态的逻辑
            pass

    @property
    def duration_days(self):
        """任务持续天数"""
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days + 1
        return 0

    @property
    def time_progress_percentage(self):
        """基于时间的进度百分比"""
        if self.status == 'completed':
            return 100
        elif self.status == 'open':
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

    def can_start(self):
        """检查任务是否可以开始（所有依赖任务都已完成）"""
        return all(dep.status == 'completed' for dep in self.dependencies.all())

    def get_blocking_dependencies(self):
        """获取阻塞此任务的依赖任务"""
        return self.dependencies.exclude(status='completed')

    def get_dependency_chain(self):
        """获取完整的依赖链"""
        chain = []
        visited = set()

        def build_chain(task):
            if task.id in visited:
                return  # 避免循环依赖
            visited.add(task.id)

            for dep in task.dependencies.all():
                build_chain(dep)
                if dep not in chain:
                    chain.append(dep)

        build_chain(self)
        return chain

    def has_circular_dependency(self, new_dependency):
        """检查是否会产生循环依赖"""
        if new_dependency == self:
            return True

        # 检查新依赖是否依赖于当前任务
        def check_circular(task, target, visited=None):
            if visited is None:
                visited = set()

            if task.id in visited:
                return False
            visited.add(task.id)

            if task == target:
                return True

            return any(check_circular(dep, target, visited.copy())
                      for dep in task.dependencies.all())

        return check_circular(new_dependency, self)

    def clean(self):
        """数据验证"""
        from django.core.exceptions import ValidationError

        # 验证日期逻辑
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValidationError('开始日期不能晚于结束日期')

        if self.end_date and self.deadline:
            if self.end_date > self.deadline:
                raise ValidationError('结束日期不能晚于截止时间')

        # 验证任务日期是否在工地日期范围内
        if self.worksite:
            if self.start_date and self.worksite.start_date and self.start_date < self.worksite.start_date:
                raise ValidationError('任务开始日期不能早于工地开始日期')
            if self.end_date and self.worksite.end_date and self.end_date > self.worksite.end_date:
                raise ValidationError('任务结束日期不能晚于工地结束日期')

        # 验证子任务日期是否在父任务日期范围内
        if self.parent_task:
            if self.start_date and self.parent_task.start_date and self.start_date < self.parent_task.start_date:
                raise ValidationError('子任务开始日期不能早于父任务开始日期')
            if self.end_date and self.parent_task.end_date and self.end_date > self.parent_task.end_date:
                raise ValidationError('子任务结束日期不能晚于父任务结束日期')

    def save(self, *args, **kwargs):
        # 如果没有设置deadline，使用end_date作为默认值
        if not self.deadline and self.end_date:
            self.deadline = self.end_date

        self.full_clean()
        super().save(*args, **kwargs)


class TaskDependency(models.Model):
    """任务依赖关系模型 - 更详细的依赖管理"""

    # 依赖类型
    DEPENDENCY_TYPE_CHOICES = [
        ('finish_to_start', '完成-开始'),  # 前置任务完成后，后续任务才能开始
        ('start_to_start', '开始-开始'),   # 前置任务开始后，后续任务才能开始
        ('finish_to_finish', '完成-完成'), # 前置任务完成后，后续任务才能完成
        ('start_to_finish', '开始-完成'),  # 前置任务开始后，后续任务才能完成
    ]

    predecessor = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='successor_dependencies',
        verbose_name='前置任务'
    )

    successor = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='predecessor_dependencies',
        verbose_name='后续任务'
    )

    dependency_type = models.CharField(
        max_length=20,
        choices=DEPENDENCY_TYPE_CHOICES,
        default='finish_to_start',
        verbose_name='依赖类型'
    )

    lag_days = models.IntegerField(
        default=0,
        verbose_name='滞后天数',
        help_text='依赖关系的延迟天数（可以为负数表示提前）'
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '任务依赖'
        verbose_name_plural = '任务依赖'
        unique_together = ['predecessor', 'successor']
        ordering = ['created_at']

    def __str__(self):
        return f"{self.predecessor.name} → {self.successor.name} ({self.get_dependency_type_display()})"

    def clean(self):
        """数据验证"""
        from django.core.exceptions import ValidationError

        if self.predecessor == self.successor:
            raise ValidationError('任务不能依赖自己')

        # 检查循环依赖
        if self.would_create_cycle():
            raise ValidationError('此依赖关系会创建循环依赖')

    def would_create_cycle(self):
        """检查是否会创建循环依赖"""
        def has_path(start, end, visited=None):
            if visited is None:
                visited = set()

            if start.id in visited:
                return False
            visited.add(start.id)

            if start == end:
                return True

            # 检查所有后续任务
            for dep in TaskDependency.objects.filter(predecessor=start):
                if has_path(dep.successor, end, visited.copy()):
                    return True

            return False

        return has_path(self.successor, self.predecessor)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


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
