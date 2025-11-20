from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class User(AbstractUser):
    """Custom user model for LITRevu."""
    pass


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
