#!/usr/bin/env python
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_pm.settings')
django.setup()

from drawings.models import Drawing
from tasks.models import Task, TaskAnnotation

def debug_drawing_8():
    """调试图纸8的数据"""

    print('🔍 调试图纸8的数据...\n')

    try:
        drawing = Drawing.objects.get(pk=8)
        print(f'📄 图纸: {drawing.name}')
        print(f'   ID: {drawing.pk}')
        print(f'   文件: {drawing.file.name if drawing.file else "无文件"}')
        print(f'   项目: {drawing.project.name if drawing.project else "无项目"}')

        # 检查关联任务
        related_tasks = drawing.tasks.all()
        print(f'\n🔗 关联任务数量: {related_tasks.count()}')

        for task in related_tasks:
            print(f'   - {task.name} (ID: {task.pk})')
            print(f'     项目: {task.project.name if task.project else "无项目"}')
            print(f'     状态: {task.get_status_display()}')

        # 检查标注
        all_annotations = drawing.annotations.all()
        print(f'\n🎯 图纸标注数量: {all_annotations.count()}')

        for annotation in all_annotations:
            print(f'   - {annotation.get_annotation_type_display()}: {annotation.color} - {annotation.content}')
            print(f'     任务: {annotation.task.name}')
            print(f'     位置: ({annotation.x_coordinate}, {annotation.y_coordinate})')

        # 如果没有关联任务，尝试找一些任务关联到这个图纸
        if related_tasks.count() == 0:
            print('\n⚠️  没有关联任务，查找可关联的任务...')

            if drawing.project:
                project_tasks = drawing.project.tasks.all()
                print(f'   项目任务数量: {project_tasks.count()}')

                if project_tasks.exists():
                    task = project_tasks.first()
                    task.drawings.add(drawing)
                    print(f'✅ 将任务 "{task.name}" 关联到图纸')

                    # 创建测试标注
                    annotation = TaskAnnotation.objects.create(
                        task=task,
                        drawing=drawing,
                        annotation_type='point',
                        x_coordinate=200,
                        y_coordinate=150,
                        color='red',
                        content='测试标注点',
                        page_number=1
                    )
                    print(f'✅ 创建测试标注: {annotation.content}')

                    # 再次检查
                    related_tasks = drawing.tasks.all()
                    all_annotations = drawing.annotations.all()

                    print(f'\n📊 更新后数据:')
                    print(f'   关联任务: {related_tasks.count()} 个')
                    print(f'   标注数量: {all_annotations.count()} 个')

        print(f'\n🌐 测试页面: http://127.0.0.1:8000/drawings/{drawing.pk}/')

        return drawing, related_tasks, all_annotations

    except Drawing.DoesNotExist:
        print('❌ 图纸8不存在')
        return None, None, None

if __name__ == '__main__':
    debug_drawing_8()
