from django.db import models
from django.utils import timezone

"""
Soft delete managers
"""


class TimeStampedSoftDeleteManager(models.Manager):
    """
    Manager returns 'alive_only' as true or false depending on what arguments
    the model is instantiated with.
    """

    def __init__(self, *args, **kwargs):
        """
        Manager is instantiated with a keyword argument that specifies
        if we want to see only items that haven't been soft deleted,
        or if we want to see everything. If there's no **kwarg, default
        to True.
        """
        self.alive_only = kwargs.pop("alive_only", True)
        super().__init__(*args, **kwargs)

    def get_queryset(self):
        """
        If we only want 'alive' results, we call .filter to only return
        database rows where deleted_at evaluates to None. Otherwise we just
        return everything.
        """
        if self.alive_only:
            return TimeStampedSoftDeleteQueryset(self.model).filter(deleted_at=None)
        return TimeStampedSoftDeleteQueryset(self.model)

    def published(self):
        return self.get_queryset().published()

    def active(self):
        return self.get_queryset().active()

    def expired(self):
        return self.get_queryset().expired()


class TimeStampedSoftDeleteQueryset(models.QuerySet):
    def alive(self):
        """Helper to get only the alive results."""
        return self.filter(deleted_at=None)

    def dead(self):
        """Helper to get only the dead results."""
        return self.exclude(deleted_at=None)

    def published(self):
        """Returns all surveys that are published"""
        return self.filter(
            published=True,
        )

    def active(self):
        """Returns all surveys that are published, and have a closing date of
        greater than or equal to today's date, in ascending order."""
        return self.filter(
            published=True,
            close_date_time__gte=timezone.now().today(),
            open_date_time__lte=timezone.now().today(),
        )

    def expired(self):
        """Returns all surveys that are published, and have a closing date of
        less than today's date, in descending order."""
        return self.filter(
            published=True,
            close_date_time__lte=timezone.now().today(),
        )
