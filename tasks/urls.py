from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    path('', views.task_list, name='task_list'),
    path('create/', views.task_create, name='task_create'),
    path('create/step2/', views.task_create_step2, name='task_create_step2'),
    path('project/<int:project_id>/create/', views.project_task_create, name='project_task_create'),
    path('worksite/<int:worksite_id>/create/', views.worksite_task_create, name='worksite_task_create'),
    path('save-annotations/', views.save_annotations, name='save_annotations'),
    path('create-annotation/', views.create_annotation, name='create_annotation'),
    path('<int:pk>/', views.task_detail, name='task_detail'),
    path('<int:pk>/update/', views.task_update, name='task_update'),
    path('<int:pk>/delete/', views.task_delete, name='task_delete'),
    path('annotation/<int:annotation_id>/update/', views.update_annotation, name='update_annotation'),
    path('annotation/<int:annotation_id>/delete/', views.delete_annotation, name='delete_annotation'),
    path('annotation/create/', views.create_annotation, name='create_annotation'),
    # 子任务管理
    path('<int:parent_task_id>/subtask/create/', views.subtask_create, name='subtask_create'),
    path('subtask/<int:subtask_id>/update-status/', views.subtask_update_status, name='subtask_update_status'),
    path('subtask/<int:subtask_id>/delete/', views.subtask_delete, name='subtask_delete'),
    # 任务依赖管理
    path('<int:task_id>/dependency/add/', views.task_add_dependency, name='task_add_dependency'),
    path('dependency/<int:dependency_id>/remove/', views.task_remove_dependency, name='task_remove_dependency'),
    path('<int:task_id>/dependency/status/', views.task_dependency_status, name='task_dependency_status'),
]
