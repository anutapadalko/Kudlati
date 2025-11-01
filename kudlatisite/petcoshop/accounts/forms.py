from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, UserRole

# тип акаунта для вибору при реєстрації
ACCOUNT_TYPE_CHOICES = [
    (UserRole.CUSTOMER, "B2C — Покупець"),
    (UserRole.B2B, "B2B — Бізнес"),
]

class RegisterUserForm(UserCreationForm):
    account_type = forms.ChoiceField(
        choices=ACCOUNT_TYPE_CHOICES,
        label="Тип акаунта",
        required=True
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "account_type")