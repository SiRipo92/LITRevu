from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
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
    # Defines the data for a Ticket
    title = models.CharField(max_length=128)
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

    class Meta:
        verbose_name = "Ticket"
        verbose_name_plural = "Tickets"
        ordering = ['-time_created']

    def __str__(self):
        return f"{self.title} (par {self.user.username})"


class Review(models.Model):
    """
    A user's critique of a book/article. If posted in response to a
    Ticket, the (ticket, user) pair must be unique so each user can
    only review a given ticket once.

    Fields:
        ticket: ForeignKey to the Ticket being reviewed.
        rating: Integer 0–5 (inclusive), validated by Min/MaxValueValidator.
        headline: Short title/summary of the review.
        body: Optional long-form text content.
        user: Author of the review (FK to AUTH_USER_MODEL).
        time_created: Timestamp set on creation.
    """
    ticket = models.ForeignKey(to=Ticket, on_delete=models.CASCADE)
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
        """Title used in the feed."""
        return self.headline

    class Meta:
        verbose_name = "Review"
        verbose_name_plural = "Reviews"
        ordering = ['-id']
        constraints = [
            UniqueConstraint(fields=['user', 'ticket'], name='unique_review_per_user_ticket')
        ]

    def __str__(self):
        return f"{self.headline} — {self.user}"


class UserFollows(models.Model):
    """
    Represents a user following another user (directed edge).

    The (user, followed_user) pair is constrained to be unique to prevent
    duplicate follow rows.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="following",
    )
    followed_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="followers",
    )

    class Meta:
        """Enforce uniqueness of a (follower, followed) pair."""
        unique_together = ("user", "followed_user")
        verbose_name = "User Follow"
        verbose_name_plural = "User Follows"

    def __str__(self):
        """Readable representation: '<user> follows <followed_user>'."""
        return f"{self.user.username} follows {self.followed_user.username}"
