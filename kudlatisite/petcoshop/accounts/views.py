from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib.auth import login
from .forms import RegisterUserForm
from .models import UserRole, CustomerProfile, B2BProfile
from django.contrib import messages
from django.contrib.auth.views import LoginView

class LogInView(LoginView):
    template_name = "accounts/sign_in.html"
    authentication_form = AuthenticationForm

    def get_success_url(self):
        return reverse_lazy('accounts:b2c_profile')

class RegisterView(CreateView):
    form_class = RegisterUserForm
    template_name = "accounts/user_creation.html"
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        print("✅ form_valid called!")
        user = form.save(commit=False)
        user.role = form.cleaned_data["account_type"]
        user.save()
        print("✅ user saved:", user)

        # створюємо профіль за типом
        if user.role == UserRole.CUSTOMER:
            CustomerProfile.objects.create(user=user, email=user.email)
        elif user.role == UserRole.B2B:
            B2BProfile.objects.create(user=user, company_name="Без назви", email=user.email)

        login(self.request, user)
        messages.success(self.request, f"Вітаємо, {user.username}! Ваш акаунт створено.")
        return super().form_valid(form)

    def form_invalid(self, form):
        print("❌ Form errors:", form.errors)
        return super().form_invalid(form)

class ProfileView(TemplateView):
    template_name = "accounts/b2c_account.html"