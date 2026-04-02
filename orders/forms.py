from django import forms
from .models import Order

class CheckoutForm(forms.ModelForm):
    discount_code = forms.CharField(
        required=False,
        help_text="Enter your Loyal Customer Discount code if you have one."
    )

    class Meta:
        model = Order
        fields = ['shipping_address']
        widgets = {
            'shipping_address': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter your full shipping address...'}),
        }