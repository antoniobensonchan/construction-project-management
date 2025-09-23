from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Project, WorkSite
from .forms import ProjectForm, WorkSiteForm


@login_required
def project_list(request):
    """项目列表页面"""
    projects = Project.objects.filter(owner=request.user).order_by('-created_at')
    return render(request, 'projects/project_list.html', {
        'projects': projects
    })


@login_required
def project_create(request):
    """创建项目"""
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            messages.success(request, f'项目"{project.name}"创建成功！')
            return redirect('projects:project_detail', pk=project.pk)
    else:
        form = ProjectForm()

    return render(request, 'projects/project_create.html', {
        'form': form
    })


@login_required
def project_detail(request, pk):
    """项目详情页面（项目主页）"""
    project = get_object_or_404(Project, pk=pk, owner=request.user)

    # 获取项目的工地
    worksites = project.worksites.all().order_by('-created_at')

    # 获取项目相关数据（通过工地）
    drawings = []
    all_tasks = []
    for worksite in worksites:
        drawings.extend(worksite.drawings.all())
        all_tasks.extend(worksite.tasks.all())

    # 按时间排序
    drawings = sorted(drawings, key=lambda x: x.uploaded_at, reverse=True)
    all_tasks = sorted(all_tasks, key=lambda x: x.created_at, reverse=True)

    # 分离主任务和子任务
    main_tasks = [task for task in all_tasks if task.parent_task is None]
    subtasks = [task for task in all_tasks if task.parent_task is not None]

    # 统计数据
    stats = {
        'total_worksites': worksites.count(),
        'total_drawings': len(drawings),
        'total_tasks': len(all_tasks),
        'main_tasks': len(main_tasks),
        'subtasks': len(subtasks),
        'completed_tasks': len([t for t in all_tasks if t.status == 'completed']),
        'pending_tasks': len([t for t in all_tasks if t.status == 'pending']),
        'in_progress_tasks': len([t for t in all_tasks if t.status == 'in_progress']),
    }

    return render(request, 'projects/project_detail.html', {
        'project': project,
        'worksites': worksites,
        'drawings': drawings,
        'tasks': main_tasks,  # Only main tasks for the tasks tab
        'subtasks': subtasks,  # Separate subtasks for the new tab
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


# ==================== 工地管理视图 ====================

@login_required
def worksite_create(request, project_pk):
    """创建工地"""
    project = get_object_or_404(Project, pk=project_pk, owner=request.user)

    if request.method == 'POST':
        form = WorkSiteForm(request.POST, project=project)
        if form.is_valid():
            worksite = form.save(commit=False)
            worksite.project = project
            worksite.save()
            messages.success(request, f'工地"{worksite.name}"创建成功！')
            return redirect('projects:project_detail', pk=project.pk)
    else:
        form = WorkSiteForm(project=project)

    return render(request, 'projects/worksite_create.html', {
        'form': form,
        'project': project
    })


@login_required
def worksite_detail(request, pk):
    """工地详情页面"""
    worksite = get_object_or_404(WorkSite, pk=pk, project__owner=request.user)

    # 获取工地相关数据
    drawings = worksite.drawings.all().order_by('-uploaded_at')
    tasks = worksite.tasks.all().order_by('-created_at')

    # 统计数据
    stats = {
        'total_drawings': drawings.count(),
        'total_tasks': tasks.count(),
        'completed_tasks': tasks.filter(status='completed').count(),
        'pending_tasks': tasks.filter(status='pending').count(),
        'in_progress_tasks': tasks.filter(status='in_progress').count(),
    }

    return render(request, 'projects/worksite_detail.html', {
        'worksite': worksite,
        'project': worksite.project,
        'drawings': drawings,
        'tasks': tasks,
        'stats': stats
    })


@login_required
def worksite_update(request, pk):
    """更新工地"""
    worksite = get_object_or_404(WorkSite, pk=pk, project__owner=request.user)

    if request.method == 'POST':
        form = WorkSiteForm(request.POST, instance=worksite, project=worksite.project)
        if form.is_valid():
            form.save()
            messages.success(request, f'工地"{worksite.name}"更新成功！')
            return redirect('projects:worksite_detail', pk=worksite.pk)
    else:
        form = WorkSiteForm(instance=worksite, project=worksite.project)

    return render(request, 'projects/worksite_update.html', {
        'form': form,
        'worksite': worksite,
        'project': worksite.project
    })


@login_required
def worksite_delete(request, pk):
    """删除工地"""
    worksite = get_object_or_404(WorkSite, pk=pk, project__owner=request.user)
    project = worksite.project

    if request.method == 'POST':
        worksite_name = worksite.name
        worksite.delete()
        messages.success(request, f'工地"{worksite_name}"已删除')
        return redirect('projects:project_detail', pk=project.pk)

    return render(request, 'projects/worksite_delete_confirm.html', {
        'worksite': worksite,
        'project': project
    })
