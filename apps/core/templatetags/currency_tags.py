import decimal
from decimal import Decimal
from django import template

register = template.Library()

@register.filter(name='clean_amount')
def clean_amount(value):
    """
    Formats a decimal or float without unnecessary trailing zeros.
    45000.00 -> 45,000
    1000.00 -> 1,000
    229.17 -> 229.17
    0.00 -> 0
    1500.50 -> 1,500.5
    """
    if value is None or value == '':
        return '0'
    try:
        val = Decimal(str(value))
        # If integer with zero fraction
        if val == val.to_integral():
            return f"{int(val):,}"
        # Format to max 2 decimal places and strip trailing zeros
        formatted = f"{val:,.2f}".rstrip('0').rstrip('.')
        return formatted
    except (ValueError, decimal.InvalidOperation, TypeError):
        return str(value)

@register.filter(name='clean_bdt')
def clean_bdt(value):
    """
    Formats clean amount with BDT suffix.
    """
    return f"{clean_amount(value)} BDT"
