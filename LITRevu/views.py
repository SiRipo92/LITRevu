"""View for LITRevu's homepage."""

from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import redirect, render

from users.forms import LoginForm


def home(request):
    """
    Global homepage for LITRevu.

    Responsibilities:
    - Display login form.
    - Handle login via custom LoginForm with 'Se souvenir de moi'.
    - Provide access to registration via link/button.
    - This view is intentionally project-level (not tied to a single feature app).
    """
    if request.method == "POST":
        form = LoginForm(request=request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)

            remember_me = bool(form.cleaned_data.get("remember_me", False))
            if remember_me:
                # Session persists (2 weeks)
                request.session.set_expiry(1209600)
            else:
                # Session ends when browser closes
                request.session.set_expiry(0)

            request.session.modified = True
            return redirect("reviews:feed")

        # Invalid credentials: redisplay form with errors
        messages.error(request, "Nom d’utilisateur ou mot de passe incorrect.")
    else:
        form = LoginForm(request=request)

    return render(request, "home.html", {"form": form})
