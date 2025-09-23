from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomLoginView(LoginView):
    """自定义登录视图"""
    form_class = CustomAuthenticationForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('projects:project_list')

    def form_valid(self, form):
        messages.success(self.request, f'欢迎回来，{form.get_user().username}！')
        return super().form_valid(form)

class CustomLogoutView(LogoutView):
    """自定义登出视图"""
    next_page = reverse_lazy('accounts:login')

    def dispatch(self, request, *args, **kwargs):
        messages.info(request, '您已成功登出')
        return super().dispatch(request, *args, **kwargs)

class SignUpView(CreateView):
    """用户注册视图"""
    form_class = CustomUserCreationForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('projects:project_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=password)
        login(self.request, user)
        messages.success(self.request, f'欢迎加入，{user.username}！注册成功')
        return response

@login_required
def profile_view(request):
    """用户资料查看"""
    return render(request, 'accounts/profile.html', {
        'user': request.user
    })

class ProfileUpdateView(UpdateView):
    """用户资料编辑视图"""
    model = User
    form_class = UserProfileForm
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('accounts:profile')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, '资料更新成功！')
        return super().form_valid(form)
