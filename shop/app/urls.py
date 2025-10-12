from django.urls import path
from .views import IndexView, FooterView, OffersView, AppView, NewsView, NoveltyView, TheMostPopularView, SingInView

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("/footer/", FooterView.as_view(), name="footre"),
    path("/offers/", OffersView.as_view(), name="offers"),
    path("/app/", AppView.as_view(), name="app"),
    path("/news/", NewsView.as_view(), name="news"),
    path("/novelty/", NoveltyView.as_view(), name="novelty"),
    path("/the_most_popular/", TheMostPopularView.as_view(), name="the_most_popular"),
    path("/sing_in/", SingInView.as_view(), name="sing_in")
]
