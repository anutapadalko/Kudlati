from django.views.generic import TemplateView
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm

class LogInView(TemplateView):
    template_name = "accounts/sign_in.html"
    authentication_form = AuthenticationForm

class RegisterView(TemplateView):
    template_name = "accounts/user_creation.html"
    authentication_form = UserCreationForm