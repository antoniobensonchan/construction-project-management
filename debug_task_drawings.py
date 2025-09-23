#!/usr/bin/env python
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_pm.settings')
django.setup()

from projects.models import Project
from drawings.models import Drawing
from tasks.models import Task

def debug_task_drawings():
    """调试任务-图纸关联"""

    print('🔍 调试任务-图纸关联...\n')

    project = Project.objects.first()
    if not project:
        print('❌ 没有找到项目')
        return

    print(f'📋 项目: {project.name}')

    tasks = project.tasks.all()
    print(f'📝 任务数量: {tasks.count()}')

    for task in tasks:
        print(f'\n任务: {task.name} (ID: {task.pk})')
        print(f'  关联图纸数量: {task.drawings.count()}')
        for drawing in task.drawings.all():
            print(f'    - {drawing.name} (ID: {drawing.pk})')

    # 找一个有图纸关联的任务
    task_with_drawings = None
    for task in tasks:
        if task.drawings.exists():
            task_with_drawings = task
            break

    if task_with_drawings:
        print(f'\n✅ 找到有图纸关联的任务: {task_with_drawings.name}')
        print(f'   任务ID: {task_with_drawings.pk}')
        print(f'   关联图纸: {task_with_drawings.drawings.count()} 张')

        # 为这个任务创建测试标注
        from tasks.models import TaskAnnotation

        # 删除现有标注
        TaskAnnotation.objects.filter(task=task_with_drawings).delete()

        drawing = task_with_drawings.drawings.first()
        annotation = TaskAnnotation.objects.create(
            task=task_with_drawings,
            drawing=drawing,
            annotation_type='point',
            x_coordinate=100,
            y_coordinate=150,
            color='red',
            content='测试红色点标记',
            page_number=1
        )

        print(f'✅ 创建测试标注: {annotation.content}')
        print(f'🌐 测试页面: http://127.0.0.1:8000/tasks/{task_with_drawings.pk}/')

    else:
        print('❌ 没有找到有图纸关联的任务')

if __name__ == '__main__':
    debug_task_drawings()
