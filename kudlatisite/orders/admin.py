from django.contrib import admin
from .models import Order, OrderToProduct


class OrderItemInline(admin.TabularInline):
    model = OrderToProduct
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'is_paid',
                    'created_at', 'lmd']  # Бачимо LMD в списку
    list_filter = ['status', 'is_paid', 'created_at']
    # Дозволяє бачити товари прямо всередині замовлення
    inlines = [OrderItemInline]
