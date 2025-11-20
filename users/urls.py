from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    path("register/", views.register, name="register"),
    path("logout/", views.logout_view, name="logout"),

    # User areas
    path("moi/posts/", views.my_posts, name="my_posts"),
    path("moi/follows/", views.my_follows, name="my_follows"),
    path("moi/follows/unfollow/<int:user_id>/", views.unfollow_user, name="unfollow"),
]

