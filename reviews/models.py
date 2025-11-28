"""Define models for Ticket and Review within Reviews app."""

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint


class Ticket(models.Model):
    """
    Placeholder for content a user wants to review.

    Fields:
    - title: Required name of the ticket to be created
    - description: Optional description of the ticket
    - user: Author of the ticket
    - image: Optional image associated to the ticket
    - time_created: Auto timestamp for when the ticket is created
    """

    DEFAULT_AUTHOR_LABEL = "Auteur inconnu"

    # Defines the data for a Ticket
    title = models.CharField(max_length=128)
    author = models.CharField(
        "Auteur",
        max_length=128,
        blank=True,
        help_text="Nom de l'auteur du livre ou de l'article (facultatif).",
    )
    description = models.TextField(max_length=2048, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tickets",
    )
    image = models.ImageField(
        upload_to="ticket_images/",
        blank=True,
        null=True,
    )
    time_created = models.DateTimeField(auto_now_add=True)

    @property
    def display_title(self) -> str:
        """Title used in the feed."""
        return self.title

    @property
    def display_author(self) -> str:
        """
        Return the author name, or a default French label if none is provided.
        """
        return (self.author or "").strip() or self.DEFAULT_AUTHOR_LABEL

    class Meta:
        """Django metadata options for the Ticket model."""

        verbose_name = "Ticket"
        verbose_name_plural = "Tickets"
        ordering = ['-time_created']

    def __str__(self):
        """Return a readable representation with title and author username."""
        return f"{self.title} (par {self.user.username})"


class Review(models.Model):
    """
    Represents a user's critique of a book or article.

    If posted in response to a Ticket, the (ticket, user) pair must be
    unique so each user can only review a given ticket once.

    Fields:
        ticket: ForeignKey to the Ticket being reviewed.
        rating: Integer 0–5 (inclusive), validated by Min/MaxValueValidator.
        headline: Short title or summary of the review.
        body: Optional long-form text content.
        user: Author of the review (FK to AUTH_USER_MODEL).
        time_created: Timestamp set on creation.
    """

    ticket = models.ForeignKey(
        to=Ticket,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    rating = models.PositiveSmallIntegerField(
        # validates that rating must be between 0 and 5
        validators=[MinValueValidator(0), MaxValueValidator(5)])
    headline = models.CharField(max_length=128)
    body = models.CharField(max_length=8192, blank=True)
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    time_created = models.DateTimeField(auto_now_add=True)

    @property
    def display_title(self) -> str:
        """Return the title used in the feed."""
        return self.headline

    class Meta:
        """Django metadata options for the Review model."""

        verbose_name = "Review"
        verbose_name_plural = "Reviews"
        ordering = ['-id']
        constraints = [
            UniqueConstraint(fields=['user', 'ticket'], name='unique_review_per_user_ticket'),
            models.UniqueConstraint(fields=["ticket"], name="unique_review_per_ticket")
        ]

    def __str__(self):
        """Return a readable representation with headlineand author."""
        return f"{self.headline} — {self.user}"
