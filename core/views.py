"""
Optimized base views for the construction PM system
"""
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.db.models import Prefetch, Q
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache
import time
import logging

from .mixins import (
    UserOwnedMixin, OptimizedQueryMixin, CacheMixin,
    APIResponseMixin, BulkOperationMixin
)
from .utils import LoggingUtils

logger = logging.getLogger(__name__)


class BaseListView(LoginRequiredMixin, UserOwnedMixin, OptimizedQueryMixin, ListView):
    """Optimized base list view with user ownership and query optimization"""

    paginate_by = 20
    context_object_name = 'objects'

    def get_queryset(self):
        """Get optimized queryset for current user"""
        queryset = super().get_queryset()

        # Apply user filtering if model has owner field
        if hasattr(self.model, 'owner'):
            queryset = queryset.filter(owner=self.request.user)

        # Apply search if search_fields is defined
        search_query = self.request.GET.get('search')
        if search_query and hasattr(self, 'search_fields'):
            search_filter = Q()
            for field in self.search_fields:
                search_filter |= Q(**{f"{field}__icontains": search_query})
            queryset = queryset.filter(search_filter)

        # Apply ordering
        ordering = self.get_ordering()
        if ordering:
            queryset = queryset.order_by(*ordering)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add search query to context
        context['search_query'] = self.request.GET.get('search', '')

        # Add filter options if defined
        if hasattr(self, 'filter_fields'):
            for field in self.filter_fields:
                filter_value = self.request.GET.get(field)
                if filter_value:
                    context[f'{field}_filter'] = filter_value

        return context


class BaseDetailView(LoginRequiredMixin, UserOwnedMixin, OptimizedQueryMixin, DetailView):
    """Optimized base detail view with ownership verification"""

    def get_object(self, queryset=None):
        """Get object with ownership verification"""
        obj = super().get_object(queryset)

        # Verify ownership based on model type
        if hasattr(obj, 'owner'):
            if obj.owner != self.request.user:
                raise PermissionDenied("You don't have permission to access this object")
        elif hasattr(obj, 'project'):
            self.verify_project_ownership(obj.project)
        elif hasattr(obj, 'worksite'):
            self.verify_worksite_ownership(obj.worksite)

        return obj

    def get_queryset(self):
        """Get optimized queryset with related objects"""
        queryset = super().get_queryset()

        # Add select_related and prefetch_related if defined
        if hasattr(self, 'select_related_fields'):
            queryset = queryset.select_related(*self.select_related_fields)

        if hasattr(self, 'prefetch_related_fields'):
            queryset = queryset.prefetch_related(*self.prefetch_related_fields)

        return queryset


class BaseCreateView(LoginRequiredMixin, UserOwnedMixin, CreateView):
    """Optimized base create view"""

    def form_valid(self, form):
        """Set owner and log action"""
        # Set owner if model has owner field
        if hasattr(form.instance, 'owner'):
            form.instance.owner = self.request.user

        response = super().form_valid(form)

        # Log user action
        LoggingUtils.log_user_action(
            self.request.user,
            'create',
            self.model.__name__,
            self.object.pk
        )

        # Add success message
        messages.success(
            self.request,
            f'{self.model._meta.verbose_name}创建成功！'
        )

        return response

    def get_form_kwargs(self):
        """Add additional form kwargs"""
        kwargs = super().get_form_kwargs()

        # Add user to form kwargs if form accepts it
        if hasattr(self.form_class, 'user'):
            kwargs['user'] = self.request.user

        return kwargs


class BaseUpdateView(LoginRequiredMixin, UserOwnedMixin, UpdateView):
    """Optimized base update view"""

    def get_object(self, queryset=None):
        """Get object with ownership verification"""
        obj = super().get_object(queryset)

        # Verify ownership
        if hasattr(obj, 'owner'):
            if obj.owner != self.request.user:
                raise PermissionDenied("You don't have permission to edit this object")
        elif hasattr(obj, 'project'):
            self.verify_project_ownership(obj.project)
        elif hasattr(obj, 'worksite'):
            self.verify_worksite_ownership(obj.worksite)

        return obj

    def form_valid(self, form):
        """Log action and add success message"""
        response = super().form_valid(form)

        # Log user action
        LoggingUtils.log_user_action(
            self.request.user,
            'update',
            self.model.__name__,
            self.object.pk
        )

        # Add success message
        messages.success(
            self.request,
            f'{self.model._meta.verbose_name}更新成功！'
        )

        return response


class BaseDeleteView(LoginRequiredMixin, UserOwnedMixin, DeleteView):
    """Optimized base delete view"""

    def get_object(self, queryset=None):
        """Get object with ownership verification"""
        obj = super().get_object(queryset)

        # Verify ownership
        if hasattr(obj, 'owner'):
            if obj.owner != self.request.user:
                raise PermissionDenied("You don't have permission to delete this object")
        elif hasattr(obj, 'project'):
            self.verify_project_ownership(obj.project)
        elif hasattr(obj, 'worksite'):
            self.verify_worksite_ownership(obj.worksite)

        return obj

    def delete(self, request, *args, **kwargs):
        """Log action and add success message"""
        obj = self.get_object()
        obj_name = str(obj)

        # Log user action
        LoggingUtils.log_user_action(
            request.user,
            'delete',
            self.model.__name__,
            obj.pk,
            {'name': obj_name}
        )

        response = super().delete(request, *args, **kwargs)

        # Add success message
        messages.success(
            request,
            f'{self.model._meta.verbose_name}"{obj_name}"删除成功！'
        )

        return response


class BaseAPIView(LoginRequiredMixin, UserOwnedMixin, APIResponseMixin):
    """Base API view with consistent response format"""

    def dispatch(self, request, *args, **kwargs):
        """Add performance logging"""
        start_time = time.time()

        try:
            response = super().dispatch(request, *args, **kwargs)

            # Log performance
            execution_time = time.time() - start_time
            LoggingUtils.log_performance(
                f"{self.__class__.__name__}.{request.method.lower()}",
                execution_time
            )

            return response

        except Exception as e:
            logger.error(f"API error in {self.__class__.__name__}: {str(e)}")
            return self.error_response(f"服务器错误: {str(e)}", status=500)


class CachedListView(BaseListView, CacheMixin):
    """List view with caching support"""

    cache_timeout = 300  # 5 minutes

    @method_decorator(cache_page(cache_timeout))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_cache_key(self):
        """Generate cache key for this view"""
        return f"{self.__class__.__name__}_{self.request.user.id}_{self.request.GET.urlencode()}"


class BulkActionView(BaseAPIView, BulkOperationMixin):
    """View for handling bulk operations"""

    allowed_actions = ['delete', 'update_status', 'export']

    def post(self, request, *args, **kwargs):
        """Handle bulk actions"""
        action = request.POST.get('action')
        object_ids = request.POST.getlist('object_ids')

        if not action or action not in self.allowed_actions:
            return self.error_response("无效的操作")

        if not object_ids:
            return self.error_response("请选择要操作的项目")

        try:
            result = self.perform_bulk_action(action, object_ids, request.POST)
            return self.success_response(result, f"批量{action}操作完成")

        except Exception as e:
            logger.error(f"Bulk action error: {str(e)}")
            return self.error_response(f"批量操作失败: {str(e)}")

    def perform_bulk_action(self, action, object_ids, data):
        """Perform the actual bulk action"""
        queryset = self.get_queryset().filter(id__in=object_ids)

        if action == 'delete':
            count = queryset.count()
            queryset.delete()
            return {'deleted_count': count}

        elif action == 'update_status':
            new_status = data.get('new_status')
            if not new_status:
                raise ValueError("新状态不能为空")

            count = queryset.update(status=new_status)
            return {'updated_count': count}

        elif action == 'export':
            # This would be implemented based on specific needs
            return {'export_url': '/path/to/export/file'}

        else:
            raise ValueError(f"不支持的操作: {action}")


class DashboardView(BaseListView, CacheMixin):
    """Dashboard view with aggregated data"""

    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get cached dashboard data or calculate it
        cache_key = f"dashboard_{self.request.user.id}"
        dashboard_data = cache.get(cache_key)

        if dashboard_data is None:
            dashboard_data = self.calculate_dashboard_data()
            cache.set(cache_key, dashboard_data, 300)  # Cache for 5 minutes

        context.update(dashboard_data)
        return context

    def calculate_dashboard_data(self):
        """Calculate dashboard statistics"""
        from projects.models import Project
        from tasks.models import Task
        from drawings.models import Drawing

        user_projects = self.get_user_projects()

        return {
            'total_projects': user_projects.count(),
            'active_projects': user_projects.filter(status='active').count(),
            'total_tasks': Task.objects.filter(worksite__project__owner=self.request.user).count(),
            'completed_tasks': Task.objects.filter(
                worksite__project__owner=self.request.user,
                status='completed'
            ).count(),
            'total_drawings': Drawing.objects.filter(
                worksite__project__owner=self.request.user
            ).count(),
            'recent_projects': user_projects.order_by('-created_at')[:5],
            'recent_tasks': Task.objects.filter(
                worksite__project__owner=self.request.user
            ).order_by('-created_at')[:10]
        }
