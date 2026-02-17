from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, UserRole
from .models import B2BProfile

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

class B2BProfileForm(forms.ModelForm):
    class Meta:
        model = B2BProfile
        fields = [
            "company_name",
            "contact_first_name",
            "contact_last_name",
            "email",
            "phone",
            "legal_address",
            "actual_address",
            "edrpou_or_ipn",
            "client_type",
            "min_order_amount",
            "payment_terms",
            "delivery_terms",
            "individual_discount_percent",
            "contracts_link",
            "notes",
        ]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "legal_address": forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
            "actual_address": forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
        }