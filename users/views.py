"""Defines Behavior of User Views to register, logout, follow/unfollow and for user posts."""

from itertools import chain

from django.contrib.auth import get_user_model, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse

from LITRevu.utils.toast import redirect_with_toast
from reviews.models import Review, Ticket

from .forms import RegistrationForm
from .models import UserFollows

User = get_user_model()


def register(request):
    """Create a new user and redirect to home with a querystring allowing toast to display message."""
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()  # regular user; passwords hashed
            return HttpResponseRedirect(
                f"{reverse('home')}?registered=1&u={user.username}"
            )
    else:
        form = RegistrationForm()

    return render(request, "registration/register.html", {"form": form})


def logout_view(request):
    """Log the user out and redirect to home with a query param so JS can show a toast."""
    if request.method == "POST":
        logout(request)
    # redirect to /?logout=1 for the toast JS
    return redirect(f"{reverse('home')}?logout=1")


@login_required
def my_follows(request):
    """Abonnements page views handling redirects/errors when managing list of follows."""
    user = request.user

    # ---------- 1. Process follow form ----------
    if request.method == "POST":
        username = request.POST.get("username", "").strip()

        # CASE A — No username provided
        if not username:
            return redirect_with_toast(request, "error", "Veuillez entrer un nom d'utilisateur.")

        # CASE B — User does not exist
        try:
            target = User.objects.get(username=username)
        except User.DoesNotExist:
            return redirect_with_toast(request, "error", "Cet utilisateur n'existe pas.")

        # CASE C — Cannot follow yourself
        if target == request.user:
            return redirect_with_toast(request, "error", "Vous ne pouvez pas vous suivre vous-même.")

        # CASE D — Already following
        if UserFollows.objects.filter(user=user, followed_user=target).exists():
            return redirect_with_toast(request, "info", f"Vous suivez déjà {target.username}.")

        # CASE E — Create follow
        UserFollows.objects.create(user=user, followed_user=target)
        return redirect_with_toast(request, "success", f"Vous suivez désormais {target.username}.")

    # ---------- 2. Display lists ----------
    following_list = User.objects.filter(followers__user=request.user)
    followers_list = User.objects.filter(following__followed_user=request.user)

    return render(
        request,
        "users/pages/follows.html",
        {
            "following_list": following_list,
            "followers_list": followers_list,
        },
    )


@login_required
def unfollow_user(request, user_id):
    """Handle changes in view when a user is unfollowed."""
    if request.method != "POST":
        return redirect("users:my_follows")

    try:
        target = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return redirect_with_toast(request, "error", "Utilisateur introuvable.")

    relation = UserFollows.objects.filter(
        user=request.user, followed_user=target
    ).first()

    if not relation:
        return redirect_with_toast(request, "error", "Vous ne suivez pas cet utilisateur.")

    relation.delete()
    return redirect_with_toast(request, "info", f"Vous ne suivez plus {target.username}.")


@login_required
def my_posts(request):
    """Display only the current user's tickets and reviews."""
    user_tickets = Ticket.objects.filter(user=request.user)
    user_reviews = Review.objects.filter(user=request.user)

    feed_items = sorted(
        chain(user_tickets, user_reviews),
        key=lambda obj: obj.time_created,
        reverse=True,
    )

    return render(
        request,
        "users/pages/my_posts.html",
        {
            "feed_items": feed_items,
            "is_my_posts_page": True,
        },
    )
