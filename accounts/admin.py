from django.contrib import admin
from .models import UserProfile

class PromotionAdmin(admin.ModelAdmin):
    list_display = ('title', 'discount_percent', 'is_active')
    filter_horizontal = ('products',)


admin.site.register(UserProfile)
