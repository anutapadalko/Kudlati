from django.contrib import admin, messages
from django.contrib.admin.helpers import ActionForm
from django.utils.translation import gettext as _
from django import forms

from parler.admin import TranslatableAdmin, TranslatableTabularInline
from parler.forms import TranslatableModelForm

from .models import (
    Category, ProductType, CoatType,
    Product, ProductImage,
    HomeBanner, Promotion
)


@admin.register(Category)
class CategoryAdmin(TranslatableAdmin):
    list_display = ("__str__", "slug", "is_active", "sort_order")
    list_filter = ("is_active",)
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
    list_filter = ("is_active", "requires_coat_type")
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
    list_filter = ("is_active",)
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


# ✅ Форма для dropdown в actions (саме адмінський ActionForm, НЕ forms.ActionForm)
class PromotionActionForm(ActionForm):
    promotion = forms.ModelChoiceField(
        queryset=Promotion.objects.none(),
        required=False,
        label=_("Promotion"),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["promotion"].queryset = Promotion.objects.all().order_by("-priority", "-id")


@admin.register(Product)
class ProductAdmin(TranslatableAdmin):
    list_display = ("__str__", "article", "category", "product_type", "coat_type", "price", "stock_qty", "is_active")
    list_filter = ("is_active", "category", "product_type", "coat_type")
    search_fields = ("translations__name", "article", "batch_code")
    readonly_fields = ("created_at", "updated_at")
    inlines = [ProductImageInline]

    fieldsets = (
        (_("Звʼязки"), {"fields": ("category", "product_type", "coat_type")}),
        (_("Основні"), {"fields": ("article", "volume_ml", "price", "cost_price", "stock_qty")}),
        (_("Партія"), {"fields": ("batch_code", "expiry_date")}),
        (_("Статус"), {"fields": ("is_active",)}),
        (_("Переклади"), {"fields": ("name", "description")}),
        (_("Службові"), {"fields": ("created_at", "updated_at")}),
    )

    action_form = PromotionActionForm
    actions = ["add_selected_to_promotion", "remove_selected_from_promotion"]

    @admin.action(description=_("Add selected products to Promotion (choose in dropdown)"))
    def add_selected_to_promotion(self, request, queryset):
        promo_id = request.POST.get("promotion")
        if not promo_id:
            self.message_user(request, _("Select a Promotion in the dropdown first."), level=messages.ERROR)
            return

        promotion = Promotion.objects.get(pk=promo_id)

        # ✅ Безпечно для великих списків (bulk через through)
        through = Promotion.products.through
        product_ids = list(queryset.values_list("id", flat=True))
        through.objects.bulk_create(
            [through(promotion_id=promotion.id, product_id=pid) for pid in product_ids],
            ignore_conflicts=True,
        )

        self.message_user(
            request,
            _("Added %(count)s products to promotion '%(promo)s'.") % {"count": len(product_ids), "promo": str(promotion)},
            level=messages.SUCCESS,
        )

    @admin.action(description=_("Remove selected products from Promotion (choose in dropdown)"))
    def remove_selected_from_promotion(self, request, queryset):
        promo_id = request.POST.get("promotion")
        if not promo_id:
            self.message_user(request,
                              _("Select a Promotion in the dropdown first."), level=messages.ERROR)
            return

        promotion = Promotion.objects.get(pk=promo_id)

        through = Promotion.products.through
        product_ids = list(queryset.values_list("id", flat=True))
        deleted, _ = through.objects.filter(promotion_id=promotion.id, product_id__in=product_ids).delete()

        self.message_user(
            request,
            _("Removed %(count)s products from promotion '%(promo)s'.") % {"count": len(product_ids), "promo": str(promotion)},
            level=messages.SUCCESS,
        )


@admin.register(HomeBanner)
class HomeBannerAdmin(TranslatableAdmin):
    list_display = ("title", "order", "is_active")
    list_editable = ("order", "is_active")
    search_fields = ("translations__title",)
    fields = ("title", "image", "link", "order", "is_active")


# ✅ Окремий ModelAdmin для Promotion (а не форма!)
@admin.register(Promotion)
class PromotionAdmin(TranslatableAdmin):
    list_display = ("__str__", "discount_percent", "priority", "is_active", "starts_at", "ends_at")
    list_filter = ("is_active",)
    search_fields = ("translations__title", "slug")
    ordering = ("-priority", "-id")
    filter_horizontal = ("products",)

    fieldsets = (
        (None, {"fields": ("slug", "discount_percent", "priority", "is_active", "starts_at", "ends_at")}),
        (_("Переклади"), {"fields": ("title", "badge")}),
        (_("Товари в акції"), {"fields": ("products",)}),
    )

    def get_prepopulated_fields(self, request, obj=None):
        return {"slug": ("title",)}
