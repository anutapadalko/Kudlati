from django.contrib import admin
from .models import Order, OrderToProduct

# Цей клас дозволяє бачити товари прямо на сторінці замовлення


class OrderItemInline(admin.TabularInline):
    model = OrderToProduct
    # Щоб не вантажити випадаючий список, якщо товарів багато
    raw_id_fields = ['product']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Які колонки показувати у списку всіх замовлень
    list_display = ['id', 'user', 'first_name', 'last_name',
                    'phone', 'status', 'is_paid', 'created_at']

    # Фільтри збоку (дуже зручно)
    list_filter = ['status', 'is_paid', 'created_at']

    # Головна магія: підключаємо товари всередину
    inlines = [OrderItemInline]
