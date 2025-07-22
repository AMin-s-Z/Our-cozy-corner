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

@register.filter
def add_class(field, css_class):
    """
    Add a CSS class to the form field.
    
    Usage: {{ form.field|add_class:"form-control" }}
    """
    return field.as_widget(attrs={"class": f"{field.field.widget.attrs.get('class', '')} {css_class}".strip()})