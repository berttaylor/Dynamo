import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Custom User model, allowing for further fields to be added at a later date, if required.

    NOTE: Subclassing AbstractUser also subclasses AbstractBaseUser, and both
    come with their own additional fields such as is_active and last_login.
    """

    # Replace the ID field with a UUID for better security
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    first_name = None
    last_name = None

    email = models.EmailField(_("email address"), unique=True)

    def __str__(self):
        return str(self.username)

    class Meta:
        verbose_name_plural = "Users"
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["username"]),
        ]
