#!/usr/bin/env python
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_pm.settings')
django.setup()

from projects.models import Project
from drawings.models import Drawing
from tasks.models import Task

def fix_task_drawing_relations():
    """修复任务-图纸关联关系"""

    print('🔧 修复任务-图纸关联关系...\n')

    # 获取项目和相关数据
    project = Project.objects.first()
    if not project:
        print('❌ 没有找到项目')
        return

    drawings = project.drawings.all()
    tasks = project.tasks.all()

    print(f'📋 项目: {project.name}')
    print(f'📄 图纸数量: {drawings.count()}')
    print(f'📝 任务数量: {tasks.count()}')

    if not drawings.exists():
        print('❌ 项目没有图纸')
        return

    # 为每个任务关联图纸
    for i, task in enumerate(tasks):
        # 清除现有关联
        task.drawings.clear()

        # 根据任务类型关联不同图纸
        if '基础' in task.name:
            # 基础施工关联结构图
            structure_drawings = drawings.filter(name__icontains='结构')
            if structure_drawings.exists():
                task.drawings.add(structure_drawings.first())
        elif '墙体' in task.name or '砌筑' in task.name:
            # 墙体施工关联平面图
            plan_drawings = drawings.filter(name__icontains='平面')
            if plan_drawings.exists():
                task.drawings.add(plan_drawings.first())
        elif '立面' in task.name or '外墙' in task.name:
            # 立面相关关联立面图
            elevation_drawings = drawings.filter(name__icontains='立面')
            if elevation_drawings.exists():
                task.drawings.add(elevation_drawings.first())
        else:
            # 其他任务关联第一张图纸
            if drawings.exists():
                task.drawings.add(drawings.first())

        print(f'✅ 任务 "{task.name}" 关联了 {task.drawings.count()} 张图纸')
        for drawing in task.drawings.all():
            print(f'   - {drawing.name}')

    print(f'\n📊 修复后统计:')
    for task in tasks:
        print(f'   {task.name}: {task.drawings.count()} 张图纸')

    print(f'\n✅ 任务-图纸关联关系修复完成！')

    return True

if __name__ == '__main__':
    try:
        fix_task_drawing_relations()
    except Exception as e:
        print(f'❌ 修复过程中出错: {e}')
        import traceback
        traceback.print_exc()
