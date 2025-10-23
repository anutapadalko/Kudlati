from django.urls import path
from .views import IndexView, SaleView, ShopView, SignInView

app_name = "customer_portal"

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("sale/", SaleView.as_view(), name="sale"),
    path("shop/", ShopView.as_view(), name="shop"),
    path("sign-in/", SignInView.as_view(), name="sign_in"),
]