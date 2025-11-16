import io
import shutil
import tempfile

from PIL import Image
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from reviews.models import Ticket

User = get_user_model()

# Create an isolated temp MEDIA root for this test module
TEMP_MEDIA_ROOT = tempfile.mkdtemp(prefix="media-tests-")


def make_image_file(name="test.jpg", fmt="JPEG", size=(8, 8), color=(255, 0, 0)):
    """
    Build a tiny in-memory image and wrap it in SimpleUploadedFile so it behaves
    like a user-upload via <input type="file">.
    """
    bio = io.BytesIO()
    img = Image.new("RGB", size=size, color=color)
    img.save(bio, format=fmt)
    bio.seek(0)
    content_type = "image/jpeg" if fmt.upper() == "JPEG" else "image/png"
    return SimpleUploadedFile(name=name, content=bio.read(), content_type=content_type)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT, MEDIA_URL="/media/")
class TicketViewsTests(TestCase):
    """End-to-end view tests covering the ticket CRUD pages and related listings."""

    @classmethod
    def setUpTestData(cls):
        """Create two users shared by all tests."""
        cls.user = User.objects.create_user(username="alice", password="pass12345")
        cls.other = User.objects.create_user(username="bob", password="pass12345")

    @classmethod
    def tearDownClass(cls):
        """Remove the temporary MEDIA directory created for this module."""
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        """Authenticate as the main user for request flows requiring login."""
        self.client.force_login(self.user)

    # -------- feed --------
    def test_feed_lists_tickets_newest_first(self):
        """GET /flux/ : tickets should be ordered newest-first in the feed."""
        t1 = Ticket.objects.create(title="old", description="", user=self.user)
        t2 = Ticket.objects.create(title="new", description="", user=self.user)
        resp = self.client.get(reverse("reviews:feed"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "reviews/pages/feed.html")
        ids = [t.id for t in resp.context["tickets"]]
        self.assertEqual(ids, [t2.id, t1.id])

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
        self.assertEqual(resp.context["form"].instance.id, t.id)

    def test_edit_ticket_post_updates_title_and_keeps_image(self):
        """POST edit without delete flag updates fields but preserves the existing image."""
        t = Ticket.objects.create(title="Old", description="", user=self.user)
        # First attach an image
        self.client.post(
            reverse("reviews:edit_ticket", args=[t.id]),
            data={"title": "Old", "description": "d", "image": make_image_file()},
            follow=False,
        )
        t.refresh_from_db()
        self.assertTrue(bool(t.image))

        # Now update title, keep image (no delete_existing_image flag)
        resp = self.client.post(
            reverse("reviews:edit_ticket", args=[t.id]),
            data={"title": "New Title", "description": "d"},
            follow=False,
        )
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse("reviews:posts"))
        t.refresh_from_db()
        self.assertEqual(t.title, "New Title")
        self.assertTrue(bool(t.image))

    def test_edit_ticket_post_can_remove_existing_image(self):
        """POST edit with delete_existing_image removes the image and redirects."""
        t = Ticket.objects.create(
            title="With Img", description="", user=self.user, image=make_image_file()
        )
        resp = self.client.post(
            reverse("reviews:edit_ticket", args=[t.id]),
            data={"title": "With Img", "description": "", "delete_existing_image": "true"},
            follow=False,
        )
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse("reviews:posts"))
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
        self.assertRedirects(resp, reverse("reviews:posts"))
        self.assertFalse(Ticket.objects.filter(id=t.id).exists())

    # -------- my_posts --------
    def test_my_posts_only_shows_owned(self):
        """GET my_posts lists only the authenticated user's tickets."""
        mine = Ticket.objects.create(title="mine", description="", user=self.user)
        theirs = Ticket.objects.create(title="theirs", description="", user=self.other)
        resp = self.client.get(reverse("reviews:posts"))
        self.assertEqual(resp.status_code, 200)
        ids = [t.id for t in resp.context["tickets"]]
        self.assertIn(mine.id, ids)
        self.assertNotIn(theirs.id, ids)

    # -------- create_review (placeholder) --------
    def test_create_review_placeholder_renders(self):
        """GET create_review placeholder should render and attach the target ticket in context."""
        t = Ticket.objects.create(title="stub", description="", user=self.user)
        resp = self.client.get(reverse("reviews:create_review", args=[t.id]))
        self.assertEqual(resp.status_code, 200)
        # Placeholder template name you currently use:
        self.assertTemplateUsed(resp, "placeholders/create_review.html")
        self.assertEqual(resp.context["ticket"].id, t.id)
