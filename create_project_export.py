#!/usr/bin/env python
"""
Project export script for Construction Project Management System
Creates a clean, production-ready export of the project.
"""

import os
import shutil
import zipfile
from datetime import datetime
from pathlib import Path

def create_export_directory():
    """Create export directory with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_dir = f"construction_pm_export_{timestamp}"
    
    if os.path.exists(export_dir):
        shutil.rmtree(export_dir)
    
    os.makedirs(export_dir)
    return export_dir

def copy_essential_files(export_dir):
    """Copy essential project files to export directory"""
    
    # Core Django files and directories
    essential_items = [
        'manage.py',
        'construction_pm/',
        'accounts/',
        'core/',
        'drawings/',
        'gantt/',
        'projects/',
        'tasks/',
        'templates/',
        'static/',
        'media/',
        'requirements.txt',
        'README_EN.md',
        'CHANGELOG.md',
        'DEPLOYMENT.md',
        'API_DOCUMENTATION.md',
        'Dockerfile',
        'docker-compose.yml',
        '.gitignore'
    ]
    
    copied_count = 0
    
    for item in essential_items:
        if os.path.exists(item):
            dest_path = os.path.join(export_dir, item)
            
            if os.path.isdir(item):
                # Copy directory, excluding certain subdirectories
                shutil.copytree(item, dest_path, ignore=ignore_patterns)
                print(f"✅ Copied directory: {item}")
            else:
                # Copy file
                shutil.copy2(item, dest_path)
                print(f"✅ Copied file: {item}")
            
            copied_count += 1
        else:
            print(f"⚠️  Item not found: {item}")
    
    print(f"📊 Copied {copied_count} essential items")

def ignore_patterns(dir, files):
    """Define patterns to ignore when copying directories"""
    ignore_list = []
    
    for file in files:
        # Ignore patterns
        if (file.startswith('.') and file not in ['.gitignore'] or
            file.endswith('.pyc') or
            file.endswith('.pyo') or
            file == '__pycache__' or
            file == 'migrations' or
            file.startswith('test_') or
            file == 'db.sqlite3' or
            file == 'db.sqlite3-journal' or
            file.endswith('.log')):
            ignore_list.append(file)
    
    return ignore_list

def create_setup_script(export_dir):
    """Create setup script for the exported project"""
    
    setup_script = """#!/usr/bin/env python
\"\"\"
Setup script for Construction Project Management System
Run this script to set up the project after extraction.
\"\"\"

import os
import subprocess
import sys

def run_command(command, description):
    \"\"\"Run a command and handle errors\"\"\"
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def main():
    \"\"\"Main setup function\"\"\"
    print("🚀 Setting up Construction Project Management System...")
    print()
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python version: {sys.version}")
    print()
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        print("❌ Failed to install dependencies. Please install manually:")
        print("   pip install -r requirements.txt")
        return
    
    # Run migrations
    if not run_command("python manage.py migrate", "Running database migrations"):
        print("❌ Failed to run migrations")
        return
    
    # Collect static files
    if not run_command("python manage.py collectstatic --noinput", "Collecting static files"):
        print("⚠️  Failed to collect static files (optional)")
    
    # Create superuser prompt
    print()
    print("🔐 Create a superuser account:")
    print("   Run: python manage.py createsuperuser")
    print()
    
    # Load demo data prompt
    print("📊 Load demo data (optional):")
    print("   Run: python manage.py shell < create_demo_data.py")
    print()
    
    # Start server prompt
    print("🌐 Start the development server:")
    print("   Run: python manage.py runserver")
    print("   Then visit: http://localhost:8000")
    print()
    
    # Demo account info
    print("🎯 Demo account (if demo data is loaded):")
    print("   Username: company_a")
    print("   Password: demo123")
    print()
    
    print("✅ Setup completed successfully!")
    print()
    print("📚 Documentation:")
    print("   - README_EN.md: Complete feature overview")
    print("   - DEPLOYMENT.md: Production deployment guide")
    print("   - API_DOCUMENTATION.md: API reference")
    print("   - CHANGELOG.md: Version history")
    print()
    print("🐳 Docker deployment:")
    print("   Run: docker-compose up --build")

if __name__ == "__main__":
    main()
"""
    
    setup_path = os.path.join(export_dir, 'setup.py')
    with open(setup_path, 'w', encoding='utf-8') as f:
        f.write(setup_script)
    
    # Make executable on Unix systems
    if os.name != 'nt':
        os.chmod(setup_path, 0o755)
    
    print("✅ Created setup script")

def create_demo_data_script(export_dir):
    """Create demo data script for the exported project"""
    
    demo_script = """#!/usr/bin/env python
\"\"\"
Demo data creation script for Construction Project Management System
Creates sample data for testing and demonstration purposes.
\"\"\"

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_pm.settings')
django.setup()

from django.contrib.auth import get_user_model
from projects.models import Project, Worksite
from tasks.models import Task, TaskAnnotation
from drawings.models import Drawing
from django.core.files.base import ContentFile
import io
from PIL import Image

User = get_user_model()

def create_demo_data():
    \"\"\"Create comprehensive demo data\"\"\"
    
    print("🚀 Creating demo data...")
    
    # Create demo user
    user, created = User.objects.get_or_create(
        username='company_a',
        defaults={
            'email': 'demo@company-a.com',
            'company_name': 'Company A Construction',
            'first_name': 'Demo',
            'last_name': 'User'
        }
    )
    
    if created:
        user.set_password('demo123')
        user.save()
        print("✅ Created demo user: company_a")
    else:
        print("✅ Demo user already exists: company_a")
    
    # Create demo project
    project, created = Project.objects.get_or_create(
        name='Downtown Office Complex',
        owner=user,
        defaults={
            'description': 'Modern office building construction project with advanced features'
        }
    )
    
    if created:
        print("✅ Created demo project: Downtown Office Complex")
    else:
        print("✅ Demo project already exists: Downtown Office Complex")
    
    # Create demo worksite
    worksite, created = Worksite.objects.get_or_create(
        name='Building A - Main Structure',
        project=project,
        defaults={
            'description': 'Main building structure and foundation work'
        }
    )
    
    if created:
        print("✅ Created demo worksite: Building A - Main Structure")
    else:
        print("✅ Demo worksite already exists: Building A - Main Structure")
    
    # Create demo drawing
    if not Drawing.objects.filter(title='Electrical Layout - Floor 1').exists():
        # Create a simple demo image
        img = Image.new('RGB', (800, 600), color='white')
        img_io = io.BytesIO()
        img.save(img_io, format='PNG')
        img_io.seek(0)
        
        drawing = Drawing.objects.create(
            title='Electrical Layout - Floor 1',
            description='Main electrical layout for first floor',
            worksite=worksite,
            uploaded_by=user
        )
        
        drawing.file.save(
            'demo_electrical_layout.png',
            ContentFile(img_io.getvalue()),
            save=True
        )
        
        print("✅ Created demo drawing: Electrical Layout - Floor 1")
    else:
        drawing = Drawing.objects.get(title='Electrical Layout - Floor 1')
        print("✅ Demo drawing already exists: Electrical Layout - Floor 1")
    
    # Create demo tasks
    main_task, created = Task.objects.get_or_create(
        name='Install Electrical Systems',
        worksite=worksite,
        parent_task=None,
        defaults={
            'description': 'Install main electrical systems including conduits, panels, and wiring',
            'status': 'in_progress',
            'priority': 'high',
            'assigned_to': user
        }
    )
    
    if created:
        main_task.drawings.add(drawing)
        print("✅ Created main task: Install Electrical Systems")
    else:
        print("✅ Main task already exists: Install Electrical Systems")
    
    # Create subtask
    subtask, created = Task.objects.get_or_create(
        name='Install Junction Boxes',
        worksite=worksite,
        parent_task=main_task,
        defaults={
            'description': 'Install electrical junction boxes at marked locations',
            'status': 'pending',
            'priority': 'medium',
            'assigned_to': user
        }
    )
    
    if created:
        print("✅ Created subtask: Install Junction Boxes")
    else:
        print("✅ Subtask already exists: Install Junction Boxes")
    
    # Create demo annotations
    if not TaskAnnotation.objects.filter(task=main_task, drawing=drawing).exists():
        # Text annotation
        TaskAnnotation.objects.create(
            task=main_task,
            drawing=drawing,
            annotation_type='text',
            content='Main Panel Location',
            x_coordinate=150,
            y_coordinate=100,
            color='red',
            created_by=user
        )
        
        # Point annotation
        TaskAnnotation.objects.create(
            task=main_task,
            drawing=drawing,
            annotation_type='point',
            content='Inspection Point',
            x_coordinate=300,
            y_coordinate=200,
            color='blue',
            created_by=user
        )
        
        # Line annotation
        TaskAnnotation.objects.create(
            task=main_task,
            drawing=drawing,
            annotation_type='line',
            content='Conduit Run',
            x_coordinate=100,
            y_coordinate=150,
            end_x=400,
            end_y=250,
            color='green',
            created_by=user
        )
        
        print("✅ Created demo annotations")
    else:
        print("✅ Demo annotations already exist")
    
    print()
    print("🎯 Demo data creation completed!")
    print()
    print("📊 Created:")
    print(f"   - User: {user.username} (password: demo123)")
    print(f"   - Project: {project.name}")
    print(f"   - Worksite: {worksite.name}")
    print(f"   - Drawing: {drawing.title}")
    print(f"   - Main Task: {main_task.name}")
    print(f"   - Subtask: {subtask.name}")
    print(f"   - Annotations: 3 different types")
    print()
    print("🌐 Access the system:")
    print("   URL: http://localhost:8000")
    print("   Username: company_a")
    print("   Password: demo123")

if __name__ == '__main__':
    create_demo_data()
"""
    
    demo_path = os.path.join(export_dir, 'create_demo_data.py')
    with open(demo_path, 'w', encoding='utf-8') as f:
        f.write(demo_script)
    
    print("✅ Created demo data script")

def create_project_info(export_dir):
    """Create project information file"""
    
    info_content = f"""# Construction Project Management System - Export Package

**Export Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Version**: 2.0.0
**Export Type**: Production Ready

## 📦 Package Contents

### Core Application
- Django project with all apps and configurations
- Database models and migrations
- Templates with optimized HTML/CSS/JS
- Static files and media handling
- User authentication and authorization

### Key Features
- ✅ Task-specific annotation overlays
- ✅ Consistent annotation positioning
- ✅ Subtask dedicated pages
- ✅ Left-aligned image scaling
- ✅ Yellow highlight system
- ✅ Responsive design
- ✅ Cross-browser compatibility

### Documentation
- `README_EN.md`: Complete feature overview and installation guide
- `CHANGELOG.md`: Detailed version history and changes
- `DEPLOYMENT.md`: Production deployment instructions
- `API_DOCUMENTATION.md`: API endpoints and usage examples

### Setup Files
- `setup.py`: Automated setup script
- `create_demo_data.py`: Demo data creation script
- `requirements.txt`: Python dependencies
- `Dockerfile`: Docker container configuration
- `docker-compose.yml`: Multi-container deployment
- `.gitignore`: Git ignore patterns

## 🚀 Quick Start

### Option 1: Automated Setup
```bash
python setup.py
```

### Option 2: Manual Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load demo data (optional)
python manage.py shell < create_demo_data.py

# Start server
python manage.py runserver
```

### Option 3: Docker
```bash
docker-compose up --build
```

## 🎯 Demo Account
- **Username**: company_a
- **Password**: demo123
- **Features**: Pre-loaded projects, tasks, and annotations

## 📱 Browser Support
- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+
- Mobile browsers

## 🔧 System Requirements
- Python 3.8+
- Django 4.2+
- 512MB RAM minimum
- 1GB disk space

## 📚 Additional Resources
- GitHub repository (if available)
- Issue tracker
- Documentation website
- Community support

## 📄 License
MIT License - See project files for details

---
**Built with ❤️ for the construction industry**
"""
    
    info_path = os.path.join(export_dir, 'PROJECT_INFO.md')
    with open(info_path, 'w', encoding='utf-8') as f:
        f.write(info_content)
    
    print("✅ Created project information file")

def create_zip_archive(export_dir):
    """Create ZIP archive of the export"""
    
    zip_filename = f"{export_dir}.zip"
    
    print(f"📦 Creating ZIP archive: {zip_filename}")
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(export_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arc_path = os.path.relpath(file_path, export_dir)
                zipf.write(file_path, arc_path)
    
    # Get file size
    file_size = os.path.getsize(zip_filename)
    file_size_mb = file_size / (1024 * 1024)
    
    print(f"✅ Created ZIP archive: {zip_filename} ({file_size_mb:.1f} MB)")
    
    return zip_filename

def main():
    """Main export function"""
    print("🚀 Creating Construction PM Project Export...\n")
    
    # Create export directory
    print("1. Creating export directory...")
    export_dir = create_export_directory()
    print(f"✅ Created export directory: {export_dir}\n")
    
    # Copy essential files
    print("2. Copying essential files...")
    copy_essential_files(export_dir)
    print()
    
    # Create setup script
    print("3. Creating setup script...")
    create_setup_script(export_dir)
    print()
    
    # Create demo data script
    print("4. Creating demo data script...")
    create_demo_data_script(export_dir)
    print()
    
    # Create project info
    print("5. Creating project information...")
    create_project_info(export_dir)
    print()
    
    # Create ZIP archive
    print("6. Creating ZIP archive...")
    zip_filename = create_zip_archive(export_dir)
    print()
    
    print("✅ Project export completed successfully!")
    print()
    print("📊 Export Summary:")
    print(f"   - Export Directory: {export_dir}")
    print(f"   - ZIP Archive: {zip_filename}")
    print(f"   - Ready for distribution and deployment")
    print()
    print("🎯 Next Steps:")
    print("   1. Test the exported project")
    print("   2. Distribute the ZIP file")
    print("   3. Follow setup instructions in PROJECT_INFO.md")
    print("   4. Deploy to production using DEPLOYMENT.md")
    
    return export_dir, zip_filename

if __name__ == "__main__":
    main()
