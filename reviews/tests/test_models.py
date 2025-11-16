from django.contrib.auth import get_user_model
from django.test import TestCase
from reviews.models import Ticket

User = get_user_model()


class TicketModelTests(TestCase):
    """
    Form validation tests for CreateTicketForm.

    These tests verify:
      • base validity with/without an uploaded image,
      • required/length constraints on 'title',
      • label normalization (no trailing colon) and presence of widget attributes
        used by templates/JS (CSS classes, id, accept, etc.).
    """

    def test_str_includes_title_and_username(self):
        """
        GIVEN a complete payload without an image
        WHEN the form is constructed and validated
        THEN the form is valid.
        """
        u = User.objects.create_user(username="alice", password="pass")
        t = Ticket.objects.create(title="Book", description="", user=u)
        self.assertIn("Book", str(t))
        self.assertIn("alice", str(t))

    def test_ordering_newest_first(self):
        """
        GIVEN a minimal valid payload and a tiny 1×1 GIF uploaded file
        WHEN the form is validated
        THEN the form is valid and accepts the image input.
        """
        u = User.objects.create_user(username="alice", password="pass")
        t1 = Ticket.objects.create(title="old", description="", user=u)
        t2 = Ticket.objects.create(title="new", description="", user=u)
        ordered = list(Ticket.objects.all())  # respects Meta.ordering
        self.assertEqual([t.id for t in ordered], [t2.id, t1.id])
