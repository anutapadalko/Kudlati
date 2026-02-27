# catalog/urls.py
from django.urls import path
from . import views
from .views import like_toggle

app_name = "catalog"

urlpatterns = [
    path("categories/", views.category_list, name="categories"),
    path("category/<slug:slug>/", views.category_products, name="category"),
    path("product/<str:article>/", views.product_detail, name="product"),
    path("products/<int:product_id>/like-toggle/", like_toggle, name="like_toggle"),
]

