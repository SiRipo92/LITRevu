from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Ticket, Review
from .forms import CreateTicketForm
from django.contrib import messages


@login_required
def feed(request):
    """
    Display the user's feed (Flux).
    Shows the list of tickets and provides access to ticket creation.
    """
    tickets = Ticket.objects.all().order_by("-time_created")
    return render(request, "reviews/pages/feed.html", {"tickets": tickets})


@login_required
def create_ticket(request):
    """Form for 'Demander une critique'."""
    if request.method == "POST":
        form = CreateTicketForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.time_created = timezone.now()
            ticket.save()
            return redirect("reviews:feed")
    else:
        form = CreateTicketForm()

    return render(request, "reviews/forms/submit_ticket.html", {"form": form})


@login_required
def edit_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)

    if request.method == "POST":
        form = CreateTicketForm(request.POST, request.FILES, instance=ticket)
        if form.is_valid():
            ticket = form.save(commit=False)

            # If the JS set this hidden input to true, remove the existing image
            if request.POST.get("delete_existing_image") == "true":
                if ticket.image:
                    ticket.image.delete(save=False)
                ticket.image = None

            ticket.save()
            messages.success(request, "Votre ticket a été mis à jour avec succès.")
            return redirect("reviews:posts")
    else:
        form = CreateTicketForm(instance=ticket)

    # Placeholder centered with original title
    form.fields["title"].widget.attrs["placeholder"] = ticket.title
    form.fields["title"].widget.attrs["class"] += " text-center"

    return render(request, "reviews/forms/submit_ticket.html", {
        "form": form,
        "editing": True,
    })


@login_required
def delete_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)
    ticket.delete()
    messages.success(request, "Le ticket a été supprimé avec succès.")
    return redirect("reviews:posts")


@login_required
def create_review(request, ticket_id):
    """
    Placeholder view for creating a review attached to a specific Ticket.
    """
    ticket = Ticket.objects.get(pk=ticket_id)
    return render(request, "placeholders/create_review.html", {"ticket": ticket})


@login_required
def my_posts(request):
    """Display only the current user's tickets and reviews."""
    user_tickets = Ticket.objects.filter(user=request.user).order_by("-time_created")
    user_reviews = Review.objects.filter(user=request.user).order_by("-time_created")

    return render(request, "reviews/pages/my_posts.html", {
        "tickets": user_tickets,
        "reviews": user_reviews,
    })


@login_required
def follows_placeholder(request):
    return render(request, "placeholders/follows.html")
