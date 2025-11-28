"""Tests for the Ticket model behaviour."""

from django.contrib.auth import get_user_model
from django.test import TestCase

from reviews.models import Ticket

User = get_user_model()


class TicketModelTests(TestCase):
    """Tests for Ticket string representation and default ordering."""

    def test_str_includes_title_and_username(self):
        """Test that __str__ includes the ticket title and username.

        GIVEN a Ticket instance created for a user,
        WHEN str() is called on the Ticket,
        THEN the resulting string contains both the title and the username.
        """
        u = User.objects.create_user(username="alice", password="pass")
        t = Ticket.objects.create(title="Book", description="", user=u)
        self.assertIn("Book", str(t))
        self.assertIn("alice", str(t))

    def test_ordering_newest_first(self):
        """Test that Ticket objects are ordered from newest to oldest.

        GIVEN two Ticket instances created sequentially,
        WHEN all Ticket objects are retrieved,
        THEN the most recently created Ticket appears first.
        """
        u = User.objects.create_user(username="alice", password="pass")
        t1 = Ticket.objects.create(title="old", description="", user=u)
        t2 = Ticket.objects.create(title="new", description="", user=u)
        ordered = list(Ticket.objects.all())  # respects Meta.ordering
        self.assertEqual([t.id for t in ordered], [t2.id, t1.id])
