from django import forms
from .models import Order

PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 21)]


class CartAddProductForm(forms.Form):
    # Дозволяємо вибрати кількість від 1 до 20
    quantity = forms.TypedChoiceField(
        choices=PRODUCT_QUANTITY_CHOICES,
        coerce=int,
        label="Кількість"
    )
    # Приховане поле: чи додавати до існуючої кількості, чи перезаписувати її
    override = forms.BooleanField(
        required=False, initial=False, widget=forms.HiddenInput)


class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'phone', 'address', 'comment']
        # Ми не додаємо сюди status, is_paid чи user, бо це заповнюється автоматично
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ваше ім\'я'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ваше прізвище'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+380...'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Місто, вулиця, відділення пошти'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Коментар до замовлення (необов\'язково)'}),
        }
