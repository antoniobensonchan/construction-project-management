from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    """自定义用户注册表单"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入邮箱地址'
        })
    )
    company_name = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入公司名称'
        })
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入联系电话（可选）'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'company_name', 'phone', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '请输入用户名'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '请输入密码'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '请确认密码'
        })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.company_name = self.cleaned_data['company_name']
        user.phone = self.cleaned_data['phone']
        if commit:
            user.save()
        return user

class CustomAuthenticationForm(AuthenticationForm):
    """自定义登录表单"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '请输入用户名或邮箱'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '请输入密码'
        })

class UserProfileForm(forms.ModelForm):
    """用户资料编辑表单"""

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'company_name', 'phone')
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入姓'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入名'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入邮箱地址'
            }),
            'company_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入公司名称'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入联系电话'
            }),
        }
