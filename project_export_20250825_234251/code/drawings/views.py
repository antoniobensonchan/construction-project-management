from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .models import Drawing
from .forms import DrawingUploadForm
from projects.models import Project


def drawing_list(request):
    """图纸列表页面"""
    drawings = Drawing.objects.all()
    return render(request, 'drawings/drawing_list.html', {
        'drawings': drawings
    })


def drawing_upload(request, project_id=None):
    """图纸上传页面"""
    project = None
    if project_id:
        project = get_object_or_404(Project, pk=project_id)

    if request.method == 'POST':
        form = DrawingUploadForm(request.POST, request.FILES)
        if form.is_valid():
            drawing = form.save(commit=False)
            if project:
                drawing.project = project
            drawing.save()
            messages.success(request, f'图纸上传成功：{drawing.name}')

            if project:
                return redirect('projects:project_detail', pk=project.pk)
            else:
                return redirect('drawings:drawing_list')
        else:
            # 返回错误信息
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        form = DrawingUploadForm()

    return render(request, 'drawings/drawing_upload.html', {
        'form': form,
        'project': project
    })


def project_drawing_upload(request, project_id):
    """项目内图纸上传"""
    return drawing_upload(request, project_id)


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

    # 获取使用此图纸的所有任务
    related_tasks = drawing.tasks.all().select_related('project')

    # 获取此图纸上的所有标注
    all_annotations = drawing.annotations.all().select_related('task')

    return render(request, 'drawings/drawing_detail.html', {
        'drawing': drawing,
        'related_tasks': related_tasks,
        'all_annotations': all_annotations
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
