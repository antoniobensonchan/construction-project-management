"""
Core mixins for views and models
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django.db import models
from django.utils import timezone
from datetime import date


class UserOwnedMixin:
    """Mixin for views that require user ownership verification"""

    def get_user_projects(self):
        """Get projects owned by current user"""
        return self.request.user.owned_projects.all()

    def verify_project_ownership(self, project):
        """Verify that current user owns the project"""
        if project.owner != self.request.user:
            raise PermissionDenied("You don't have permission to access this project")
        return project

    def verify_worksite_ownership(self, worksite):
        """Verify that current user owns the worksite's project"""
        return self.verify_project_ownership(worksite.project)

    def verify_task_ownership(self, task):
        """Verify that current user owns the task's project"""
        return self.verify_project_ownership(task.worksite.project)

    def verify_drawing_ownership(self, drawing):
        """Verify that current user owns the drawing's project"""
        return self.verify_project_ownership(drawing.worksite.project)


class OptimizedQueryMixin:
    """Mixin for optimized database queries"""

    def get_optimized_projects(self, user):
        """Get projects with optimized queries"""
        return user.owned_projects.select_related().prefetch_related(
            'worksites',
            'worksites__tasks',
            'worksites__drawings'
        )

    def get_optimized_tasks(self, project):
        """Get tasks with optimized queries"""
        return project.worksites.prefetch_related(
            'tasks__subtasks',
            'tasks__dependencies',
            'tasks__predecessor_dependencies',
            'tasks__drawings'
        )

    def get_optimized_worksites(self, project):
        """Get worksites with optimized queries"""
        return project.worksites.select_related('project').prefetch_related(
            'tasks',
            'drawings',
            'tasks__subtasks'
        )


class TimestampMixin(models.Model):
    """Abstract model mixin for timestamp fields"""

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        abstract = True


class DateValidationMixin:
    """Mixin for date validation logic"""

    def validate_date_range(self, start_date, end_date, field_prefix=""):
        """Validate that start_date <= end_date"""
        if start_date and end_date and start_date > end_date:
            field_name = f"{field_prefix}日期" if field_prefix else "日期"
            raise models.ValidationError(f'{field_name}开始时间不能晚于结束时间')

    def validate_date_within_parent(self, start_date, end_date, parent_start, parent_end, parent_name="父级"):
        """Validate that dates are within parent date range"""
        if start_date and parent_start and start_date < parent_start:
            raise models.ValidationError(f'开始日期不能早于{parent_name}开始日期')

        if end_date and parent_end and end_date > parent_end:
            raise models.ValidationError(f'结束日期不能晚于{parent_name}结束日期')

    def calculate_progress_by_time(self, start_date, end_date, status=None):
        """Calculate progress based on time elapsed"""
        if status == 'completed':
            return 100
        elif status in ['cancelled', 'suspended']:
            return 0

        if not start_date or not end_date:
            return 0

        today = date.today()
        if today < start_date:
            return 0
        elif today > end_date:
            return 100
        else:
            total_days = (end_date - start_date).days
            elapsed_days = (today - start_date).days
            return min(100, int((elapsed_days / total_days) * 100)) if total_days > 0 else 0


class StatusChoicesMixin:
    """Mixin for common status choices"""

    PROJECT_STATUS_CHOICES = [
        ('planning', '规划中'),
        ('active', '进行中'),
        ('completed', '已完成'),
        ('suspended', '暂停'),
        ('cancelled', '已取消'),
    ]

    TASK_STATUS_CHOICES = [
        ('open', '开放'),
        ('in_progress', '进行中'),
        ('pending', '待处理'),
        ('completed', '已完成'),
    ]

    TASK_TYPE_CHOICES = [
        ('new_construction', '新建施工'),
        ('repair', '整改修复'),
        ('inspection', '检查验收'),
        ('maintenance', '维护保养'),
    ]

    WORKSITE_STATUS_CHOICES = [
        ('planning', '规划中'),
        ('active', '施工中'),
        ('completed', '已完成'),
        ('suspended', '暂停'),
    ]


class CacheMixin:
    """Mixin for caching common calculations"""

    def get_cached_or_calculate(self, cache_key, calculation_func, timeout=300):
        """Get cached value or calculate and cache it"""
        from django.core.cache import cache

        cached_value = cache.get(cache_key)
        if cached_value is not None:
            return cached_value

        calculated_value = calculation_func()
        cache.set(cache_key, calculated_value, timeout)
        return calculated_value

    def invalidate_cache(self, cache_keys):
        """Invalidate multiple cache keys"""
        from django.core.cache import cache

        if isinstance(cache_keys, str):
            cache_keys = [cache_keys]

        for key in cache_keys:
            cache.delete(key)


class BulkOperationMixin:
    """Mixin for bulk database operations"""

    def bulk_create_with_validation(self, model_class, objects_data, batch_size=100):
        """Bulk create objects with validation"""
        objects = []
        for data in objects_data:
            obj = model_class(**data)
            obj.full_clean()  # Validate before creating
            objects.append(obj)

        return model_class.objects.bulk_create(objects, batch_size=batch_size)

    def bulk_update_fields(self, queryset, updates, batch_size=100):
        """Bulk update specific fields"""
        objects = list(queryset)
        for obj in objects:
            for field, value in updates.items():
                setattr(obj, field, value)

        return queryset.model.objects.bulk_update(
            objects,
            list(updates.keys()),
            batch_size=batch_size
        )


class FormValidationMixin:
    """Mixin for common form validation"""

    def validate_date_fields(self, start_field='start_date', end_field='end_date'):
        """Validate date fields in forms"""
        cleaned_data = super().clean() if hasattr(super(), 'clean') else self.cleaned_data
        start_date = cleaned_data.get(start_field)
        end_date = cleaned_data.get(end_field)

        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError(f'{start_field}不能晚于{end_field}')

        return cleaned_data

    def add_date_widget_attrs(self, field_name):
        """Add HTML5 date widget attributes"""
        if field_name in self.fields:
            self.fields[field_name].widget.attrs.update({
                'type': 'date',
                'class': 'form-control'
            })


class APIResponseMixin:
    """Mixin for consistent API responses"""

    def success_response(self, data=None, message="操作成功"):
        """Return success response"""
        from django.http import JsonResponse

        response_data = {
            'success': True,
            'message': message
        }
        if data:
            response_data['data'] = data

        return JsonResponse(response_data)

    def error_response(self, message="操作失败", errors=None, status=400):
        """Return error response"""
        from django.http import JsonResponse

        response_data = {
            'success': False,
            'message': message
        }
        if errors:
            response_data['errors'] = errors

        return JsonResponse(response_data, status=status)

    def paginated_response(self, queryset, page_size=20, page=1):
        """Return paginated response"""
        from django.core.paginator import Paginator
        from django.http import JsonResponse

        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)

        return JsonResponse({
            'success': True,
            'data': {
                'items': [item.to_dict() if hasattr(item, 'to_dict') else str(item) for item in page_obj],
                'pagination': {
                    'current_page': page_obj.number,
                    'total_pages': paginator.num_pages,
                    'total_items': paginator.count,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous(),
                }
            }
        })
