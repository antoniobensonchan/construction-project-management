#!/usr/bin/env python
"""
创建用于甘特图展示的演示数据
用户 → 项目 → 工地 → 任务 → 子任务
任务将具有不同的开始和结束日期，以便在甘特图上更好地展示
"""
import os
import django
from datetime import date, timedelta

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_pm.settings')
django.setup()

from django.contrib.auth import get_user_model
from projects.models import Project, WorkSite
from tasks.models import Task

User = get_user_model()

def create_gantt_demo_data():
    """创建用于甘特图展示的演示数据"""

    print('🏗️  创建甘特图演示数据...\n')

    # 1. 获取或创建演示用户
    print('1. 获取演示用户:')

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

    # 2. 获取或创建项目
    print('\n2. 获取演示项目:')

    projects_data = [
        # 公司A的项目
        {
            'owner': created_users[0],
            'name': '现代办公大楼建设项目',
            'description': '位于市中心的30层现代化办公大楼，总建筑面积50000平方米',
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=90),
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

    # 3. 获取或创建工地
    print('\n3. 获取工地:')

    worksites_data = [
        # 项目1的工地
        {
            'project': created_projects[0],
            'name': '主楼施工区',
            'description': '办公大楼主体建筑施工区域',
            'location': '北京市朝阳区CBD核心区A地块',
            'site_manager': '王工',
            'contact_phone': '13900139001',
            'status': 'active',
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=60)
        },
        {
            'project': created_projects[0],
            'name': '地下车库施工区',
            'description': '地下三层车库施工区域',
            'location': '北京市朝阳区CBD核心区B地块',
            'site_manager': '李工',
            'contact_phone': '13900139002',
            'status': 'active',
            'start_date': date.today() + timedelta(days=10),
            'end_date': date.today() + timedelta(days=50)
        }
    ]

    created_worksites = []
    for worksite_data in worksites_data:
        worksite, created = WorkSite.objects.get_or_create(
            name=worksite_data['name'],
            project=worksite_data['project'],
            defaults=worksite_data
        )
        if created:
            print(f'   ✅ 创建工地: {worksite.name} (项目: {worksite.project.name})')
        else:
            print(f'   ℹ️  工地已存在: {worksite.name} (项目: {worksite.project.name})')
        created_worksites.append(worksite)

    # 4. 为每个工地创建任务和子任务（具有不同的开始和结束日期）
    print('\n4. 创建任务和子任务（具有不同的日期）:')

    # 定义任务数据，包含不同的开始和结束日期
    tasks_data = [
        # 主楼施工区的任务
        {
            'worksite': created_worksites[0],
            'name': '地基工程',
            'description': '主楼地基施工',
            'task_type': 'new_construction',
            'responsible_person': '王工',
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=15),
            'status': 'in_progress',
            'subtasks': [
                {
                    'name': '地质勘探',
                    'description': '地质勘探作业',
                    'task_type': 'new_construction',
                    'responsible_person': '张师傅',
                    'start_date': date.today(),
                    'end_date': date.today() + timedelta(days=5),
                    'status': 'completed'
                },
                {
                    'name': '基坑开挖',
                    'description': '基坑开挖作业',
                    'task_type': 'new_construction',
                    'responsible_person': '李师傅',
                    'start_date': date.today() + timedelta(days=5),
                    'end_date': date.today() + timedelta(days=10),
                    'status': 'completed'
                },
                {
                    'name': '地基浇筑',
                    'description': '地基混凝土浇筑',
                    'task_type': 'new_construction',
                    'responsible_person': '赵师傅',
                    'start_date': date.today() + timedelta(days=10),
                    'end_date': date.today() + timedelta(days=15),
                    'status': 'in_progress'
                }
            ]
        },
        {
            'worksite': created_worksites[0],
            'name': '主体结构',
            'description': '主楼主体结构施工',
            'task_type': 'new_construction',
            'responsible_person': '王工',
            'start_date': date.today() + timedelta(days=10),
            'end_date': date.today() + timedelta(days=40),
            'status': 'pending',
            'subtasks': [
                {
                    'name': '1-5层结构',
                    'description': '办公楼1-5层结构施工',
                    'task_type': 'new_construction',
                    'responsible_person': '王工',
                    'start_date': date.today() + timedelta(days=10),
                    'end_date': date.today() + timedelta(days=25),
                    'status': 'pending'
                },
                {
                    'name': '6-10层结构',
                    'description': '办公楼6-10层结构施工',
                    'task_type': 'new_construction',
                    'responsible_person': '王工',
                    'start_date': date.today() + timedelta(days=25),
                    'end_date': date.today() + timedelta(days=40),
                    'status': 'pending'
                }
            ]
        },
        {
            'worksite': created_worksites[0],
            'name': '机电安装',
            'description': '主楼机电设备安装',
            'task_type': 'new_construction',
            'responsible_person': '陈工',
            'start_date': date.today() + timedelta(days=35),
            'end_date': date.today() + timedelta(days=55),
            'status': 'pending',
            'subtasks': [
                {
                    'name': '电气系统',
                    'description': '电气系统安装',
                    'task_type': 'new_construction',
                    'responsible_person': '陈工',
                    'start_date': date.today() + timedelta(days=35),
                    'end_date': date.today() + timedelta(days=45),
                    'status': 'pending'
                },
                {
                    'name': '暖通空调',
                    'description': '暖通空调系统安装',
                    'task_type': 'new_construction',
                    'responsible_person': '陈工',
                    'start_date': date.today() + timedelta(days=40),
                    'end_date': date.today() + timedelta(days=50),
                    'status': 'pending'
                },
                {
                    'name': '给排水系统',
                    'description': '给排水系统安装',
                    'task_type': 'new_construction',
                    'responsible_person': '陈工',
                    'start_date': date.today() + timedelta(days=45),
                    'end_date': date.today() + timedelta(days=55),
                    'status': 'pending'
                }
            ]
        },
        # 地下车库施工区的任务
        {
            'worksite': created_worksites[1],
            'name': '地下结构',
            'description': '地下车库结构施工',
            'task_type': 'new_construction',
            'responsible_person': '李工',
            'start_date': date.today() + timedelta(days=10),
            'end_date': date.today() + timedelta(days=35),
            'status': 'pending',
            'subtasks': [
                {
                    'name': '地下开挖',
                    'description': '地下车库开挖作业',
                    'task_type': 'new_construction',
                    'responsible_person': '李工',
                    'start_date': date.today() + timedelta(days=10),
                    'end_date': date.today() + timedelta(days=20),
                    'status': 'pending'
                },
                {
                    'name': '结构施工',
                    'description': '地下车库结构施工',
                    'task_type': 'new_construction',
                    'responsible_person': '李工',
                    'start_date': date.today() + timedelta(days=20),
                    'end_date': date.today() + timedelta(days=35),
                    'status': 'pending'
                }
            ]
        },
        {
            'worksite': created_worksites[1],
            'name': '设备安装',
            'description': '地下车库设备安装',
            'task_type': 'new_construction',
            'responsible_person': '李工',
            'start_date': date.today() + timedelta(days=30),
            'end_date': date.today() + timedelta(days=50),
            'status': 'pending',
            'subtasks': [
                {
                    'name': '通风系统',
                    'description': '地下车库通风系统安装',
                    'task_type': 'new_construction',
                    'responsible_person': '李工',
                    'start_date': date.today() + timedelta(days=30),
                    'end_date': date.today() + timedelta(days=40),
                    'status': 'pending'
                },
                {
                    'name': '照明系统',
                    'description': '地下车库照明系统安装',
                    'task_type': 'new_construction',
                    'responsible_person': '李工',
                    'start_date': date.today() + timedelta(days=35),
                    'end_date': date.today() + timedelta(days=45),
                    'status': 'pending'
                },
                {
                    'name': '消防系统',
                    'description': '地下车库消防系统安装',
                    'task_type': 'new_construction',
                    'responsible_person': '李工',
                    'start_date': date.today() + timedelta(days=40),
                    'end_date': date.today() + timedelta(days=50),
                    'status': 'pending'
                }
            ]
        }
    ]

    created_tasks = []
    for task_data in tasks_data:
        # 创建主任务
        subtasks_data = task_data.pop('subtasks', [])
        # 确保deadline设置为end_date（为了向后兼容）
        task_data['deadline'] = task_data['end_date']
        
        task, created = Task.objects.get_or_create(
            name=task_data['name'],
            worksite=task_data['worksite'],
            defaults=task_data
        )
        if created:
            print(f'   ✅ 创建任务: {task.name} ({task.start_date} to {task.end_date})')
        else:
            print(f'   ℹ️  任务已存在: {task.name} ({task.start_date} to {task.end_date})')
        created_tasks.append(task)

        # 创建子任务
        for subtask_data in subtasks_data:
            subtask_data['worksite'] = task.worksite
            subtask_data['parent_task'] = task
            # 确保deadline设置为end_date（为了向后兼容）
            subtask_data['deadline'] = subtask_data['end_date']
            
            subtask, created = Task.objects.get_or_create(
                name=subtask_data['name'],
                parent_task=task,
                defaults=subtask_data
            )
            if created:
                print(f'     ✅ 创建子任务: {subtask.name} ({subtask.start_date} to {subtask.end_date})')
            else:
                print(f'     ℹ️  子任务已存在: {subtask.name} ({subtask.start_date} to {subtask.end_date})')

    # 5. 统计信息
    print(f'\n📊 甘特图数据统计:')
    print(f'   用户数量: {User.objects.count()}')
    print(f'   项目数量: {Project.objects.count()}')
    print(f'   工地数量: {WorkSite.objects.count()}')
    print(f'   任务数量: {Task.objects.count()}')
    print(f'   主任务数量: {Task.objects.filter(parent_task__isnull=True).count()}')
    print(f'   子任务数量: {Task.objects.filter(parent_task__isnull=False).count()}')

    # 6. 展示层次结构
    print(f'\n🏗️  数据层次结构:')
    for user in created_users:
        print(f'👤 {user.company_name} ({user.username})')
        for project in user.owned_projects.all():
            print(f'  📁 {project.name}')
            for worksite in project.worksites.all():
                print(f'    🏗️  {worksite.name} ({worksite.start_date} to {worksite.end_date})')
                main_tasks = worksite.tasks.filter(parent_task__isnull=True)
                for task in main_tasks:
                    print(f'      📋 {task.name} ({task.start_date} to {task.end_date}) [{task.get_status_display()}]')
                    for subtask in task.subtasks.all():
                        print(f'        📝 {subtask.name} ({subtask.start_date} to {subtask.end_date}) [{subtask.get_status_display()}]')

    print(f'\n🌐 测试页面:')
    print(f'   登录页面: http://127.0.0.1:8000/accounts/login/')
    print(f'   项目列表: http://127.0.0.1:8000/projects/')
    print(f'   甘特图页面: http://127.0.0.1:8000/gantt/')

    print(f'\n🔐 测试账户:')
    print(f'   账户1: company_a / demo123 (建筑公司A)')
    print(f'   账户2: company_b / demo123 (建筑公司B)')

    print(f'\n✅ 甘特图演示数据创建完成！')
    print(f'现在可以查看具有不同日期的任务在甘特图上的展示效果！')

    return created_users, created_projects, created_worksites, created_tasks

if __name__ == '__main__':
    try:
        create_gantt_demo_data()
    except Exception as e:
        print(f'❌ 创建演示数据时出错: {e}')
        import traceback
        traceback.print_exc()