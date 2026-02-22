from django.views.generic import TemplateView
from django.db.models import Prefetch, Q
from django.core.paginator import Paginator
from django.utils import timezone
from catalog.models import Category, Product, ProductType, ProductImage, HomeBanner, ProductLike
from django.views.generic import TemplateView
from catalog.views import _session_likes

SESSION_KEY = "liked_product_ids"



class CategoriesContextMixin:
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categories"] = (
            Category.objects.filter(is_active=True)
            .active_translations()
            .order_by("sort_order", "slug")
            .prefetch_related("translations")
        )
        return ctx


class ProductsBaseMixin:
    """
    Твій базовий queryset для товарів (з картинками і translations).
    """
    def get_images_qs(self):
        return ProductImage.objects.order_by("-is_main", "sort_order", "id")

    def get_products_base_qs(self):
        images_qs = self.get_images_qs()
        return (
            Product.objects.filter(is_active=True)
            .active_translations()
            .select_related("category", "product_type")
            .prefetch_related(
                "translations",
                Prefetch("images", queryset=images_qs, to_attr="prefetched_images"),
            )
        )

    def get_liked_ids(self):
        request = self.request
        if request.user.is_authenticated:
            return set(ProductLike.objects.filter(user=request.user).values_list("product_id", flat=True))

        raw = request.session.get(SESSION_KEY, [])
        ids = set()
        for x in raw:
            try:
                ids.add(int(x))
            except (TypeError, ValueError):
                pass
        return ids


class IndexView(CategoriesContextMixin, ProductsBaseMixin, TemplateView):
    template_name = "main/index.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx["products"] = (
            self.get_products_base_qs()
            .order_by("-created_at")[:24]
        )

        ctx["banners"] = HomeBanner.objects.filter(is_active=True).order_by("order", "id")
        return ctx


class SaleView(CategoriesContextMixin, ProductsBaseMixin, TemplateView):
    template_name = "main/sale.html"
    paginate_by = 12

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        now = timezone.now()

        qs = (
            self.get_products_base_qs()
            .filter(promotions__is_active=True)
            .filter(
                Q(promotions__starts_at__isnull=True) | Q(promotions__starts_at__lte=now),
                Q(promotions__ends_at__isnull=True) | Q(promotions__ends_at__gte=now),
            )
            .distinct()
            .order_by("-created_at")
        )

        paginator = Paginator(qs, self.paginate_by)
        page_obj = paginator.get_page(self.request.GET.get("page", 1))

        ctx["page_obj"] = page_obj
        ctx["is_paginated"] = page_obj.has_other_pages()
        ctx["products"] = page_obj.object_list

        return ctx


class ShopView(CategoriesContextMixin, ProductsBaseMixin, TemplateView):
    template_name = "main/shop.html"
    paginate_by = 12  # можеш змінити на 16

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        # Для селекту "Тип"
        ctx["product_types"] = (
            ProductType.objects.filter(is_active=True)
            .active_translations()
            .order_by("sort_order", "slug")
            .prefetch_related("translations")
        )

        qs = self.get_products_base_qs()

        g = self.request.GET

        # --- Пошук ---
        q = (g.get("q") or "").strip()
        if q:
            qs = qs.filter(
                Q(article__icontains=q) |
                Q(translations__name__icontains=q)
            ).distinct()

        # --- Фільтр: категорія ---
        category_slug = (g.get("category") or "").strip()
        if category_slug:
            qs = qs.filter(category__slug=category_slug)

        # --- Фільтр: тип продукту ---
        type_slug = (g.get("type") or "").strip()
        if type_slug:
            qs = qs.filter(product_type__slug=type_slug)

        # --- Фільтр: тільки зі знижкою/акцією ---
        # (працює, якщо в тебе є Product.promotions related_name)
        if g.get("sale") == "1":
            qs = qs.filter(promotions__is_active=True).distinct()

        # --- Фільтр: ціна ---
        min_price = (g.get("min_price") or "").strip()
        max_price = (g.get("max_price") or "").strip()
        if min_price:
            qs = qs.filter(price__gte=min_price)
        if max_price:
            qs = qs.filter(price__lte=max_price)

        # --- Сортування ---
        sort = g.get("sort") or "-created_at"
        allowed_sorts = {
            "-created_at", "created_at",
            "price", "-price",
            "translations__name", "-translations__name",
        }
        if sort not in allowed_sorts:
            sort = "-created_at"

        qs = qs.order_by(sort)

        # --- Пагінація ---
        paginator = Paginator(qs, self.paginate_by)
        page_number = g.get("page") or 1
        page_obj = paginator.get_page(page_number)

        ctx["page_obj"] = page_obj
        ctx["is_paginated"] = page_obj.has_other_pages()

        # залишаємо твою змінну products, щоб мінімально чіпати шаблони
        ctx["products"] = page_obj.object_list

        # щоб пагінація зберігала фільтри
        params = g.copy()
        params.pop("page", None)
        ctx["querystring"] = params.urlencode()

        return ctx


class AboutView(TemplateView):
    template_name = "main/about.html"


class WishlistView(TemplateView):
    template_name = "main/wishlist.html"  # або accounts/wishlist.html як хочеш

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            liked_ids = list(
                ProductLike.objects.filter(user=self.request.user)
                .values_list("product_id", flat=True)
            )
        else:
            liked_ids = sorted(_session_likes(self.request))

        # якщо хочеш — використовуй свій ProductsBaseMixin і prefetch_images
        products = (
            Product.objects.filter(id__in=liked_ids, is_active=True)
            .active_translations()
            .prefetch_related("translations")
        )

        ctx["products"] = products
        ctx["liked_ids"] = set(liked_ids)
        return ctx
