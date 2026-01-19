# inventory/templatetags/currency.py
from django import template

register = template.Library()


@register.filter
def cents_to_dollars(value):
    try:
        cents = int(value)
    except (TypeError, ValueError):
        return "$0.00"
    return f"${cents / 100:.2f}"
