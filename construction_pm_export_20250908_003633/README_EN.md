# Construction Project Management System

A comprehensive construction project management system built with Django, featuring advanced drawing annotation capabilities and task-specific overlay management.

## 🚀 Key Features

### 📋 Project & Task Management
- **Multi-level Project Structure**: Projects → Worksites → Tasks → Subtasks
- **Task-specific Annotation Overlays**: Different tasks show different marks on the same drawing
- **Subtask Management**: Dedicated pages for subtasks with simplified interface
- **Progress Tracking**: Visual progress indicators and status management
- **Responsive Task Lists**: Real-time task status updates

### 📐 Advanced Drawing Management
- **Drawing Annotation System**: Point, text, and line annotations on technical drawings
- **Task-specific Overlays**: Each task can have its own set of annotations on shared drawings
- **Consistent Positioning**: Annotations maintain accurate positions across different pages
- **Left-aligned Scaling**: Images scale to fit preview while maintaining left alignment
- **Yellow Highlight System**: Clean highlighting with yellow glow without changing annotation appearance

### 🎨 User Interface
- **Dual Page System**: 
  - Drawing Detail Pages: Full annotation management and drawing preview
  - Task Detail Pages: Task-focused view with relevant drawing annotations
- **Responsive Design**: Works on desktop and mobile devices
- **Consistent Styling**: Unified annotation appearance across all pages
- **Professional Layout**: Clean, modern interface optimized for construction workflows

### 🔧 Technical Features
- **Scalable Architecture**: Django-based backend with modular design
- **Database Optimization**: Efficient queries and data relationships
- **Cross-browser Compatibility**: Works on Chrome, Firefox, Edge, and Safari
- **Performance Optimized**: Fast loading and smooth interactions

## 📊 System Architecture

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

## 🛠 Installation

### Prerequisites
- Python 3.8+
- Django 4.2+
- SQLite (default) or PostgreSQL/MySQL

### Quick Start
```bash
# Clone the repository
git clone <repository-url>
cd ConstructionPMProject

# Install dependencies
pip install -r requirements.txt

# Run database migrations
python manage.py migrate

# Create demo data (optional)
python manage.py shell < create_demo_data.py

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

### Demo Account
- **Username**: `company_a`
- **Password**: `demo123`
- **Features**: Pre-loaded with sample projects, tasks, and annotations

## 📖 Usage Guide

### 1. Project Management
- Create and manage construction projects
- Organize projects by worksites
- Track project progress and status

### 2. Task Management
- Create main tasks and subtasks
- Assign tasks to team members
- Track task progress and deadlines
- Use dedicated subtask pages for focused work

### 3. Drawing Annotation System
- Upload technical drawings (images/PDFs)
- Add task-specific annotations:
  - **Point annotations**: Mark specific locations
  - **Text annotations**: Add notes and labels
  - **Line annotations**: Draw lines and measurements
- View different annotation overlays per task
- Maintain consistent annotation positioning

### 4. Navigation
- **Drawing Detail Pages**: `http://localhost:8000/drawings/{id}/`
  - Full drawing management interface
  - All annotation tools
  - Task-specific overlay switching
- **Task Detail Pages**: `http://localhost:8000/tasks/{id}/`
  - Task-focused interface
  - Relevant drawing annotations
  - Simplified layout for task execution

## 🎯 Key Improvements in This Version

### Annotation System Enhancements
- ✅ **Task-specific Overlays**: Different tasks show different annotations on the same drawing
- ✅ **Consistent Positioning**: Fixed annotation alignment issues between pages
- ✅ **Left-aligned Scaling**: Images scale properly while maintaining accurate annotation positions
- ✅ **Solid White Backgrounds**: Text annotations use consistent white backgrounds
- ✅ **Yellow Highlight Only**: Clean highlighting system that doesn't change annotation appearance

### User Interface Improvements
- ✅ **Subtask Dedicated Pages**: Specialized interface for subtasks without drawing preview complexity
- ✅ **Responsive Design**: Works seamlessly on different screen sizes
- ✅ **Professional Styling**: Consistent, modern interface design
- ✅ **Optimized Performance**: Fast loading and smooth interactions

### Technical Optimizations
- ✅ **Code Simplification**: Removed complex scaling calculations in favor of reliable CSS solutions
- ✅ **Cross-browser Compatibility**: Consistent behavior across all modern browsers
- ✅ **Database Efficiency**: Optimized queries and data relationships
- ✅ **Maintainable Code**: Clean, well-documented codebase

## 🔧 Technical Details

### Database Models
- **Project**: Top-level project container
- **Worksite**: Project subdivisions
- **Task**: Main work items with subtask support
- **Drawing**: Technical drawings with file management
- **TaskAnnotation**: Task-specific annotations with position data
- **User**: Company-based user management

### Key Technologies
- **Backend**: Django 4.2, Python 3.8+
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Database**: SQLite (development), PostgreSQL/MySQL (production)
- **File Storage**: Local filesystem with media handling
- **Authentication**: Django's built-in authentication system

### API Endpoints
- Project management: `/projects/`
- Task management: `/tasks/`
- Drawing management: `/drawings/`
- Annotation management: `/annotations/`
- User authentication: `/accounts/`

## 📱 Browser Support
- ✅ Chrome 80+
- ✅ Firefox 75+
- ✅ Safari 13+
- ✅ Edge 80+
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

## 🚀 Deployment

### Production Setup
```bash
# Set environment variables
export DEBUG=False
export SECRET_KEY='your-secret-key'
export DATABASE_URL='your-database-url'

# Install production dependencies
pip install -r requirements.txt gunicorn

# Collect static files
python manage.py collectstatic

# Run with Gunicorn
gunicorn construction_pm.wsgi:application
```

### Docker Deployment
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["gunicorn", "construction_pm.wsgi:application", "--bind", "0.0.0.0:8000"]
```

## 🧪 Testing

### Run Tests
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test projects
python manage.py test tasks
python manage.py test drawings

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

### Test Data
- Use `create_demo_data.py` to generate test data
- Demo account includes sample projects, tasks, and annotations
- Test different annotation types and task scenarios

## 📚 Documentation

### Code Documentation
- Inline comments for complex logic
- Docstrings for all functions and classes
- Type hints where applicable
- README files in each app directory

### User Documentation
- Feature guides in `/docs/` directory
- Video tutorials (planned)
- API documentation (planned)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Submit a pull request

### Code Style
- Follow PEP 8 for Python code
- Use meaningful variable names
- Add comments for complex logic
- Write tests for new features

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation in `/docs/`
- Review the demo data and examples

## 🔄 Version History

### v2.0.0 (Current)
- Task-specific annotation overlays
- Consistent annotation positioning
- Subtask dedicated pages
- Left-aligned image scaling
- Yellow highlight system
- Performance optimizations

### v1.0.0
- Basic project and task management
- Drawing upload and viewing
- Simple annotation system
- User authentication

## 🎯 Roadmap

### Planned Features
- [ ] Real-time collaboration
- [ ] Mobile app
- [ ] Advanced reporting
- [ ] Integration with CAD software
- [ ] Offline support
- [ ] Advanced user permissions
- [ ] Notification system
- [ ] File version control

---

**Built with ❤️ for the construction industry**
