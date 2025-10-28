from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def feed(request):
    """Reviews page entry point for logged-in users."""
    return render(request, "reviews/feed.html")
