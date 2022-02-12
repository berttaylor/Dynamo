from django.db import models
from users.utils import get_sentinel_user

from collabl.base.models import TimeStampedBase


class FAQCategory(TimeStampedBase):
    """
    Categories of FAQ questions. e.g. Technical
    These are used to sort the questions on the front end.
    """

    name = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        help_text="The title of the category.",
    )

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "FAQ Categories"

        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["created_at"]),
        ]


class FAQ(TimeStampedBase):
    """
    Frequently Asked Questions - These will be added as required to
    address any issues where users often need assistance or information.
    """

    category = models.ForeignKey(
        "FAQCategory",
        help_text="The category of the FAQ Question",
        on_delete=models.SET_NULL,
        related_name="questions",
        null=True,
    )

    question = models.TextField(help_text="The question")

    answer = models.TextField(help_text="The answer to the question")

    position = models.PositiveSmallIntegerField(
        help_text="The position in which the question should be displayed "
        "within its category section - 1 = 1st",
    )

    def __str__(self):
        return str(self.question)

    class Meta:
        ordering = ["question"]
        verbose_name_plural = "FAQ Questions"

        indexes = [
            models.Index(fields=["question"]),
        ]


class SupportMessage(TimeStampedBase):
    """
    This stores any support messages sent to the system admin (me).
    """

    name = models.CharField(
        help_text="Name of the person sending the message",
        max_length=100,
    )

    email = models.EmailField(
        help_text="The email address that I should reply to",
    )

    related_user_account = models.ForeignKey(
        "users.User",
        help_text="The user account, if the user was logged in",
        on_delete=models.SET(get_sentinel_user),
        related_name="support_messages_sent",
        null=True,
        blank=True,
    )

    message = models.TextField(
        help_text="Please describe the issue in as much detail as possible"
    )

    read = models.BooleanField(
        default=False, help_text="whether or not the message has been read"
    )

    def __str__(self):
        return f"Support Message from {self.name}"

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Support Messages"

        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["created_at"]),
        ]
