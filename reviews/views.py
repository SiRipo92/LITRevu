"""Views for the Reviews app [Feed, Ticket & Review Creation/Modification/Deletion]."""

from itertools import chain

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from LITRevu.utils.toast import redirect_with_toast
from users.models import UserFollows

from .forms import CreateTicketForm, ReviewForm
from .models import Review, Ticket


@login_required
def feed(request):
    """Display the main feed for the logged-in user and followed accounts."""
    user = request.user

    # IDs of users that the logged-in user follows
    following_ids = UserFollows.objects.filter(
        user=user
    ).values_list("followed_user_id", flat=True)

    # Include the user that's logged-in
    visible_ids = list(following_ids) + [user.id]

    # Only show posts from these users
    tickets = Ticket.objects.filter(user_id__in=visible_ids)

    # Reviews:
    #   - from the user + followed users
    #   - OR any review that answers one of the user's tickets
    reviews = Review.objects.filter(
        Q(user_id__in=visible_ids) | Q(ticket__user=user)
    ).distinct()

    # Merge + sort by creation date (newest first)
    feed_items = sorted(
        chain(tickets, reviews),
        key=lambda obj: obj.time_created,
        reverse=True,
    )

    # ---- Pagination (10 items per page) ----
    paginator = Paginator(feed_items, 10)
    page_number = request.GET.get("page", 1)

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    context = {
        "feed_items": page_obj.object_list,
        "page_obj": page_obj,
        # is_my_posts_page is False by default in template tag
    }

    # AJAX requests get only the cards + pagination controls (partial)
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return render(request, "reviews/partials/feed_list.html", context)

    # Normal full-page render
    return render(request, "reviews/pages/feed.html", context)


@login_required
def create_ticket(request):
    """Display and handle the 'Demander une critique' ticket creation form."""
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
    """Edit an existing ticket; keeps, updates, or removes image based on user actions."""
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
            return redirect(reverse("users:my_posts"))

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
    """Delete one of the current user's tickets and redirect to their posts page."""
    ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)
    ticket.delete()
    messages.success(request, "Le ticket a été supprimé avec succès.")
    return redirect("users:my_posts")


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
            return redirect(reverse("users:my_posts"))
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
    """Delete a review if the current user is its author, otherwise return 403."""
    review = get_object_or_404(Review, id=review_id)

    if review.user != request.user:
        return HttpResponseForbidden("Not allowed.")

    # Delete immediately (no confirmation screen)
    review.delete()
    return redirect("users:my_posts")
