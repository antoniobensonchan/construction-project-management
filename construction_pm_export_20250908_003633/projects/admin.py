from django.contrib import admin
from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'start_date', 'end_date', 'progress_percentage', 'created_at']
    list_filter = ['status', 'start_date', 'end_date']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'progress_percentage']

    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'description', 'status')
        }),
        ('时间安排', {
            'fields': ('start_date', 'end_date')
        }),
        ('系统信息', {
            'fields': ('created_at', 'updated_at', 'progress_percentage'),
            'classes': ('collapse',)
        })
    )
