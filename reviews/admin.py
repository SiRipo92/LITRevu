from django.contrib import admin
from .models import Ticket, Review


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "time_created")
    search_fields = ("title", "description", "user__username")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("headline", "rating", "user", "ticket", "time_created")
    search_fields = ("headline", "body", "user__username")