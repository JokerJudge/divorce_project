from django.template.defaulttags import register
from django import template

@register.filter
def get_item(object, key):
    if isinstance(object, dict):
        return object.get(key)
    elif isinstance(object, list):
        return object[key]

@register.filter
def get_from_object(obj, atribute):
    output = exec(f'{obj}.{atribute}')
    return output

@register.filter
def to_range(object):
    return range(object)

@register.filter
def plus_one(object):
    sum = object + 1
    return sum

class CounterNode(template.Node):
    def __init__(self, varname):
        self.varname = varname

    def render(self, context):
        if self.varname in context:
            context[self.varname] += 1
        else:
            context[self.varname] = 1
        return ''


@register.tag
def counter(parser, token):
    try:
        tag_name, args = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError(
            "'counter' node requires a variable name.")
    return CounterNode(args)

