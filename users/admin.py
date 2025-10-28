from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Use Django's built-in UserAdmin for the custom User model.
    This preserves the standard admin experience (search, filters, fieldsets).
    """
    pass
