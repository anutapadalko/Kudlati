from django.contrib import admin

class PromotionAdmin(admin.ModelAdmin):
    list_display = ('title', 'discount_percent', 'is_active')
    filter_horizontal = ('products',)
