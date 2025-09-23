from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Task, TaskAnnotation
from .forms import TaskCreateForm, TaskDrawingSelectForm, ProjectTaskCreateForm
from drawings.models import Drawing
from projects.models import Project


def task_list(request):
    """任务列表页面"""
    tasks = Task.objects.all().select_related('project').prefetch_related('drawings')
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
    return render(request, 'tasks/task_detail.html', {
        'task': task
    })


def task_update(request, pk):
    """任务更新页面"""
    task = get_object_or_404(Task, pk=pk)

    if request.method == 'POST':
        form = TaskCreateForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, '任务更新成功')
            return redirect('tasks:task_detail', pk=task.pk)
    else:
        form = TaskCreateForm(instance=task)

    return render(request, 'tasks/task_update.html', {
        'form': form,
        'task': task
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

            # 获取关联的图纸
            drawing_id = data.get('drawing_id')
            drawing = None
            if drawing_id:
                try:
                    drawing = Drawing.objects.get(pk=drawing_id)
                except Drawing.DoesNotExist:
                    drawing = task.drawings.first() if task.drawings.exists() else None
            else:
                drawing = task.drawings.first() if task.drawings.exists() else None

            if not drawing:
                return JsonResponse({
                    'success': False,
                    'error': '无法找到关联的图纸'
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
    """项目内任务创建"""
    project = get_object_or_404(Project, pk=project_id)

    if request.method == 'POST':
        form = ProjectTaskCreateForm(request.POST, project=project)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.save()
            form.save_m2m()  # 保存多对多关系
            messages.success(request, f'任务 "{task.name}" 创建成功！')
            return redirect('projects:project_detail', pk=project.pk)
    else:
        form = ProjectTaskCreateForm(project=project)

    return render(request, 'tasks/project_task_create.html', {
        'form': form,
        'project': project
    })
