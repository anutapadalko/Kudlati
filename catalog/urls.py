# catalog/urls.py
from django.urls import path
from . import views

app_name = "catalog"

urlpatterns = [
    path("categories/", views.category_list, name="categories"),
    path("category/<slug:slug>/", views.category_products, name="category"),
    path("product/<str:sku>/", views.product_detail, name="product"),
]
