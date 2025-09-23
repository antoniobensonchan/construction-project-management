# PythonAnywhere 部署指南

## 🗄️ 步驟 1: 設置 MySQL 資料庫

1. **登入 PythonAnywhere Dashboard**
   - 前往: https://www.pythonanywhere.com/user/antoniobensonchan/

2. **創建 MySQL 資料庫**
   - 點擊 "Databases" 標籤
   - 在 "Create database" 部分輸入資料庫名稱: `construction_pm`
   - 點擊 "Create" 按鈕

3. **記錄資料庫資訊**
   ```
   資料庫名稱: antoniobensonchan$construction_pm
   用戶名: antoniobensonchan
   密碼: [您設置的密碼]
   主機: antoniobensonchan.mysql.pythonanywhere-services.com
   ```

## 📁 步驟 2: 克隆 GitHub 專案

1. **打開 Bash Console**
   - 在 Dashboard 點擊 "Tasks" → "Bash console"

2. **克隆專案**
   ```bash
   cd ~
   git clone https://github.com/antoniobensonchan/construction-project-management.git
   cd construction-project-management
   ```

## 🐍 步驟 3: 設置虛擬環境

```bash
# 創建虛擬環境
mkvirtualenv --python=/usr/bin/python3.10 construction-pm

# 激活虛擬環境
workon construction-pm

# 安裝依賴
pip install -r requirements.txt

# 安裝 MySQL 客戶端
pip install mysqlclient
```

## ⚙️ 步驟 4: 配置環境變數

創建 `.env` 文件：
```bash
nano .env
```

內容：
```env
SECRET_KEY=your-super-secret-key-change-this-in-production
DEBUG=False
ALLOWED_HOSTS=antoniobensonchan.pythonanywhere.com

# MySQL Database
DB_ENGINE=django.db.backends.mysql
DB_NAME=antoniobensonchan$construction_pm
DB_USER=antoniobensonchan
DB_PASSWORD=your_mysql_password
DB_HOST=antoniobensonchan.mysql.pythonanywhere-services.com
DB_PORT=3306
```

## 🔧 步驟 5: 更新 Django 設置

編輯 `construction_pm/settings.py`：
```python
# 在文件頂部添加
import os
from decouple import config

# 資料庫配置
DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE', default='django.db.backends.sqlite3'),
        'NAME': config('DB_NAME', default=BASE_DIR / 'db.sqlite3'),
        'USER': config('DB_USER', default=''),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default=''),
        'PORT': config('DB_PORT', default=''),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'use_unicode': True,
        },
    }
}

# 靜態文件設置
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# 媒體文件設置
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

## 🗃️ 步驟 6: 資料庫遷移

```bash
# 激活虛擬環境
workon construction-pm
cd ~/construction-project-management

# 執行遷移
python manage.py makemigrations
python manage.py migrate

# 收集靜態文件
python manage.py collectstatic --noinput

# 創建超級用戶
python manage.py createsuperuser

# 載入演示數據（可選）
python manage.py shell < create_demo_data.py
```

## 🌐 步驟 7: 配置 Web App

1. **前往 Web 標籤**
   - 點擊 "Web" 標籤
   - 點擊 "Add a new web app"

2. **選擇框架**
   - 選擇 "Manual configuration"
   - 選擇 "Python 3.10"

3. **配置 WSGI 文件**
   編輯 `/var/www/antoniobensonchan_pythonanywhere_com_wsgi.py`：
   ```python
   import os
   import sys
   
   # 添加專案路徑
   path = '/home/antoniobensonchan/construction-project-management'
   if path not in sys.path:
       sys.path.insert(0, path)
   
   # 設置 Django 設置模組
   os.environ['DJANGO_SETTINGS_MODULE'] = 'construction_pm.settings'
   
   # 導入 Django WSGI 應用
   from django.core.wsgi import get_wsgi_application
   application = get_wsgi_application()
   ```

4. **設置虛擬環境**
   - 在 "Virtualenv" 部分輸入: `/home/antoniobensonchan/.virtualenvs/construction-pm`

5. **配置靜態文件**
   - URL: `/static/`
   - Directory: `/home/antoniobensonchan/construction-project-management/staticfiles/`
   
   - URL: `/media/`
   - Directory: `/home/antoniobensonchan/construction-project-management/media/`

## 🔄 步驟 8: 重新載入應用

1. 點擊綠色的 "Reload" 按鈕
2. 訪問: https://antoniobensonchan.pythonanywhere.com

## 🎯 測試部署

1. **訪問網站**: https://antoniobensonchan.pythonanywhere.com
2. **登入測試**:
   - 用戶名: `company_a`
   - 密碼: `demo123`
3. **管理員登入**: https://antoniobensonchan.pythonanywhere.com/admin/

## 🔧 故障排除

### 查看錯誤日誌
```bash
# 在 Bash console 中
tail -f /var/log/antoniobensonchan.pythonanywhere.com.error.log
```

### 常見問題
1. **資料庫連接錯誤**: 檢查 `.env` 文件中的資料庫配置
2. **靜態文件問題**: 重新執行 `python manage.py collectstatic`
3. **權限問題**: 確保文件權限正確

## 📝 部署後檢查清單

- [ ] 資料庫連接正常
- [ ] 靜態文件載入正常
- [ ] 媒體文件上傳功能正常
- [ ] 用戶登入功能正常
- [ ] PDF 圖紙上傳和顯示正常
- [ ] 任務管理功能正常
- [ ] 甘特圖顯示正常

## 🎉 完成！

您的建築專案管理系統現在已經在 PythonAnywhere 上運行！

訪問地址: https://antoniobensonchan.pythonanywhere.com
