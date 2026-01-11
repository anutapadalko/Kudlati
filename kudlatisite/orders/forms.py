from django import forms

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
