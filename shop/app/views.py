from django.views.generic import TemplateView

class IndexView(TemplateView):
    template_name = 'pages/index.html'
    title = ''

class BlogView(TemplateView):
    template_name = 'main/blog.html'
    title = ''

class SaleView(TemplateView):
    template_name = 'main/sale.html'
    title = ''

class ShopView(TemplateView):
    template_name = 'main/shop.html'
    title = ''

class SingInView(TemplateView):
    template_name = 'main/sing_in.html'
    title = ''
