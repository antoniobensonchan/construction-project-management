from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .models import Drawing
from .forms import DrawingUploadForm
from projects.models import Project, WorkSite
from tasks.models import Task


def drawing_list(request):
    """图纸列表页面"""
    # 只显示用户拥有的项目下的图纸
    if request.user.is_authenticated:
        drawings = Drawing.objects.filter(worksite__project__owner=request.user).order_by('-uploaded_at')
    else:
        drawings = Drawing.objects.none()

    return render(request, 'drawings/drawing_list.html', {
        'drawings': drawings
    })


def drawing_upload(request, project_id=None):
    """图纸上传页面（已废弃，请使用工地图纸上传）"""
    # 重定向到图纸列表，因为现在图纸属于工地
    messages.warning(request, '请在具体工地中上传图纸')
    return redirect('drawings:drawing_list')


def worksite_drawing_upload(request, worksite_id):
    """工地图纸上传页面"""
    worksite = get_object_or_404(WorkSite, pk=worksite_id, project__owner=request.user)

    if request.method == 'POST':
        form = DrawingUploadForm(request.POST, request.FILES)
        if form.is_valid():
            drawing = form.save(commit=False)
            drawing.worksite = worksite
            drawing.save()
            messages.success(request, f'图纸上传成功：{drawing.name}')
            return redirect('projects:worksite_detail', pk=worksite.pk)
        else:
            # 返回错误信息
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        form = DrawingUploadForm()

    return render(request, 'drawings/worksite_drawing_upload.html', {
        'form': form,
        'worksite': worksite,
        'project': worksite.project
    })


def project_drawing_upload(request, project_id):
    """项目内图纸上传（重定向到项目详情）"""
    project = get_object_or_404(Project, pk=project_id, owner=request.user)

    messages.info(request, '图纸应该在具体工地中上传。请选择一个工地，然后在工地中上传图纸。')
    return redirect('projects:project_detail', pk=project.pk)


@csrf_exempt
@require_http_methods(["POST"])
def drawing_upload_ajax(request):
    """AJAX图纸上传接口"""
    try:
        form = DrawingUploadForm(request.POST, request.FILES)
        if form.is_valid():
            drawing = form.save()
            return JsonResponse({
                'success': True,
                'message': f'图纸上传成功：{drawing.name}',
                'drawing_id': drawing.id,
                'drawing_name': drawing.name
            })
        else:
            errors = []
            for field, field_errors in form.errors.items():
                for error in field_errors:
                    errors.append(error)
            return JsonResponse({
                'success': False,
                'errors': errors
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'errors': [str(e)]
        })


def drawing_detail(request, pk):
    """图纸详情页面（预览）"""
    drawing = get_object_or_404(Drawing, pk=pk)

    # 获取使用此图纸的所有任务（通过标注关联）
    related_tasks = Task.objects.filter(
        annotations__drawing=drawing
    ).distinct().select_related('worksite', 'worksite__project')

    # 获取此图纸上的所有标注
    all_annotations = drawing.annotations.all().select_related('task', 'task__worksite')

    return render(request, 'drawings/drawing_detail.html', {
        'drawing': drawing,
        'related_tasks': related_tasks,
        'all_annotations': all_annotations,
        'worksite': drawing.worksite,
        'project': drawing.worksite.project if drawing.worksite else None
    })


def drawing_delete(request, pk):
    """删除图纸"""
    drawing = get_object_or_404(Drawing, pk=pk)

    if request.method == 'POST':
        drawing_name = drawing.name
        drawing.delete()
        messages.success(request, f'图纸 "{drawing_name}" 已删除')
        return redirect('drawings:drawing_list')

    return render(request, 'drawings/drawing_delete.html', {
        'drawing': drawing
    })
