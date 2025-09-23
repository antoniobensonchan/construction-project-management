# 🏗️ Construction Project Management System

[![Django](https://img.shields.io/badge/Django-4.2.7-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.1.3-purple.svg)](https://getbootstrap.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A comprehensive construction project management system featuring advanced PDF drawing annotations, task management, and project visualization.

## ✨ Key Features

### 🎯 Revolutionary Annotation System
- **Task-specific overlays**: Different tasks show different annotations on the same drawing
- **Pixel-perfect positioning**: Consistent annotation placement across all pages
- **Multiple annotation types**: Points, rectangles, text, and lines
- **Real-time collaboration**: Multiple teams can work on the same drawings

### 📊 Project Management
- **Hierarchical structure**: Projects → Worksites → Tasks → Subtasks
- **Gantt chart visualization**: Interactive timeline with dependencies
- **Progress tracking**: Real-time status updates and progress calculation
- **Task dependencies**: Four dependency types with lag time support

### 🔐 Enterprise Features
- **Company isolation**: Complete data separation between companies
- **User authentication**: Secure login with role-based access
- **File management**: PDF upload with validation and thumbnail generation
- **Responsive design**: Works on desktop and mobile devices

## 🚀 Quick Start

### Using Docker (Recommended)
```bash
git clone https://github.com/antoniobensonchan/construction-project-management.git
cd construction-project-management
docker-compose up --build
```

### Manual Installation
```bash
# Clone the repository
git clone https://github.com/antoniobensonchan/construction-project-management.git
cd construction-project-management

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Run migrations
python manage.py migrate

# Load demo data (optional)
python manage.py shell < create_demo_data.py

# Start development server
python manage.py runserver
```

## 🎯 Demo Account
- **Username**: `company_a`
- **Password**: `demo123`

## 📚 Documentation

- [Installation Guide](DEPLOYMENT.md)
- [API Documentation](API_DOCUMENTATION.md)
- [Change Log](CHANGELOG.md)
- [Project Summary](PROJECT_SUMMARY.md)

## 🛠️ Tech Stack

- **Backend**: Django 4.2.7, Python 3.8+
- **Frontend**: Bootstrap 5, JavaScript ES6+, PDF.js
- **Database**: SQLite (dev), MySQL/PostgreSQL (prod)
- **Deployment**: Docker, Gunicorn, Nginx

## 🏗️ Architecture

```
Projects
├── Worksites
│   ├── Tasks (Main Tasks)
│   │   ├── Subtasks
│   │   └── Annotations (Task-specific)
│   └── Drawings
│       └── Annotations (Shared across tasks)
└── Users (Company-based access control)
```

## 🌟 Screenshots

### Project Dashboard
![Project Dashboard](docs/screenshots/dashboard.png)

### Drawing Annotation System
![Drawing Annotations](docs/screenshots/annotations.png)

### Gantt Chart Visualization
![Gantt Chart](docs/screenshots/gantt.png)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for the construction industry
- Inspired by modern project management needs
- Designed with user experience in mind

## 📞 Support

If you have any questions or need help, please:
- Open an issue on GitHub
- Check the documentation
- Contact the development team

---

**Ready to revolutionize your construction project management? The future of construction technology is here.**
