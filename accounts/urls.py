from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views
from accounts.forms import CustomLoginForm

urlpatterns = [
    # Custom registration and profile views you will build
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('register/success/', views.RegistrationSuccessView.as_view(), name='registration-success'),
    path('password/', auth_views.PasswordChangeView.as_view(
                template_name='accounts/password_change.html',
                success_url=reverse_lazy('profile')
            ), name='password-change'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('profile/delete/', views.UserDeleteView.as_view(), name='delete-account'),

    # Django's built-in authentication views
    path('login/', auth_views.LoginView.as_view(
        template_name='accounts/login.html',
        redirect_authenticated_user=True,
        authentication_form=CustomLoginForm
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]