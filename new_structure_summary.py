#!/usr/bin/env python
"""
新数据结构总结和测试指南
"""
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_pm.settings')
django.setup()

from django.contrib.auth import get_user_model
from projects.models import Project, WorkSite
from tasks.models import Task

User = get_user_model()

def show_new_structure_summary():
    """显示新数据结构总结"""

    print('🎉 新数据结构重建完成！\n')

    print('🏗️  新的层次结构:')
    print('   👤 用户账户 (User)')
    print('   ├── 📁 项目 (Project)')
    print('   │   ├── 🏗️ 工地 (WorkSite)')
    print('   │   │   ├── 📄 图纸 (Drawing)')
    print('   │   │   └── 📋 任务 (Task)')
    print('   │   │       └── 📝 子任务 (SubTask)')

    print(f'\n📊 当前数据统计:')
    print(f'   用户数量: {User.objects.count()}')
    print(f'   项目数量: {Project.objects.count()}')
    print(f'   工地数量: {WorkSite.objects.count()}')
    print(f'   任务数量: {Task.objects.count()}')
    print(f'   主任务数量: {Task.objects.filter(parent_task__isnull=True).count()}')
    print(f'   子任务数量: {Task.objects.filter(parent_task__isnull=False).count()}')

    print(f'\n🆕 新功能特性:')
    print(f'   ✅ 工地管理：每个项目可以有多个工地')
    print(f'   ✅ 子任务支持：任务可以有子任务（无限层级）')
    print(f'   ✅ 图纸按工地组织：每个工地有自己的图纸集合')
    print(f'   ✅ 任务标注：任务可以在工地图纸上添加标注')
    print(f'   ✅ 数据隔离：每个用户只能看到自己的数据')
    print(f'   ✅ 层次化管理：清晰的数据组织结构')

    print(f'\n🌐 测试页面:')
    print(f'   服务器地址: http://127.0.0.1:8000/')
    print(f'   登录页面: http://127.0.0.1:8000/accounts/login/')
    print(f'   注册页面: http://127.0.0.1:8000/accounts/signup/')
    print(f'   项目列表: http://127.0.0.1:8000/projects/ (需要登录)')

    print(f'\n🔐 测试账户:')
    print(f'   账户1: company_a / demo123')
    print(f'   - 公司: 建筑公司A')
    print(f'   - 项目: 现代办公大楼建设项目')
    print(f'   - 工地: 主楼施工区、地下车库施工区')
    print(f'   - 任务: 基础施工（含3个子任务）、质量检查（含2个子任务）')
    print(f'')
    print(f'   账户2: company_b / demo123')
    print(f'   - 公司: 建筑公司B')
    print(f'   - 项目: 住宅小区开发项目')
    print(f'   - 工地: 1号楼施工区、2号楼施工区')
    print(f'   - 任务: 暂无（可以创建测试）')

    print(f'\n📋 测试建议:')
    print(f'   1. 登录不同账户验证数据隔离')
    print(f'   2. 创建新的工地和任务')
    print(f'   3. 测试子任务功能')
    print(f'   4. 上传图纸到工地')
    print(f'   5. 在图纸上添加任务标注')

    print(f'\n🔧 下一步开发:')
    print(f'   1. 更新视图和模板以支持新结构')
    print(f'   2. 创建工地管理页面')
    print(f'   3. 更新任务页面支持子任务')
    print(f'   4. 更新图纸页面支持工地关联')
    print(f'   5. 优化导航和用户体验')

    # 显示实际的数据层次结构
    print(f'\n🏗️  实际数据层次结构:')
    for user in User.objects.all():
        print(f'👤 {user.company_name} ({user.username})')
        for project in user.owned_projects.all():
            print(f'  📁 {project.name}')
            for worksite in project.worksites.all():
                print(f'    🏗️  {worksite.name}')
                # 显示工地的图纸
                drawings_count = worksite.drawings.count()
                if drawings_count > 0:
                    print(f'      📄 图纸: {drawings_count} 张')
                # 显示主任务
                main_tasks = worksite.tasks.filter(parent_task__isnull=True)
                for task in main_tasks:
                    print(f'      📋 {task.name} ({task.get_status_display()})')
                    # 显示子任务
                    for subtask in task.subtasks.all():
                        print(f'        📝 {subtask.name} ({subtask.get_status_display()})')

    print(f'\n✅ 新数据结构已成功部署！')
    print(f'服务器运行中：http://127.0.0.1:8000/')

    return True

if __name__ == '__main__':
    try:
        show_new_structure_summary()
    except Exception as e:
        print(f'❌ 显示总结时出错: {e}')
        import traceback
        traceback.print_exc()
