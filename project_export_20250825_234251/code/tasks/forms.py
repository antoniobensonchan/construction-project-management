from django import forms
from django.utils import timezone
from datetime import date, timedelta
from .models import Task
from drawings.models import Drawing
from projects.models import Project


class TaskCreateForm(forms.ModelForm):
    """任务创建表单 - 步骤1：填写任务信息"""

    class Meta:
        model = Task
        fields = ['name', 'task_type', 'responsible_person', 'deadline']
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
            'deadline': '截止时间'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 设置默认截止时间为3天后（仅新建任务）
        if not self.instance.pk:
            self.fields['deadline'].initial = date.today() + timedelta(days=3)
        else:
            # 编辑任务时，移除最小日期限制
            self.fields['deadline'].widget.attrs.pop('min', None)

    def clean_deadline(self):
        """验证截止时间"""
        deadline = self.cleaned_data.get('deadline')
        if deadline and deadline < date.today():
            raise forms.ValidationError('截止时间不能是过去的日期')
        return deadline


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

        # 如果指定了项目，只显示该项目的图纸
        if project:
            self.fields['drawings'].queryset = project.drawings.all()
            if not project.drawings.exists():
                self.fields['drawings'].help_text = '该项目还没有图纸，请先上传图纸'
        else:
            self.fields['drawings'].queryset = Drawing.objects.all()
