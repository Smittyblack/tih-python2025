from django import template

register = template.Library()

@register.filter
def split(value, arg):
    """
    Split a string by a delimiter and return a specific part.
    Usage: {{ value|split:"delimiter:index" }}
    Example: {{ "v=abc123"|split:"v=:1" }} returns "abc123"
    """
    if not value:
        return ''
    try:
        delimiter, index = arg.split(':')
        parts = value.split(delimiter)
        return parts[int(index)] if len(parts) > int(index) else ''
    except (ValueError, IndexError):
        return ''