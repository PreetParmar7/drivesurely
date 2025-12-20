from django import template

register = template.Library()

@register.filter
def indian_price(value):
    try:
        value = float(value)

        if value >= 10000000:
            return f"{value/10000000:.1f} Cr"
        elif value >= 100000:
            return f"{value/100000:.1f} Lakh"
        else:
            return f"{int(value):,}"
    except:
        return value
