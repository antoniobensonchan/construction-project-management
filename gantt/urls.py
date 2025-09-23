from django.urls import path
from . import views

app_name = 'gantt'

urlpatterns = [
    # 甘特图页面
    path('project/<int:project_id>/', views.project_gantt, name='project_gantt'),

    # 甘特图数据API
    path('api/project/<int:project_id>/data/', views.gantt_data_api, name='gantt_data_api'),

    # PDF导出
    path('project/<int:project_id>/export-pdf/', views.export_gantt_pdf, name='export_gantt_pdf'),
    path('project/<int:project_id>/export-simple-pdf/', views.export_gantt_simple_pdf, name='export_gantt_simple_pdf'),

    # 替代导出方案
    path('project/<int:project_id>/export-csv/', views.export_gantt_csv, name='export_gantt_csv'),
]
