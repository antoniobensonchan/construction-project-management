from django import forms
from django.utils import timezone
from datetime import date, timedelta
from .models import Task, TaskDependency
from drawings.models import Drawing
from projects.models import Project


class TaskCreateForm(forms.ModelForm):
    """任务创建表单 - 步骤1：填写任务信息"""

    # 显式定义日期字段
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }, format='%Y-%m-%d'),
        input_formats=['%Y-%m-%d'],
        label='开始日期'
    )

    end_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }, format='%Y-%m-%d'),
        input_formats=['%Y-%m-%d'],
        label='结束日期'
    )

    # 依赖任务选择
    dependencies = forms.ModelMultipleChoiceField(
        queryset=Task.objects.none(),
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        }),
        required=False,
        label='依赖任务',
        help_text='选择此任务依赖的其他任务（必须等待这些任务完成后才能开始）'
    )

    class Meta:
        model = Task
        fields = ['name', 'task_type', 'responsible_person', 'start_date', 'end_date', 'deadline', 'dependencies']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入任务名称，如"3层东墙钢筋绑扎"',
                'maxlength': 200
            }),
            'task_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'responsible_person': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入负责人姓名，如"张三"',
                'maxlength': 100
            }),
            'deadline': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'min': date.today().strftime('%Y-%m-%d')
            })
        }
        labels = {
            'name': '任务名称',
            'task_type': '任务类型',
            'responsible_person': '负责人',
            'start_date': '开始日期',
            'end_date': '结束日期',
            'deadline': '截止时间',
            'dependencies': '依赖任务'
        }

    def __init__(self, *args, **kwargs):
        worksite = kwargs.pop('worksite', None)
        super().__init__(*args, **kwargs)

        # 设置依赖任务选项（排除自己和子任务）
        if worksite:
            available_tasks = Task.objects.filter(worksite=worksite)
            if self.instance.pk:
                # 编辑时排除自己和自己的子任务
                available_tasks = available_tasks.exclude(pk=self.instance.pk)
                available_tasks = available_tasks.exclude(parent_task=self.instance)
            self.fields['dependencies'].queryset = available_tasks

        # 设置默认日期（仅新建任务）
        if not self.instance.pk:
            today = date.today()
            self.fields['start_date'].initial = today
            self.fields['end_date'].initial = today + timedelta(days=3)
            self.fields['deadline'].initial = today + timedelta(days=3)

            # 如果有工地信息，设置日期范围限制
            if worksite:
                if worksite.start_date:
                    self.fields['start_date'].widget.attrs['min'] = worksite.start_date.isoformat()
                if worksite.end_date:
                    self.fields['end_date'].widget.attrs['max'] = worksite.end_date.isoformat()
                    self.fields['deadline'].widget.attrs['max'] = worksite.end_date.isoformat()
        else:
            # 编辑任务时，移除日期限制
            for field_name in ['start_date', 'end_date', 'deadline']:
                self.fields[field_name].widget.attrs.pop('min', None)
                self.fields[field_name].widget.attrs.pop('max', None)

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        deadline = cleaned_data.get('deadline')
        dependencies = cleaned_data.get('dependencies', [])

        # 验证日期逻辑
        if start_date and end_date:
            if start_date > end_date:
                raise forms.ValidationError('开始日期不能晚于结束日期')

        if end_date and deadline:
            if end_date > deadline:
                raise forms.ValidationError('结束日期不能晚于截止时间')

        # 验证依赖关系
        if self.instance.pk:
            for dep in dependencies:
                if self.instance.has_circular_dependency(dep):
                    raise forms.ValidationError(f'与任务"{dep.name}"存在循环依赖关系')

        return cleaned_data

    def clean_deadline(self):
        """验证截止时间"""
        deadline = self.cleaned_data.get('deadline')
        if deadline and deadline < date.today():
            raise forms.ValidationError('截止时间不能是过去的日期')
        return deadline


class SubtaskCreateForm(forms.ModelForm):
    """子任务创建表单"""

    # 显式定义日期字段
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }, format='%Y-%m-%d'),
        input_formats=['%Y-%m-%d'],
        label='开始日期'
    )

    end_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }, format='%Y-%m-%d'),
        input_formats=['%Y-%m-%d'],
        label='结束日期'
    )

    class Meta:
        model = Task
        fields = ['name', 'description', 'task_type', 'responsible_person', 'start_date', 'end_date', 'deadline', 'status']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入子任务名称',
                'maxlength': 200
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '请输入子任务描述（可选）'
            }),
            'task_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'responsible_person': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入负责人姓名',
                'maxlength': 100
            }),
            'deadline': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'min': date.today().strftime('%Y-%m-%d')
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            })
        }
        labels = {
            'name': '子任务名称',
            'description': '子任务描述',
            'task_type': '任务类型',
            'responsible_person': '负责人',
            'start_date': '开始日期',
            'end_date': '结束日期',
            'deadline': '截止时间',
            'status': '状态'
        }

    def __init__(self, *args, **kwargs):
        parent_task = kwargs.pop('parent_task', None)
        super().__init__(*args, **kwargs)

        # 设置默认日期和类型（仅新建子任务）
        if not self.instance.pk and parent_task:
            # 默认日期范围在父任务范围内
            self.fields['start_date'].initial = parent_task.start_date or date.today()
            self.fields['end_date'].initial = parent_task.end_date or (date.today() + timedelta(days=3))
            self.fields['deadline'].initial = parent_task.deadline or (date.today() + timedelta(days=3))

            # 设置默认任务类型为父任务类型
            self.fields['task_type'].initial = parent_task.task_type

            # 设置日期范围限制
            if parent_task.start_date:
                self.fields['start_date'].widget.attrs['min'] = parent_task.start_date.isoformat()
            if parent_task.end_date:
                self.fields['end_date'].widget.attrs['max'] = parent_task.end_date.isoformat()
            if parent_task.deadline:
                self.fields['deadline'].widget.attrs['max'] = parent_task.deadline.isoformat()
        elif not self.instance.pk:
            # 没有父任务时的默认值
            today = date.today()
            self.fields['start_date'].initial = today
            self.fields['end_date'].initial = today + timedelta(days=3)
            self.fields['deadline'].initial = today + timedelta(days=3)

    def clean(self):
        """验证子任务数据"""
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        deadline = cleaned_data.get('deadline')

        # 验证日期逻辑
        if start_date and end_date:
            if start_date > end_date:
                raise forms.ValidationError('开始日期不能晚于结束日期')

        if end_date and deadline:
            if end_date > deadline:
                raise forms.ValidationError('结束日期不能晚于截止时间')

        return cleaned_data

    def clean_deadline(self):
        """验证截止时间"""
        deadline = self.cleaned_data.get('deadline')
        if deadline and deadline < date.today():
            raise forms.ValidationError('截止时间不能是过去的日期')
        return deadline


class SubtaskUpdateForm(forms.ModelForm):
    """子任务更新表单（仅状态）"""

    class Meta:
        model = Task
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-select form-select-sm'
            })
        }


class TaskDependencyForm(forms.ModelForm):
    """任务依赖关系表单"""

    class Meta:
        model = TaskDependency
        fields = ['predecessor', 'dependency_type', 'lag_days']
        widgets = {
            'predecessor': forms.Select(attrs={
                'class': 'form-select'
            }),
            'dependency_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'lag_days': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '-365',
                'max': '365',
                'value': '0'
            })
        }
        labels = {
            'predecessor': '前置任务',
            'dependency_type': '依赖类型',
            'lag_days': '滞后天数'
        }

    def __init__(self, *args, **kwargs):
        successor_task = kwargs.pop('successor_task', None)
        super().__init__(*args, **kwargs)

        if successor_task:
            # 设置可选的前置任务（排除自己和已有依赖）
            available_tasks = Task.objects.filter(worksite=successor_task.worksite)
            available_tasks = available_tasks.exclude(pk=successor_task.pk)

            # 排除已有的依赖任务
            existing_deps = successor_task.dependencies.all()
            available_tasks = available_tasks.exclude(pk__in=[dep.pk for dep in existing_deps])

            self.fields['predecessor'].queryset = available_tasks

    def clean(self):
        cleaned_data = super().clean()
        predecessor = cleaned_data.get('predecessor')

        if predecessor and hasattr(self, 'successor_task'):
            # 检查循环依赖
            if self.successor_task.has_circular_dependency(predecessor):
                raise forms.ValidationError(f'与任务"{predecessor.name}"存在循环依赖关系')

        return cleaned_data


class TaskDrawingSelectForm(forms.Form):
    """任务创建表单 - 步骤2：选择关联图纸"""

    drawing = forms.ModelChoiceField(
        queryset=Drawing.objects.all(),
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        }),
        empty_label=None,
        label='选择关联图纸'
    )

    def __init__(self, *args, **kwargs):
        # 可以传入预选的图纸ID
        preselected_drawing_id = kwargs.pop('preselected_drawing_id', None)
        super().__init__(*args, **kwargs)

        # 按上传时间倒序排列图纸
        self.fields['drawing'].queryset = Drawing.objects.all().order_by('-uploaded_at')

        # 如果有预选图纸，设置为初始值
        if preselected_drawing_id:
            try:
                drawing = Drawing.objects.get(id=preselected_drawing_id)
                self.fields['drawing'].initial = drawing
            except Drawing.DoesNotExist:
                pass

    def clean_drawing(self):
        """验证选择的图纸"""
        drawing = self.cleaned_data.get('drawing')
        if not drawing:
            raise forms.ValidationError('请选择一张图纸')
        return drawing


class ProjectTaskCreateForm(forms.ModelForm):
    """项目内任务创建表单"""

    drawings = forms.ModelMultipleChoiceField(
        queryset=Drawing.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        }),
        label='关联图纸'
    )

    class Meta:
        model = Task
        fields = ['name', 'description', 'task_type', 'responsible_person', 'deadline', 'drawings']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入任务名称，如：3层东墙砌筑施工'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '请输入任务描述（可选）'
            }),
            'task_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'responsible_person': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入负责人姓名'
            }),
            'deadline': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'min': timezone.now().date().isoformat()
            })
        }
        labels = {
            'name': '任务名称',
            'description': '任务描述',
            'task_type': '任务类型',
            'responsible_person': '负责人',
            'deadline': '截止时间',
            'drawings': '关联图纸'
        }

    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)

        # 设置默认截止时间为3天后
        if not self.instance.pk:
            self.fields['deadline'].initial = date.today() + timedelta(days=3)
        else:
            # 编辑任务时，移除最小日期限制
            self.fields['deadline'].widget.attrs.pop('min', None)

        # 如果指定了项目，只显示该项目下所有工地的图纸
        if project:
            # 获取项目下所有工地的图纸
            project_drawings = Drawing.objects.filter(worksite__project=project)
            self.fields['drawings'].queryset = project_drawings
            if not project_drawings.exists():
                self.fields['drawings'].help_text = '该项目还没有图纸，请先在工地中上传图纸'
        else:
            self.fields['drawings'].queryset = Drawing.objects.all()
