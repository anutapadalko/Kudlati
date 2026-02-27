from django import forms
from django.contrib.auth.models import User
from .models import UserProfile
from phonenumber_field.formfields import PhoneNumberField


class LoginForm(forms.ModelForm):
    # overload django password input, make hiding input
    password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = User
        fields = ("email", "password")


class RegisterForm(forms.ModelForm):
    # include email validation
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True

    phone = PhoneNumberField(region="UA", required=False)

    # overload django password input, make hiding input
    password = forms.CharField(widget=forms.PasswordInput())

    type = forms.ChoiceField(choices=UserProfile.PROFILE_TYPE)
    class Meta:
        model = User
        fields = ("email", "password", "first_name", "last_name", "phone", "type")
