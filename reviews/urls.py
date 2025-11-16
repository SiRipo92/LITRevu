from django.urls import path
from . import views

app_name = "reviews"

urlpatterns = [
    # temporary placeholders so header links resolve
    path("", views.feed, name="feed"),
    path("ticket/creer/", views.create_ticket, name="create_ticket"),
    path("ticket/modifier/<int:ticket_id>/", views.edit_ticket, name="edit_ticket"),
    path("ticket/supprimer/<int:ticket_id>/", views.delete_ticket, name="delete_ticket"),
    path("review/creer/<int:ticket_id>/", views.create_review, name="create_review"),
    path("mes-posts/", views.my_posts, name="posts"),
    path("abonnements/", views.follows_placeholder, name="follows"),
]
