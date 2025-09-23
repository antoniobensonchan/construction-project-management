#!/usr/bin/env python
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_pm.settings')
django.setup()

from drawings.models import Drawing
from tasks.models import Task, TaskAnnotation

def debug_drawing_9():
    """调试图纸9的数据"""

    print('🔍 调试图纸9的数据...\n')

    try:
        drawing = Drawing.objects.get(pk=9)
        print(f'📄 图纸: {drawing.name}')
        print(f'   ID: {drawing.pk}')
        print(f'   文件: {drawing.file.name if drawing.file else "无文件"}')
        print(f'   文件类型: {drawing.file_type}')
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
            if annotation.end_x and annotation.end_y:
                print(f'     终点: ({annotation.end_x}, {annotation.end_y})')

        # 如果没有标注，创建一些测试标注
        if all_annotations.count() == 0:
            print('\n⚠️  没有标注，创建测试标注...')

            if related_tasks.exists():
                task = related_tasks.first()

                # 创建不同类型的标注
                test_annotations = [
                    {
                        'annotation_type': 'point',
                        'x_coordinate': 150,
                        'y_coordinate': 100,
                        'color': 'red',
                        'content': '红色检查点',
                        'page_number': 1
                    },
                    {
                        'annotation_type': 'text',
                        'x_coordinate': 200,
                        'y_coordinate': 200,
                        'color': 'blue',
                        'content': '蓝色文字标注',
                        'page_number': 1
                    },
                    {
                        'annotation_type': 'line',
                        'x_coordinate': 100,
                        'y_coordinate': 250,
                        'end_x': 300,
                        'end_y': 300,
                        'color': 'green',
                        'content': '绿色线条标注',
                        'page_number': 1
                    }
                ]

                for ann_data in test_annotations:
                    annotation = TaskAnnotation.objects.create(
                        task=task,
                        drawing=drawing,
                        **ann_data
                    )
                    print(f'✅ 创建标注: {annotation.get_annotation_type_display()} - {annotation.color}')

                # 重新获取标注
                all_annotations = drawing.annotations.all()
            else:
                print('   没有关联任务，无法创建标注')

        print(f'\n📊 最终数据:')
        print(f'   图纸: {drawing.name}')
        print(f'   关联任务: {related_tasks.count()} 个')
        print(f'   标注数量: {all_annotations.count()} 个')

        print(f'\n🌐 测试页面: http://127.0.0.1:8000/drawings/{drawing.pk}/')
        print(f'🌐 对比页面: http://127.0.0.1:8000/tasks/7/')

        return drawing, related_tasks, all_annotations

    except Drawing.DoesNotExist:
        print('❌ 图纸9不存在')
        return None, None, None

if __name__ == '__main__':
    debug_drawing_9()
