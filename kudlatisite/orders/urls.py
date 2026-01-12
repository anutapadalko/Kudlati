from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.cart_detail, name='cart_detail'),
    path('add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('create/', views.order_create, name='order_create'),
    path('pay/<int:order_id>/', views.order_pay, name='order_pay'),
    path('success/<int:order_id>/', views.payment_success, name='payment_success'),
]
