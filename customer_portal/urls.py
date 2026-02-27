from django.urls import path, include
from .views import IndexView, SaleView, ShopView, AboutView, WishlistView

app_name = "customer_portal"

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("sale/", SaleView.as_view(), name="sale"),
    path("shop/", ShopView.as_view(), name="shop"),
    path("about/", AboutView.as_view(), name="about"),
    path('i18n/', include('django.conf.urls.i18n')),
    path("wishlist/", WishlistView.as_view(), name="wishlist"),
]
