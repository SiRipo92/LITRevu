from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from django.db import models


class Ticket(models.Model):
    """
    Placeholder for content a user wants to review.

   Extend this model later with fields like `title`, `description`, `image`,
   `time_created`, etc.
   """
    # Your Ticket model definition goes here
    pass


class Review(models.Model):
    """
    A review for a given ticket, authored by a user.

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

    def __str__(self):
        """Readable representation: '<user> follows <followed_user>'."""
        return f"{self.user.username} follows {self.followed_user.username}"
