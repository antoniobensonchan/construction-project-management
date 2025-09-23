from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    # 项目管理
    path('', views.project_list, name='project_list'),
    path('create/', views.project_create, name='project_create'),
    path('<int:pk>/', views.project_detail, name='project_detail'),
    path('<int:pk>/update/', views.project_update, name='project_update'),
    path('<int:pk>/delete/', views.project_delete, name='project_delete'),
    path('<int:pk>/status/', views.project_status_update, name='project_status_update'),

    # 工地管理
    path('<int:project_pk>/worksites/create/', views.worksite_create, name='worksite_create'),
    path('worksites/<int:pk>/', views.worksite_detail, name='worksite_detail'),
    path('worksites/<int:pk>/update/', views.worksite_update, name='worksite_update'),
    path('worksites/<int:pk>/delete/', views.worksite_delete, name='worksite_delete'),
]
