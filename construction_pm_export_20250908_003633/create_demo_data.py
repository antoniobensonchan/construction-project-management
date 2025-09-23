#!/usr/bin/env python
"""
Demo data creation script for Construction Project Management System
Creates sample data for testing and demonstration purposes.
"""

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
    """Create comprehensive demo data"""
    
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
