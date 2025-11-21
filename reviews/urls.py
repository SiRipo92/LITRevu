from django.urls import path
from . import views

app_name = "reviews"

urlpatterns = [
    # temporary placeholders so header links resolve
    path("", views.feed, name="feed"),

    # Tickets (Request for Critiques)
    path("ticket/creer/", views.create_ticket, name="create_ticket"),
    path("ticket/modifier/<int:ticket_id>/", views.edit_ticket, name="edit_ticket"),
    path("ticket/supprimer/<int:ticket_id>/", views.delete_ticket, name="delete_ticket"),

    # Reviews (Creating a critique & responding to requests)
    path("critique/creer/<int:ticket_id>/", views.create_review, name="create_review"),
    path("critique/creer/", views.create_review, name="create_review"),
    path("critique/creer/<int:ticket_id>/", views.create_review, name="create_review_for_ticket"),
    path("critique/modifier/<int:review_id>/", views.edit_review, name="edit_review"),
    path("critique/supprimer/<int:review_id>/", views.delete_review, name="delete_review"),
]
