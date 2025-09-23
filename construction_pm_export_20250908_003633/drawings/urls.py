from django.urls import path
from . import views

app_name = 'drawings'

urlpatterns = [
    path('', views.drawing_list, name='drawing_list'),
    path('upload/', views.drawing_upload, name='drawing_upload'),
    path('upload/ajax/', views.drawing_upload_ajax, name='drawing_upload_ajax'),
    path('project/<int:project_id>/upload/', views.project_drawing_upload, name='project_drawing_upload'),
    path('worksite/<int:worksite_id>/upload/', views.worksite_drawing_upload, name='worksite_drawing_upload'),
    path('<int:pk>/', views.drawing_detail, name='drawing_detail'),
    path('<int:pk>/delete/', views.drawing_delete, name='drawing_delete'),
]
