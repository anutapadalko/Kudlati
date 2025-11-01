from django.urls import path
from .views import LogInView, RegisterView, ProfileView
from django.contrib.auth.views import LogoutView

app_name = "accounts"
urlpatterns = [
     path('login/', LogInView.as_view(), name='login'),
     path('logout/', LogoutView.as_view(template_name='accounts/sign_out.html'), name='logout'),
     path('register/', RegisterView.as_view(), name='register'),
     path('b2c_profile/', ProfileView.as_view(), name='b2c_profile'),
]