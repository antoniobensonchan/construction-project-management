#!/usr/bin/env python
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_pm.settings')
django.setup()

from projects.models import Project
from drawings.models import Drawing
from tasks.models import Task, TaskAnnotation

def create_test_annotations():
    """创建测试标注数据"""

    print('🎨 创建测试标注数据...\n')

    # 获取测试数据
    project = Project.objects.first()
    if not project:
        print('❌ 没有找到项目')
        return

    task = project.tasks.first()
    if not task:
        print('❌ 没有找到任务')
        return

    drawing = task.drawings.first()
    if not drawing:
        print('❌ 任务没有关联图纸')
        return

    print(f'📋 项目: {project.name}')
    print(f'📝 任务: {task.name}')
    print(f'📄 图纸: {drawing.name}')

    # 删除现有标注
    TaskAnnotation.objects.filter(task=task).delete()
    print('🗑️  清除现有标注')

    # 创建测试标注
    annotations_data = [
        {
            'annotation_type': 'point',
            'x_coordinate': 100,
            'y_coordinate': 150,
            'color': 'red',
            'content': '红色点标记测试',
            'page_number': 1
        },
        {
            'annotation_type': 'point',
            'x_coordinate': 200,
            'y_coordinate': 100,
            'color': 'blue',
            'content': '蓝色点标记测试',
            'page_number': 1
        },
        {
            'annotation_type': 'line',
            'x_coordinate': 50,
            'y_coordinate': 200,
            'end_x': 250,
            'end_y': 250,
            'color': 'green',
            'content': '绿色线条测试',
            'page_number': 1
        },
        {
            'annotation_type': 'text',
            'x_coordinate': 300,
            'y_coordinate': 80,
            'color': 'orange',
            'content': '橙色文字标注测试',
            'page_number': 1
        },
        {
            'annotation_type': 'line',
            'x_coordinate': 150,
            'y_coordinate': 300,
            'end_x': 350,
            'end_y': 320,
            'color': 'purple',
            'content': '紫色线条测试',
            'page_number': 1
        }
    ]

    created_annotations = []
    for i, annotation_data in enumerate(annotations_data):
        annotation = TaskAnnotation.objects.create(
            task=task,
            drawing=drawing,
            **annotation_data
        )
        created_annotations.append(annotation)
        print(f'✅ 创建标注 {i+1}: {annotation.get_annotation_type_display()} - {annotation.color} - {annotation.content}')

    print(f'\n📊 标注创建完成:')
    print(f'   任务: {task.name}')
    print(f'   图纸: {drawing.name}')
    print(f'   标注数量: {len(created_annotations)}')

    # 显示颜色分布
    color_counts = {}
    for annotation in created_annotations:
        color = annotation.color
        color_counts[color] = color_counts.get(color, 0) + 1

    print(f'\n🎨 颜色分布:')
    for color, count in color_counts.items():
        print(f'   {color}: {count} 个')

    print(f'\n🌐 测试页面:')
    print(f'   任务详情 (只读): http://127.0.0.1:8000/tasks/{task.pk}/')
    print(f'   任务编辑 (可编辑): http://127.0.0.1:8000/tasks/{task.pk}/update/')

    print(f'\n✅ 测试标注创建完成！')

    return created_annotations

if __name__ == '__main__':
    try:
        create_test_annotations()
    except Exception as e:
        print(f'❌ 创建过程中出错: {e}')
        import traceback
        traceback.print_exc()
