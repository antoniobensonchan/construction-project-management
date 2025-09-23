#!/usr/bin/env python
"""
验证导出文件的完整性
"""
import os
import json
import zipfile

def verify_export():
    """验证导出文件"""

    print('🔍 验证导出文件完整性...\n')

    # 查找导出的zip文件
    zip_files = [f for f in os.listdir('.') if f.startswith('project_export_') and f.endswith('.zip')]

    if not zip_files:
        print('❌ 未找到导出的zip文件')
        return

    zip_file = zip_files[0]  # 使用最新的导出文件
    print(f'📦 验证文件: {zip_file}')

    # 检查zip文件大小
    zip_size = os.path.getsize(zip_file) / (1024 * 1024)
    print(f'📊 文件大小: {zip_size:.2f} MB')

    # 检查zip文件内容
    print(f'\n📁 检查zip文件内容:')

    with zipfile.ZipFile(zip_file, 'r') as zipf:
        file_list = zipf.namelist()

        # 必需的文件和目录
        required_items = [
            'README.md',
            'requirements.txt',
            'setup_project.py',
            'database_data.json',
            'code/',
            'media/'
        ]

        print(f'   总文件数: {len(file_list)}')

        for item in required_items:
            found = any(f.startswith(item) for f in file_list)
            status = '✅' if found else '❌'
            print(f'   {status} {item}')

        # 检查代码目录
        code_files = [f for f in file_list if f.startswith('code/')]
        print(f'   📂 代码文件: {len(code_files)} 个')

        # 检查媒体文件
        media_files = [f for f in file_list if f.startswith('media/')]
        print(f'   📂 媒体文件: {len(media_files)} 个')

        # 检查数据文件
        if 'database_data.json' in file_list:
            print(f'\n📊 检查数据文件:')

            # 读取数据文件内容
            with zipf.open('database_data.json') as data_file:
                data_content = data_file.read().decode('utf-8')
                data = json.loads(data_content)

                # 统计各类型数据
                model_counts = {}
                for item in data:
                    model = item['model']
                    model_counts[model] = model_counts.get(model, 0) + 1

                for model, count in model_counts.items():
                    print(f'     {model}: {count} 个')

    print(f'\n✅ 导出文件验证完成！')

    # 生成部署命令
    print(f'\n🚀 部署命令 (复制到新电脑执行):')
    print(f'```bash')
    print(f'# 1. 解压文件')
    print(f'unzip {zip_file}')
    print(f'cd {zip_file[:-4]}')  # 移除.zip扩展名
    print(f'')
    print(f'# 2. 创建虚拟环境')
    print(f'python -m venv venv')
    print(f'')
    print(f'# 3. 激活虚拟环境')
    print(f'# Windows:')
    print(f'venv\\Scripts\\activate')
    print(f'# Linux/Mac:')
    print(f'# source venv/bin/activate')
    print(f'')
    print(f'# 4. 复制代码文件')
    print(f'# Windows:')
    print(f'xcopy /E /I code\\* .\\')
    print(f'# Linux/Mac:')
    print(f'# cp -r code/* ./')
    print(f'')
    print(f'# 5. 自动设置')
    print(f'python setup_project.py')
    print(f'')
    print(f'# 6. 启动服务器')
    print(f'python manage.py runserver')
    print(f'```')

    return zip_file

if __name__ == '__main__':
    verify_export()
