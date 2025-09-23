#!/usr/bin/env python
"""
项目导出脚本
用于导出整个项目的数据和文件，以便在另一台电脑上部署
"""
import os
import django
import json
import shutil
from datetime import datetime

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_pm.settings')
django.setup()

from django.core import serializers
from projects.models import Project
from drawings.models import Drawing
from tasks.models import Task, TaskAnnotation

def export_project_data():
    """导出项目数据"""

    print('📦 开始导出项目数据...\n')

    # 创建导出目录
    export_dir = f'project_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    os.makedirs(export_dir, exist_ok=True)

    # 1. 导出数据库数据
    print('1. 导出数据库数据...')

    # 导出所有模型数据
    all_objects = []

    # 项目数据
    projects = Project.objects.all()
    all_objects.extend(projects)
    print(f'   - 项目: {projects.count()} 个')

    # 图纸数据
    drawings = Drawing.objects.all()
    all_objects.extend(drawings)
    print(f'   - 图纸: {drawings.count()} 个')

    # 任务数据
    tasks = Task.objects.all()
    all_objects.extend(tasks)
    print(f'   - 任务: {tasks.count()} 个')

    # 标注数据
    annotations = TaskAnnotation.objects.all()
    all_objects.extend(annotations)
    print(f'   - 标注: {annotations.count()} 个')

    # 序列化数据
    serialized_data = serializers.serialize('json', all_objects, indent=2)

    # 保存数据文件
    data_file = os.path.join(export_dir, 'database_data.json')
    with open(data_file, 'w', encoding='utf-8') as f:
        f.write(serialized_data)

    print(f'   ✅ 数据已保存到: {data_file}')

    # 2. 复制媒体文件
    print('\n2. 复制媒体文件...')

    media_source = 'media'
    media_dest = os.path.join(export_dir, 'media')

    if os.path.exists(media_source):
        shutil.copytree(media_source, media_dest)
        print(f'   ✅ 媒体文件已复制到: {media_dest}')

        # 统计文件
        file_count = 0
        for root, dirs, files in os.walk(media_dest):
            file_count += len(files)
        print(f'   📁 总文件数: {file_count}')
    else:
        print('   ⚠️  媒体目录不存在')

    # 3. 复制项目代码
    print('\n3. 复制项目代码...')

    code_dest = os.path.join(export_dir, 'code')
    os.makedirs(code_dest, exist_ok=True)

    # 要复制的目录和文件
    items_to_copy = [
        'construction_pm',
        'projects',
        'drawings',
        'tasks',
        'templates',
        'static',
        'manage.py',
        'requirements.txt'
    ]

    for item in items_to_copy:
        if os.path.exists(item):
            dest_path = os.path.join(code_dest, item)
            if os.path.isdir(item):
                shutil.copytree(item, dest_path)
                print(f'   ✅ 目录已复制: {item}')
            else:
                shutil.copy2(item, dest_path)
                print(f'   ✅ 文件已复制: {item}')
        else:
            print(f'   ⚠️  项目不存在: {item}')

    # 4. 生成requirements.txt
    print('\n4. 生成依赖文件...')

    requirements_content = """Django==4.2.7
Pillow==10.0.1
python-decouple==3.8
"""

    requirements_file = os.path.join(export_dir, 'requirements.txt')
    with open(requirements_file, 'w', encoding='utf-8') as f:
        f.write(requirements_content)

    print(f'   ✅ 依赖文件已生成: {requirements_file}')

    # 5. 生成部署说明
    print('\n5. 生成部署说明...')

    readme_content = f"""# 建筑项目管理系统部署指南

## 导出信息
- 导出时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- 项目数量: {projects.count()}
- 图纸数量: {drawings.count()}
- 任务数量: {tasks.count()}
- 标注数量: {annotations.count()}

## 部署步骤

### 1. 环境准备
```bash
# 安装Python 3.8+
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\\Scripts\\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 项目设置
```bash
# 复制代码文件
cp -r code/* ./

# 复制媒体文件
cp -r media ./

# 数据库迁移
python manage.py makemigrations
python manage.py migrate

# 导入数据
python manage.py loaddata database_data.json

# 创建超级用户（可选）
python manage.py createsuperuser

# 收集静态文件
python manage.py collectstatic
```

### 3. 运行项目
```bash
# 开发环境
python manage.py runserver

# 访问地址
http://127.0.0.1:8000/
```

### 4. 验证部署
- 访问项目列表页面
- 检查图纸是否正常显示
- 验证任务和标注功能
- 测试文件上传功能

## 注意事项
1. 确保Python版本兼容（推荐3.8+）
2. 媒体文件路径可能需要调整
3. 数据库配置可能需要修改
4. 静态文件路径可能需要配置

## 故障排除
- 如果图片不显示，检查MEDIA_URL和MEDIA_ROOT设置
- 如果样式丢失，运行python manage.py collectstatic
- 如果数据导入失败，先运行migrate再导入数据
"""

    readme_file = os.path.join(export_dir, 'README.md')
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(readme_content)

    print(f'   ✅ 部署说明已生成: {readme_file}')

    # 6. 生成导入脚本
    print('\n6. 生成导入脚本...')

    import_script = f"""#!/usr/bin/env python
'''
自动导入脚本
在新环境中运行此脚本来导入数据
'''
import os
import django
import subprocess
import sys

def setup_project():
    print('🚀 开始设置项目...')

    # 1. 安装依赖
    print('1. 安装依赖...')
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])

    # 2. 数据库迁移
    print('2. 数据库迁移...')
    subprocess.run([sys.executable, 'manage.py', 'makemigrations'])
    subprocess.run([sys.executable, 'manage.py', 'migrate'])

    # 3. 导入数据
    print('3. 导入数据...')
    subprocess.run([sys.executable, 'manage.py', 'loaddata', 'database_data.json'])

    # 4. 收集静态文件
    print('4. 收集静态文件...')
    subprocess.run([sys.executable, 'manage.py', 'collectstatic', '--noinput'])

    print('✅ 项目设置完成！')
    print('🌐 运行: python manage.py runserver')

if __name__ == '__main__':
    setup_project()
"""

    import_script_file = os.path.join(export_dir, 'setup_project.py')
    with open(import_script_file, 'w', encoding='utf-8') as f:
        f.write(import_script)

    print(f'   ✅ 导入脚本已生成: {import_script_file}')

    # 7. 创建压缩包
    print('\n7. 创建压缩包...')

    import zipfile

    zip_file = f'{export_dir}.zip'
    with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(export_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arc_path = os.path.relpath(file_path, export_dir)
                zipf.write(file_path, arc_path)

    print(f'   ✅ 压缩包已创建: {zip_file}')

    # 8. 显示总结
    print(f'\n📦 导出完成！')
    print(f'📁 导出目录: {export_dir}')
    print(f'📦 压缩包: {zip_file}')

    # 计算大小
    zip_size = os.path.getsize(zip_file) / (1024 * 1024)
    print(f'📊 压缩包大小: {zip_size:.2f} MB')

    print(f'\n🚀 部署步骤:')
    print(f'1. 将 {zip_file} 复制到目标电脑')
    print(f'2. 解压缩文件')
    print(f'3. 按照 README.md 中的说明部署')
    print(f'4. 或者直接运行 setup_project.py 自动设置')

    return export_dir, zip_file

if __name__ == '__main__':
    export_project_data()
