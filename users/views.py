from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponseRedirect
from urllib.parse import urlencode
from django.contrib.auth import login, logout
from django.contrib import messages
from .forms import RegistrationForm, LoginForm


def home(request):
    """
    US02: Login user via custom LoginForm (with 'Se souvenir de moi' option).
    - If already authenticated (GET), show message + logout option instead of forms.
    """
    if request.user.is_authenticated:
        # If already logged in:
        if request.method != "POST":
            # Render index with an info message & logout button
            return render(
                request,
                "users/index.html",
                {
                    "already_logged_in": True,  # drives template state
                    "form": LoginForm(request=request),  # harmless; not shown
                },
            )
        # If POST while logged in, just go to feed
        return redirect("reviews:feed")

    if request.method == "POST":
        form = LoginForm(request=request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            remember_me_raw = form.cleaned_data.get("remember_me", False)
            remember_me = bool(remember_me_raw) and str(remember_me_raw).lower() not in ("false", "0", "off")

            if remember_me:
                request.session.set_expiry(1209600)  # 2 weeks
            else:
                request.session.set_expiry(0)  # expire on browser close

            request.session.modified = True

            # Redirect to namespaced feed
            return redirect("reviews:feed")

        else:
            messages.error(request, "Nom d’utilisateur ou mot de passe incorrect.")
    else:
        form = LoginForm(request=request)

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


def logout_view(request):
    """
    Log the user out and redirect to home with a query param so JS can show a toast.
    """
    if request.method == "POST":
        logout(request)
    # redirect to /?logout=1 for the toast JS
    return redirect(f"{reverse('home')}?logout=1")
