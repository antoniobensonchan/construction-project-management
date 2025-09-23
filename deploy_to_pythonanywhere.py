#!/usr/bin/env python3
"""
PythonAnywhere 自動部署腳本
在 PythonAnywhere 的 Bash console 中運行此腳本
"""
import os
import subprocess
import sys

def run_command(command, description=""):
    """執行命令並顯示結果"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} 成功")
        if result.stdout:
            print(f"輸出: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} 失敗: {e}")
        if e.stderr:
            print(f"錯誤: {e.stderr}")
        return False

def create_env_file():
    """創建環境變數文件"""
    print("📝 創建環境變數文件...")
    
    # 獲取用戶輸入
    mysql_password = input("請輸入您的 MySQL 密碼: ")
    secret_key = input("請輸入 Django SECRET_KEY (或按 Enter 使用預設): ") or "django-production-key-change-this-in-real-deployment"
    
    env_content = f"""# Django Settings
SECRET_KEY={secret_key}
DEBUG=False
ALLOWED_HOSTS=antoniobensonchan.pythonanywhere.com

# MySQL Database
DB_ENGINE=django.db.backends.mysql
DB_NAME=antoniobensonchan$construction_pm
DB_USER=antoniobensonchan
DB_PASSWORD={mysql_password}
DB_HOST=antoniobensonchan.mysql.pythonanywhere-services.com
DB_PORT=3306

# File Upload Settings
FILE_UPLOAD_MAX_MEMORY_SIZE=10485760
DATA_UPLOAD_MAX_MEMORY_SIZE=10485760
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ 環境變數文件創建成功")

def update_settings():
    """更新 Django 設置文件"""
    print("⚙️ 更新 Django 設置...")
    
    settings_path = 'construction_pm/settings.py'
    
    # 讀取現有設置
    with open(settings_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 添加必要的導入和配置
    if 'from decouple import config' not in content:
        # 在文件開頭添加導入
        imports = """import os
from decouple import config

"""
        content = imports + content
    
    # 更新資料庫配置
    db_config = """
# Database Configuration for PythonAnywhere
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
        } if config('DB_ENGINE', default='').startswith('django.db.backends.mysql') else {},
    }
}
"""
    
    # 替換資料庫配置
    if 'DATABASES = {' in content:
        # 找到 DATABASES 配置的開始和結束
        start = content.find('DATABASES = {')
        brace_count = 0
        end = start
        for i, char in enumerate(content[start:], start):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    end = i + 1
                    break
        
        content = content[:start] + db_config + content[end:]
    else:
        content += db_config
    
    # 添加靜態文件配置
    static_config = """
# Static files (CSS, JavaScript, Images) for PythonAnywhere
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files for PythonAnywhere
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
"""
    
    if 'STATIC_ROOT' not in content:
        content += static_config
    
    # 寫回文件
    with open(settings_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Django 設置更新成功")

def create_wsgi_file():
    """創建 WSGI 配置文件"""
    print("🌐 創建 WSGI 配置文件...")
    
    wsgi_content = """import os
import sys

# Add your project directory to the sys.path
path = '/home/antoniobensonchan/construction-project-management'
if path not in sys.path:
    sys.path.insert(0, path)

# Set the Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'construction_pm.settings'

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
"""
    
    wsgi_path = '/var/www/antoniobensonchan_pythonanywhere_com_wsgi.py'
    
    try:
        with open(wsgi_path, 'w') as f:
            f.write(wsgi_content)
        print("✅ WSGI 文件創建成功")
        return True
    except PermissionError:
        print("⚠️  無法直接創建 WSGI 文件，請手動創建")
        print(f"文件路徑: {wsgi_path}")
        print("文件內容:")
        print(wsgi_content)
        return False

def main():
    """主部署函數"""
    print("🚀 開始 PythonAnywhere 部署...")
    print("=" * 50)
    
    # 檢查是否在正確的目錄
    if not os.path.exists('manage.py'):
        print("❌ 請確保您在專案根目錄中運行此腳本")
        return False
    
    # 步驟 1: 安裝依賴
    if not run_command("pip install -r requirements.txt", "安裝 Python 依賴"):
        return False
    
    if not run_command("pip install mysqlclient", "安裝 MySQL 客戶端"):
        print("⚠️  如果 mysqlclient 安裝失敗，請嘗試:")
        print("pip install PyMySQL")
        print("然後在 settings.py 中添加: import pymysql; pymysql.install_as_MySQLdb()")
    
    # 步驟 2: 創建環境變數文件
    create_env_file()
    
    # 步驟 3: 更新 Django 設置
    update_settings()
    
    # 步驟 4: 資料庫遷移
    if not run_command("python manage.py makemigrations", "創建資料庫遷移"):
        print("⚠️  遷移創建失敗，但繼續執行...")
    
    if not run_command("python manage.py migrate", "執行資料庫遷移"):
        print("❌ 資料庫遷移失敗，請檢查資料庫配置")
        return False
    
    # 步驟 5: 收集靜態文件
    if not run_command("python manage.py collectstatic --noinput", "收集靜態文件"):
        print("⚠️  靜態文件收集失敗，但繼續執行...")
    
    # 步驟 6: 創建 WSGI 文件
    create_wsgi_file()
    
    # 步驟 7: 載入演示數據
    load_demo = input("是否載入演示數據？(y/N): ").lower().strip()
    if load_demo == 'y':
        if os.path.exists('create_demo_data.py'):
            run_command("python manage.py shell < create_demo_data.py", "載入演示數據")
        else:
            print("⚠️  找不到演示數據腳本")
    
    print("\n🎉 部署腳本執行完成！")
    print("=" * 50)
    print("📋 接下來的手動步驟:")
    print("1. 前往 PythonAnywhere Web 標籤")
    print("2. 設置虛擬環境路徑: /home/antoniobensonchan/.virtualenvs/construction-pm")
    print("3. 配置靜態文件:")
    print("   - URL: /static/")
    print("   - Directory: /home/antoniobensonchan/construction-project-management/staticfiles/")
    print("4. 配置媒體文件:")
    print("   - URL: /media/")
    print("   - Directory: /home/antoniobensonchan/construction-project-management/media/")
    print("5. 點擊 'Reload' 按鈕重新載入應用")
    print("6. 訪問: https://antoniobensonchan.pythonanywhere.com")
    print("\n🎯 測試帳戶:")
    print("用戶名: company_a")
    print("密碼: demo123")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ 部署被用戶中斷")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 部署過程中發生錯誤: {e}")
        sys.exit(1)
