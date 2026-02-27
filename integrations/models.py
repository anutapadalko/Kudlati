from django.db import models
from catalog.models import Product


class Promotion(models.Model):
    title = models.CharField(max_length=200, verbose_name="Назва акції")
    discount_percent = models.PositiveIntegerField(
        default=0, verbose_name="Відсоток знижки")
    is_active = models.BooleanField(default=True, verbose_name="Активна")

    products = models.ManyToManyField(
        Product,
        related_name="promotions",
        blank=True,
        verbose_name="Товари",
    )

    def __str__(self):
        return self.title