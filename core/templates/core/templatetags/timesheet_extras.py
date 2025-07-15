from django import template

register = template.Library()

@register.filter
def hours(td):
    """Convert timedelta to float hours with two decimals"""
    if td:
        return round(td.total_seconds() / 3600, 2)
    return 0.0
