from decimal import Decimal
from django.conf import settings
from catalog.models import Product


class Cart:
    def __init__(self, request):
        """
        Ініціалізуємо кошик
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # Якщо кошика ще немає в сесії - створюємо порожній
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, update_quantity=False):
        """
        Додаємо товар у кошик або оновлюємо його кількість
        """
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                # Зберігаємо ціну як рядок для JSON
                'price': str(product.price)
            }

        if update_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity

        self.save()

    def save(self):
        """
        Позначаємо сесію як "змінену", щоб Django її зберіг
        """
        self.session.modified = True

    def remove(self, product):
        """
        Видалення товару з кошика
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        """
        Перебираємо товари в кошику і отримуємо їх з бази даних
        """
        product_ids = self.cart.keys()
        # Отримуємо об'єкти product і додаємо їх у кошик
        products = Product.objects.filter(id__in=product_ids)

        cart = self.cart.copy()
        for product in products:
            cart[str(product.id)]['product'] = product

        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """
        Підрахунок всіх товарів у кошику (для іконки в шапці)
        """
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """
        Загальна вартість кошика
        """
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        """
        Очищення кошика (наприклад, після оформлення замовлення)
        """
        del self.session[settings.CART_SESSION_ID]
        self.save()
