from django.shortcuts import render
from django.views.generic import TemplateView


class IndexView(TemplateView):
    template_name = "main/index.html"

class SaleView(TemplateView):
    template_name = "main/sale.html"

class ShopView(TemplateView):
    template_name = "main/shop.html"

class AboutView(TemplateView):
    template_name = "main/about.html"
    