import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from collabl.storages import user_image_upload_to
from users.managers import CustomUserManager


class User(AbstractUser):
    """
    Custom User model, allowing for further fields to be added at a later date, if required.

    NOTE: Subclassing AbstractUser also subclasses AbstractBaseUser, and both
    come with their own additional fields such as is_active and last_login.
    """

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    username = None

    # Replace the ID field with a UUID for better security
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)

    email = models.EmailField(_("email address"), unique=True)

    image = models.FileField(
        upload_to=user_image_upload_to,
        help_text="Image for your profile (optional)",
        null=True,
        blank=True,
    )

    def __str__(self):
        return str(self.first_name + " " + self.last_name)

    class Meta:
        verbose_name_plural = "Users"
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["first_name"]),
        ]
