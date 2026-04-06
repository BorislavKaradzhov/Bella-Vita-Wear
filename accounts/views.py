from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.contrib.auth.views import PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from .forms import CustomUserCreationForm, CustomUserChangeForm, CustomPasswordChangeForm

User = get_user_model()

class UserRegistrationView(CreateView):
    """Handles new user sign-ups."""
    model = User
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('registration-success')

class RegistrationSuccessView(TemplateView):
    template_name = 'accounts/registration_success.html'

class UserProfileView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """Allows users to view and update their own profile data."""
    model = User
    form_class = CustomUserChangeForm
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('profile')
    success_message = "Your profile information has been successfully updated!"

    def get_object(self, queryset=None):
        # This ensures users can only edit THEIR OWN profile
        return self.request.user

class UserDeleteView(LoginRequiredMixin, DeleteView):
    """Allows users to permanently delete their account."""
    model = User
    template_name = 'accounts/profile_confirm_delete.html'
    success_url = reverse_lazy('design-list')

    def get_object(self, queryset=None):
        return self.request.user

class CustomPasswordChangeView(SuccessMessageMixin, PasswordChangeView):
    template_name = 'accounts/password_change.html'
    form_class = CustomPasswordChangeForm
    success_url = reverse_lazy('profile')
    success_message = "Your password has been successfully updated!"