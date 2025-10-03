from django.urls import path
from .views import IndexView, BestSellingProductsView, CategoriesView, DiscountByEmailView, HeaderView, HelloSectionView, NewlyArrivedView, TrendingProductsView, TwoOfferBlocksView

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("best-selling-products/", BestSellingProductsView.as_view(),
         name="best_selling_products"),
    path("categories/", CategoriesView.as_view(), name="categories"),
    path("discount-by-email/", DiscountByEmailView.as_view(),
         name="discount_by_email"),
    path("header/", HeaderView.as_view(), name="header"),
    path("hello-section/", HelloSectionView.as_view(), name="hello_section"),
    path("newly-arrived/", NewlyArrivedView.as_view(),
         name="newly_arrived"),
    path("trending-products/", TrendingProductsView.as_view(),
         name="trending_products"),
    path("two-offer-blocks/", TwoOfferBlocksView.as_view(),
         name="two_offer_blocks"),
]
