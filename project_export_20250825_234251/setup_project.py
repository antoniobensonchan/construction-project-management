#!/usr/bin/env python
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
