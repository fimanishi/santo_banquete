from django import template
import locale

register = template.Library()


@register.filter(name="display_decimals")
def display_decimals(value):
    locale.setlocale(locale.LC_MONETARY, "pt_BR.UTF-8")
    return locale.currency(value, symbol=False)
