#!/usr/bin/env python
"""
最终演示设置脚本
创建完整的演示数据，展示新的UI和用户认证系统
"""
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_pm.settings')
django.setup()

from django.contrib.auth import get_user_model
from projects.models import Project
from drawings.models import Drawing
from tasks.models import Task, TaskAnnotation
from datetime import date, timedelta

User = get_user_model()

def create_demo_data():
    """创建完整的演示数据"""

    print('🎨 创建完整演示数据...\n')

    # 1. 创建演示用户
    print('1. 创建演示用户:')

    users_data = [
        {
            'username': 'company_a',
            'email': 'admin@company-a.com',
            'company_name': '建筑公司A',
            'phone': '13800138001',
            'first_name': '张',
            'last_name': '总'
        },
        {
            'username': 'company_b',
            'email': 'admin@company-b.com',
            'company_name': '建筑公司B',
            'phone': '13800138002',
            'first_name': '李',
            'last_name': '总'
        },
        {
            'username': 'company_c',
            'email': 'admin@company-c.com',
            'company_name': '建筑公司C',
            'phone': '13800138003',
            'first_name': '王',
            'last_name': '总'
        }
    ]

    created_users = []
    for user_data in users_data:
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults=user_data
        )
        if created:
            user.set_password('demo123')
            user.save()
            print(f'   ✅ 创建用户: {user.username} ({user.company_name})')
        else:
            print(f'   ℹ️  用户已存在: {user.username} ({user.company_name})')
        created_users.append(user)

    # 2. 为每个用户创建项目
    print('\n2. 创建演示项目:')

    projects_data = [
        # 公司A的项目
        {
            'owner': created_users[0],
            'name': '现代办公大楼建设项目',
            'description': '位于市中心的30层现代化办公大楼，总建筑面积50000平方米',
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=365),
            'status': 'active'
        },
        {
            'owner': created_users[0],
            'name': '高端住宅小区项目',
            'description': '包含5栋高层住宅楼的高端小区开发项目',
            'start_date': date.today() + timedelta(days=30),
            'end_date': date.today() + timedelta(days=500),
            'status': 'planning'
        },
        # 公司B的项目
        {
            'owner': created_users[1],
            'name': '商业综合体建设',
            'description': '集购物、餐饮、娱乐于一体的大型商业综合体',
            'start_date': date.today() - timedelta(days=60),
            'end_date': date.today() + timedelta(days=300),
            'status': 'active'
        },
        {
            'owner': created_users[1],
            'name': '工业园区厂房建设',
            'description': '现代化工业园区标准厂房建设项目',
            'start_date': date.today() + timedelta(days=90),
            'end_date': date.today() + timedelta(days=450),
            'status': 'planning'
        },
        # 公司C的项目
        {
            'owner': created_users[2],
            'name': '学校教学楼改造',
            'description': '某中学教学楼的现代化改造升级项目',
            'start_date': date.today() - timedelta(days=30),
            'end_date': date.today() + timedelta(days=180),
            'status': 'active'
        }
    ]

    created_projects = []
    for project_data in projects_data:
        project, created = Project.objects.get_or_create(
            name=project_data['name'],
            owner=project_data['owner'],
            defaults=project_data
        )
        if created:
            print(f'   ✅ 创建项目: {project.name} (所有者: {project.owner.company_name})')
        else:
            print(f'   ℹ️  项目已存在: {project.name} (所有者: {project.owner.company_name})')
        created_projects.append(project)

    # 3. 统计信息
    print(f'\n📊 演示数据统计:')
    print(f'   用户数量: {User.objects.count()}')
    print(f'   项目数量: {Project.objects.count()}')

    for user in created_users:
        user_projects = user.owned_projects.count()
        print(f'   {user.company_name}: {user_projects} 个项目')

    # 4. 功能展示说明
    print(f'\n🎨 新功能展示:')
    print(f'   ✅ 现代化UI设计 (类似Augment Code风格)')
    print(f'   ✅ 用户认证系统 (注册/登录/登出)')
    print(f'   ✅ 数据隔离 (每个用户只能看到自己的项目)')
    print(f'   ✅ 个人资料管理')
    print(f'   ✅ 响应式设计')
    print(f'   ✅ 现代化导航栏')

    print(f'\n🌐 演示页面:')
    print(f'   登录页面: http://127.0.0.1:8000/accounts/login/')
    print(f'   注册页面: http://127.0.0.1:8000/accounts/signup/')
    print(f'   项目列表: http://127.0.0.1:8000/projects/ (需要登录)')
    print(f'   个人资料: http://127.0.0.1:8000/accounts/profile/ (需要登录)')

    print(f'\n🔐 演示账户:')
    print(f'   账户1: company_a / demo123 (建筑公司A - 2个项目)')
    print(f'   账户2: company_b / demo123 (建筑公司B - 2个项目)')
    print(f'   账户3: company_c / demo123 (建筑公司C - 1个项目)')

    print(f'\n🎯 测试流程:')
    print(f'   1. 访问登录页面，使用演示账户登录')
    print(f'   2. 查看现代化的项目列表页面')
    print(f'   3. 创建新项目测试功能')
    print(f'   4. 查看个人资料页面')
    print(f'   5. 登出后尝试用其他账户登录')
    print(f'   6. 验证数据隔离（每个用户只能看到自己的项目）')

    print(f'\n✨ UI特色:')
    print(f'   - 现代化配色方案')
    print(f'   - 流畅的动画效果')
    print(f'   - 卡片式设计')
    print(f'   - 响应式布局')
    print(f'   - 优雅的表单设计')
    print(f'   - 直观的导航体验')

    print(f'\n🎉 演示数据创建完成！')
    print(f'现在您可以体验完整的现代化建筑项目管理系统！')

    return created_users, created_projects

if __name__ == '__main__':
    try:
        create_demo_data()
    except Exception as e:
        print(f'❌ 创建演示数据时出错: {e}')
        import traceback
        traceback.print_exc()
