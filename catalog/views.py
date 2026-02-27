from django.shortcuts import render, get_object_or_404
from .models import Category, Product, ProductImage, ProductLike
from django.db.models import Prefetch
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.http import require_POST


SESSION_KEY = "liked_product_ids"
def category_list(request):
    categories = (Category.objects
                  .filter(is_active=True)
                  .active_translations()
                  .order_by("sort_order", "slug")
                  .prefetch_related("translations"))
    return render(request, "catalog/category_list.html", {"categories": categories})

def category_detail(request, slug):
    category = get_object_or_404(Category.objects.active_translations(), slug=slug)

    return render(request, "catalog/category_detail.html", {"category": category})

def product_detail(request, article):
    images_qs = ProductImage.objects.order_by("-is_main", "sort_order", "id")

    product = get_object_or_404(
        Product.objects.active_translations()
               .select_related("category", "product_type", "coat_type")
               .prefetch_related("translations",
                                 Prefetch("images", queryset=images_qs, to_attr="prefetched_images")),
        article=article,
        is_active=True,
    )

    related = (Product.objects.filter(is_active=True, category=product.category)
               .exclude(pk=product.pk)
               .active_translations()
               .prefetch_related("translations")
               .order_by("-created_at")[:8])

    return render(request, "main/product_detail.html", {
        "product": product,
        "related": related,
    })

def category_products(request, slug):
    category = get_object_or_404(
        Category.objects.active_translations(), slug=slug, is_active=True
    )

    images_qs = ProductImage.objects.order_by("-is_main", "sort_order", "id")
    products = (
        Product.objects.filter(is_active=True, category=category)
        .active_translations()
        .select_related("product_type", "coat_type")
        .prefetch_related(
            "translations",
            Prefetch("images", queryset=images_qs, to_attr="prefetched_images"),
        )
        .order_by("-created_at")
    )

    # ВАЖЛИВО: рендеримо твій існуючий шаблон
    return render(request, "main/shop.html", {
        "products": products,     # шаблон уже очікує це ім’я
        "category": category,     # опційно — щоб змінити заголовок
    })


def _session_likes(request) -> set[int]:
    raw = request.session.get(SESSION_KEY, [])
    ids = set()
    for x in raw:
        try:
            ids.add(int(x))
        except (TypeError, ValueError):
            pass
    return ids

def _save_session_likes(request, ids: set[int]):
    request.session[SESSION_KEY] = sorted(ids)
    request.session.modified = True

@require_POST
def like_toggle(request, product_id: int):
    product = get_object_or_404(Product, pk=product_id)

    liked = False

    if request.user.is_authenticated:
        obj, created = ProductLike.objects.get_or_create(user=request.user, product=product)
        if created:
            liked = True
        else:
            obj.delete()
            liked = False
    else:
        ids = _session_likes(request)
        if product.id in ids:
            ids.remove(product.id)
            liked = False
        else:
            ids.add(product.id)
            liked = True
        _save_session_likes(request, ids)

    # якщо це AJAX — повертаємо JSON
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"liked": liked, "product_id": product.id})

    # fallback: редірект назад
    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or reverse("customer_portal:shop")
    return HttpResponseRedirect(next_url)