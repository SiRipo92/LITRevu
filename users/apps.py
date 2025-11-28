"""Register users app to be collected in settings.py."""

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """Name accounts as 'users' to be registered in Apps."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
