from django.views.generic import TemplateView


class IndexView(TemplateView):
    template_name = 'pages/index.html'
    title = ''


class HeaderView(TemplateView):
    template_name = 'main/header.html'
    title = ''


class HelloSectionView(TemplateView):
    template_name = 'main/hello_section.html'
    title = ''


class AboutView(TemplateView):
    template_name = "main/about.html"
    title = ""


class ShopView(TemplateView):
    template_name = "main/shop.html"
    title = ""


class FooterView(TemplateView):
    template_name = 'main/footer.html'
    title = ''


class OffersView(TemplateView):
    template_name = 'main/offers.html'
    title = ''


class AppView(TemplateView):
    template_name = 'main/app.html'
    title = ''


class NewsView(TemplateView):
    template_name = 'main/news.html'
    title = ''


class NoveltyView(TemplateView):
    template_name = 'main/novelty.html'
    title = ''


class TheMostPopularView(TemplateView):
    template_name = 'main/the_most_popular.html'
    title = ''


class SingInView(TemplateView):
    template_name = 'main/sing_in.html'
    title = ''
