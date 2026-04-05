from django import forms
from .models import Order
import re


# ==========================================
# CUSTOMER CHECKOUT FORM
# ==========================================
class CheckoutForm(forms.ModelForm):
    discount_code = forms.CharField(
        required=False,
        help_text="Enter your discount code if you have one.",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., SAVE20'})
    )

    postal_code = forms.CharField(
        max_length=10,
        label="Postal/ZIP Code",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 90210 or A1A 1A1'})
    )

    class Meta:
        model = Order
        fields = ['shipping_address']
        widgets = {
            'shipping_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '123 Main St\nApt 4B\nCity, State'
            }),
        }
        labels = {
            'shipping_address': 'Full Delivery Address',
        }

    def clean_postal_code(self):
        code = self.cleaned_data.get('postal_code')
        if not re.match(r'^[a-zA-Z0-9\s\-]{4,10}$', code):
            raise forms.ValidationError("Please enter a valid postal/ZIP code format.")
        return code


# ==========================================
# STAFF FULFILLMENT FORM
# ==========================================
class StaffOrderUpdateForm(forms.ModelForm):
    order_id = forms.CharField(label="Order ID", required=False)

    class Meta:
        model = Order
        fields = ['order_id', 'status', 'total_price']
        labels = {
            'status': 'Current Order Status',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Manually grab the ID from the database instance and put it in our custom field
        if self.instance and self.instance.pk:
            self.initial['order_id'] = f"#{self.instance.pk}"


        self.fields['order_id'].disabled = True
        self.fields['order_id'].widget.attrs['class'] = 'form-control bg-light text-muted'

        # We use `.get()` or safe-checks here just in case total_price is also behaving differently
        if 'total_price' in self.fields:
            self.fields['total_price'].disabled = True
            self.fields['total_price'].widget.attrs['class'] = 'form-control bg-light text-muted'

        self.fields['status'].widget.attrs['class'] = 'form-select fw-bold'

    def clean_status(self):
        status = self.cleaned_data.get('status')
        # Custom Validation: Prevent going backwards from Fulfilled to Pending
        if self.instance.status == 'Fulfilled' and status == 'Pending':
            raise forms.ValidationError(
                "You cannot change a fulfilled order back to pending. Please use 'Cancelled' if necessary.")
        return status