from django import forms
from django.utils import timezone
from datetime import date, timedelta
from .models import Project


class ProjectForm(forms.ModelForm):
    """项目创建/编辑表单"""

    # 显式定义日期字段以确保格式正确
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
        model = Project
        fields = ['name', 'description', 'start_date', 'end_date', 'status']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入项目名称，如：阳光花园3号楼建设项目'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': '请输入项目描述，如：地上18层住宅楼，框架结构'
            }),

            'status': forms.Select(attrs={
                'class': 'form-select'
            })
        }
        labels = {
            'name': '项目名称',
            'description': '项目描述',
            'start_date': '开始日期',
            'end_date': '结束日期',
            'status': '项目状态'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 新建项目时设置默认值
        if not self.instance.pk:
            # 默认开始日期为今天
            self.fields['start_date'].initial = date.today()
            # 默认结束日期为3个月后
            self.fields['end_date'].initial = date.today() + timedelta(days=90)
            # 默认状态为规划中
            self.fields['status'].initial = 'planning'

            # 设置日期限制
            self.fields['start_date'].widget.attrs['min'] = date.today().isoformat()
        else:
            # 编辑项目时移除日期限制
            self.fields['start_date'].widget.attrs.pop('min', None)
            self.fields['end_date'].widget.attrs.pop('min', None)

            # 确保日期字段显示现有值
            if self.instance.start_date:
                self.fields['start_date'].initial = self.instance.start_date
            if self.instance.end_date:
                self.fields['end_date'].initial = self.instance.end_date

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date:
            if start_date > end_date:
                raise forms.ValidationError('开始日期不能晚于结束日期')

            # 检查项目持续时间是否合理（不超过5年）
            duration = (end_date - start_date).days
            if duration > 1825:  # 5年
                raise forms.ValidationError('项目持续时间不能超过5年')

            if duration < 1:
                raise forms.ValidationError('项目至少需要持续1天')

        return cleaned_data
