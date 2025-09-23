#!/usr/bin/env python
"""
Code optimization script for Construction Project Management System
This script performs various code optimizations and cleanup tasks.
"""

import os
import re
import shutil
from pathlib import Path

def remove_test_files():
    """Remove test files created during development"""
    test_files = [
        'test_annotation_consistency_fix.py',
        'test_annotation_alignment_fix.py',
        'test_responsive_annotations.py',
        'test_annotation_fix_final.py',
        'test_revert_to_working_state.py',
        'test_left_aligned_annotations.py',
        'test_consistent_scaling.py',
        'test_left_aligned_preview.py',
        'test_scaled_left_aligned_images.py',
        'test_solid_white_background.py',
        'test_yellow_highlight_only.py'
    ]

    removed_count = 0
    for file_name in test_files:
        if os.path.exists(file_name):
            os.remove(file_name)
            removed_count += 1
            print(f"✅ Removed test file: {file_name}")

    print(f"📊 Removed {removed_count} test files")

def optimize_templates():
    """Optimize template files by removing unnecessary comments and whitespace"""
    template_dirs = ['templates']
    optimized_count = 0

    for template_dir in template_dirs:
        if os.path.exists(template_dir):
            for root, dirs, files in os.walk(template_dir):
                for file in files:
                    if file.endswith('.html'):
                        file_path = os.path.join(root, file)
                        optimize_html_file(file_path)
                        optimized_count += 1

    print(f"📊 Optimized {optimized_count} template files")

def optimize_html_file(file_path):
    """Optimize a single HTML file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Remove excessive whitespace while preserving structure
        # Remove empty lines with only whitespace
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)

        # Remove trailing whitespace from lines
        content = re.sub(r'[ \t]+$', '', content, flags=re.MULTILINE)

        # Remove development comments (but keep important ones)
        content = re.sub(r'<!--\s*注释：[^>]*-->', '', content)
        content = re.sub(r'<!--\s*DEBUG[^>]*-->', '', content)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"✅ Optimized template: {file_path}")

    except Exception as e:
        print(f"❌ Error optimizing {file_path}: {e}")

def optimize_static_files():
    """Optimize static files (CSS, JS)"""
    static_dirs = ['static', 'staticfiles']
    optimized_count = 0

    for static_dir in static_dirs:
        if os.path.exists(static_dir):
            for root, dirs, files in os.walk(static_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    if file.endswith('.css'):
                        optimize_css_file(file_path)
                        optimized_count += 1
                    elif file.endswith('.js'):
                        optimize_js_file(file_path)
                        optimized_count += 1

    print(f"📊 Optimized {optimized_count} static files")

def optimize_css_file(file_path):
    """Optimize a CSS file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Remove excessive whitespace
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        content = re.sub(r'[ \t]+$', '', content, flags=re.MULTILINE)

        # Remove development comments
        content = re.sub(r'/\*\s*DEBUG[^*]*\*/', '', content)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"✅ Optimized CSS: {file_path}")

    except Exception as e:
        print(f"❌ Error optimizing CSS {file_path}: {e}")

def optimize_js_file(file_path):
    """Optimize a JavaScript file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Remove excessive whitespace
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        content = re.sub(r'[ \t]+$', '', content, flags=re.MULTILINE)

        # Remove development comments and console.logs
        content = re.sub(r'//\s*DEBUG[^\n]*\n', '\n', content)
        content = re.sub(r'console\.log\([^)]*\);\s*\n?', '', content)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"✅ Optimized JS: {file_path}")

    except Exception as e:
        print(f"❌ Error optimizing JS {file_path}: {e}")

def optimize_python_files():
    """Optimize Python files by removing unused imports and cleaning up"""
    python_files = []

    # Find all Python files
    for root, dirs, files in os.walk('.'):
        # Skip virtual environments and migrations
        if 'venv' in root or 'migrations' in root or '__pycache__' in root:
            continue

        for file in files:
            if file.endswith('.py') and not file.startswith('test_'):
                python_files.append(os.path.join(root, file))

    optimized_count = 0
    for file_path in python_files:
        if optimize_python_file(file_path):
            optimized_count += 1

    print(f"📊 Optimized {optimized_count} Python files")

def optimize_python_file(file_path):
    """Optimize a single Python file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # Remove excessive blank lines
        content = re.sub(r'\n\s*\n\s*\n\s*\n', '\n\n\n', content)

        # Remove trailing whitespace
        content = re.sub(r'[ \t]+$', '', content, flags=re.MULTILINE)

        # Remove debug print statements
        content = re.sub(r'^\s*print\s*\(\s*["\']DEBUG[^)]*\)\s*$', '', content, flags=re.MULTILINE)

        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Optimized Python: {file_path}")
            return True

        return False

    except Exception as e:
        print(f"❌ Error optimizing Python {file_path}: {e}")
        return False

def create_requirements_txt():
    """Create or update requirements.txt with current dependencies"""
    try:
        # Basic requirements for the project
        requirements = [
            "Django>=4.2.0,<5.0.0",
            "Pillow>=10.0.0",
            "python-decouple>=3.8",
            "whitenoise>=6.5.0",
            "gunicorn>=21.2.0",
        ]

        with open('requirements.txt', 'w') as f:
            for req in requirements:
                f.write(f"{req}\n")

        print("✅ Created/updated requirements.txt")

    except Exception as e:
        print(f"❌ Error creating requirements.txt: {e}")

def create_gitignore():
    """Create or update .gitignore file"""
    gitignore_content = """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
.python-version

# celery beat schedule file
celerybeat-schedule

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# Django specific
media/
staticfiles/
static/admin/
static/rest_framework/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Project specific
test_*.py
*.zip
backup_*
"""

    try:
        with open('.gitignore', 'w') as f:
            f.write(gitignore_content)
        print("✅ Created/updated .gitignore")
    except Exception as e:
        print(f"❌ Error creating .gitignore: {e}")

def create_docker_files():
    """Create Docker configuration files"""

    # Dockerfile
    dockerfile_content = """FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \\
    && apt-get install -y --no-install-recommends \\
        postgresql-client \\
        gcc \\
        python3-dev \\
        musl-dev \\
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Create media and static directories
RUN mkdir -p /app/media /app/staticfiles

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health/ || exit 1

# Run the application
CMD ["gunicorn", "construction_pm.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
"""

    # docker-compose.yml
    docker_compose_content = """version: '3.8'

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
      - static_volume:/app/staticfiles

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=construction_pm
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
  media_volume:
  static_volume:
"""

    try:
        with open('Dockerfile', 'w') as f:
            f.write(dockerfile_content)
        print("✅ Created Dockerfile")

        with open('docker-compose.yml', 'w') as f:
            f.write(docker_compose_content)
        print("✅ Created docker-compose.yml")

    except Exception as e:
        print(f"❌ Error creating Docker files: {e}")

def main():
    """Main optimization function"""
    print("🚀 Starting code optimization...\n")

    # Remove test files
    print("1. Removing test files...")
    remove_test_files()
    print()

    # Optimize templates
    print("2. Optimizing templates...")
    optimize_templates()
    print()

    # Optimize static files
    print("3. Optimizing static files...")
    optimize_static_files()
    print()

    # Optimize Python files
    print("4. Optimizing Python files...")
    optimize_python_files()
    print()

    # Create/update project files
    print("5. Creating/updating project files...")
    create_requirements_txt()
    create_gitignore()
    create_docker_files()
    print()

    print("✅ Code optimization completed!")
    print("\n📊 Summary:")
    print("   - Removed development test files")
    print("   - Optimized HTML templates")
    print("   - Optimized CSS and JavaScript files")
    print("   - Cleaned up Python files")
    print("   - Updated requirements.txt")
    print("   - Created/updated .gitignore")
    print("   - Created Docker configuration files")
    print("\n🎯 Next steps:")
    print("   - Review the optimized code")
    print("   - Test the application")
    print("   - Create project export zip")
    print("   - Deploy to production")

if __name__ == "__main__":
    main()
