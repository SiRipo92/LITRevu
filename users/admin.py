"""Register UserFollows in admin panel."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, UserFollows


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Use Django's built-in UserAdmin for the custom User model.

    This preserves the standard admin experience (search, filters, fieldsets).
    """

    pass


@admin.register(UserFollows)
class UserFollowsAdmin(admin.ModelAdmin):
    """Adds UserFollows model to the admin panel under Users namespace."""

    list_display = ("user", "followed_user")
    search_fields = ("user__username", "followed_user__username")
