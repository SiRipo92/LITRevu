"""Defines the url patterns used by the views in the Reviews app."""

from django.urls import path

from . import views

app_name = "reviews"

urlpatterns = [
    # temporary placeholders so header links resolve
    path("", views.feed, name="feed"),

    # Tickets (Request for Critiques)
    path("ticket/creer/", views.TicketCreateView.as_view(), name="create_ticket"),
    path("ticket/<int:ticket_id>/modifier/", views.TicketUpdateView.as_view(), name="edit_ticket"),
    path("ticket/<int:ticket_id>/supprimer/", views.TicketDeleteView.as_view(), name="delete_ticket"),

    # Reviews (Creating a critique & responding to requests)
    path("critique/creer/", views.ReviewCreateView.as_view(), name="create_review"),
    path("critique/creer/<int:ticket_id>/", views.ReviewCreateView.as_view(), name="create_review_for_ticket"),
    path("critique/<int:review_id>/modifier/", views.ReviewUpdateView.as_view(), name="edit_review"),
    path("critique/<int:review_id>/supprimer/", views.ReviewDeleteView.as_view(), name="delete_review"),
]
