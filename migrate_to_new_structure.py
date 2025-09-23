#!/usr/bin/env python
"""
迁移到新的数据结构：用户 → 项目 → 工地 → 任务 → 子任务
"""
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_pm.settings')
django.setup()

from django.contrib.auth import get_user_model
from projects.models import Project
from drawings.models import Drawing
from tasks.models import Task

User = get_user_model()

def migrate_to_new_structure():
    """迁移到新的数据结构"""

    print('🔄 开始迁移到新的数据结构...\n')

    print('📊 当前数据统计:')
    print(f'   用户数量: {User.objects.count()}')
    print(f'   项目数量: {Project.objects.count()}')
    print(f'   图纸数量: {Drawing.objects.count()}')
    print(f'   任务数量: {Task.objects.count()}')

    print(f'\n🏗️  新的数据结构:')
    print(f'   用户账户 (User)')
    print(f'   ├── 项目 (Project)')
    print(f'       ├── 工地 (WorkSite)')
    print(f'           ├── 图纸 (Drawing)')
    print(f'           └── 任务 (Task)')
    print(f'               └── 子任务 (SubTask)')

    print(f'\n📋 迁移计划:')
    print(f'   1. 为每个项目创建默认工地')
    print(f'   2. 将现有图纸迁移到工地')
    print(f'   3. 将现有任务迁移到工地')
    print(f'   4. 创建示例子任务')
    print(f'   5. 更新所有关联关系')

    print(f'\n⚠️  重要说明:')
    print(f'   由于数据结构变化较大，建议:')
    print(f'   1. 备份当前数据库')
    print(f'   2. 重新创建数据库')
    print(f'   3. 运行新的演示数据脚本')

    print(f'\n🔧 推荐操作步骤:')
    print(f'   1. 停止服务器')
    print(f'   2. 删除数据库文件: rm db.sqlite3')
    print(f'   3. 删除迁移文件: rm */migrations/0*.py')
    print(f'   4. 重新创建迁移: python manage.py makemigrations')
    print(f'   5. 应用迁移: python manage.py migrate')
    print(f'   6. 创建超级用户: python manage.py createsuperuser')
    print(f'   7. 运行新的演示数据脚本')

    print(f'\n✅ 新结构的优势:')
    print(f'   ✅ 更清晰的层次结构')
    print(f'   ✅ 支持多工地项目')
    print(f'   ✅ 图纸按工地组织')
    print(f'   ✅ 任务支持子任务')
    print(f'   ✅ 更好的权限控制')
    print(f'   ✅ 更灵活的数据组织')

    return True

def create_new_demo_data():
    """创建新结构的演示数据"""

    print(f'\n🎯 创建新结构演示数据...')

    # 这个函数将在新的数据库结构创建后实现
    print(f'   此功能将在数据库重建后实现')

    return True

if __name__ == '__main__':
    try:
        migrate_to_new_structure()

        print(f'\n🎉 迁移计划制定完成！')
        print(f'请按照推荐步骤重建数据库以使用新结构。')

    except Exception as e:
        print(f'❌ 迁移过程中出错: {e}')
        import traceback
        traceback.print_exc()
