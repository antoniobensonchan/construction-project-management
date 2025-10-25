#!/usr/bin/env python
"""
为甘特图演示项目添加任务
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

def add_gantt_tasks():
    """为甘特图演示项目添加任务"""
    
    print('🏗️  为甘特图演示项目添加任务...\n')
    
    # 获取甘特图演示项目
    try:
        project = Project.objects.get(name='甘特图演示项目')
        print(f'✅ 找到项目: {project.name}')
    except Project.DoesNotExist:
        print('❌ 未找到甘特图演示项目')
        return
    
    # 获取工地
    try:
        main_worksite = WorkSite.objects.get(project=project, name='主楼施工区')
        garage_worksite = WorkSite.objects.get(project=project, name='地下车库施工区')
        print(f'✅ 找到工地: {main_worksite.name}, {garage_worksite.name}')
    except WorkSite.DoesNotExist:
        print('❌ 未找到所需工地')
        return
    
    # 定义主楼施工区的任务
    main_site_tasks = [
        {
            'name': '地基工程',
            'description': '主楼地基施工',
            'task_type': 'new_construction',
            'responsible_person': '王工',
            'start_date': date(2025, 10, 26),
            'end_date': date(2025, 11, 10),
            'status': 'in_progress',
            'subtasks': [
                {
                    'name': '地质勘探',
                    'description': '地质勘探作业',
                    'task_type': 'new_construction',
                    'responsible_person': '张师傅',
                    'start_date': date(2025, 10, 26),
                    'end_date': date(2025, 10, 31),
                    'status': 'completed'
                },
                {
                    'name': '基坑开挖',
                    'description': '基坑开挖作业',
                    'task_type': 'new_construction',
                    'responsible_person': '李师傅',
                    'start_date': date(2025, 10, 31),
                    'end_date': date(2025, 11, 5),
                    'status': 'completed'
                },
                {
                    'name': '地基浇筑',
                    'description': '地基混凝土浇筑',
                    'task_type': 'new_construction',
                    'responsible_person': '赵师傅',
                    'start_date': date(2025, 11, 5),
                    'end_date': date(2025, 11, 10),
                    'status': 'in_progress'
                }
            ]
        },
        {
            'name': '主体结构',
            'description': '主楼主体结构施工',
            'task_type': 'new_construction',
            'responsible_person': '王工',
            'start_date': date(2025, 11, 5),
            'end_date': date(2025, 12, 15),
            'status': 'pending',
            'subtasks': [
                {
                    'name': '1-5层结构',
                    'description': '办公楼1-5层结构施工',
                    'task_type': 'new_construction',
                    'responsible_person': '王工',
                    'start_date': date(2025, 11, 5),
                    'end_date': date(2025, 11, 25),
                    'status': 'pending'
                },
                {
                    'name': '6-10层结构',
                    'description': '办公楼6-10层结构施工',
                    'task_type': 'new_construction',
                    'responsible_person': '王工',
                    'start_date': date(2025, 11, 25),
                    'end_date': date(2025, 12, 10),
                    'status': 'pending'
                },
                {
                    'name': '11-15层结构',
                    'description': '办公楼11-15层结构施工',
                    'task_type': 'new_construction',
                    'responsible_person': '王工',
                    'start_date': date(2025, 12, 10),
                    'end_date': date(2025, 12, 15),
                    'status': 'pending'
                }
            ]
        },
        {
            'name': '机电安装',
            'description': '主楼机电设备安装',
            'task_type': 'new_construction',
            'responsible_person': '陈工',
            'start_date': date(2025, 12, 10),
            'end_date': date(2026, 1, 10),
            'status': 'pending',
            'subtasks': [
                {
                    'name': '电气系统',
                    'description': '电气系统安装',
                    'task_type': 'new_construction',
                    'responsible_person': '陈工',
                    'start_date': date(2025, 12, 10),
                    'end_date': date(2025, 12, 25),
                    'status': 'pending'
                },
                {
                    'name': '暖通空调',
                    'description': '暖通空调系统安装',
                    'task_type': 'new_construction',
                    'responsible_person': '陈工',
                    'start_date': date(2025, 12, 20),
                    'end_date': date(2026, 1, 5),
                    'status': 'pending'
                },
                {
                    'name': '给排水系统',
                    'description': '给排水系统安装',
                    'task_type': 'new_construction',
                    'responsible_person': '陈工',
                    'start_date': date(2025, 12, 30),
                    'end_date': date(2026, 1, 10),
                    'status': 'pending'
                }
            ]
        }
    ]
    
    # 定义地下车库施工区的任务
    garage_site_tasks = [
        {
            'name': '地下结构',
            'description': '地下车库结构施工',
            'task_type': 'new_construction',
            'responsible_person': '李工',
            'start_date': date(2025, 11, 5),
            'end_date': date(2025, 12, 5),
            'status': 'pending',
            'subtasks': [
                {
                    'name': '地下开挖',
                    'description': '地下车库开挖作业',
                    'task_type': 'new_construction',
                    'responsible_person': '李工',
                    'start_date': date(2025, 11, 5),
                    'end_date': date(2025, 11, 15),
                    'status': 'pending'
                },
                {
                    'name': '结构施工',
                    'description': '地下车库结构施工',
                    'task_type': 'new_construction',
                    'responsible_person': '李工',
                    'start_date': date(2025, 11, 15),
                    'end_date': date(2025, 12, 5),
                    'status': 'pending'
                }
            ]
        },
        {
            'name': '设备安装',
            'description': '地下车库设备安装',
            'task_type': 'new_construction',
            'responsible_person': '李工',
            'start_date': date(2025, 12, 1),
            'end_date': date(2026, 1, 5),
            'status': 'pending',
            'subtasks': [
                {
                    'name': '通风系统',
                    'description': '地下车库通风系统安装',
                    'task_type': 'new_construction',
                    'responsible_person': '李工',
                    'start_date': date(2025, 12, 1),
                    'end_date': date(2025, 12, 15),
                    'status': 'pending'
                },
                {
                    'name': '照明系统',
                    'description': '地下车库照明系统安装',
                    'task_type': 'new_construction',
                    'responsible_person': '李工',
                    'start_date': date(2025, 12, 10),
                    'end_date': date(2025, 12, 25),
                    'status': 'pending'
                },
                {
                    'name': '消防系统',
                    'description': '地下车库消防系统安装',
                    'task_type': 'new_construction',
                    'responsible_person': '李工',
                    'start_date': date(2025, 12, 20),
                    'end_date': date(2026, 1, 5),
                    'status': 'pending'
                }
            ]
        }
    ]
    
    # 创建主楼施工区的任务
    print(f'\n📋 为主楼施工区创建任务:')
    for task_data in main_site_tasks:
        subtasks_data = task_data.pop('subtasks', [])
        # 设置deadline以保持向后兼容
        task_data['deadline'] = task_data['end_date']
        
        task, created = Task.objects.get_or_create(
            name=task_data['name'],
            worksite=main_worksite,
            defaults=task_data
        )
        if created:
            print(f'   ✅ 创建任务: {task.name} ({task.start_date} to {task.end_date})')
        else:
            print(f'   ℹ️  任务已存在: {task.name} ({task.start_date} to {task.end_date})')
            
        # 创建子任务
        for subtask_data in subtasks_data:
            subtask_data['worksite'] = main_worksite
            subtask_data['parent_task'] = task
            # 设置deadline以保持向后兼容
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
    
    # 创建地下车库施工区的任务
    print(f'\n📋 为地下车库施工区创建任务:')
    for task_data in garage_site_tasks:
        subtasks_data = task_data.pop('subtasks', [])
        # 设置deadline以保持向后兼容
        task_data['deadline'] = task_data['end_date']
        
        task, created = Task.objects.get_or_create(
            name=task_data['name'],
            worksite=garage_worksite,
            defaults=task_data
        )
        if created:
            print(f'   ✅ 创建任务: {task.name} ({task.start_date} to {task.end_date})')
        else:
            print(f'   ℹ️  任务已存在: {task.name} ({task.start_date} to {task.end_date})')
            
        # 创建子任务
        for subtask_data in subtasks_data:
            subtask_data['worksite'] = garage_worksite
            subtask_data['parent_task'] = task
            # 设置deadline以保持向后兼容
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
    
    # 显示统计信息
    print(f'\n📊 甘特图任务统计:')
    print(f'   项目: {project.name}')
    print(f'   工地: {main_worksite.name}, {garage_worksite.name}')
    print(f'   主任务数量: {Task.objects.filter(worksite__project=project, parent_task__isnull=True).count()}')
    print(f'   子任务数量: {Task.objects.filter(worksite__project=project, parent_task__isnull=False).count()}')
    print(f'   总任务数量: {Task.objects.filter(worksite__project=project).count()}')
    
    print(f'\n✅ 甘特图任务创建完成！')
    print(f'现在可以访问甘特图页面查看具有不同日期的任务展示效果！')

if __name__ == '__main__':
    try:
        add_gantt_tasks()
    except Exception as e:
        print(f'❌ 创建任务时出错: {e}')
        import traceback
        traceback.print_exc()