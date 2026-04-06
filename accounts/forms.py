from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm

User = get_user_model()


class BootstrapFormMixin:
    """A mixin that automatically applies Bootstrap classes and floating labels to any form."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            # Add the base Bootstrap class (preserving any existing classes if needed)
            existing_classes = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f'form-control {existing_classes}'.strip()

            # Add the placeholder for floating labels
            if field.label:
                field.widget.attrs['placeholder'] = field.label

class CustomUserCreationForm(BootstrapFormMixin, UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'phone_number', 'shipping_address')

class CustomUserChangeForm(BootstrapFormMixin, forms.ModelForm):
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
        self.fields['username'].widget.attrs['class'] += ' bg-light' # Append the gray background

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

class CustomLoginForm(BootstrapFormMixin, AuthenticationForm):
    pass

class CustomPasswordChangeForm(BootstrapFormMixin, PasswordChangeForm):
    pass