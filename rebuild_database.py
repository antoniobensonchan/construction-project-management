#!/usr/bin/env python
"""
重建数据库以支持新的数据结构
"""
import os
import shutil
import glob

def rebuild_database():
    """重建数据库"""

    print('🔄 重建数据库以支持新结构...\n')

    # 1. 删除数据库文件
    print('1. 删除现有数据库文件:')
    if os.path.exists('db.sqlite3'):
        os.remove('db.sqlite3')
        print('   ✅ 删除 db.sqlite3')
    else:
        print('   ℹ️  db.sqlite3 不存在')

    # 2. 删除迁移文件（保留__init__.py）
    print('\n2. 删除迁移文件:')
    migration_patterns = [
        'accounts/migrations/0*.py',
        'projects/migrations/0*.py',
        'drawings/migrations/0*.py',
        'tasks/migrations/0*.py'
    ]

    for pattern in migration_patterns:
        files = glob.glob(pattern)
        for file in files:
            os.remove(file)
            print(f'   ✅ 删除 {file}')

    if not any(glob.glob(pattern) for pattern in migration_patterns):
        print('   ℹ️  没有找到迁移文件')

    print('\n✅ 数据库重建准备完成！')
    print('\n📋 接下来请手动执行以下命令:')
    print('   1. python manage.py makemigrations')
    print('   2. python manage.py migrate')
    print('   3. python manage.py createsuperuser')
    print('   4. python create_new_demo_data.py')
    print('   5. python manage.py runserver')

    return True

if __name__ == '__main__':
    try:
        rebuild_database()
    except Exception as e:
        print(f'❌ 重建过程中出错: {e}')
        import traceback
        traceback.print_exc()
