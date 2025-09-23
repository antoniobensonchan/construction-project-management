#!/usr/bin/env python
"""
Setup script for Construction Project Management System
Run this script to set up the project after extraction.
"""

import os
import subprocess
import sys

def run_command(command, description):
    """Run a command and handle errors"""
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
    """Main setup function"""
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
