from django.urls import path
from .views import IndexView, BlogView, SaleView, ShopView, SingInView

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("/blog/", BlogView.as_view(), name="blog"),
    path("/sale/", SaleView.as_view(), name="sale"),
    path("/shop/", ShopView.as_view(), name="shop"),
    path("/sing_in/", SingInView.as_view(), name="sing_in")
]
