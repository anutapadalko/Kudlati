from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from catalog.models import Product
from .cart import Cart
from .forms import CartAddProductForm
from .models import OrderToProduct
from .forms import OrderCreateForm


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
        # Якщо користувач відправив форму
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            # 1. Створюємо замовлення, але поки не зберігаємо в БД
            order = form.save(commit=False)

            # 2. Якщо користувач залогінений, прив'язуємо замовлення до нього
            if request.user.is_authenticated:
                order.user = request.user

            # 3. Тепер зберігаємо замовлення (щоб отримати ID)
            order.save()

            # 4. Переносимо товари з кошика в базу даних (OrderToProduct)
            for item in cart:
                OrderToProduct.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity']
                )

            # 5. Очищаємо кошик
            cart.clear()

            # 6. Показуємо сторінку успіху (створимо її пізніше)
            return render(request, 'main/order_success.html', {'order': order})

    else:
        # Якщо GET-запит (користувач просто зайшов на сторінку)
        # Якщо він залогінений, пробуємо підставити його дані
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                # 'email': request.user.email, # Якщо в Order є email
            }
        form = OrderCreateForm(initial=initial_data)

    return render(request, 'main/checkout.html', {'cart': cart, 'form': form})
