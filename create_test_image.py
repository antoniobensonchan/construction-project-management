#!/usr/bin/env python
"""
创建测试图片文件
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_test_drawing():
    """创建一个测试建筑图纸"""
    # 创建一个800x600的白色背景图片
    width, height = 800, 600
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)

    # 绘制标题
    try:
        # 尝试使用系统字体
        font_title = ImageFont.truetype("arial.ttf", 24)
        font_text = ImageFont.truetype("arial.ttf", 16)
    except:
        # 如果没有找到字体，使用默认字体
        font_title = ImageFont.load_default()
        font_text = ImageFont.load_default()

    # 绘制标题
    draw.text((50, 30), "建筑施工图纸 - 测试图", fill='black', font=font_title)

    # 绘制建筑平面图
    # 外墙
    draw.rectangle([100, 100, 700, 500], outline='black', width=3)

    # 内墙
    draw.line([100, 250, 700, 250], fill='black', width=2)  # 水平分隔
    draw.line([400, 100, 400, 500], fill='black', width=2)  # 垂直分隔

    # 门
    draw.arc([380, 240, 420, 260], 0, 90, fill='blue', width=2)
    draw.text((350, 270), "门", fill='blue', font=font_text)

    # 窗户
    draw.rectangle([150, 95, 200, 105], outline='blue', width=2)
    draw.text((150, 110), "窗", fill='blue', font=font_text)

    draw.rectangle([550, 95, 600, 105], outline='blue', width=2)
    draw.text((550, 110), "窗", fill='blue', font=font_text)

    # 标注一些关键位置
    # 预埋件位置
    draw.ellipse([180, 180, 190, 190], outline='red', width=2)
    draw.text((195, 180), "预埋件位置", fill='red', font=font_text)

    # 浇筑区域
    draw.rectangle([450, 150, 550, 200], outline='green', width=2)
    draw.text((450, 205), "混凝土浇筑区域", fill='green', font=font_text)

    # 钢筋位置
    draw.line([120, 350, 180, 350], fill='orange', width=3)
    draw.line([120, 370, 180, 370], fill='orange', width=3)
    draw.line([120, 390, 180, 390], fill='orange', width=3)
    draw.text((190, 365), "钢筋布置", fill='orange', font=font_text)

    # 尺寸标注
    draw.text((350, 520), "总长: 6000mm", fill='black', font=font_text)
    draw.text((720, 300), "总高: 4000mm", fill='black', font=font_text)

    # 图例
    draw.text((50, 520), "图例:", fill='black', font=font_text)
    draw.text((50, 540), "红色: 预埋件  绿色: 浇筑区  橙色: 钢筋  蓝色: 门窗", fill='black', font=font_text)

    return image

if __name__ == '__main__':
    # 创建测试图片
    test_image = create_test_drawing()

    # 保存为不同格式
    formats = [
        ('test_drawing.jpg', 'JPEG'),
        ('test_drawing.png', 'PNG'),
        ('test_drawing.bmp', 'BMP')
    ]

    for filename, format_name in formats:
        test_image.save(filename, format_name)
        print(f"已创建测试图片: {filename}")

    print("\n测试图片创建完成！")
    print("您现在可以使用这些图片测试系统的图片上传和标注功能。")
