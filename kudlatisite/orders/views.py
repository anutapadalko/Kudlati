from django.shortcuts import render, redirect  # Переконайся, що є redirect
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from catalog.models import Product
from .cart import Cart
from .forms import CartAddProductForm
from .models import Order, OrderToProduct
from .forms import OrderCreateForm
from django.conf import settings
from .liqpay_internal import LiqPay
from django.views.generic import TemplateView  # Це для сторінки оплати


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


def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            order.save()

            for item in cart:
                OrderToProduct.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity']
                )
            cart.clear()

            # --- НОВА ЛОГІКА ---

            # 1. Якщо обрали LiqPay -> перекидаємо на сторінку оплати
            if order.payment_method == 'card':
                return redirect('orders:order_pay', order_id=order.id)

            # 2. Якщо обрали Готівку -> відразу дякуємо
            else:
                return render(request, 'main/order_success.html', {'order': order})

            # -------------------

    else:
        # ... твій код для GET запиту ...
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
            }
        form = OrderCreateForm(initial=initial_data)

    return render(request, 'main/checkout.html', {'cart': cart, 'form': form})


def order_pay(request, order_id):
    order = Order.objects.get(id=order_id)

    # Ініціалізуємо LiqPay
    liqpay = LiqPay(settings.LIQPAY_PUBLIC_KEY, settings.LIQPAY_PRIVATE_KEY)

    # Формуємо параметри для кнопки
    params = {
        'action': 'pay',
        'amount': str(order.get_total_cost()),  # Загальна сума
        'currency': 'UAH',
        'description': f'Оплата замовлення №{order.id}',
        'order_id': str(order.id),
        'version': '3',
        'sandbox': 1,  # 1 - це тестовий режим (гроші не списуються)
        'server_url': 'http://.../pay-callback/',  # Поки що заглушка
        # Куди повернути клієнта після оплати
        'result_url': 'http://127.0.0.1:8000/cart/success/{}'.format(order.id),
    }

    # Генеруємо HTML-форму (кнопку)
    signature = liqpay.cnb_signature(params)
    data = liqpay.cnb_data(params)

    return render(request, 'main/pay.html', {'signature': signature, 'data': data})


def payment_success(request, order_id):
    order = Order.objects.get(id=order_id)

    # Позначаємо в базі, що гроші прийшли
    order.is_paid = True
    order.save()

    return render(request, 'main/order_success.html', {'order': order})
