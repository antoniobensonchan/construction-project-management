#!/bin/bash
# PythonAnywhere 部署命令清單
# 在 PythonAnywhere Bash Console 中逐行執行

echo "🚀 PythonAnywhere 部署開始..."

# 1. 克隆專案
cd ~
git clone https://github.com/antoniobensonchan/construction-project-management.git
cd construction-project-management

# 2. 創建並激活虛擬環境
mkvirtualenv --python=/usr/bin/python3.10 construction-pm
workon construction-pm

# 3. 安裝依賴
pip install -r requirements.txt
pip install mysqlclient python-decouple

# 4. 創建環境變數文件
cat > .env << 'EOF'
SECRET_KEY=django-production-key-change-this-in-real-deployment
DEBUG=False
ALLOWED_HOSTS=antoniobensonchan.pythonanywhere.com

# MySQL Database - 請修改密碼
DB_ENGINE=django.db.backends.mysql
DB_NAME=antoniobensonchan$construction_pm
DB_USER=antoniobensonchan
DB_PASSWORD=YOUR_MYSQL_PASSWORD_HERE
DB_HOST=antoniobensonchan.mysql.pythonanywhere-services.com
DB_PORT=3306

FILE_UPLOAD_MAX_MEMORY_SIZE=10485760
DATA_UPLOAD_MAX_MEMORY_SIZE=10485760
EOF

echo "⚠️  請編輯 .env 文件並設置正確的 MySQL 密碼:"
echo "nano .env"

# 5. 資料庫遷移
python manage.py makemigrations
python manage.py migrate

# 6. 收集靜態文件
python manage.py collectstatic --noinput

# 7. 創建超級用戶
python manage.py createsuperuser

# 8. 載入演示數據（可選）
# python manage.py shell < create_demo_data.py

echo "✅ 命令執行完成！"
echo "請繼續手動配置 Web App..."
