from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'phone_number', 'shipping_address')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Loop through every field to apply Bootstrap styling and Floating Label placeholders
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label

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

        # Add Bootstrap styling and placeholder for the disabled field
        self.fields['username'].widget.attrs.update({
            'class': 'form-control bg-light',
            'placeholder': self.fields['username'].label
        })

        for field_name, field in self.fields.items():
            if field_name != 'username':
                field.widget.attrs['class'] = 'form-control'
                # Add placeholder so Floating Labels work on the profile update page too!
                if field.label:
                    field.widget.attrs['placeholder'] = field.label

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

class CustomLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Apply Bootstrap classes and placeholders for floating labels
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label