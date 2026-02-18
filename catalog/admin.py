from django.contrib import admin
from parler.admin import TranslatableAdmin, TranslatableTabularInline
from django.utils.translation import gettext_lazy as _
from .models import Category, ProductType, CoatType, Product, ProductImage, HomeBanner


@admin.register(Category)
class CategoryAdmin(TranslatableAdmin):
    list_display = ("__str__", "slug", "is_active", "sort_order")
    list_filter  = ("is_active",)
    search_fields = ("translations__name", "slug")
    ordering = ("sort_order", "slug")
    fieldsets = (
        (None, {"fields": ("slug", "icon", "is_active", "sort_order")}),
        (_("Переклади"), {"fields": ("name",)}),
    )

    def get_prepopulated_fields(self, request, obj=None):
        return {"slug": ("name",)}


@admin.register(ProductType)
class ProductTypeAdmin(TranslatableAdmin):
    list_display = ("__str__", "slug", "requires_coat_type", "is_active", "sort_order")
    list_filter  = ("is_active", "requires_coat_type")
    search_fields = ("translations__name", "slug")
    ordering = ("sort_order", "slug")
    fieldsets = (
        (None, {"fields": ("slug", "requires_coat_type", "is_active", "sort_order")}),
        (_("Переклади"), {"fields": ("name",)}),
    )

    def get_prepopulated_fields(self, request, obj=None):
        return {"slug": ("name",)}


@admin.register(CoatType)
class CoatTypeAdmin(TranslatableAdmin):
    list_display = ("__str__", "is_active", "sort_order")
    list_filter  = ("is_active",)
    search_fields = ("translations__name", "id")
    ordering = ("sort_order", "id")
    fieldsets = (
        (None, {"fields": ("is_active", "sort_order")}),
        (_("Переклади"), {"fields": ("name",)}),
    )


class ProductImageInline(TranslatableTabularInline):
    model = ProductImage
    extra = 1
    fields = ("image", "alt", "sort_order", "is_main")
    ordering = ("sort_order",)


@admin.register(Product)
class ProductAdmin(TranslatableAdmin):
    list_display = ("__str__", "article", "category", "product_type", "coat_type", "price", "stock_qty", "is_active")
    list_filter  = ("is_active", "category", "product_type", "coat_type")
    search_fields = ("translations__name", "article", "batch_code")
    readonly_fields = ("created_at", "updated_at")
    inlines = [ProductImageInline]
    fieldsets = (
        (_("Звʼязки"), {"fields": ("category", "product_type", "coat_type")}),
        (_("Основні"), {"fields": ("article", "volume_ml", "price", "cost_price", "stock_qty")}),
        (_("Партія"),  {"fields": ("batch_code", "expiry_date")}),
        (_("Статус"),  {"fields": ("is_active",)}),
        (_("Переклади"), {"fields": ("name", "description")}),
        (_("Службові"), {"fields": ("created_at", "updated_at")}),
    )

@admin.register(HomeBanner)
class HomeBannerAdmin(TranslatableAdmin):
    list_display = ("title", "order", "is_active")
    list_editable = ("order", "is_active")
    search_fields = ("translations__title",)

    fields = ("title", "image", "link", "order", "is_active")