"""
Core utility functions
"""
import os
import logging
from datetime import date, timedelta
from django.core.exceptions import ValidationError
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone

logger = logging.getLogger(__name__)


class DateUtils:
    """Utility class for date operations"""

    @staticmethod
    def validate_date_range(start_date, end_date, max_duration_days=None):
        """Validate date range with optional maximum duration"""
        if not start_date or not end_date:
            return True

        if start_date > end_date:
            raise ValidationError('开始日期不能晚于结束日期')

        if max_duration_days:
            duration = (end_date - start_date).days
            if duration > max_duration_days:
                raise ValidationError(f'时间跨度不能超过{max_duration_days}天')

        return True

    @staticmethod
    def calculate_working_days(start_date, end_date, exclude_weekends=True):
        """Calculate working days between two dates"""
        if not start_date or not end_date or start_date > end_date:
            return 0

        total_days = (end_date - start_date).days + 1

        if not exclude_weekends:
            return total_days

        # Count weekends to exclude
        current_date = start_date
        weekend_days = 0

        while current_date <= end_date:
            if current_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
                weekend_days += 1
            current_date += timedelta(days=1)

        return total_days - weekend_days

    @staticmethod
    def get_date_range_overlap(start1, end1, start2, end2):
        """Get overlap between two date ranges"""
        if not all([start1, end1, start2, end2]):
            return None

        overlap_start = max(start1, start2)
        overlap_end = min(end1, end2)

        if overlap_start <= overlap_end:
            return (overlap_start, overlap_end)

        return None


class FileUtils:
    """Utility class for file operations"""

    @staticmethod
    def get_file_size_mb(file_path):
        """Get file size in MB"""
        try:
            if os.path.exists(file_path):
                size_bytes = os.path.getsize(file_path)
                return round(size_bytes / (1024 * 1024), 2)
        except Exception as e:
            logger.error(f"Error getting file size for {file_path}: {e}")
        return 0

    @staticmethod
    def validate_file_extension(filename, allowed_extensions):
        """Validate file extension"""
        if not filename:
            return False

        ext = filename.lower().split('.')[-1]
        return ext in [ext.lower() for ext in allowed_extensions]

    @staticmethod
    def generate_unique_filename(original_filename, prefix="", suffix=""):
        """Generate unique filename with timestamp"""
        import uuid
        from datetime import datetime

        name, ext = os.path.splitext(original_filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]

        return f"{prefix}{name}_{timestamp}_{unique_id}{suffix}{ext}"


class QueryUtils:
    """Utility class for database query optimizations"""

    @staticmethod
    def get_related_objects_count(queryset, related_field):
        """Get count of related objects efficiently"""
        from django.db.models import Count
        return queryset.annotate(
            related_count=Count(related_field)
        ).values_list('related_count', flat=True)

    @staticmethod
    def bulk_update_status(model_class, object_ids, new_status):
        """Bulk update status for multiple objects"""
        with transaction.atomic():
            return model_class.objects.filter(
                id__in=object_ids
            ).update(
                status=new_status,
                updated_at=timezone.now()
            )

    @staticmethod
    def get_objects_with_stats(queryset, stats_fields):
        """Get objects with calculated statistics"""
        from django.db.models import Count, Avg, Sum

        annotations = {}
        for field_name, aggregation in stats_fields.items():
            if aggregation == 'count':
                annotations[f'{field_name}_count'] = Count(field_name)
            elif aggregation == 'avg':
                annotations[f'{field_name}_avg'] = Avg(field_name)
            elif aggregation == 'sum':
                annotations[f'{field_name}_sum'] = Sum(field_name)

        return queryset.annotate(**annotations)


class CacheUtils:
    """Utility class for caching operations"""

    @staticmethod
    def get_cache_key(prefix, *args):
        """Generate cache key from prefix and arguments"""
        key_parts = [str(prefix)]
        key_parts.extend([str(arg) for arg in args])
        return ":".join(key_parts)

    @staticmethod
    def cache_model_method(timeout=300):
        """Decorator for caching model method results"""
        def decorator(func):
            def wrapper(self, *args, **kwargs):
                cache_key = CacheUtils.get_cache_key(
                    f"{self.__class__.__name__}_{func.__name__}",
                    self.pk,
                    *args
                )

                result = cache.get(cache_key)
                if result is None:
                    result = func(self, *args, **kwargs)
                    cache.set(cache_key, result, timeout)

                return result
            return wrapper
        return decorator

    @staticmethod
    def invalidate_model_cache(model_instance, method_names):
        """Invalidate cache for specific model methods"""
        for method_name in method_names:
            cache_key = CacheUtils.get_cache_key(
                f"{model_instance.__class__.__name__}_{method_name}",
                model_instance.pk
            )
            cache.delete(cache_key)


class ValidationUtils:
    """Utility class for validation operations"""

    @staticmethod
    def validate_positive_number(value, field_name="数值"):
        """Validate that a number is positive"""
        if value is not None and value <= 0:
            raise ValidationError(f'{field_name}必须大于0')
        return value

    @staticmethod
    def validate_percentage(value, field_name="百分比"):
        """Validate percentage value (0-100)"""
        if value is not None and (value < 0 or value > 100):
            raise ValidationError(f'{field_name}必须在0-100之间')
        return value

    @staticmethod
    def validate_phone_number(phone_number):
        """Validate Chinese phone number format"""
        import re

        if not phone_number:
            return True

        # Chinese mobile phone pattern
        pattern = r'^1[3-9]\d{9}$'
        if not re.match(pattern, phone_number):
            raise ValidationError('请输入有效的手机号码')

        return True

    @staticmethod
    def validate_required_fields(data, required_fields):
        """Validate that required fields are present and not empty"""
        errors = {}

        for field in required_fields:
            if field not in data or not data[field]:
                errors[field] = f'{field}是必填字段'

        if errors:
            raise ValidationError(errors)

        return True


class ProgressUtils:
    """Utility class for progress calculations"""

    @staticmethod
    def calculate_weighted_progress(items, weight_field='weight', progress_field='progress'):
        """Calculate weighted average progress"""
        if not items:
            return 0

        total_weight = sum(getattr(item, weight_field, 1) for item in items)
        if total_weight == 0:
            return 0

        weighted_sum = sum(
            getattr(item, progress_field, 0) * getattr(item, weight_field, 1)
            for item in items
        )

        return round(weighted_sum / total_weight, 1)

    @staticmethod
    def calculate_completion_rate(completed_count, total_count):
        """Calculate completion rate as percentage"""
        if total_count == 0:
            return 0

        return round((completed_count / total_count) * 100, 1)

    @staticmethod
    def get_progress_status(progress_percentage):
        """Get progress status based on percentage"""
        if progress_percentage >= 100:
            return 'completed'
        elif progress_percentage >= 75:
            return 'nearly_complete'
        elif progress_percentage >= 25:
            return 'in_progress'
        elif progress_percentage > 0:
            return 'started'
        else:
            return 'not_started'


class ExportUtils:
    """Utility class for data export operations"""

    @staticmethod
    def export_to_csv(queryset, fields, filename=None):
        """Export queryset to CSV"""
        import csv
        from django.http import HttpResponse
        from datetime import datetime

        if not filename:
            filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        writer = csv.writer(response)

        # Write header
        header = [field.replace('_', ' ').title() for field in fields]
        writer.writerow(header)

        # Write data
        for obj in queryset:
            row = []
            for field in fields:
                value = getattr(obj, field, '')
                if hasattr(value, 'strftime'):  # Date/datetime field
                    value = value.strftime('%Y-%m-%d')
                row.append(str(value))
            writer.writerow(row)

        return response

    @staticmethod
    def export_to_excel(queryset, fields, filename=None, sheet_name='Data'):
        """Export queryset to Excel (requires openpyxl)"""
        try:
            from openpyxl import Workbook
            from django.http import HttpResponse
            from datetime import datetime
            import io

            if not filename:
                filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

            wb = Workbook()
            ws = wb.active
            ws.title = sheet_name

            # Write header
            header = [field.replace('_', ' ').title() for field in fields]
            ws.append(header)

            # Write data
            for obj in queryset:
                row = []
                for field in fields:
                    value = getattr(obj, field, '')
                    if hasattr(value, 'strftime'):  # Date/datetime field
                        value = value.strftime('%Y-%m-%d')
                    row.append(str(value))
                ws.append(row)

            # Save to memory
            output = io.BytesIO()
            wb.save(output)
            output.seek(0)

            response = HttpResponse(
                output.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="{filename}"'

            return response

        except ImportError:
            raise ImportError("openpyxl is required for Excel export. Install with: pip install openpyxl")


class LoggingUtils:
    """Utility class for logging operations"""

    @staticmethod
    def log_user_action(user, action, object_type, object_id, details=None):
        """Log user actions for audit trail"""
        logger.info(
            f"User {user.username} performed {action} on {object_type} {object_id}",
            extra={
                'user_id': user.id,
                'action': action,
                'object_type': object_type,
                'object_id': object_id,
                'details': details or {}
            }
        )

    @staticmethod
    def log_performance(func_name, execution_time, query_count=None):
        """Log performance metrics"""
        message = f"Function {func_name} executed in {execution_time:.2f}s"
        if query_count:
            message += f" with {query_count} database queries"

        logger.info(message, extra={
            'function': func_name,
            'execution_time': execution_time,
            'query_count': query_count
        })
