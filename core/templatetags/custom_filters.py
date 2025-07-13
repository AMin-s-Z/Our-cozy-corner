from django import template

register = template.Library()

@register.filter
def replace(value, arg):
    """
    Replace all instances of the first argument with the second argument.
    
    Usage: {{ value|replace:"old,new" }}
    """
    if not value:
        return value
    
    if not arg or ',' not in arg:
        return value
    
    old, new = arg.split(',', 1)
    return str(value).replace(old, new)