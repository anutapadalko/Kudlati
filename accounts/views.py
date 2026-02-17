from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, DetailView
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib.auth import login
from .forms import RegisterUserForm
from .models import UserRole, CustomerProfile, B2BProfile
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from .forms import B2BProfileForm
from django.views.generic.edit import UpdateView
from django.shortcuts import get_object_or_404

class LogInView(LoginView):
    template_name = "accounts/sign_in.html"
    authentication_form = AuthenticationForm

    def get_success_url(self):
        user = self.request.user
        if user.role == UserRole.B2B:
            return reverse_lazy('accounts:b2b_profile')
        return reverse_lazy('accounts:b2c_profile')


class RegisterView(CreateView):
    form_class = RegisterUserForm
    template_name = "accounts/user_creation.html"

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

        # логінимо користувача
        login(self.request, user)
        messages.success(self.request, f"Вітаємо, {user.username}! Ваш акаунт створено.")

        # ДИНАМІЧНЕ ПЕРЕНАПРАВЛЕННЯ
        if user.role == UserRole.B2B:
            return redirect("accounts:b2b_profile")
        else:
            return redirect("accounts:b2c_profile")

    def form_invalid(self, form):
        print("❌ Form errors:", form.errors)
        return super().form_invalid(form)


class ProfileView(LoginRequiredMixin, DetailView):
    template_name = "accounts/b2c_account.html"
    model = CustomerProfile
    context_object_name = "profile"

    def get_object(self, queryset=None):
        return get_object_or_404(CustomerProfile, user=self.request.user)

class B2BProfileView(LoginRequiredMixin, DetailView):
    model = B2BProfile
    template_name = "accounts/b2b_account.html"
    context_object_name = "profile"

    def get_object(self, queryset=None):
        return get_object_or_404(B2BProfile, user=self.request.user)

class EditB2BProfileView(LoginRequiredMixin, UpdateView):
    model = B2BProfile
    form_class = B2BProfileForm
    template_name = "accounts/edit_b2b_profile.html"
    success_url = reverse_lazy("accounts:b2b_profile")

    def get_object(self, queryset=None):
        return get_object_or_404(B2BProfile, user=self.request.user)