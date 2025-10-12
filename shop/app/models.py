# from django.db import models

# class Category(models.Model):
#     name = models.CharField(max_length=100)

# class Product(models.Model):
#     category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
#     name = models.CharField(max_length=200)
#     description = models.TextField(blank=True)
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#     stock = models.PositiveIntegerField()
#     image = models.ImageField(upload_to="products/")
