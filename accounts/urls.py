from django.urls import path
from .views import LoginView, RegisterView, RegularProfileView

app_name = "accounts"
urlpatterns = [
     path('login/', LoginView.as_view(), name='login'),
     path('register/', RegisterView.as_view(), name='register'),
     path('regular/', RegularProfileView.as_view(), name='regular')
     # path('logout/', LogoutView.as_view(template_name='accounts/sign_out.html'), name='logout'),
     # path('b2c_profile/', ProfileView.as_view(), name='b2c_profile'),
     # path('b2b_profile/', B2BProfileView.as_view(), name='b2b_profile'),
     # path('b2b_profile/edit/', EditB2BProfileView.as_view(), name='edit_b2b_profile'),
]
