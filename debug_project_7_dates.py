#!/usr/bin/env python
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_pm.settings')
django.setup()

from projects.models import Project

def debug_project_7_dates():
    """调试项目7的日期数据"""

    print('🔍 调试项目7的日期数据...\n')

    try:
        project = Project.objects.get(pk=7)
        print(f'📋 项目: {project.name}')
        print(f'   ID: {project.pk}')
        print(f'   开始日期: {project.start_date}')
        print(f'   开始日期类型: {type(project.start_date)}')
        print(f'   结束日期: {project.end_date}')
        print(f'   结束日期类型: {type(project.end_date)}')

        if project.start_date:
            print(f'   开始日期ISO格式: {project.start_date.isoformat()}')
            print(f'   开始日期字符串: {project.start_date.strftime("%Y-%m-%d")}')

        if project.end_date:
            print(f'   结束日期ISO格式: {project.end_date.isoformat()}')
            print(f'   结束日期字符串: {project.end_date.strftime("%Y-%m-%d")}')

        print(f'\n🌐 测试页面: http://127.0.0.1:8000/projects/{project.pk}/update/')

        return project

    except Project.DoesNotExist:
        print('❌ 项目7不存在')
        return None

if __name__ == '__main__':
    debug_project_7_dates()
