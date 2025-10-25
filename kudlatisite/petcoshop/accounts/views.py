from django.views.generic import TemplateView
from django.contrib.auth.forms import AuthenticationForm

class LogInView(TemplateView):
    template_name = "accounts/sign_in.html"
    authentication_form = AuthenticationForm
