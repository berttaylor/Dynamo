from django.db import models


# Create your models here.
from dynamo.base.models import TimeStampedSoftDeleteBase
from users.utils import get_sentinel_user


class Message(TimeStampedSoftDeleteBase):
    """
    Chat messages on a collaboration/group pages are stored here.

    Group messages are saved with a group, collaboration messages are saved with a collaboration (only)

    There are not intended to be viewed together, but rather are filtered by either group or collaboration.
    """

    user = models.ForeignKey(
        "users.User",
        help_text="User who wrote the message",
        on_delete=models.SET(get_sentinel_user),
        related_name="collaboration_chat_messages",
    )

    group = models.ForeignKey(
        "groups.Group",
        help_text="The group where the message was written",
        on_delete=models.CASCADE,
        related_name="chat_messages",
        blank=True,
        null=True,
    )

    collaboration = models.ForeignKey(
        "collaborations.Collaboration",
        help_text="The Collaboration this message belongs to - blank if it is a general group message",
        on_delete=models.CASCADE,
        related_name="chat_messages",
        blank=True,
        null=True,
    )

    message = models.TextField(
        help_text="The message itself"
    )

    def __str__(self):
        return f"{self.created_at:[ %d%b'%y %I:%M%p ]} {self.user}: '{self.message}'"

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Chat Messages"

        indexes = [
            models.Index(fields=["created_at"]),
        ]

