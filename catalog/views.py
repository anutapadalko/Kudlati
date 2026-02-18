from django.shortcuts import render, get_object_or_404
from .models import Category, Product, ProductImage
from django.db.models import Prefetch  

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