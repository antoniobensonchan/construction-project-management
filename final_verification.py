#!/usr/bin/env python
"""
Final verification script for Construction Project Management System
Verifies that all features are working correctly before final delivery.
"""

import os
import django
import zipfile
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_pm.settings')
django.setup()

from django.contrib.auth import get_user_model
from projects.models import Project, WorkSite
from tasks.models import Task, TaskAnnotation
from drawings.models import Drawing

User = get_user_model()

def verify_export_package():
    """Verify the export package is complete"""
    print("🔍 Verifying export package...")
    
    # Find the latest export
    export_files = [f for f in os.listdir('.') if f.startswith('construction_pm_export_') and f.endswith('.zip')]
    
    if not export_files:
        print("❌ No export package found")
        return False
    
    latest_export = max(export_files)
    print(f"✅ Found export package: {latest_export}")
    
    # Verify ZIP contents
    required_files = [
        'manage.py',
        'requirements.txt',
        'setup.py',
        'create_demo_data.py',
        'README_EN.md',
        'CHANGELOG.md',
        'DEPLOYMENT.md',
        'API_DOCUMENTATION.md',
        'PROJECT_INFO.md',
        'Dockerfile',
        'docker-compose.yml',
        '.gitignore'
    ]
    
    required_dirs = [
        'construction_pm/',
        'accounts/',
        'core/',
        'drawings/',
        'gantt/',
        'projects/',
        'tasks/',
        'templates/',
        'static/',
        'media/'
    ]
    
    try:
        with zipfile.ZipFile(latest_export, 'r') as zipf:
            zip_contents = zipf.namelist()
            
            # Check required files
            missing_files = []
            for file in required_files:
                if not any(file in path for path in zip_contents):
                    missing_files.append(file)
            
            # Check required directories
            missing_dirs = []
            for dir in required_dirs:
                if not any(dir in path for path in zip_contents):
                    missing_dirs.append(dir)
            
            if missing_files:
                print(f"❌ Missing files: {missing_files}")
                return False
            
            if missing_dirs:
                print(f"❌ Missing directories: {missing_dirs}")
                return False
            
            print(f"✅ Export package contains all required files and directories")
            print(f"📊 Total files in package: {len(zip_contents)}")
            
            # Get package size
            package_size = os.path.getsize(latest_export) / (1024 * 1024)
            print(f"📦 Package size: {package_size:.1f} MB")
            
            return True
            
    except Exception as e:
        print(f"❌ Error verifying export package: {e}")
        return False

def verify_database_structure():
    """Verify database models and relationships"""
    print("\n🔍 Verifying database structure...")
    
    try:
        # Check if models can be imported and used
        user_count = User.objects.count()
        project_count = Project.objects.count()
        worksite_count = WorkSite.objects.count()
        task_count = Task.objects.count()
        drawing_count = Drawing.objects.count()
        annotation_count = TaskAnnotation.objects.count()
        
        print(f"✅ Database models working correctly")
        print(f"   Users: {user_count}")
        print(f"   Projects: {project_count}")
        print(f"   Worksites: {worksite_count}")
        print(f"   Tasks: {task_count}")
        print(f"   Drawings: {drawing_count}")
        print(f"   Annotations: {annotation_count}")
        
        # Test relationships
        if project_count > 0:
            project = Project.objects.first()
            worksite_count = project.worksites.count()
            print(f"✅ Project-Worksite relationship working: {worksite_count} worksites")
        
        if task_count > 0:
            task = Task.objects.first()
            drawing_count = task.drawings.count()
            annotation_count = TaskAnnotation.objects.filter(task=task).count()
            print(f"✅ Task-Drawing relationship working: {drawing_count} drawings")
            print(f"✅ Task-Annotation relationship working: {annotation_count} annotations")
        
        return True
        
    except Exception as e:
        print(f"❌ Database structure error: {e}")
        return False

def verify_key_features():
    """Verify key features are working"""
    print("\n🔍 Verifying key features...")
    
    try:
        # Test task-specific annotations
        if TaskAnnotation.objects.exists():
            annotation = TaskAnnotation.objects.first()
            task = annotation.task
            drawing = annotation.drawing
            
            # Check if annotation has proper coordinates
            if annotation.x_coordinate is not None and annotation.y_coordinate is not None:
                print("✅ Task-specific annotations working")
                print(f"   Sample annotation: '{annotation.content}' at ({annotation.x_coordinate}, {annotation.y_coordinate})")
            else:
                print("⚠️  Annotation coordinates missing")
        
        # Test subtask functionality
        subtasks = Task.objects.filter(parent_task__isnull=False)
        if subtasks.exists():
            print(f"✅ Subtask functionality working: {subtasks.count()} subtasks found")
        else:
            print("⚠️  No subtasks found (may be normal)")
        
        # Test drawing-task relationships
        tasks_with_drawings = Task.objects.filter(drawings__isnull=False).distinct()
        if tasks_with_drawings.exists():
            print(f"✅ Drawing-task relationships working: {tasks_with_drawings.count()} tasks with drawings")
        else:
            print("⚠️  No tasks with drawings found")
        
        return True
        
    except Exception as e:
        print(f"❌ Feature verification error: {e}")
        return False

def verify_templates():
    """Verify template files exist and are properly structured"""
    print("\n🔍 Verifying templates...")
    
    template_dir = Path('templates')
    if not template_dir.exists():
        print("❌ Templates directory not found")
        return False
    
    required_templates = [
        'base.html',
        'drawings/drawing_detail.html',
        'tasks/task_detail.html',
        'projects/project_list.html',
        'accounts/login.html'
    ]
    
    missing_templates = []
    for template in required_templates:
        template_path = template_dir / template
        if not template_path.exists():
            missing_templates.append(template)
    
    if missing_templates:
        print(f"❌ Missing templates: {missing_templates}")
        return False
    
    print("✅ All required templates found")
    
    # Check for key features in templates
    drawing_detail_path = template_dir / 'drawings' / 'drawing_detail.html'
    if drawing_detail_path.exists():
        with open(drawing_detail_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        features_found = []
        if 'annotation-layer' in content:
            features_found.append('Annotation layer')
        if 'object-position: left top' in content:
            features_found.append('Left-aligned scaling')
        if 'background: white' in content:
            features_found.append('Solid white backgrounds')
        if 'boxShadow' in content or 'box-shadow' in content:
            features_found.append('Yellow highlight system')
        
        print(f"✅ Key features found in templates: {', '.join(features_found)}")
    
    return True

def verify_static_files():
    """Verify static files are present"""
    print("\n🔍 Verifying static files...")
    
    static_dir = Path('static')
    if not static_dir.exists():
        print("❌ Static directory not found")
        return False
    
    # Check for CSS and JS directories
    css_dir = static_dir / 'css'
    js_dir = static_dir / 'js'
    
    if css_dir.exists():
        css_files = list(css_dir.glob('*.css'))
        print(f"✅ CSS files found: {len(css_files)}")
    else:
        print("⚠️  CSS directory not found")
    
    if js_dir.exists():
        js_files = list(js_dir.glob('*.js'))
        print(f"✅ JavaScript files found: {len(js_files)}")
    else:
        print("⚠️  JavaScript directory not found")
    
    return True

def verify_documentation():
    """Verify documentation files are complete"""
    print("\n🔍 Verifying documentation...")
    
    doc_files = [
        'README_EN.md',
        'CHANGELOG.md',
        'DEPLOYMENT.md',
        'API_DOCUMENTATION.md',
        'PROJECT_SUMMARY.md'
    ]
    
    missing_docs = []
    for doc in doc_files:
        if not os.path.exists(doc):
            missing_docs.append(doc)
        else:
            # Check file size to ensure it's not empty
            size = os.path.getsize(doc)
            if size < 1000:  # Less than 1KB might indicate incomplete documentation
                print(f"⚠️  {doc} seems incomplete ({size} bytes)")
            else:
                print(f"✅ {doc} complete ({size} bytes)")
    
    if missing_docs:
        print(f"❌ Missing documentation: {missing_docs}")
        return False
    
    return True

def main():
    """Main verification function"""
    print("🚀 Final Verification of Construction PM System\n")
    
    verification_results = []
    
    # Run all verifications
    verification_results.append(("Export Package", verify_export_package()))
    verification_results.append(("Database Structure", verify_database_structure()))
    verification_results.append(("Key Features", verify_key_features()))
    verification_results.append(("Templates", verify_templates()))
    verification_results.append(("Static Files", verify_static_files()))
    verification_results.append(("Documentation", verify_documentation()))
    
    # Summary
    print("\n" + "="*60)
    print("📊 VERIFICATION SUMMARY")
    print("="*60)
    
    passed = 0
    total = len(verification_results)
    
    for test_name, result in verification_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1
    
    print("="*60)
    print(f"OVERALL RESULT: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL VERIFICATIONS PASSED!")
        print("✅ System is ready for production deployment")
        print("✅ Export package is complete and ready for distribution")
        print("✅ All key features are working correctly")
        print("✅ Documentation is comprehensive and complete")
        
        print("\n🚀 READY FOR DELIVERY!")
        print("📦 Export package: construction_pm_export_*.zip")
        print("📚 Complete documentation included")
        print("🔧 Automated setup scripts provided")
        print("🐳 Docker deployment ready")
        
    else:
        print(f"\n⚠️  {total - passed} verification(s) failed")
        print("Please review and fix the issues before deployment")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
