from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Project
from .forms import ProjectForm


def project_list(request):
    """项目列表页面"""
    projects = Project.objects.all().order_by('-created_at')
    return render(request, 'projects/project_list.html', {
        'projects': projects
    })


def project_create(request):
    """创建项目"""
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save()
            messages.success(request, f'项目"{project.name}"创建成功！')
            return redirect('projects:project_detail', pk=project.pk)
    else:
        form = ProjectForm()

    return render(request, 'projects/project_create.html', {
        'form': form
    })


def project_detail(request, pk):
    """项目详情页面（项目主页）"""
    project = get_object_or_404(Project, pk=pk)

    # 获取项目相关数据
    drawings = project.drawings.all().order_by('-uploaded_at')
    tasks = project.tasks.all().order_by('-created_at')

    # 统计数据
    stats = {
        'total_drawings': drawings.count(),
        'total_tasks': tasks.count(),
        'completed_tasks': tasks.filter(status='completed').count(),
        'pending_tasks': tasks.filter(status='pending').count(),
        'in_progress_tasks': tasks.filter(status='in_progress').count(),
    }

    return render(request, 'projects/project_detail.html', {
        'project': project,
        'drawings': drawings,
        'tasks': tasks,
        'stats': stats
    })


def project_update(request, pk):
    """更新项目"""
    project = get_object_or_404(Project, pk=pk)

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, f'项目"{project.name}"更新成功！')
            return redirect('projects:project_detail', pk=project.pk)
    else:
        form = ProjectForm(instance=project)

    return render(request, 'projects/project_update.html', {
        'form': form,
        'project': project
    })


def project_delete(request, pk):
    """删除项目"""
    project = get_object_or_404(Project, pk=pk)

    if request.method == 'POST':
        project_name = project.name
        project.delete()
        messages.success(request, f'项目"{project_name}"已删除')
        return redirect('projects:project_list')

    return render(request, 'projects/project_delete_confirm.html', {
        'project': project
    })


@require_http_methods(["POST"])
def project_status_update(request, pk):
    """更新项目状态（AJAX）"""
    project = get_object_or_404(Project, pk=pk)
    new_status = request.POST.get('status')

    if new_status in dict(Project.STATUS_CHOICES):
        project.status = new_status
        project.save()
        return JsonResponse({
            'success': True,
            'message': f'项目状态已更新为"{project.get_status_display()}"'
        })

    return JsonResponse({
        'success': False,
        'message': '无效的状态值'
    })
