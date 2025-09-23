# Deployment Guide

This guide covers various deployment options for the Construction Project Management System.

## 🚀 Quick Deployment Options

### 1. Local Development
```bash
# Clone and setup
git clone <repository-url>
cd ConstructionPMProject
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### 2. Production with Gunicorn
```bash
# Install production dependencies
pip install gunicorn

# Collect static files
python manage.py collectstatic --noinput

# Run with Gunicorn
gunicorn construction_pm.wsgi:application --bind 0.0.0.0:8000
```

### 3. Docker Deployment
```bash
# Build image
docker build -t construction-pm .

# Run container
docker run -p 8000:8000 construction-pm
```

## 🔧 Environment Configuration

### Environment Variables
Create a `.env` file in the project root:

```env
# Django Settings
DEBUG=False
SECRET_KEY=your-super-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/construction_pm

# File Storage
MEDIA_ROOT=/var/www/construction-pm/media
STATIC_ROOT=/var/www/construction-pm/static

# Security Settings
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
```

### Database Configuration

#### PostgreSQL (Recommended for Production)
```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'construction_pm',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

#### MySQL
```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'construction_pm',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

## 🐳 Docker Deployment

### Dockerfile
```dockerfile
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Run the application
CMD ["gunicorn", "construction_pm.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### Docker Compose
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - DATABASE_URL=postgresql://postgres:password@db:5432/construction_pm
    depends_on:
      - db
    volumes:
      - media_volume:/app/media
      - static_volume:/app/static

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=construction_pm
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - media_volume:/var/www/media
      - static_volume:/var/www/static
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web

volumes:
  postgres_data:
  media_volume:
  static_volume:
```

## 🌐 Web Server Configuration

### Nginx Configuration
```nginx
upstream construction_pm {
    server web:8000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    client_max_body_size 20M;

    location / {
        proxy_pass http://construction_pm;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    location /static/ {
        alias /var/www/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /var/www/media/;
        expires 1y;
        add_header Cache-Control "public";
    }
}
```

### Apache Configuration
```apache
<VirtualHost *:80>
    ServerName yourdomain.com
    Redirect permanent / https://yourdomain.com/
</VirtualHost>

<VirtualHost *:443>
    ServerName yourdomain.com
    
    SSLEngine on
    SSLCertificateFile /path/to/cert.pem
    SSLCertificateKeyFile /path/to/key.pem
    
    ProxyPreserveHost On
    ProxyPass /static/ !
    ProxyPass /media/ !
    ProxyPass / http://127.0.0.1:8000/
    ProxyPassReverse / http://127.0.0.1:8000/
    
    Alias /static/ /var/www/construction-pm/static/
    Alias /media/ /var/www/construction-pm/media/
    
    <Directory /var/www/construction-pm/static/>
        Require all granted
    </Directory>
    
    <Directory /var/www/construction-pm/media/>
        Require all granted
    </Directory>
</VirtualHost>
```

## ☁️ Cloud Deployment

### AWS Elastic Beanstalk
1. Install EB CLI: `pip install awsebcli`
2. Initialize: `eb init`
3. Create environment: `eb create production`
4. Deploy: `eb deploy`

### Heroku
```bash
# Install Heroku CLI and login
heroku login

# Create app
heroku create your-app-name

# Set environment variables
heroku config:set DEBUG=False
heroku config:set SECRET_KEY=your-secret-key

# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Deploy
git push heroku main

# Run migrations
heroku run python manage.py migrate

# Create superuser
heroku run python manage.py createsuperuser
```

### DigitalOcean App Platform
```yaml
# .do/app.yaml
name: construction-pm
services:
- name: web
  source_dir: /
  github:
    repo: your-username/construction-pm
    branch: main
  run_command: gunicorn construction_pm.wsgi:application
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: DEBUG
    value: "False"
  - key: SECRET_KEY
    value: "your-secret-key"
databases:
- name: db
  engine: PG
  version: "13"
```

## 🔒 Security Checklist

### Pre-deployment Security
- [ ] Set `DEBUG = False` in production
- [ ] Use a strong, unique `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS` properly
- [ ] Enable HTTPS with SSL certificates
- [ ] Set up proper database credentials
- [ ] Configure secure file permissions
- [ ] Enable security headers
- [ ] Set up proper backup procedures

### Security Headers
```python
# settings.py
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
```

## 📊 Monitoring & Logging

### Application Monitoring
```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/construction-pm/django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### Health Check Endpoint
```python
# urls.py
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({'status': 'healthy'})

urlpatterns = [
    path('health/', health_check, name='health_check'),
    # ... other patterns
]
```

## 🔄 Backup & Recovery

### Database Backup
```bash
# PostgreSQL
pg_dump construction_pm > backup_$(date +%Y%m%d_%H%M%S).sql

# MySQL
mysqldump construction_pm > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Media Files Backup
```bash
# Create media backup
tar -czf media_backup_$(date +%Y%m%d_%H%M%S).tar.gz media/

# Sync to cloud storage (AWS S3 example)
aws s3 sync media/ s3://your-bucket/media-backup/
```

### Automated Backup Script
```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/construction-pm"

# Create backup directory
mkdir -p $BACKUP_DIR

# Database backup
pg_dump construction_pm > $BACKUP_DIR/db_$DATE.sql

# Media files backup
tar -czf $BACKUP_DIR/media_$DATE.tar.gz media/

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
```

## 🚨 Troubleshooting

### Common Issues

#### Static Files Not Loading
```bash
# Collect static files
python manage.py collectstatic --noinput

# Check STATIC_ROOT setting
# Verify web server configuration
```

#### Database Connection Issues
```bash
# Test database connection
python manage.py dbshell

# Check database credentials
# Verify database server is running
```

#### Permission Issues
```bash
# Fix file permissions
chown -R www-data:www-data /var/www/construction-pm
chmod -R 755 /var/www/construction-pm
```

### Performance Optimization
```python
# settings.py
# Enable caching
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}

# Database optimization
DATABASES['default']['CONN_MAX_AGE'] = 60

# Static files compression
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
```

---

For more detailed information, refer to the [Django deployment documentation](https://docs.djangoproject.com/en/4.2/howto/deployment/).
