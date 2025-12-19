"""Tests for ticket and review views (ticket CRUD, review CRUD, and feed pages)."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from reviews.models import Review, Ticket

User = get_user_model()


class TicketViewsTests(TestCase):
    """End-to-end view tests covering the ticket CRUD pages and related listings."""

    @classmethod
    def setUpTestData(cls):
        """Create two users shared by all tests."""
        cls.user = User.objects.create_user(username="alice", password="pass12345")
        cls.other = User.objects.create_user(username="bob", password="pass12345")

    def setUp(self):
        """Authenticate as the main user for request flows requiring login."""
        self.client.force_login(self.user)

    # -------- create_ticket --------
    def test_create_ticket_get_renders_form(self):
        """GET create form renders the expected template."""
        resp = self.client.get(reverse("reviews:create_ticket"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "reviews/forms/submit_ticket.html")

    def test_create_ticket_post_creates_and_redirects(self):
        """Valid POST creates a ticket then redirects to the feed."""
        resp = self.client.post(
            reverse("reviews:create_ticket"),
            data={"title": "Via view", "description": "body"},
            follow=False,
        )
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse("reviews:feed"))
        self.assertTrue(Ticket.objects.filter(title="Via view", user=self.user).exists())

    def test_create_ticket_invalid_keeps_form(self):
        """Invalid POST (missing title) re-renders the form with errors."""
        resp = self.client.post(
            reverse("reviews:create_ticket"),
            data={"title": "", "description": "no title"},
            follow=False,
        )
        self.assertEqual(resp.status_code, 200)  # stays on form
        self.assertTemplateUsed(resp, "reviews/forms/submit_ticket.html")
        self.assertFalse(Ticket.objects.filter(description="no title").exists())

    # -------- edit_ticket --------
    def test_edit_ticket_get_prefills_and_sets_editing_flag(self):
        """GET edit page should prefill the form and expose an 'editing' flag in context."""
        t = Ticket.objects.create(title="T", description="D", user=self.user)
        resp = self.client.get(reverse("reviews:edit_ticket", args=[t.id]))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.context.get("editing"))
        self.assertTemplateUsed(resp, "reviews/forms/submit_ticket.html")
        self.assertEqual(resp.context["ticket_form"].instance.id, t.id)

    def test_edit_ticket_post_can_remove_existing_image(self):
        """POST edit with delete_existing_image removes the image and redirects."""
        t = Ticket.objects.create(
            title="With Img",
            description="",
            user=self.user,
            image="ticket_images/dummy.jpg",  # simple fake path, no real file needed
        )
        resp = self.client.post(
            reverse("reviews:edit_ticket", args=[t.id]),
            data={
                "title": "With Img",
                "description": "",
                "delete_existing_image": "true",
            },
            follow=False,
        )
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse("users:my_posts"))
        t.refresh_from_db()
        self.assertFalse(bool(t.image))

    def test_edit_ticket_404_for_non_owner(self):
        """Non-owners should get 404 when attempting to edit someone else's ticket."""
        t = Ticket.objects.create(title="Not yours", description="", user=self.other)
        resp = self.client.get(reverse("reviews:edit_ticket", args=[t.id]))
        self.assertEqual(resp.status_code, 404)

    # -------- delete_ticket --------
    def test_delete_ticket_removes_and_redirects(self):
        """POST delete removes the ticket and redirects to 'posts'."""
        t = Ticket.objects.create(title="Delete me", description="", user=self.user)
        resp = self.client.post(reverse("reviews:delete_ticket", args=[t.id]))
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse("users:my_posts"))
        self.assertFalse(Ticket.objects.filter(id=t.id).exists())


class ReviewAndFeedViewsTests(TestCase):
    """Tests for feed and review-related views.

    Covers:
    - feed
    - my_posts
    - create_review (standalone + response mode)
    - edit_review
    - delete_review.
    """

    @classmethod
    def setUpTestData(cls):
        """Create shared users used across review/feed view tests."""
        cls.user = User.objects.create_user(username="ivy", password="StrongPassw0rd!")
        cls.other = User.objects.create_user(username="john", password="password123")

    def setUp(self):
        """Log in the main user and create a base ticket and review."""
        # Auth user
        self.client.force_login(self.user)

        # Base ticket + review
        self.ticket = Ticket.objects.create(
            title="Book",
            description="A desc",
            user=self.user,
        )

        self.review = Review.objects.create(
            headline="Good",
            body="Nice",
            rating=4,
            user=self.user,
            ticket=self.ticket,
        )

        # URLs grouped like in views.py
        self.urls = {
            "feed": reverse("reviews:feed"),
            "my_posts": reverse("users:my_posts"),

            "create_review_standalone": reverse("reviews:create_review"),
            "create_review_response": reverse("reviews:create_review_for_ticket", args=[self.ticket.id]),

            "edit_review": reverse("reviews:edit_review", args=[self.review.id]),
            "delete_review": reverse("reviews:delete_review", args=[self.review.id]),
        }

    # ------------------------
    # FEED AND POSTS
    # ------------------------

    def test_feed_shows_tickets_and_reviews(self):
        """Feed view returns at least one item in the 'feed_items' context list."""
        resp = self.client.get(self.urls["feed"])
        self.assertEqual(resp.status_code, 200)
        self.assertIn("feed_items", resp.context)
        self.assertGreaterEqual(len(resp.context["feed_items"]), 1)

    # ------------------------
    # CREATE REVIEW — RESPONSE MODE
    # ------------------------

    def test_create_review_response_mode_get(self):
        """GET create_review_for_ticket renders response mode with the target ticket."""
        ticket = Ticket.objects.create(title="New", description="Ticket", user=self.other)
        url = reverse("reviews:create_review_for_ticket", args=[ticket.id])

        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.context["is_response_mode"])
        self.assertEqual(resp.context["ticket"].id, ticket.id)

    # ------------------------
    # CREATE REVIEW — STANDALONE MODE
    # ------------------------

    def test_create_review_standalone_get(self):
        """GET create_review shows standalone mode with ticket and review forms."""
        resp = self.client.get(self.urls["create_review_standalone"])
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.context["is_response_mode"])
        self.assertIn("ticket_form", resp.context)
        self.assertIn("review_form", resp.context)

    def test_create_review_standalone_post_creates_ticket_and_review(self):
        """Valid POST creates both a new Ticket and a new Review for the user."""
        resp = self.client.post(
            self.urls["create_review_standalone"],
            data={
                # Ticket section
                "title": "New Ticket",
                "description": "New Desc",
                # Review section
                "headline": "Solid",
                "rating": 4,
                "body": "Enjoyed it",
            },
        )
        self.assertRedirects(resp, reverse("reviews:feed"))

        self.assertEqual(Ticket.objects.count(), 2)   # original + new
        self.assertEqual(Review.objects.count(), 2)   # original + new

        new_ticket = Ticket.objects.latest("id")
        new_review = Review.objects.latest("id")

        self.assertEqual(new_ticket.user, self.user)
        self.assertEqual(new_review.ticket, new_ticket)
        self.assertEqual(new_review.user, self.user)

    # ------------------------
    # EDIT REVIEW
    # ------------------------

    def test_edit_review_get_displays_prefilled_form(self):
        """GET edit_review returns a prefilled form in response mode."""
        resp = self.client.get(self.urls["edit_review"])
        self.assertEqual(resp.status_code, 200)
        form = resp.context["review_form"]
        self.assertEqual(form.instance.id, self.review.id)
        self.assertTrue(resp.context["is_response_mode"])

    def test_edit_review_wrong_user_gets_404(self):
        """Editing another user's review should return a 404 response."""
        # Create a separate ticket for the other user's review
        other_ticket = Ticket.objects.create(
            title="Second ticket",
            description="",
            user=self.other,
        )

        other_review = Review.objects.create(
            headline="Other review",
            body="Body",
            rating=3,
            user=self.other,
            ticket=other_ticket,
        )

        url = reverse("reviews:edit_review", args=[other_review.id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    # ------------------------
    # DELETE REVIEW
    # ------------------------

    def test_delete_review_post_redirects_and_deletes(self):
        """POST delete_review deletes the review and redirects to my_posts."""
        resp = self.client.post(self.urls["delete_review"])
        self.assertRedirects(resp, reverse("users:my_posts"))
        self.assertFalse(Review.objects.filter(id=self.review.id).exists())

    def test_delete_review_wrong_user_returns_404(self):
        """Deleting another user's review via POST should return HTTP 404."""
        other_ticket = Ticket.objects.create(title="X", description="Y", user=self.other)
        other_review = Review.objects.create(
            headline="Bad",
            body="Nope",
            rating=1,
            user=self.other,
            ticket=other_ticket,
        )
        url = reverse("reviews:delete_review", args=[other_review.id])

        resp = self.client.post(url)

        self.assertEqual(resp.status_code, 404)
