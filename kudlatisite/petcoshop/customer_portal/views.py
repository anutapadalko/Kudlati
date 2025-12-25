from catalog.models import Category
from django.shortcuts import render
from django.views.generic import TemplateView
from django.db.models import Prefetch
from catalog.models import Category, Product, ProductImage
from catalog.models import Product


class CategoriesContextMixin:
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categories"] = (Category.objects.filter(is_active=True)
                             .active_translations()
                             .order_by("sort_order", "slug")
                             .prefetch_related("translations"))
        return ctx


class IndexView(CategoriesContextMixin, TemplateView):
    template_name = "main/index.html"


class SaleView(TemplateView):
    template_name = "main/sale.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        products = Product.objects.prefetch_related('promotions', 'translations').filter(
            promotions__isnull=False,
            promotions__is_active=True
        ).distinct()

        context['products'] = products
        return context


class ShopView(TemplateView):
    template_name = "main/shop.html"

    from django.shortcuts import render


class CategoriesContextMixin:
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categories"] = (Category.objects.filter(is_active=True)
                             .active_translations()
                             .order_by("sort_order", "slug")
                             .prefetch_related("translations"))
        return ctx


class IndexView(CategoriesContextMixin, TemplateView):
    template_name = "main/index.html"


class ShopView(TemplateView):
    template_name = "main/shop.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        images_qs = ProductImage.objects.order_by(
            "-is_main", "sort_order", "id")

        products = (
            Product.objects.filter(is_active=True)
            .active_translations()
            .select_related("category", "product_type")
            .prefetch_related(
                "translations",
                Prefetch("images", queryset=images_qs,
                         to_attr="prefetched_images"),
            )
            .order_by("-created_at")[:24]
        )
        ctx["products"] = products
        return ctx


class AboutView(TemplateView):
    template_name = "main/about.html"


class AboutView(TemplateView):
    template_name = "main/about.html"
