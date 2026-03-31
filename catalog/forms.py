from django import forms
from django.core.exceptions import ValidationError
from .models import Design

class DesignForm(forms.ModelForm):
    class Meta:
        model = Design
        fields = ['title', 'category', 'description', 'image', 'available_garments']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter design details...'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
        }
        help_texts = {
            'title': 'Must be at least 3 characters long.',
        }

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if not title[0].isupper():
            raise ValidationError("The design title must start with a capital letter.")
        return title

class ReadOnlyDesignForm(DesignForm):
    """Example of a form with disabled fields for the exam requirement."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.disabled = True