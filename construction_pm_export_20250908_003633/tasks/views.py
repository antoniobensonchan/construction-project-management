from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import date, timedelta
from .models import Task, TaskAnnotation, TaskDependency
from .forms import TaskCreateForm, TaskDrawingSelectForm, ProjectTaskCreateForm, SubtaskCreateForm, SubtaskUpdateForm, TaskDependencyForm
from drawings.models import Drawing
from projects.models import Project, WorkSite


def task_list(request):
    """任务列表页面"""
    # 只显示当前用户拥有的项目下的任务
    if request.user.is_authenticated:
        tasks = Task.objects.filter(
            worksite__project__owner=request.user
        ).select_related('worksite', 'worksite__project').order_by('-created_at')
    else:
        tasks = Task.objects.none()

    return render(request, 'tasks/task_list.html', {
        'tasks': tasks
    })


def task_create(request):
    """任务创建 - 步骤1：填写任务信息"""
    if request.method == 'POST':
        form = TaskCreateForm(request.POST)
        if form.is_valid():
            # 将表单数据保存到session中
            request.session['task_data'] = {
                'name': form.cleaned_data['name'],
                'task_type': form.cleaned_data['task_type'],
                'responsible_person': form.cleaned_data['responsible_person'],
                'deadline': form.cleaned_data['deadline'].strftime('%Y-%m-%d'),
            }

            # 检查是否有预选图纸
            preselected_drawing_id = request.GET.get('drawing_id')
            if preselected_drawing_id:
                request.session['preselected_drawing_id'] = preselected_drawing_id

            return redirect('tasks:task_create_step2')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        form = TaskCreateForm()

    return render(request, 'tasks/task_create.html', {
        'form': form,
        'step': 1
    })


def task_create_step2(request):
    """任务创建 - 步骤2：选择关联图纸"""
    # 检查是否有步骤1的数据
    task_data = request.session.get('task_data')
    if not task_data:
        messages.error(request, '请先完成任务信息填写')
        return redirect('tasks:task_create')

    # 检查是否有可用图纸
    if not Drawing.objects.exists():
        messages.error(request, '暂无可用图纸，请先上传PDF图纸')
        return redirect('drawings:drawing_upload')

    if request.method == 'POST':
        preselected_drawing_id = request.session.get('preselected_drawing_id')
        form = TaskDrawingSelectForm(request.POST, preselected_drawing_id=preselected_drawing_id)

        if form.is_valid():
            # 创建任务
            task = Task.objects.create(
                name=task_data['name'],
                task_type=task_data['task_type'],
                responsible_person=task_data['responsible_person'],
                deadline=task_data['deadline'],
                drawing=form.cleaned_data['drawing']
            )

            # 保存标注数据
            annotations_data = request.session.get('annotations_data', [])
            for annotation_data in annotations_data:
                TaskAnnotation.objects.create(
                    task=task,
                    annotation_type=annotation_data['type'],
                    page_number=annotation_data['page'],
                    x_coordinate=annotation_data['x'],
                    y_coordinate=annotation_data['y'],
                    width=annotation_data.get('width'),
                    height=annotation_data.get('height'),
                    content=annotation_data.get('note', '') or annotation_data.get('text', '')
                )

            # 清除session数据
            request.session.pop('task_data', None)
            request.session.pop('preselected_drawing_id', None)
            request.session.pop('annotations_data', None)

            annotation_count = len(annotations_data)
            if annotation_count > 0:
                messages.success(request, f'任务创建成功，已关联图纸：{task.drawing.name}，保存了{annotation_count}个标注')
            else:
                messages.success(request, f'任务创建成功，已关联图纸：{task.drawing.name}')
            return redirect('tasks:task_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        preselected_drawing_id = request.session.get('preselected_drawing_id')
        form = TaskDrawingSelectForm(preselected_drawing_id=preselected_drawing_id)

    return render(request, 'tasks/task_create_step2.html', {
        'form': form,
        'task_data': task_data,
        'step': 2
    })


def task_detail(request, pk):
    """任务详情页面"""
    task = get_object_or_404(Task, pk=pk)

    # 检查是否为子任务
    if task.parent_task:
        # 子任务使用简化的模板，不显示图纸预览
        return render(request, 'tasks/subtask_detail.html', {
            'task': task,
            'parent_task': task.parent_task,
            'worksite': task.worksite
        })
    else:
        # 主任务使用完整的模板，包含图纸预览和子任务管理
        worksite_drawings = []
        if task.worksite:
            worksite_drawings = task.worksite.drawings.all()

        return render(request, 'tasks/task_detail.html', {
            'task': task,
            'worksite_drawings': worksite_drawings,
            'worksite': task.worksite
        })


def task_update(request, pk):
    """任务更新页面"""
    task = get_object_or_404(Task, pk=pk)

    # 获取任务所属工地的图纸
    worksite_drawings = []
    if task.worksite:
        worksite_drawings = task.worksite.drawings.all()

    if request.method == 'POST':
        # 处理日期字段
        from datetime import datetime

        # 获取表单数据
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')
        deadline_str = request.POST.get('deadline')

        # 转换日期
        if start_date_str:
            task.start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        if end_date_str:
            task.end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        if deadline_str:
            task.deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date()

        # 更新其他字段
        task.name = request.POST.get('name', task.name)
        task.task_type = request.POST.get('task_type', task.task_type)
        task.responsible_person = request.POST.get('responsible_person', task.responsible_person)
        task.status = request.POST.get('status', task.status)

        try:
            task.save()
            messages.success(request, '任务更新成功')
            return redirect('tasks:task_detail', pk=task.pk)
        except Exception as e:
            messages.error(request, f'任务更新失败: {str(e)}')

    # 创建表单用于显示（不用于处理数据）
    form = TaskCreateForm(instance=task, worksite=task.worksite)

    return render(request, 'tasks/task_update.html', {
        'form': form,
        'task': task,
        'worksite_drawings': worksite_drawings,
        'worksite': task.worksite
    })


def task_delete(request, pk):
    """任务删除"""
    task = get_object_or_404(Task, pk=pk)

    if request.method == 'POST':
        task_name = task.name
        task.delete()
        messages.success(request, f'任务"{task_name}"已删除')
        return redirect('tasks:task_list')

    return render(request, 'tasks/task_delete_confirm.html', {
        'task': task
    })


@csrf_exempt
def save_annotations(request):
    """保存标注数据到session"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            annotations = data.get('annotations', [])

            # 验证标注数据
            validated_annotations = []
            for annotation in annotations:
                if len(validated_annotations) >= 10:  # 最多10个标注
                    break

                # 验证必要字段
                if all(key in annotation for key in ['type', 'x', 'y', 'page']):
                    validated_annotation = {
                        'type': annotation['type'],
                        'x': float(annotation['x']),
                        'y': float(annotation['y']),
                        'page': int(annotation['page'])
                    }

                    # 添加可选字段
                    if 'width' in annotation:
                        validated_annotation['width'] = float(annotation['width'])
                    if 'height' in annotation:
                        validated_annotation['height'] = float(annotation['height'])
                    if 'note' in annotation:
                        validated_annotation['note'] = str(annotation['note'])[:200]
                    if 'text' in annotation:
                        validated_annotation['text'] = str(annotation['text'])[:200]

                    validated_annotations.append(validated_annotation)

            # 保存到session
            request.session['annotations_data'] = validated_annotations

            return JsonResponse({
                'success': True,
                'message': f'已保存{len(validated_annotations)}个标注',
                'count': len(validated_annotations)
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

    return JsonResponse({'success': False, 'error': '仅支持POST请求'})


@csrf_exempt
def update_annotation(request, annotation_id):
    """更新标注"""
    if request.method == 'POST':
        try:
            annotation = get_object_or_404(TaskAnnotation, id=annotation_id)
            data = json.loads(request.body)

            # 更新标注属性
            if 'content' in data:
                annotation.content = data['content'][:200]
            if 'color' in data:
                annotation.color = data['color']
            if 'x_coordinate' in data:
                annotation.x_coordinate = float(data['x_coordinate'])
            if 'y_coordinate' in data:
                annotation.y_coordinate = float(data['y_coordinate'])
            if 'end_x' in data:
                annotation.end_x = float(data['end_x'])
            if 'end_y' in data:
                annotation.end_y = float(data['end_y'])

            annotation.save()

            return JsonResponse({
                'success': True,
                'message': '标注更新成功'
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

    return JsonResponse({'success': False, 'error': '仅支持POST请求'})


@csrf_exempt
def delete_annotation(request, annotation_id):
    """删除标注"""
    if request.method == 'POST':
        try:
            annotation = get_object_or_404(TaskAnnotation, id=annotation_id)
            annotation.delete()

            return JsonResponse({
                'success': True,
                'message': '标注删除成功'
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

    return JsonResponse({'success': False, 'error': '仅支持POST请求'})


@csrf_exempt
def create_annotation(request):
    """创建新标注"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # 获取任务
            task_id = data.get('task_id')
            task = get_object_or_404(Task, id=task_id)

            # 获取关联的图纸（从任务所属工地获取）
            drawing_id = data.get('drawing_id')
            drawing = None

            # 获取任务所属工地的图纸
            worksite_drawings = []
            if task.worksite:
                worksite_drawings = task.worksite.drawings.all()

            if drawing_id:
                try:
                    # 确保图纸属于任务的工地
                    drawing = worksite_drawings.filter(pk=drawing_id).first()
                    if not drawing:
                        drawing = Drawing.objects.get(pk=drawing_id)
                        # 验证图纸是否属于任务的工地
                        if drawing.worksite != task.worksite:
                            return JsonResponse({
                                'success': False,
                                'error': '图纸不属于任务所在的工地'
                            })
                except Drawing.DoesNotExist:
                    drawing = worksite_drawings.first() if worksite_drawings else None
            else:
                drawing = worksite_drawings.first() if worksite_drawings else None

            if not drawing:
                return JsonResponse({
                    'success': False,
                    'error': '无法找到工地图纸，请先为工地上传图纸'
                })

            # 创建标注
            annotation = TaskAnnotation.objects.create(
                task=task,
                drawing=drawing,
                annotation_type=data.get('annotation_type'),
                x_coordinate=float(data.get('x_coordinate')),
                y_coordinate=float(data.get('y_coordinate')),
                end_x=float(data.get('end_x')) if data.get('end_x') else None,
                end_y=float(data.get('end_y')) if data.get('end_y') else None,
                color=data.get('color', 'red'),
                content=data.get('content', ''),
                page_number=int(data.get('page_number', 1))
            )

            return JsonResponse({
                'success': True,
                'message': '标注创建成功',
                'annotation_id': annotation.id
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

    return JsonResponse({'success': False, 'error': '仅支持POST请求'})


def project_task_create(request, project_id):
    """项目内任务创建（重定向到项目详情）"""
    project = get_object_or_404(Project, pk=project_id, owner=request.user)

    messages.info(request, '任务应该在具体工地中创建。请选择一个工地，然后在工地中创建任务。')
    return redirect('projects:project_detail', pk=project.pk)


def worksite_task_create(request, worksite_id):
    """工地任务创建"""
    worksite = get_object_or_404(WorkSite, pk=worksite_id, project__owner=request.user)

    if request.method == 'POST':
        form = ProjectTaskCreateForm(request.POST, project=worksite.project)
        if form.is_valid():
            task = form.save(commit=False)
            task.worksite = worksite
            task.save()
            form.save_m2m()  # 保存多对多关系
            messages.success(request, f'任务 "{task.name}" 创建成功！')
            return redirect('projects:worksite_detail', pk=worksite.pk)
    else:
        form = ProjectTaskCreateForm(project=worksite.project)

    return render(request, 'tasks/worksite_task_create.html', {
        'form': form,
        'worksite': worksite,
        'project': worksite.project
    })


@csrf_exempt
def subtask_create(request, parent_task_id):
    """创建子任务"""
    parent_task = get_object_or_404(Task, pk=parent_task_id)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # 处理日期字段
            from datetime import datetime

            start_date_str = data.get('start_date')
            if start_date_str:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            else:
                start_date = parent_task.start_date or date.today()

            end_date_str = data.get('end_date')
            if end_date_str:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            else:
                end_date = parent_task.end_date or (date.today() + timedelta(days=3))

            deadline_str = data.get('deadline')
            if deadline_str:
                deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date()
            else:
                deadline = parent_task.deadline or end_date

            # 创建子任务
            subtask = Task.objects.create(
                parent_task=parent_task,
                worksite=parent_task.worksite,
                name=data.get('name', ''),
                description=data.get('description', ''),
                task_type=data.get('task_type', parent_task.task_type),
                responsible_person=data.get('responsible_person', ''),
                start_date=start_date,
                end_date=end_date,
                deadline=deadline,
                status=data.get('status', 'open')
            )

            return JsonResponse({
                'success': True,
                'message': '子任务创建成功',
                'subtask': {
                    'id': subtask.id,
                    'name': subtask.name,
                    'description': subtask.description,
                    'task_type': subtask.get_task_type_display(),
                    'responsible_person': subtask.responsible_person,
                    'deadline': subtask.deadline.strftime('%Y-%m-%d') if subtask.deadline else '',
                    'status': subtask.get_status_display(),
                    'status_value': subtask.status
                }
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

    return JsonResponse({'success': False, 'error': '无效的请求方法'})


@csrf_exempt
def subtask_update_status(request, subtask_id):
    """更新子任务状态"""
    subtask = get_object_or_404(Task, pk=subtask_id)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_status = data.get('status')

            if new_status in ['open', 'in_progress', 'pending', 'completed']:
                subtask.status = new_status
                subtask.save()

                # 更新父任务进度
                subtask.update_parent_progress()

                return JsonResponse({
                    'success': True,
                    'message': '子任务状态更新成功',
                    'new_status': subtask.get_status_display(),
                    'progress': subtask.parent_task.get_progress_percentage() if subtask.parent_task else 0
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': '无效的状态值'
                })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

    return JsonResponse({'success': False, 'error': '无效的请求方法'})


@csrf_exempt
def subtask_delete(request, subtask_id):
    """删除子任务"""
    subtask = get_object_or_404(Task, pk=subtask_id)

    if request.method == 'POST':
        try:
            parent_task = subtask.parent_task
            subtask_name = subtask.name
            subtask.delete()

            return JsonResponse({
                'success': True,
                'message': f'子任务"{subtask_name}"已删除',
                'progress': parent_task.get_progress_percentage() if parent_task else 0
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

    return JsonResponse({'success': False, 'error': '无效的请求方法'})


@csrf_exempt
def task_add_dependency(request, task_id):
    """添加任务依赖"""
    task = get_object_or_404(Task, pk=task_id)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            predecessor_id = data.get('predecessor_id')
            dependency_type = data.get('dependency_type', 'finish_to_start')
            lag_days = int(data.get('lag_days', 0))

            predecessor = get_object_or_404(Task, pk=predecessor_id)

            # 检查循环依赖
            if task.has_circular_dependency(predecessor):
                return JsonResponse({
                    'success': False,
                    'error': f'与任务"{predecessor.name}"存在循环依赖关系'
                })

            # 创建依赖关系
            dependency, created = TaskDependency.objects.get_or_create(
                predecessor=predecessor,
                successor=task,
                defaults={
                    'dependency_type': dependency_type,
                    'lag_days': lag_days
                }
            )

            if not created:
                return JsonResponse({
                    'success': False,
                    'error': '依赖关系已存在'
                })

            return JsonResponse({
                'success': True,
                'message': f'成功添加依赖任务"{predecessor.name}"',
                'dependency': {
                    'id': dependency.id,
                    'predecessor_name': predecessor.name,
                    'dependency_type': dependency.get_dependency_type_display(),
                    'lag_days': dependency.lag_days
                }
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

    return JsonResponse({'success': False, 'error': '无效的请求方法'})


@csrf_exempt
def task_remove_dependency(request, dependency_id):
    """移除任务依赖"""
    dependency = get_object_or_404(TaskDependency, pk=dependency_id)

    if request.method == 'POST':
        try:
            predecessor_name = dependency.predecessor.name
            dependency.delete()

            return JsonResponse({
                'success': True,
                'message': f'已移除依赖任务"{predecessor_name}"'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

    return JsonResponse({'success': False, 'error': '无效的请求方法'})


def task_dependency_status(request, task_id):
    """获取任务依赖状态"""
    task = get_object_or_404(Task, pk=task_id)

    dependencies = []
    for dep in task.predecessor_dependencies.all():
        dependencies.append({
            'id': dep.id,
            'predecessor_name': dep.predecessor.name,
            'predecessor_status': dep.predecessor.get_status_display(),
            'predecessor_completed': dep.predecessor.status == 'completed',
            'dependency_type': dep.get_dependency_type_display(),
            'lag_days': dep.lag_days
        })

    blocking_deps = task.get_blocking_dependencies()

    return JsonResponse({
        'can_start': task.can_start(),
        'dependencies': dependencies,
        'blocking_count': blocking_deps.count(),
        'blocking_tasks': [{'name': dep.name, 'status': dep.get_status_display()} for dep in blocking_deps]
    })
