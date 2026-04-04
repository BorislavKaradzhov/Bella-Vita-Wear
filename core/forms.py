from django import forms
from django.core.validators import MinLengthValidator

class ContactUsForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        label="Full Name",
        widget=forms.TextInput(attrs={'placeholder': 'e.g., Jane Doe', 'class': 'form-control'}),
        validators=[MinLengthValidator(3, message="Please provide your full name (minimum 3 characters).")]
    )
    email = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(attrs={'placeholder': 'you@example.com', 'class': 'form-control'}),
        error_messages={'invalid': 'Please enter a valid email address so we can get back to you.'}
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'How can we help you today?', 'class': 'form-control', 'rows': 5}),
        validators=[MinLengthValidator(20, message="Please provide a bit more detail (minimum 20 characters).")]
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and "@spam.com" in email:
            raise forms.ValidationError("Please use a valid personal or business email.")
        return email