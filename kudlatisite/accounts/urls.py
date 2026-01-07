from django.urls import path
from .views import LogInView, RegisterView, ProfileView, B2BProfileView, EditB2BProfileView
from django.contrib.auth.views import LogoutView

app_name = "accounts"
urlpatterns = [
     path('login/', LogInView.as_view(), name='login'),
     path('logout/', LogoutView.as_view(template_name='accounts/sign_out.html'), name='logout'),
     path('register/', RegisterView.as_view(), name='register'),
     path('b2c_profile/', ProfileView.as_view(), name='b2c_profile'),
     path('b2b_profile/', B2BProfileView.as_view(), name='b2b_profile'),
     path('b2b_profile/edit/', EditB2BProfileView.as_view(), name='edit_b2b_profile'),
]