from django.views.generic import TemplateView


class IndexView(TemplateView):
    template_name = 'main/index.html'
    title = ''


class BestSellingProductsView(TemplateView):
    template_name = 'main/best_selling_products.html'
    title = ''


class CategoriesView(TemplateView):
    template_name = 'main/categories.html'
    title = ''


class DiscountByEmailView(TemplateView):
    template_name = 'main/discount_by_email.html'
    title = ''


class HeaderView(TemplateView):
    template_name = 'main/header.html'
    title = ''


class HelloSectionView(TemplateView):
    template_name = 'main/hello_section.html'
    title = ''


class NewlyArrivedView(TemplateView):
    template_name = 'main/newly_arrived.html'
    title = ''


class TrendingProductsView(TemplateView):
    template_name = 'main/trending_products.html'
    title = ''


class TwoOfferBlocksView(TemplateView):
    template_name = 'main/two_offer_blocks.html'
    title = ''
