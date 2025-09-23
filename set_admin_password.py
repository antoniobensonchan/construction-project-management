#!/usr/bin/env python
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_pm.settings')
django.setup()

from django.contrib.auth.models import User

try:
    user = User.objects.get(username='admin')
    user.set_password('admin123')
    user.save()
    print('Admin password set to: admin123')
except User.DoesNotExist:
    print('Admin user not found')
