from django import template
from django.utils.translation import get_language
from catalog.models import ShopAddress

register = template.Library()

@register.simple_tag
def get_shop_addresses():
    lang = get_language()
    return (
        ShopAddress.objects.filter(is_active=True)
        .active_translations(lang)
        .order_by("order", "id")
    )
