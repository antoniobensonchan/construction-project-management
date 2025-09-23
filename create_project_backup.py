#!/usr/bin/env python
"""
创建项目备份ZIP文件
"""
import os
import zipfile
import datetime
from pathlib import Path

def create_project_backup():
    """创建项目完整备份"""

    print('📦 创建项目备份ZIP文件...\n')

    # 获取当前项目根目录
    project_root = Path.cwd()
    project_name = project_root.name

    # 创建备份文件名（包含时间戳）
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f'{project_name}_backup_{timestamp}.zip'
    backup_path = project_root / backup_filename

    print(f'📁 项目根目录: {project_root}')
    print(f'📦 备份文件名: {backup_filename}')
    print(f'📍 备份路径: {backup_path}')

    # 需要包含的文件和目录
    include_patterns = [
        # Django项目核心文件
        'manage.py',
        'requirements.txt',
        'README.md',

        # 项目设置和配置
        'construction_pm/',

        # 应用目录
        'accounts/',
        'projects/',
        'tasks/',
        'drawings/',

        # 模板和静态文件
        'templates/',
        'static/',
        'media/',

        # 数据库文件（如果使用SQLite）
        'db.sqlite3',

        # 测试文件
        'test_*.py',

        # 文档文件
        '*.md',
        '*.txt',

        # 配置文件
        '*.ini',
        '*.cfg',
        '*.json',
        '*.yaml',
        '*.yml',
    ]

    # 需要排除的文件和目录
    exclude_patterns = [
        '__pycache__/',
        '*.pyc',
        '*.pyo',
        '*.pyd',
        '.git/',
        '.gitignore',
        '.vscode/',
        '.idea/',
        'venv/',
        'env/',
        '.env',
        'node_modules/',
        '*.log',
        'logs/',
        '.DS_Store',
        'Thumbs.db',
        '*.tmp',
        '*.temp',
        'backup_*.zip',
        '*_backup_*.zip',
    ]

    def should_include_file(file_path):
        """判断文件是否应该包含在备份中"""
        file_str = str(file_path)

        # 检查排除模式
        for pattern in exclude_patterns:
            if pattern.endswith('/'):
                # 目录模式
                if f'/{pattern}' in file_str or file_str.startswith(pattern):
                    return False
            elif '*' in pattern:
                # 通配符模式
                import fnmatch
                if fnmatch.fnmatch(file_str, pattern) or fnmatch.fnmatch(file_path.name, pattern):
                    return False
            else:
                # 精确匹配
                if pattern in file_str:
                    return False

        return True

    def get_all_files():
        """获取所有需要备份的文件"""
        files_to_backup = []

        for root, dirs, files in os.walk(project_root):
            # 过滤目录
            dirs[:] = [d for d in dirs if should_include_file(Path(root) / d)]

            for file in files:
                file_path = Path(root) / file
                if should_include_file(file_path):
                    # 计算相对路径
                    rel_path = file_path.relative_to(project_root)
                    files_to_backup.append((file_path, rel_path))

        return files_to_backup

    try:
        # 获取所有文件
        print('🔍 扫描项目文件...')
        files_to_backup = get_all_files()

        print(f'📊 找到 {len(files_to_backup)} 个文件需要备份')

        # 创建ZIP文件
        print('📦 创建ZIP文件...')
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
            for file_path, rel_path in files_to_backup:
                try:
                    zipf.write(file_path, rel_path)
                    print(f'  ✅ {rel_path}')
                except Exception as e:
                    print(f'  ❌ {rel_path}: {e}')

        # 获取备份文件信息
        backup_size = backup_path.stat().st_size
        backup_size_mb = backup_size / (1024 * 1024)

        print(f'\n✅ 备份创建成功！')
        print(f'📦 备份文件: {backup_filename}')
        print(f'📏 文件大小: {backup_size_mb:.2f} MB')
        print(f'📁 文件数量: {len(files_to_backup)}')

        # 创建备份说明文件
        readme_content = f"""# 建筑项目管理系统备份

## 备份信息
- 备份时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- 项目名称: {project_name}
- 备份文件: {backup_filename}
- 文件大小: {backup_size_mb:.2f} MB
- 文件数量: {len(files_to_backup)}

## 系统要求
- Python 3.8+
- Django 4.2+
- SQLite3 (或其他数据库)

## 安装步骤

### 1. 解压文件
```bash
unzip {backup_filename}
cd {project_name}
```

### 2. 创建虚拟环境
```bash
python -m venv venv
# Windows
venv\\Scripts\\activate
# Linux/Mac
source venv/bin/activate
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 数据库迁移
```bash
python manage.py migrate
```

### 5. 创建超级用户
```bash
python manage.py createsuperuser
```

### 6. 运行服务器
```bash
python manage.py runserver
```

## 功能特性

### 核心功能
- ✅ 用户认证和权限管理
- ✅ 项目管理
- ✅ 工地管理
- ✅ 任务管理和子任务系统
- ✅ 图纸管理和标注系统
- ✅ 任务依赖关系管理

### 最新功能
- ✅ 完整的日期管理系统（开始日期、结束日期、截止时间）
- ✅ 任务依赖关系（四种依赖类型）
- ✅ 子任务进度跟踪
- ✅ 子任务数量列显示
- ✅ 循环依赖检测
- ✅ 进度计算和可视化

### 用户界面
- ✅ 响应式设计
- ✅ Bootstrap 5 UI框架
- ✅ 图纸标注编辑器
- ✅ 实时进度更新
- ✅ 任务依赖可视化

## 测试账户
- 用户名: company_a
- 密码: demo123

## 主要页面
- 项目管理: http://127.0.0.1:8000/projects/
- 任务管理: http://127.0.0.1:8000/tasks/
- 图纸管理: http://127.0.0.1:8000/drawings/
- 管理后台: http://127.0.0.1:8000/admin/

## 技术栈
- 后端: Django 4.2
- 前端: Bootstrap 5, JavaScript
- 数据库: SQLite3
- 图纸处理: PDF.js
- 标注系统: Canvas API

## 注意事项
- 确保Python版本兼容
- 检查端口8000是否可用
- 媒体文件路径可能需要调整
- 生产环境需要配置ALLOWED_HOSTS

## 支持
如有问题，请检查Django文档或联系开发团队。
"""

        readme_path = project_root / 'BACKUP_README.md'
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)

        print(f'📝 创建说明文件: BACKUP_README.md')

        # 显示备份内容摘要
        print(f'\n📋 备份内容摘要:')

        # 统计各类文件
        file_types = {}
        for file_path, rel_path in files_to_backup:
            ext = file_path.suffix.lower()
            if not ext:
                ext = '(无扩展名)'
            file_types[ext] = file_types.get(ext, 0) + 1

        for ext, count in sorted(file_types.items()):
            print(f'   {ext}: {count} 个文件')

        print(f'\n🎯 使用说明:')
        print(f'   1. 将 {backup_filename} 复制到目标机器')
        print(f'   2. 解压文件到合适的目录')
        print(f'   3. 按照 BACKUP_README.md 中的步骤安装')
        print(f'   4. 运行 python manage.py runserver 启动服务')

        return backup_path, len(files_to_backup), backup_size_mb

    except Exception as e:
        print(f'❌ 备份创建失败: {e}')
        import traceback
        traceback.print_exc()
        return None, 0, 0

if __name__ == '__main__':
    create_project_backup()
