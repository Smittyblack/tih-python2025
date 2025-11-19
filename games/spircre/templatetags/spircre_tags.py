from django import template
from ..views import xp_for_next_level, calculate_level

register = template.Library()

@register.filter
def get_field(obj, field):
    return field.split('_')[0]

@register.filter
def get_progress(progress, skill, level):
    xp_field = f"{skill}_xp"
    current_xp = getattr(progress, xp_field)
    xp_needed = xp_for_next_level(level)
    previous_xp = sum(100 * (2 ** (i - 1)) for i in range(1, level)) if level > 1 else 0
    progress_percent = ((current_xp - previous_xp) / xp_needed) * 100
    return min(progress_percent, 100)

@register.filter
def lookup(obj, key):
    return getattr(obj, f"{key}_xp")

@register.filter
def get_field(obj, field):
    return field.split('_')[0]

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, 0)