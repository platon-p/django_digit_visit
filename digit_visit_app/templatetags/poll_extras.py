from django import template

register = template.Library()


@register.filter(name='getkey')
def getkey(value, arg):
    return value[arg] if arg in value.keys() else ''
