from itertools import chain
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseForbidden
from LITRevu.utils.toast import redirect_with_toast

from .models import Ticket, Review
from users.models import UserFollows
from .forms import CreateTicketForm, ReviewForm


@login_required
def feed(request):
    user = request.user

    # IDs of users that the logged-in user follows
    following_ids = UserFollows.objects.filter(
        user=user
    ).values_list("followed_user_id", flat=True)

    # Include the user that's logged-in
    visible_ids = list(following_ids) + [user.id]

    # Only show posts from these users
    tickets = Ticket.objects.filter(user_id__in=visible_ids)
    reviews = Review.objects.filter(user_id__in=visible_ids)
    responses_to_my_tickets = Review.objects.filter(ticket__user=request.user)

    # Merge + sort by creation date
    feed_items = sorted(
        chain(
            tickets,
            reviews,
            responses_to_my_tickets,
        ),
        key=lambda obj: obj.time_created,
        reverse=True,
    )

    return render(request, "reviews/pages/feed.html", {"feed_items": feed_items})


@login_required
def create_ticket(request):
    """Form for 'Demander une critique'."""
    if request.method == "POST":
        ticket_form = CreateTicketForm(request.POST, request.FILES)
        if ticket_form.is_valid():
            ticket = ticket_form.save(commit=False)
            ticket.user = request.user
            ticket.time_created = timezone.now()
            ticket.save()
            return redirect("reviews:feed")
    else:
        ticket_form = CreateTicketForm()

    return render(
        request,
        "reviews/forms/submit_ticket.html",
        {
            "ticket_form": ticket_form,  # <- key your include expects
            "editing": False,  # used by the component to show existing image
        },
    )


@login_required
def edit_ticket(request, ticket_id: int):
    """
    Edit an existing ticket; keeps, updates, or removes image based on user actions.
    """
    ticket = get_object_or_404(Ticket, pk=ticket_id, user=request.user)

    if request.method == "POST":
        ticket_form = CreateTicketForm(request.POST, request.FILES, instance=ticket)

        delete_flag = request.POST.get("delete_existing_image") == "true"

        # CASE 1: User clicked "Supprimer l’image"
        if delete_flag:
            # Remove image file from storage
            if ticket.image:
                ticket.image.delete(save=False)
            ticket.image = None

        # CASE 2: New file selected → handled automatically by form
        # CASE 3: No change → form keeps the current image

        if ticket_form.is_valid():
            ticket_form.save()
            return redirect(reverse("reviews:posts"))

    else:
        ticket_form = CreateTicketForm(instance=ticket)

    return render(
        request,
        "reviews/forms/submit_ticket.html",
        {
            "ticket_form": ticket_form,
            "editing": True,
        },
    )


@login_required
def delete_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)
    ticket.delete()
    messages.success(request, "Le ticket a été supprimé avec succès.")
    return redirect("reviews:posts")


@login_required
def create_review(request, ticket_id: int | None = None):
    """
    Create a review.

    - If `ticket_id` is provided, render a page with the referenced ticket on top
      and a review form below. Submitting saves a Review linked to that Ticket.
    - If `ticket_id` is absent, render a two-section form:
        1) "Livre / Article" (creates a Ticket),
        2) "Critique" (creates a Review linked to the newly created Ticket).
      The 'Envoyer' button lives at the bottom of the second section.

    Redirects to the feed on success.
    """
    if ticket_id is not None:
        # Response-to-ticket mode
        # Desactivate 'Create review button' if Review has already been posted for a ticket
        ticket = get_object_or_404(Ticket, pk=ticket_id)
        # BLOCK review creation for already-reviewed ticket
        if hasattr(ticket, "review"):
            return redirect_with_toast(
                request,
                "error",
                "Une critique existe déjà pour ce billet."
            )

        if request.method == "POST":
            form = ReviewForm(request.POST, user=request.user, ticket=ticket)
            if form.is_valid():
                review = form.save(commit=False)
                review.user = request.user
                review.ticket = ticket
                review.save()
                return redirect(reverse("reviews:feed"))
        else:
            form = ReviewForm(user=request.user, ticket=ticket)

        context = {
            "page_title": "Créer une critique",
            "is_response_mode": True,
            "ticket": ticket,
            "review_form": form,
        }
        return render(request, "reviews/forms/create_review.html", context)

    # Standalone review mode (auto-create a Ticket, then a Review)
    if request.method == "POST":
        ticket_form = CreateTicketForm(request.POST, request.FILES)
        review_form = ReviewForm(request.POST, user=request.user, ticket=None)
        if ticket_form.is_valid() and review_form.is_valid():
            new_ticket = ticket_form.save(commit=False)
            new_ticket.user = request.user
            new_ticket.save()

            # Now bind ticket into review and save
            review = review_form.save(commit=False)
            review.user = request.user
            review.ticket = new_ticket
            review.save()
            return redirect(reverse("reviews:feed"))
    else:
        ticket_form = CreateTicketForm()
        review_form = ReviewForm(user=request.user, ticket=None)

    context = {
        "page_title": "Créer une critique",
        "is_response_mode": False,
        "ticket_form": ticket_form,
        "review_form": review_form,
    }
    return render(request, "reviews/forms/create_review.html", context)


@login_required
def edit_review(request, review_id: int):
    """
    Edit an existing review.

    - Only the owner (request.user) can edit.
    - Pre-fills the form with existing review data.
    - Always shows the associated ticket at the top (response mode layout).
    """
    review = get_object_or_404(Review, pk=review_id, user=request.user)
    ticket = review.ticket  # the ticket this review responds to

    if request.method == "POST":
        form = ReviewForm(
            request.POST,
            user=request.user,
            ticket=ticket,
            instance=review,  # 👈 pre-fill with existing review
        )
        if form.is_valid():
            form.save()
            messages.success(request, "La critique a été modifiée avec succès.")
            return redirect(reverse("reviews:posts"))
    else:
        form = ReviewForm(
            user=request.user,
            ticket=ticket,
            instance=review,  # 👈 initial values in the form
        )

    context = {
        "page_title": "Modifier une critique",
        "is_response_mode": True,   # same layout as "réponse à un ticket"
        "ticket": ticket,
        "review_form": form,
        "editing": True,            # optional flag if you want different button text
    }
    return render(request, "reviews/forms/create_review.html", context)


@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    if review.user != request.user:
        return HttpResponseForbidden("Not allowed.")

    # Delete immediately (no confirmation screen)
    review.delete()
    return redirect("reviews:posts")
