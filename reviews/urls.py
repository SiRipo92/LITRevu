from django.urls import path
from . import views

app_name = "reviews"  # <-- add namespace

urlpatterns = [
    # temporary placeholders so header links resolve
    path("", views.feed_placeholder, name="feed"),
    path("posts/", views.posts_placeholder, name="posts"),
    path("abonnements/", views.follows_placeholder, name="follows"),
]
