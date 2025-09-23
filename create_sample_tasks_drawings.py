#!/usr/bin/env python
import os
import django
from datetime import date, timedelta
from django.core.files.base import ContentFile

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_pm.settings')
django.setup()

from projects.models import Project
from drawings.models import Drawing
from tasks.models import Task

def create_sample_drawings_and_tasks():
    """为示例项目创建图纸和任务"""

    # 获取第一个项目
    try:
        project = Project.objects.first()
        if not project:
            print('❌ 没有找到项目，请先运行 create_sample_data.py')
            return

        print(f'📋 为项目 "{project.name}" 创建示例数据...\n')

        # 创建示例图纸（模拟文件）
        drawings_data = [
            {
                'name': '1层平面图',
                'filename': '1F_plan.pdf'
            },
            {
                'name': '2层平面图',
                'filename': '2F_plan.pdf'
            },
            {
                'name': '立面图',
                'filename': 'elevation.pdf'
            },
            {
                'name': '结构图',
                'filename': 'structure.pdf'
            }
        ]

        created_drawings = []
        for drawing_data in drawings_data:
            # 创建模拟PDF内容
            fake_pdf_content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000074 00000 n \n0000000120 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n179\n%%EOF'

            drawing, created = Drawing.objects.get_or_create(
                name=drawing_data['name'],
                project=project,
                defaults={
                    'file': ContentFile(fake_pdf_content, drawing_data['filename']),
                    'file_type': 'pdf',
                    'file_size': len(fake_pdf_content),
                    'page_count': 1,
                    'is_valid': True
                }
            )

            if created:
                print(f'✅ 创建图纸: {drawing.name}')
                created_drawings.append(drawing)
            else:
                print(f'📋 图纸已存在: {drawing.name}')
                created_drawings.append(drawing)

        # 创建示例任务
        tasks_data = [
            {
                'name': '基础施工',
                'description': '进行建筑基础的挖掘和浇筑工作',
                'task_type': 'new_construction',
                'responsible_person': '张工',
                'deadline': date.today() + timedelta(days=15),
                'drawings': [created_drawings[0], created_drawings[3]]  # 1层平面图 + 结构图
            },
            {
                'name': '1层墙体砌筑',
                'description': '按照图纸要求进行1层墙体砌筑',
                'task_type': 'new_construction',
                'responsible_person': '李师傅',
                'deadline': date.today() + timedelta(days=25),
                'drawings': [created_drawings[0]]  # 1层平面图
            },
            {
                'name': '2层结构施工',
                'description': '2层楼板和梁柱施工',
                'task_type': 'new_construction',
                'responsible_person': '王工',
                'deadline': date.today() + timedelta(days=35),
                'drawings': [created_drawings[1], created_drawings[3]]  # 2层平面图 + 结构图
            },
            {
                'name': '外立面检查',
                'description': '检查外立面施工质量',
                'task_type': 'inspection',
                'responsible_person': '陈监理',
                'deadline': date.today() + timedelta(days=45),
                'drawings': [created_drawings[2]]  # 立面图
            }
        ]

        created_tasks = []
        for task_data in tasks_data:
            drawings = task_data.pop('drawings')

            task, created = Task.objects.get_or_create(
                name=task_data['name'],
                project=project,
                defaults=task_data
            )

            if created:
                # 设置关联图纸
                task.drawings.set(drawings)
                print(f'✅ 创建任务: {task.name} (关联 {len(drawings)} 张图纸)')
                created_tasks.append(task)
            else:
                print(f'📋 任务已存在: {task.name}')
                created_tasks.append(task)

        print(f'\n📊 项目 "{project.name}" 数据统计:')
        print(f'   图纸数量: {project.drawings.count()}')
        print(f'   任务数量: {project.tasks.count()}')

        # 显示任务-图纸关联关系
        print(f'\n🔗 任务-图纸关联关系:')
        for task in created_tasks:
            drawing_names = [d.name for d in task.drawings.all()]
            print(f'   {task.name}: {", ".join(drawing_names) if drawing_names else "无关联图纸"}')

        return created_drawings, created_tasks

    except Exception as e:
        print(f'❌ 创建示例数据时出错: {e}')
        return [], []

if __name__ == '__main__':
    print('🏗️ 创建示例图纸和任务数据...\n')
    drawings, tasks = create_sample_drawings_and_tasks()
    print(f'\n✅ 示例数据创建完成！')
    print(f'🌐 访问 http://127.0.0.1:8000/ 查看项目详情')
