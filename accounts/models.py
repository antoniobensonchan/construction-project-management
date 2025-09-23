from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """扩展用户模型"""
    company_name = models.CharField(max_length=200, verbose_name='公司名称', blank=True)
    phone = models.CharField(max_length=20, verbose_name='联系电话', blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='注册时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'

    def __str__(self):
        return f"{self.username} ({self.company_name})"
