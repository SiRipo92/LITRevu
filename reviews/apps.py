"""App configuration for the reviews application."""

from django.apps import AppConfig


class ReviewsConfig(AppConfig):
    """Django AppConfig for the reviews application."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reviews'
