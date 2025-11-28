"""Register Ticket and Review models in the Django admin."""

from django.contrib import admin

from .models import Review, Ticket


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    """Ticket class in Admin panel."""

    list_display = ("title", "user", "time_created")
    search_fields = ("title", "description", "user__username")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Review class in Admin panel."""

    list_display = ("headline", "rating", "user", "ticket", "time_created")
    search_fields = ("headline", "body", "user__username")
