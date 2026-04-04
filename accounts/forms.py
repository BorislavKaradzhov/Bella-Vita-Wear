from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'phone_number', 'shipping_address')

class CustomUserChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'phone_number', 'shipping_address')

        # Customize labels and help texts
        labels = {
            'shipping_address': 'Default Delivery Address',
            'phone_number': 'Contact Number',
        }
        help_texts = {
            'email': 'We will never share your email with third parties.',
            'username': 'Your username cannot be changed once created.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].disabled = True

        # Add Bootstrap styling (making the disabled field look grayed out)
        self.fields['username'].widget.attrs['class'] = 'form-control bg-light'

        for field_name, field in self.fields.items():
            if field_name != 'username':
                field.widget.attrs['class'] = 'form-control'

    # Implement form-level validations with user-friendly error messages
    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')

        if phone:
            # Strip out spaces or dashes the user might have typed
            clean_phone = phone.replace(" ", "").replace("-", "")

            if not clean_phone.isdigit():
                raise forms.ValidationError("Please enter a valid phone number containing only digits.")

            if len(clean_phone) < 10:
                raise forms.ValidationError("Your phone number must be at least 10 digits long.")

            return clean_phone

        return phone