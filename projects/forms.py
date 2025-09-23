from django import forms
from django.utils import timezone
from datetime import date, timedelta
from .models import Project, WorkSite


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


class WorkSiteForm(forms.ModelForm):
    """工地创建/编辑表单"""

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
        model = WorkSite
        fields = ['name', 'description', 'location', 'site_manager', 'contact_phone', 'start_date', 'end_date', 'status']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入工地名称，如：主楼施工区'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '请输入工地描述，如：办公大楼主体建筑施工区域'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入工地地址，如：北京市朝阳区CBD核心区A地块'
            }),
            'site_manager': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入工地负责人，如：王工'
            }),
            'contact_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入联系电话，如：13900139001'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            })
        }
        labels = {
            'name': '工地名称',
            'description': '工地描述',
            'location': '工地地址',
            'site_manager': '工地负责人',
            'contact_phone': '联系电话',
            'start_date': '开始日期',
            'end_date': '结束日期',
            'status': '工地状态'
        }

    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)

        # 新建工地时设置默认值
        if not self.instance.pk:
            # 默认状态为准备中
            self.fields['status'].initial = 'preparing'

            # 如果有项目信息，设置默认日期范围
            if project:
                self.fields['start_date'].initial = project.start_date
                self.fields['end_date'].initial = project.end_date

                # 设置日期范围限制
                if project.start_date:
                    self.fields['start_date'].widget.attrs['min'] = project.start_date.isoformat()
                if project.end_date:
                    self.fields['end_date'].widget.attrs['max'] = project.end_date.isoformat()
            else:
                # 默认开始日期为今天
                self.fields['start_date'].initial = date.today()
                # 默认结束日期为1个月后
                self.fields['end_date'].initial = date.today() + timedelta(days=30)
        else:
            # 编辑工地时移除日期限制
            self.fields['start_date'].widget.attrs.pop('min', None)
            self.fields['end_date'].widget.attrs.pop('max', None)

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

            # 检查工地持续时间是否合理（不超过2年）
            duration = (end_date - start_date).days
            if duration > 730:  # 2年
                raise forms.ValidationError('工地持续时间不能超过2年')

            if duration < 1:
                raise forms.ValidationError('工地至少需要持续1天')

        return cleaned_data
