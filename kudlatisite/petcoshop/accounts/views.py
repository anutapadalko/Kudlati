from django.views.generic import TemplateView

class SignInView(TemplateView):
    template_name = "accounts/sign_in.html"