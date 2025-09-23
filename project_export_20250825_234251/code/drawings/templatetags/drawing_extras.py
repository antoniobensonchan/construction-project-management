from django import template

register = template.Library()

@register.filter
def range_from(value, start=1):
    """生成从start开始到value的范围"""
    return range(start, value + 1)

@register.filter
def subtract(value, arg):
    """减法运算"""
    return value - arg

@register.filter
def add_one(value):
    """加1"""
    return value + 1
