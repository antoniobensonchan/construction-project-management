from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from projects.models import Project, WorkSite
from tasks.models import Task, TaskDependency
from datetime import date, timedelta
import json
from collections import defaultdict


@login_required
def project_gantt(request, project_id):
    """项目甘特图页面"""
    project = get_object_or_404(Project, pk=project_id, owner=request.user)

    # 获取项目的所有工地
    worksites = project.worksites.all().order_by('name')

    # 获取项目的所有任务（包括子任务）
    all_tasks = Task.objects.filter(worksite__project=project).select_related(
        'worksite', 'parent_task'
    ).prefetch_related('subtasks', 'dependencies', 'predecessor_dependencies')

    # 计算项目时间范围
    project_start = project.start_date
    project_end = project.end_date

    # 如果有任务，根据任务时间调整项目时间范围
    if all_tasks.exists():
        task_start_dates = [task.start_date for task in all_tasks if task.start_date]
        task_end_dates = [task.end_date for task in all_tasks if task.end_date]

        if task_start_dates:
            earliest_task = min(task_start_dates)
            if earliest_task < project_start:
                project_start = earliest_task

        if task_end_dates:
            latest_task = max(task_end_dates)
            if latest_task > project_end:
                project_end = latest_task

    # 按工地分组任务
    worksite_tasks = defaultdict(list)
    for task in all_tasks:
        worksite_tasks[task.worksite].append(task)

    # 为每个工地的任务排序（主任务在前，子任务在后）
    for worksite in worksite_tasks:
        tasks = worksite_tasks[worksite]
        # 先按是否为主任务排序，再按创建时间排序
        worksite_tasks[worksite] = sorted(tasks, key=lambda t: (
            t.parent_task is not None,  # 主任务在前
            t.parent_task.id if t.parent_task else 0,  # 按父任务分组
            t.created_at
        ))

    context = {
        'project': project,
        'worksites': worksites,
        'worksite_tasks': dict(worksite_tasks),
        'project_start': project_start,
        'project_end': project_end,
        'total_days': (project_end - project_start).days + 1,
        'today': date.today(),
    }

    return render(request, 'gantt/project_gantt.html', context)


@login_required
def gantt_data_api(request, project_id):
    """甘特图数据API"""
    project = get_object_or_404(Project, pk=project_id, owner=request.user)

    # 获取所有任务数据
    tasks = Task.objects.filter(worksite__project=project).select_related(
        'worksite', 'parent_task'
    ).prefetch_related('dependencies', 'predecessor_dependencies')

    # 构建甘特图数据
    gantt_data = {
        'project': {
            'id': project.id,
            'name': project.name,
            'start_date': project.start_date.isoformat(),
            'end_date': project.end_date.isoformat(),
            'status': project.status,
        },
        'worksites': [],
        'tasks': [],
        'dependencies': []
    }

    # 工地数据
    for worksite in project.worksites.all():
        gantt_data['worksites'].append({
            'id': worksite.id,
            'name': worksite.name,
            'start_date': worksite.start_date.isoformat(),
            'end_date': worksite.end_date.isoformat(),
            'status': worksite.status,
        })

    # 任务数据
    for task in tasks:
        task_data = {
            'id': task.id,
            'name': task.name,
            'worksite_id': task.worksite.id,
            'worksite_name': task.worksite.name,
            'parent_task_id': task.parent_task.id if task.parent_task else None,
            'start_date': task.start_date.isoformat(),
            'end_date': task.end_date.isoformat(),
            'deadline': task.deadline.isoformat(),
            'status': task.status,
            'task_type': task.task_type,
            'responsible_person': task.responsible_person,
            'progress': task.get_progress_percentage(),
            'duration_days': task.duration_days,
            'subtasks_count': task.get_subtasks_count(),
            'completed_subtasks': task.get_completed_subtasks_count(),
        }
        gantt_data['tasks'].append(task_data)

    # 依赖关系数据
    dependencies = TaskDependency.objects.filter(
        predecessor__worksite__project=project,
        successor__worksite__project=project
    ).select_related('predecessor', 'successor')

    for dep in dependencies:
        gantt_data['dependencies'].append({
            'id': dep.id,
            'predecessor_id': dep.predecessor.id,
            'successor_id': dep.successor.id,
            'dependency_type': dep.dependency_type,
            'lag_days': dep.lag_days,
        })

    return JsonResponse(gantt_data)


@login_required
def export_gantt_pdf(request, project_id):
    """导出甘特图PDF"""
    project = get_object_or_404(Project, pk=project_id, owner=request.user)

    try:
        # 修复hashlib兼容性问题
        import hashlib
        import sys

        # 保存原始函数
        original_md5 = hashlib.md5
        original_sha1 = hashlib.sha1
        original_sha256 = hashlib.sha256

        # 创建兼容的包装函数
        def patched_md5(*args, **kwargs):
            kwargs.pop('usedforsecurity', None)
            return original_md5(*args, **kwargs)

        def patched_sha1(*args, **kwargs):
            kwargs.pop('usedforsecurity', None)
            return original_sha1(*args, **kwargs)

        def patched_sha256(*args, **kwargs):
            kwargs.pop('usedforsecurity', None)
            return original_sha256(*args, **kwargs)

        # 应用补丁
        hashlib.md5 = patched_md5
        hashlib.sha1 = patched_sha1
        hashlib.sha256 = patched_sha256

        # 导入PDF生成库
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.pdfgen import canvas
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        from io import BytesIO

        # 创建PDF缓冲区
        buffer = BytesIO()

        # 创建PDF文档（横向）
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )

        # 获取样式
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=TA_CENTER
        )

        # 构建PDF内容
        story = []

        # 标题
        title = f"{project.name} - 施工进度表"
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 20))

        # 项目信息表
        project_info = [
            ['项目名称', project.name],
            ['项目状态', project.get_status_display()],
            ['开始日期', project.start_date.strftime('%Y年%m月%d日')],
            ['结束日期', project.end_date.strftime('%Y年%m月%d日')],
            ['报告日期', date.today().strftime('%Y年%m月%d日')],
        ]

        project_table = Table(project_info, colWidths=[2*inch, 4*inch])
        project_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        story.append(project_table)
        story.append(Spacer(1, 30))

        # 任务进度表
        # 表头
        headers = ['工作地点', '任务名称', '任务类型', '负责人', '开始日期', '结束日期', '状态', '进度']

        # 获取任务数据
        tasks_data = [headers]

        for worksite in project.worksites.all().order_by('name'):
            worksite_tasks = Task.objects.filter(worksite=worksite).order_by('parent_task', 'created_at')

            for task in worksite_tasks:
                task_name = task.name
                if task.parent_task:
                    task_name = f"  └ {task_name}"  # 子任务缩进

                progress_text = f"{task.get_progress_percentage()}%"
                if task.get_subtasks_count() > 0:
                    progress_text += f" ({task.get_completed_subtasks_count()}/{task.get_subtasks_count()})"

                row = [
                    worksite.name,
                    task_name,
                    task.get_task_type_display(),
                    task.responsible_person,
                    task.start_date.strftime('%m/%d'),
                    task.end_date.strftime('%m/%d'),
                    task.get_status_display(),
                    progress_text
                ]
                tasks_data.append(row)

        # 创建任务表格
        tasks_table = Table(tasks_data, colWidths=[
            1.2*inch,  # 工作地点
            2.0*inch,  # 任务名称
            0.8*inch,  # 任务类型
            0.8*inch,  # 负责人
            0.6*inch,  # 开始日期
            0.6*inch,  # 结束日期
            0.6*inch,  # 状态
            0.8*inch,  # 进度
        ])

        # 设置表格样式
        table_style = [
            # 表头样式
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

            # 数据行样式
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]

        # 为不同状态的任务设置不同颜色
        for i, row in enumerate(tasks_data[1:], 1):  # 跳过表头
            status = row[6]  # 状态列
            if '已完成' in status:
                table_style.append(('BACKGROUND', (0, i), (-1, i), colors.lightgreen))
            elif '进行中' in status:
                table_style.append(('BACKGROUND', (0, i), (-1, i), colors.lightyellow))
            elif '待处理' in status:
                table_style.append(('BACKGROUND', (0, i), (-1, i), colors.lightblue))

        tasks_table.setStyle(TableStyle(table_style))
        story.append(tasks_table)

        # 页脚信息
        story.append(Spacer(1, 30))
        footer_info = [
            "任务状态说明：",
            "• 开放：任务已创建，等待开始",
            "• 进行中：任务正在执行中",
            "• 待处理：任务等待前置条件完成",
            "• 已完成：任务已完成",
            "",
            f"报告生成时间：{date.today().strftime('%Y年%m月%d日')}",
            f"数据来源：{project.name} 项目管理系统"
        ]

        for info in footer_info:
            story.append(Paragraph(info, styles['Normal']))

        # 生成PDF
        doc.build(story)

        # 准备响应
        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')

        # 设置文件名
        filename = f"{project.name}_施工进度表_{date.today().strftime('%Y%m%d')}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        return response

    except ImportError as e:
        # 如果没有安装reportlab，返回错误信息
        return JsonResponse({
            'error': '请安装reportlab库以支持PDF导出功能',
            'install_command': 'pip install reportlab',
            'details': str(e)
        }, status=500)

    except Exception as e:
        # 详细的错误信息用于调试
        import traceback
        error_details = traceback.format_exc()

        return JsonResponse({
            'error': f'PDF生成失败: {str(e)}',
            'details': error_details,
            'project_id': project_id,
            'project_name': project.name
        }, status=500)


@login_required
def export_gantt_simple_pdf(request, project_id):
    """简单的PDF导出功能（备用方案）"""
    project = get_object_or_404(Project, pk=project_id, owner=request.user)

    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.units import inch
        from io import BytesIO
        import datetime

        # 修复hashlib兼容性问题
        import hashlib
        import sys

        # 保存原始函数
        original_md5 = hashlib.md5
        original_sha1 = hashlib.sha1
        original_sha256 = hashlib.sha256

        # 创建兼容的包装函数
        def patched_md5(*args, **kwargs):
            kwargs.pop('usedforsecurity', None)
            return original_md5(*args, **kwargs)

        def patched_sha1(*args, **kwargs):
            kwargs.pop('usedforsecurity', None)
            return original_sha1(*args, **kwargs)

        def patched_sha256(*args, **kwargs):
            kwargs.pop('usedforsecurity', None)
            return original_sha256(*args, **kwargs)

        # 应用补丁
        hashlib.md5 = patched_md5
        hashlib.sha1 = patched_sha1
        hashlib.sha256 = patched_sha256

        # 创建PDF缓冲区
        buffer = BytesIO()

        # 创建PDF文档（横向）
        p = canvas.Canvas(buffer, pagesize=landscape(A4))
        width, height = landscape(A4)

        # 标题
        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, height - 50, f"Project Gantt Chart: {project.name}")

        # 项目信息
        p.setFont("Helvetica", 12)
        y_position = height - 100
        p.drawString(50, y_position, f"Project: {project.name}")
        y_position -= 20
        p.drawString(50, y_position, f"Description: {project.description or 'No description'}")
        y_position -= 20
        p.drawString(50, y_position, f"Generated: {datetime.date.today().strftime('%Y-%m-%d')}")
        y_position -= 40

        # 任务列表标题
        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, y_position, "Tasks:")
        y_position -= 30

        # 表头
        p.setFont("Helvetica-Bold", 10)
        p.drawString(50, y_position, "Worksite")
        p.drawString(200, y_position, "Task Name")
        p.drawString(400, y_position, "Status")
        p.drawString(500, y_position, "Responsible")
        p.drawString(650, y_position, "Progress")
        y_position -= 20

        # 画线
        p.line(50, y_position, width - 50, y_position)
        y_position -= 10

        # 任务数据
        p.setFont("Helvetica", 9)
        for worksite in project.worksites.all().order_by('name'):
            worksite_tasks = Task.objects.filter(worksite=worksite).order_by('parent_task', 'created_at')

            for task in worksite_tasks:
                if y_position < 50:  # 如果空间不够，创建新页面
                    p.showPage()
                    y_position = height - 50
                    p.setFont("Helvetica", 9)

                task_name = task.name
                if task.parent_task:
                    task_name = f"  └ {task_name}"

                # 限制文本长度
                if len(task_name) > 25:
                    task_name = task_name[:22] + "..."

                p.drawString(50, y_position, worksite.name[:20])
                p.drawString(200, y_position, task_name)
                p.drawString(400, y_position, task.get_status_display())
                p.drawString(500, y_position, (task.responsible_person or 'Unassigned')[:15])
                p.drawString(650, y_position, f"{task.get_progress_percentage()}%")

                y_position -= 15

        # 完成PDF
        p.save()

        # 准备响应
        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')

        # 设置文件名
        filename = f"{project.name}_gantt_{datetime.date.today().strftime('%Y%m%d')}.pdf"
        # 使用ASCII文件名避免编码问题
        safe_filename = "project_gantt_" + datetime.date.today().strftime('%Y%m%d') + ".pdf"
        response['Content-Disposition'] = f'attachment; filename="{safe_filename}"'

        return response

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()

        return JsonResponse({
            'error': f'Simple PDF generation failed: {str(e)}',
            'details': error_details
        }, status=500)


@login_required
def export_gantt_csv(request, project_id):
    """导出甘特图CSV文件（替代PDF的方案）"""
    project = get_object_or_404(Project, pk=project_id, owner=request.user)

    try:
        import csv
        from django.http import HttpResponse
        import datetime

        # 创建HTTP响应
        response = HttpResponse(content_type='text/csv; charset=utf-8')

        # 设置文件名
        filename = f"project_gantt_{datetime.date.today().strftime('%Y%m%d')}.csv"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        # 添加BOM以支持Excel中文显示
        response.write('\ufeff')

        # 创建CSV写入器
        writer = csv.writer(response)

        # 写入标题行
        writer.writerow([
            '项目名称', '工地名称', '任务名称', '任务类型', '状态',
            '负责人', '进度', '开始日期', '截止日期', '创建时间', '描述'
        ])

        # 写入项目信息行
        writer.writerow([
            project.name, '', '', '项目', '', '', '', '', '',
            project.created_at.strftime('%Y-%m-%d'), project.description or ''
        ])

        # 写入任务数据
        for worksite in project.worksites.all().order_by('name'):
            worksite_tasks = Task.objects.filter(worksite=worksite).order_by('parent_task', 'created_at')

            for task in worksite_tasks:
                task_type = '子任务' if task.parent_task else '主任务'
                task_name = task.name
                if task.parent_task:
                    task_name = f"└ {task_name}"

                writer.writerow([
                    project.name,
                    worksite.name,
                    task_name,
                    task_type,
                    task.get_status_display(),
                    task.responsible_person or '未分配',
                    f"{task.get_progress_percentage()}%",
                    task.start_date.strftime('%Y-%m-%d') if task.start_date else '',
                    task.deadline.strftime('%Y-%m-%d') if task.deadline else '',
                    task.created_at.strftime('%Y-%m-%d'),
                    task.description or ''
                ])

        return response

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()

        return JsonResponse({
            'error': f'CSV导出失败: {str(e)}',
            'details': error_details
        }, status=500)
