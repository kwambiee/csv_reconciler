from django import template
import numbers


register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, '')

@register.filter
def is_numeric(value):
    return isinstance(value, numbers.Number)

@register.filter
def is_dict(value):
    return isinstance(value, dict)

@register.filter
def is_list(value):
    return isinstance(value, list)