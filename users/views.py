from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponseRedirect
from urllib.parse import urlencode

from django.contrib.auth.forms import AuthenticationForm
from .forms import RegistrationForm


def home(request):
    """
    US01: show homepage with a (non-functional) login form.
    We do NOT process login POST here.
    """
    form = AuthenticationForm(request=None)  # unbound; visuals only
    return render(request, "users/index.html", {"form": form})


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
