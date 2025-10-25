from django.urls import path
from .views import LogInView

app_name = "accounts"
urlpatterns = [
     path('login/', LogInView.as_view(), name='login'),
     # path('logout/', views.LogoutView.as_view(), name='logout'),
     # path('register/', views.RegisterView.as_view(), name='register'),
]