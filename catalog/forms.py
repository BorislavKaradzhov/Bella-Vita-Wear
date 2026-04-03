from django import forms
from django.core.exceptions import ValidationError
from .models import Design


class DesignForm(forms.ModelForm):
    class Meta:
        model = Design
        fields = [
            'category',
            'title',
            'description',
            'price',
            'image',
            'is_featured',
            'available_types',
            'available_sizes',
            'available_colors'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter design details...'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'available_types': forms.CheckboxSelectMultiple(),
            'available_sizes': forms.CheckboxSelectMultiple(),
            'available_colors': forms.CheckboxSelectMultiple(),
        }
        help_texts = {
            'title': 'Must be at least 3 characters long and start with a capital letter.',
        }

    def clean_title(self):
        title = self.cleaned_data.get('title')

        # 1. Ensure title actually exists before checking letters
        if not title:
            raise ValidationError("Title is required.")

        # 2. Enforce the length rule in the help_text
        if len(title) < 3:
            raise ValidationError("The design title must be at least 3 characters long.")

        # 3. Enforce the capital letter rule
        if not title[0].isupper():
            raise ValidationError("The design title must start with a capital letter.")

        return title


class ReadOnlyDesignForm(DesignForm):
    """Example of a form with disabled fields for the exam requirement."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.disabled = True