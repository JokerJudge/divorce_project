from django.template.defaulttags import register

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def get_from_object(obj, atribute):
    output = exec(f'{obj}.{atribute}')
    return output