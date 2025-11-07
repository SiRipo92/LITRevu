from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponseRedirect
from urllib.parse import urlencode
from django.contrib.auth import logout
from .forms import RegistrationForm


def register(request):
    """
    Create a new user and redirect back to home with a querystring
    so JS can display a success toast.
    """
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()  # regular user; passwords hashed
            qs = urlencode({"registered": "1", "u": user.username})
            return HttpResponseRedirect(f"{reverse('home')}?{qs}")
        # invalid → fall through and re-render with errors
    else:
        form = RegistrationForm()

    return render(request, "registration/register.html", {"form": form})


def logout_view(request):
    """
    Log the user out and redirect to home with a query param so JS can show a toast.
    """
    if request.method == "POST":
        logout(request)
    # redirect to /?logout=1 for the toast JS
    return redirect(f"{reverse('home')}?logout=1")
