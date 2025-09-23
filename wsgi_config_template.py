# WSGI configuration for PythonAnywhere
# 將此內容複製到: /var/www/antoniobensonchan_pythonanywhere_com_wsgi.py

import os
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
