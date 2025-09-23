#!/usr/bin/env python
import os
import django
from datetime import date, timedelta

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_pm.settings')
django.setup()

from projects.models import Project

def create_sample_projects():
    """创建示例项目数据"""

    # 项目1：阳光花园3号楼
    project1, created = Project.objects.get_or_create(
        name='阳光花园3号楼建设项目',
        defaults={
            'description': '地上18层住宅楼，框架结构，总建筑面积约15000平方米',
            'start_date': date.today() - timedelta(days=30),
            'end_date': date.today() + timedelta(days=180),
            'status': 'active'
        }
    )
    if created:
        print(f'✅ 创建项目: {project1.name}')
    else:
        print(f'📋 项目已存在: {project1.name}')

    # 项目2：商业综合体
    project2, created = Project.objects.get_or_create(
        name='城市商业综合体项目',
        defaults={
            'description': '集购物、餐饮、娱乐于一体的大型商业综合体，地下2层，地上6层',
            'start_date': date.today() - timedelta(days=60),
            'end_date': date.today() + timedelta(days=300),
            'status': 'active'
        }
    )
    if created:
        print(f'✅ 创建项目: {project2.name}')
    else:
        print(f'📋 项目已存在: {project2.name}')

    # 项目3：办公楼改造
    project3, created = Project.objects.get_or_create(
        name='老旧办公楼改造项目',
        defaults={
            'description': '对建于1990年代的办公楼进行现代化改造，包括外立面、内部装修和设备更新',
            'start_date': date.today() + timedelta(days=15),
            'end_date': date.today() + timedelta(days=120),
            'status': 'planning'
        }
    )
    if created:
        print(f'✅ 创建项目: {project3.name}')
    else:
        print(f'📋 项目已存在: {project3.name}')

    # 项目4：已完成项目
    project4, created = Project.objects.get_or_create(
        name='学校教学楼建设项目',
        defaults={
            'description': '新建5层教学楼，包含30间教室和配套设施',
            'start_date': date.today() - timedelta(days=200),
            'end_date': date.today() - timedelta(days=30),
            'status': 'completed'
        }
    )
    if created:
        print(f'✅ 创建项目: {project4.name}')
    else:
        print(f'📋 项目已存在: {project4.name}')

    print(f'\n📊 项目统计:')
    print(f'   总项目数: {Project.objects.count()}')
    print(f'   进行中: {Project.objects.filter(status="active").count()}')
    print(f'   规划中: {Project.objects.filter(status="planning").count()}')
    print(f'   已完成: {Project.objects.filter(status="completed").count()}')

    return [project1, project2, project3, project4]

if __name__ == '__main__':
    print('🏗️ 创建示例项目数据...\n')
    projects = create_sample_projects()
    print(f'\n✅ 示例数据创建完成！')
    print(f'🌐 访问 http://127.0.0.1:8000/ 查看项目列表')
