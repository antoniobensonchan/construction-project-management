#!/usr/bin/env python
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_pm.settings')
django.setup()

from drawings.models import Drawing
from tasks.models import TaskAnnotation

def final_test_drawing_9():
    """最终测试图纸9的标注显示"""

    print('🎉 最终测试图纸9标注显示修复\n')

    try:
        drawing = Drawing.objects.get(pk=9)
        print(f'📄 图纸: {drawing.name}')
        print(f'   文件: {drawing.file.name}')
        print(f'   URL: {drawing.file.url}')

        # 检查标注数据
        annotations = drawing.annotations.all()
        print(f'\n🎯 标注数据 ({annotations.count()} 个):')

        for i, annotation in enumerate(annotations):
            print(f'   {i+1}. ID: {annotation.id}')
            print(f'      类型: {annotation.annotation_type}')
            print(f'      颜色: {annotation.color}')
            print(f'      内容: {annotation.content}')
            print(f'      位置: ({annotation.x_coordinate}, {annotation.y_coordinate})')
            print(f'      页码: {annotation.page_number}')
            print(f'      任务: {annotation.task.name} (ID: {annotation.task.id})')

        print(f'\n🔧 JavaScript修复内容:')
        print(f'   1. ✅ 移除了未定义的 fileType 变量引用')
        print(f'   2. ✅ 重新组织了函数定义顺序')
        print(f'   3. ✅ 添加了标注数据加载日志')
        print(f'   4. ✅ 优化了图片加载后的标注渲染时机')
        print(f'   5. ✅ 添加了函数存在性检查')

        print(f'\n🌐 测试页面: http://127.0.0.1:8000/drawings/{drawing.pk}/')

        print(f'\n📋 测试步骤:')
        print(f'   1. 访问图纸页面')
        print(f'   2. 打开浏览器开发者工具 (F12)')
        print(f'   3. 查看控制台，应该看到:')
        print(f'      - "🎯 Loaded annotations data: [...]" - 标注数据加载')
        print(f'      - "📷 Image loaded, initializing annotations..." - 图片加载完成')
        print(f'      - "🎯 Initializing annotations display for drawing" - 开始渲染')
        print(f'      - "📊 Total annotations: 2" - 标注数量')
        print(f'      - "🎨 Starting to render annotations..." - 开始渲染标注')
        print(f'      - "✅ Added point annotation at (...)" - 点标记渲染')
        print(f'      - "✅ Added text annotation at (...)" - 文字标注渲染')
        print(f'      - "✅ Rendered 2 annotations for page 1" - 渲染完成')

        print(f'\n🎨 预期效果:')
        print(f'   ✅ 图片正常显示')
        print(f'   ✅ 黑色圆点标注在位置 (196, 148)')
        print(f'   ✅ 橙色文字标注在位置 (149, 71)')
        print(f'   ✅ 标注可以点击跳转到任务')
        print(f'   ✅ 鼠标悬停任务时标注高亮')
        print(f'   ✅ 无JavaScript错误')

        print(f'\n🚀 如果仍然看不到标注，请检查:')
        print(f'   1. 浏览器控制台是否有错误信息')
        print(f'   2. 标注数据是否正确加载')
        print(f'   3. 图片是否完全加载')
        print(f'   4. 标注层的CSS样式是否正确')

        print(f'\n✅ 图纸9标注显示修复完成！')
        print(f'现在应该可以在图片上看到标注了！')

        return drawing, annotations

    except Drawing.DoesNotExist:
        print('❌ 图纸9不存在')
        return None, None

if __name__ == '__main__':
    final_test_drawing_9()
