from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from catalog.models import Product
from .cart import Cart
from .forms import CartAddProductForm


@require_POST
def cart_add(request, product_id):
    """Обробляє додавання товару в кошик"""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)

    if form.is_valid():
        cd = form.cleaned_data
        cart.add(product=product,
                 quantity=cd['quantity'],
                 update_quantity=cd['override'])

    # Після додавання перенаправляємо на сторінку кошика
    return redirect('orders:cart_detail')


@require_POST
def cart_remove(request, product_id):
    """Видаляє товар з кошика"""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('orders:cart_detail')


def cart_detail(request):
    """Відображає сторінку кошика"""
    cart = Cart(request)
    # Додаємо форму зміни кількості для кожного товару в кошику
    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(initial={
            'quantity': item['quantity'],
            'override': True
        })

    return render(request, 'main/cart_detail.html', {'cart': cart})
