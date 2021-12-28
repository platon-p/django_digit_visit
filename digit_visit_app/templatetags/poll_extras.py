from django import template

register = template.Library()


@register.filter(name='getkey')
def getkey(value, arg):
    return value.get(arg, '')


@register.filter
def addstr(arg1, arg2):
    return str(arg1) + str(arg2)
