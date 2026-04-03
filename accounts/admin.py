from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

# Django to use the standard User interface for the custom model
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    pass