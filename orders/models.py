from django.db import models
from django.conf import settings
from catalog.models import Product  # Імпортуємо твої товари


class Order(models.Model):
    # Статуси замовлення
    STATUS_CHOICES = [
        ('new', 'Нове'),
        ('paid', 'Оплачено'),
        ('shipped', 'Відправлено'),
        ('completed', 'Завершено'),
        ('cancelled', 'Скасовано'),
    ]

    # userId: прив'язка до зареєстрованого користувача
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders'
    )

    # Технічні поля
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата створення")
    # Last Modification Date
    lmd = models.DateTimeField(
        auto_now=True, verbose_name="Дата останньої зміни")

    # Поля замовлення
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="Статус")
    is_paid = models.BooleanField(default=False, verbose_name="Оплачено")
    comment = models.TextField(blank=True, verbose_name="Коментар користувача")

    # Контактні дані (можна розширити залежно від форми доставки)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Замовлення"
        verbose_name_plural = "Замовлення"

    def __str__(self):
        return f"Order {self.id} - {self.status}"

    PAYMENT_METHODS = [
        ('cash', 'Накладений платіж (Оплата при отриманні)'),
        ('card', 'Оплата карткою (LiqPay)'),
    ]

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS,
        default='cash',
        verbose_name='Спосіб оплати'
    )

    def get_total_cost(self):
        # Рахуємо суму: ціна * кількість для кожного товару в замовленні
        return sum(item.price * item.quantity for item in self.items.all())


class OrderToProduct(models.Model):
    # Проміжна таблиця OrdrToProducts
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    # Фіксуємо ціну на момент покупки
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Item {self.product.sku} for Order {self.order.id}"
