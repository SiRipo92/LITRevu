from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def feed_placeholder(request):
    """Reviews page entry point for logged-in users."""
    return render(request, "placeholders/feed.html")


@login_required
def posts_placeholder(request):
    return render(request, "placeholders/posts.html")


@login_required
def follows_placeholder(request):
    return render(request, "placeholders/follows.html")
