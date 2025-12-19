"""Views for the Reviews app [Feed, Ticket & Review Creation/Modification/Deletion]."""

from __future__ import annotations

from itertools import chain
from typing import Any, TypeAlias, cast

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import EmptyPage, Page, PageNotAnInteger, Paginator
from django.db import IntegrityError, transaction
from django.db.models import Q, QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, UpdateView

from LITRevu.utils.toast import redirect_with_toast
from users.models import UserFollows

from .forms import CreateTicketForm, ReviewForm
from .models import Review, Ticket

FeedItem: TypeAlias = Ticket | Review

# --------- HELPER MIXINS FOR TICKET AND REVIEW FORMS TO GET CONTEXT


class TicketFormContextMixin:
    """Expose template-friendly context for Ticket forms.

    This mixin normalizes context keys to match existing templates:
    - Provides `ticket_form` (instead of the generic `form` key).
    - Provides an `editing` boolean flag used by templates.
    """

    editing: bool = False

    def get_context_data(self, **kwargs):
        """Return context data with Ticket template keys added."""
        context = super().get_context_data(**kwargs)
        context["ticket_form"] = context.get("form")
        context["editing"] = self.editing
        return context


class OwnerQuerySetMixin(LoginRequiredMixin):
    """Restrict queryset to objects owned by the current user."""

    def get_queryset(self):
        """Return queryset filtered to the current user's objects."""
        return super().get_queryset().filter(user=self.request.user)

# --------- FEED VIEW (READ OPERATION)


@login_required
def feed(request: HttpRequest) -> HttpResponse:
    """Display the main feed for the logged-in user and followed accounts."""
    # request.user is an authenticated user at runtime thanks to @login_required
    user = request.user

    # values_list(..., flat=True) yields a queryset of ints (user IDs) which is by default a tuple
    # flat=True returns single value (not a tuple), eg. [3, 7, 12] instead of [(3,), (7,), (12,)]
    following_ids: list[int] = list(
        UserFollows.objects.filter(user=user).values_list("followed_user_id", flat=True)
    )

    # Convert queryset -> concrete Python list so we can concatenate safely
    following_ids: list[int] = list(following_ids)

    # user.pk is typed as int | None in Django stubs, but for an authenticated DB user it's an int.
    user_id: int = cast(int, user.pk)

    # Final list of IDs visible in the feed
    visible_ids: list[int] = [*following_ids, user_id]

    # QuerySet[Ticket]: tickets written by visible users
    tickets: QuerySet[Ticket] = Ticket.objects.filter(user_id__in=visible_ids)

    # QuerySet[Review]: reviews written by visible users OR reviews answering one of *my* tickets
    # distinct() removes duplicate rows if queryset ends up matching the same Review with more than 1 path
    # Thereby keeping single / unique rows for Reviews
    reviews: QuerySet[Review] = Review.objects.filter(
        Q(user_id__in=visible_ids) | Q(ticket__user=user)
    ).distinct()

    # chain() creates an iterator of (Ticket | Review).
    # sorted() consumes it into a list[FeedItem] ordered by time_created desc.
    feed_items: list[FeedItem] = sorted(
        chain(tickets, reviews),
        key=lambda obj: obj.time_created,
        reverse=True,
    )

    # Paginator works over a Python sequence (here: list[FeedItem])
    paginator: Paginator = Paginator(feed_items, 10)

    # GET params are strings (or None). Use default "1" to keep type consistent.
    page_number = request.GET.get("page", 1)

    # Page: contains the items for the current page
    try:
        page_obj: Page = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # What templates consume:
    context = {
        "feed_items": page_obj.object_list,
        "page_obj": page_obj,
        # is_my_posts_page is False by default in template tag
    }

    # Header lookup returns str | None
    is_ajax: bool = request.headers.get("x-requested-with") == "XMLHttpRequest"

    if is_ajax:
        return render(request, "reviews/partials/feed_list.html", context)

    # Normal full-page render
    return render(request, "reviews/pages/feed.html", context)

# ----------------------------------------
# TICKET CRUD Operations
# ----------------------------------------


class TicketCreateView(TicketFormContextMixin, LoginRequiredMixin, CreateView):
    """Create a Ticket for the logged-in user."""

    model = Ticket
    form_class = CreateTicketForm
    template_name = "reviews/forms/submit_ticket.html"
    success_url = reverse_lazy("reviews:feed")
    editing = False

    def form_valid(self, form):
        """Attach the ticket owner before saving."""
        form.instance.user = self.request.user
        return super().form_valid(form)


class TicketUpdateView(TicketFormContextMixin, OwnerQuerySetMixin, UpdateView):
    """Update a Ticket owned by the logged-in user.

    Supports optional image removal via the `delete_existing_image` POST flag.
    """

    pk_url_kwarg = "ticket_id"
    model = Ticket
    form_class = CreateTicketForm
    template_name = "reviews/forms/submit_ticket.html"
    success_url = reverse_lazy("users:my_posts")
    editing = True

    def form_valid(self, form):
        """Handle optional image deletion and save the updated ticket."""
        delete_flag = self.request.POST.get("delete_existing_image") == "true"
        uploaded_new_image = "image" in self.request.FILES

        # delete existing image only after validation, and only if not replacing it
        if delete_flag and not uploaded_new_image and form.instance.image:
            form.instance.image.delete(save=False)
            form.instance.image = None

        return super().form_valid(form)


class TicketDeleteView(OwnerQuerySetMixin, DeleteView):
    """Delete a Ticket owned by the logged-in user (POST only)."""

    pk_url_kwarg = "ticket_id"
    model = Ticket
    success_url = reverse_lazy("users:my_posts")
    http_method_names = ["post"]

    def form_valid(self, form):
        """Delete the ticket and display a success message."""
        messages.success(self.request, "Le ticket a été supprimé avec succès.")
        return super().form_valid(form)


# ----------------------------------------
# Review CRUD Operations
# ----------------------------------------
class ReviewCreateView(LoginRequiredMixin, View):
    """Create a Review in one of two modes.

    Modes:
    - Response mode: create a Review for an existing Ticket (ticket_id provided).
    - Standalone mode: create a Ticket and its Review in one submission.

    Both modes enforce the unique constraint (user, ticket) safely.
    """

    template_name = "reviews/forms/create_review.html"

    def get(self, request, ticket_id: int | None = None):
        """Render the review creation form (response or standalone mode)."""
        if ticket_id is not None:
            ticket = get_object_or_404(Ticket, pk=ticket_id)

            if ticket.is_closed_for(request.user):
                return redirect_with_toast(
                    request, "error", "Vous avez déjà publié une critique pour ce billet."
                )

            form = ReviewForm(user=request.user, ticket=ticket)
            return render(request, self.template_name, {
                "page_title": "Créer une critique",
                "is_response_mode": True,
                "ticket": ticket,
                "review_form": form,
            })

        # standalone mode
        return render(request, self.template_name, {
            "page_title": "Créer une critique",
            "is_response_mode": False,
            "ticket_form": CreateTicketForm(),
            "review_form": ReviewForm(user=request.user, ticket=None),
        })

    def post(self, request, ticket_id: int | None = None):
        """Handle review creation submission (response or standalone mode)."""
        if ticket_id is not None:
            ticket = get_object_or_404(Ticket, pk=ticket_id)

            if ticket.is_closed_for(request.user):
                return redirect_with_toast(
                    request, "error", "Vous avez déjà publié une critique pour ce billet."
                )

            form = ReviewForm(request.POST, user=request.user, ticket=ticket)
            if form.is_valid():
                review = form.save(commit=False)
                review.user = request.user
                review.ticket = ticket

                try:
                    with transaction.atomic():
                        review.save()
                except IntegrityError:
                    # UniqueConstraint(user, ticket) hit (double submit / parallel request)
                    return redirect_with_toast(
                        request, "error", "Vous avez déjà publié une critique pour ce billet."
                    )

                return redirect(reverse("reviews:feed"))

            return render(request, self.template_name, {
                "page_title": "Créer une critique",
                "is_response_mode": True,
                "ticket": ticket,
                "review_form": form,
            })

        # --------------------------
        # Standalone mode (Ticket + Review)
        # --------------------------
        ticket_form = CreateTicketForm(request.POST, request.FILES)
        review_form = ReviewForm(request.POST, user=request.user, ticket=None)

        if ticket_form.is_valid() and review_form.is_valid():
            with transaction.atomic():
                new_ticket = ticket_form.save(commit=False)
                new_ticket.user = request.user
                new_ticket.save()

                review = review_form.save(commit=False)
                review.user = request.user
                review.ticket = new_ticket
                review.save()

            return redirect(reverse("reviews:feed"))

        return render(request, self.template_name, {
            "page_title": "Créer une critique",
            "is_response_mode": False,
            "ticket_form": ticket_form,
            "review_form": review_form,
        })


class ReviewUpdateView(OwnerQuerySetMixin, SuccessMessageMixin, UpdateView):
    """Update a Review owned by the logged-in user."""

    model = Review
    form_class = ReviewForm
    template_name = "reviews/forms/create_review.html"
    pk_url_kwarg = "review_id"
    success_url = reverse_lazy("users:my_posts")
    success_message = "La critique a été modifiée avec succès."

    def get_form_kwargs(self):
        """Inject user and ticket into ReviewForm."""
        kwargs = super().get_form_kwargs()
        review = self.get_object()
        kwargs["user"] = self.request.user
        kwargs["ticket"] = review.ticket
        return kwargs

    def get_context_data(self, **kwargs):
        """Match template context keys used by your existing template."""
        context = super().get_context_data(**kwargs)
        review = self.get_object()
        context["page_title"] = "Modifier une critique"
        context["is_response_mode"] = True
        context["ticket"] = review.ticket
        context["review_form"] = context.get("form")
        context["editing"] = True
        return context


class ReviewDeleteView(OwnerQuerySetMixin, DeleteView):
    """Delete a Review owned by the logged-in user (POST only)."""

    model = Review
    pk_url_kwarg = "review_id"
    success_url = reverse_lazy("users:my_posts")
    http_method_names = ["post"]

    def form_valid(self, form):
        """Delete the review and display a success message."""
        messages.success(self.request, "La critique a été supprimée avec succès.")
        return super().form_valid(form)
