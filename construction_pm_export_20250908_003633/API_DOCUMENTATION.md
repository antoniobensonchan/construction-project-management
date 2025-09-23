# API Documentation

This document describes the API endpoints and data structures for the Construction Project Management System.

## 🔗 Base URL
```
http://localhost:8000/  (Development)
https://yourdomain.com/ (Production)
```

## 🔐 Authentication

The system uses Django's session-based authentication. Users must log in through the web interface.

### Login
```http
POST /accounts/login/
Content-Type: application/x-www-form-urlencoded

username=your_username&password=your_password
```

### Logout
```http
POST /accounts/logout/
```

## 📊 Data Models

### Project
```json
{
  "id": 1,
  "name": "Downtown Office Complex",
  "description": "Modern office building construction",
  "owner": 1,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### Worksite
```json
{
  "id": 1,
  "name": "Building A - Foundation",
  "project": 1,
  "description": "Foundation work for main building",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Task
```json
{
  "id": 1,
  "name": "Install Electrical Conduits",
  "description": "Install main electrical conduits in basement",
  "worksite": 1,
  "parent_task": null,
  "status": "in_progress",
  "priority": "high",
  "assigned_to": 2,
  "due_date": "2024-02-01",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-16T14:20:00Z",
  "drawings": [1, 2]
}
```

### Drawing
```json
{
  "id": 1,
  "title": "Electrical Layout - Basement",
  "description": "Main electrical layout for basement level",
  "file": "/media/drawings/electrical_basement.pdf",
  "worksite": 1,
  "uploaded_by": 1,
  "uploaded_at": "2024-01-15T10:30:00Z"
}
```

### TaskAnnotation
```json
{
  "id": 1,
  "task": 1,
  "drawing": 1,
  "annotation_type": "text",
  "content": "Install junction box here",
  "x_coordinate": 150.5,
  "y_coordinate": 200.3,
  "end_x": null,
  "end_y": null,
  "color": "red",
  "created_at": "2024-01-15T10:30:00Z",
  "created_by": 1
}
```

## 🛠 API Endpoints

### Projects

#### List Projects
```http
GET /projects/
```

**Response:**
```json
{
  "projects": [
    {
      "id": 1,
      "name": "Downtown Office Complex",
      "description": "Modern office building construction",
      "owner": 1,
      "worksite_count": 3,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

#### Get Project Details
```http
GET /projects/{id}/
```

#### Create Project
```http
POST /projects/create/
Content-Type: application/x-www-form-urlencoded

name=New Project&description=Project description
```

#### Update Project
```http
POST /projects/{id}/edit/
Content-Type: application/x-www-form-urlencoded

name=Updated Project&description=Updated description
```

#### Delete Project
```http
POST /projects/{id}/delete/
```

### Worksites

#### List Worksites
```http
GET /projects/{project_id}/worksites/
```

#### Get Worksite Details
```http
GET /worksites/{id}/
```

#### Create Worksite
```http
POST /worksites/create/
Content-Type: application/x-www-form-urlencoded

name=New Worksite&project={project_id}&description=Worksite description
```

### Tasks

#### List Tasks
```http
GET /tasks/
```

**Query Parameters:**
- `worksite`: Filter by worksite ID
- `status`: Filter by status (pending, in_progress, completed, cancelled)
- `assigned_to`: Filter by assigned user ID
- `parent_task`: Filter by parent task ID (for subtasks)

#### Get Task Details
```http
GET /tasks/{id}/
```

**Response:**
```json
{
  "task": {
    "id": 1,
    "name": "Install Electrical Conduits",
    "description": "Install main electrical conduits in basement",
    "worksite": {
      "id": 1,
      "name": "Building A - Foundation",
      "project": {
        "id": 1,
        "name": "Downtown Office Complex"
      }
    },
    "status": "in_progress",
    "priority": "high",
    "assigned_to": {
      "id": 2,
      "username": "electrician1",
      "company_name": "ABC Electric"
    },
    "subtasks": [
      {
        "id": 2,
        "name": "Mark conduit locations",
        "status": "completed"
      }
    ],
    "drawings": [
      {
        "id": 1,
        "title": "Electrical Layout - Basement",
        "file": "/media/drawings/electrical_basement.pdf"
      }
    ],
    "annotations": [
      {
        "id": 1,
        "annotation_type": "text",
        "content": "Install junction box here",
        "x_coordinate": 150.5,
        "y_coordinate": 200.3
      }
    ]
  }
}
```

#### Create Task
```http
POST /tasks/create/
Content-Type: application/x-www-form-urlencoded

name=New Task&worksite={worksite_id}&description=Task description&priority=medium
```

#### Update Task
```http
POST /tasks/{id}/edit/
Content-Type: application/x-www-form-urlencoded

name=Updated Task&status=completed&description=Updated description
```

#### Create Subtask
```http
POST /tasks/create/
Content-Type: application/x-www-form-urlencoded

name=Subtask Name&parent_task={parent_id}&worksite={worksite_id}
```

### Drawings

#### List Drawings
```http
GET /drawings/
```

**Query Parameters:**
- `worksite`: Filter by worksite ID

#### Get Drawing Details
```http
GET /drawings/{id}/
```

**Response:**
```json
{
  "drawing": {
    "id": 1,
    "title": "Electrical Layout - Basement",
    "description": "Main electrical layout for basement level",
    "file": "/media/drawings/electrical_basement.pdf",
    "worksite": {
      "id": 1,
      "name": "Building A - Foundation"
    },
    "uploaded_by": {
      "id": 1,
      "username": "project_manager"
    },
    "uploaded_at": "2024-01-15T10:30:00Z",
    "related_tasks": [
      {
        "id": 1,
        "name": "Install Electrical Conduits",
        "status": "in_progress"
      }
    ],
    "all_annotations": [
      {
        "id": 1,
        "task": {
          "id": 1,
          "name": "Install Electrical Conduits"
        },
        "annotation_type": "text",
        "content": "Install junction box here",
        "x_coordinate": 150.5,
        "y_coordinate": 200.3,
        "color": "red"
      }
    ]
  }
}
```

#### Upload Drawing
```http
POST /drawings/upload/
Content-Type: multipart/form-data

title=Drawing Title&worksite={worksite_id}&file=@drawing.pdf&description=Description
```

#### Delete Drawing
```http
POST /drawings/{id}/delete/
```

### Annotations

#### Create Annotation
```http
POST /annotations/create/
Content-Type: application/json

{
  "task_id": 1,
  "drawing_id": 1,
  "annotation_type": "text",
  "content": "Install junction box here",
  "x_coordinate": 150.5,
  "y_coordinate": 200.3,
  "color": "red"
}
```

#### Update Annotation
```http
PUT /annotations/{id}/
Content-Type: application/json

{
  "content": "Updated annotation text",
  "x_coordinate": 155.0,
  "y_coordinate": 205.0
}
```

#### Delete Annotation
```http
DELETE /annotations/{id}/
```

#### Get Task Annotations
```http
GET /annotations/task/{task_id}/
```

#### Get Drawing Annotations
```http
GET /annotations/drawing/{drawing_id}/
```

**Query Parameters:**
- `task_id`: Filter annotations by specific task (for task-specific overlays)

## 📝 Annotation Types

### Point Annotation
```json
{
  "annotation_type": "point",
  "content": "Inspection point",
  "x_coordinate": 150.5,
  "y_coordinate": 200.3,
  "color": "red"
}
```

### Text Annotation
```json
{
  "annotation_type": "text",
  "content": "Install junction box here",
  "x_coordinate": 150.5,
  "y_coordinate": 200.3,
  "color": "red"
}
```

### Line Annotation
```json
{
  "annotation_type": "line",
  "content": "Conduit run",
  "x_coordinate": 100.0,
  "y_coordinate": 150.0,
  "end_x": 200.0,
  "end_y": 250.0,
  "color": "blue"
}
```

## 🔍 Search & Filtering

### Search Tasks
```http
GET /tasks/search/?q=electrical
```

### Filter by Status
```http
GET /tasks/?status=in_progress
```

### Filter by Date Range
```http
GET /tasks/?created_after=2024-01-01&created_before=2024-01-31
```

## 📊 Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Permission denied
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

## 🚨 Error Responses

```json
{
  "error": "Validation failed",
  "details": {
    "name": ["This field is required."],
    "email": ["Enter a valid email address."]
  }
}
```

## 📈 Rate Limiting

- **Authenticated users**: 1000 requests per hour
- **Anonymous users**: 100 requests per hour

## 🔄 Pagination

Large result sets are paginated:

```json
{
  "count": 150,
  "next": "http://localhost:8000/tasks/?page=2",
  "previous": null,
  "results": [...]
}
```

## 📱 WebSocket Events (Future)

*Planned for real-time updates:*

### Task Updates
```javascript
// Connect to WebSocket
const socket = new WebSocket('ws://localhost:8000/ws/tasks/');

// Listen for task updates
socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    if (data.type === 'task_update') {
        // Handle task update
        updateTaskInUI(data.task);
    }
};
```

### Annotation Updates
```javascript
// Listen for annotation changes
socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    if (data.type === 'annotation_update') {
        // Handle annotation update
        updateAnnotationInUI(data.annotation);
    }
};
```

## 🧪 Testing the API

### Using cURL
```bash
# Login and get session cookie
curl -c cookies.txt -d "username=company_a&password=demo123" \
     -X POST http://localhost:8000/accounts/login/

# Use session cookie for authenticated requests
curl -b cookies.txt http://localhost:8000/tasks/1/
```

### Using Python requests
```python
import requests

# Login
session = requests.Session()
login_data = {'username': 'company_a', 'password': 'demo123'}
session.post('http://localhost:8000/accounts/login/', data=login_data)

# Make authenticated requests
response = session.get('http://localhost:8000/tasks/1/')
task_data = response.json()
```

---

For more detailed examples and interactive API testing, consider setting up tools like Postman or Swagger UI.
