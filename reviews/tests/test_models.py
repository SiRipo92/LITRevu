from django.contrib.auth import get_user_model
from django.test import TestCase
from reviews.models import Ticket

User = get_user_model()


class TicketModelTests(TestCase):
    def test_str_includes_title_and_username(self):
        u = User.objects.create_user(username="alice", password="pass")
        t = Ticket.objects.create(title="Book", description="", user=u)
        self.assertIn("Book", str(t))
        self.assertIn("alice", str(t))

    def test_ordering_newest_first(self):
        u = User.objects.create_user(username="alice", password="pass")
        t1 = Ticket.objects.create(title="old", description="", user=u)
        t2 = Ticket.objects.create(title="new", description="", user=u)
        ordered = list(Ticket.objects.all())  # respects Meta.ordering
        self.assertEqual([t.id for t in ordered], [t2.id, t1.id])
