from django.template.defaulttags import register

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


