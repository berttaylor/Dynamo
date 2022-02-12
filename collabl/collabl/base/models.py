import uuid

from django.db import models

from .managers import TimeStampedSoftDeleteManager


class TimeStampedBase(models.Model):
    """
    Provides a base inherited by all models in the system.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # When object is created
    created_at = models.DateTimeField(
        auto_now_add=True,
        null=True,
        help_text="Timestamp of when this object was first created.",
    )

    # When object is updated in the future, after being created
    updated_at = models.DateTimeField(
        auto_now=True,
        null=True,
        help_text="Timestamp of when this object was last updated.",
    )

    class Meta:
        abstract = True


class TimeStampedSoftDeleteBase(TimeStampedBase):
    """
    Extends base model for deletion.
    """

    # Custom managers returns either only non soft-deleted items, or everything
    # Will default to true if **kwarg is missing
    objects = TimeStampedSoftDeleteManager(alive_only=False)
    alive_objects = TimeStampedSoftDeleteManager(alive_only=True)

    # Timestamp when object is soft delete - if this field is None, it hasn't been deleted
    deleted_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Timestamp of when (if) this object was soft deleted.",
    )

    class Meta:
        abstract = True
