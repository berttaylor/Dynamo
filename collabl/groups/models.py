import time

from django.db import models
from django.template.defaultfilters import slugify

from collabl.base.models import TimeStampedSoftDeleteBase
from collabl.storages import group_based_upload_to
from groups import constants as c
from users.models import User
from users.utils import get_sentinel_user
from .managers import MembershipManager


class Group(TimeStampedSoftDeleteBase):
    """
    Groups are environments where users with a common cause can chat, and create Collaborations.
    """

    name = models.CharField(
        help_text="A name for the group e.g. 'Riverdale Parents Group'",
        max_length=100,
    )

    slug = models.SlugField(
        blank=True,
        help_text="Auto-generated slug for the Group",
        max_length=150,
    )

    description = models.TextField(
        help_text="A description of the group and it's causes",
        max_length=500,
    )

    created_by = models.ForeignKey(
        "users.User",
        help_text="User who created the group",
        on_delete=models.SET(get_sentinel_user),
        related_name="groups_created",
        blank=True,
    )

    members = models.ManyToManyField(
        "users.User",
        through="Membership",
        through_fields=('group', 'user'),
        help_text="Users who are members of the Group",
        blank=True,
    )

    __saved_profile_image = None

    profile_image = models.FileField(
        upload_to=group_based_upload_to,
        help_text="Profile Image for the group. Please aim to keep this below 1mb in size.",
        null=True,
        blank=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__saved_profile_image = self.profile_image

    @property
    def active_member_count(self):
        """Returns the number of active group members"""
        return self.memberships.all().filter(status__in=[c.MEMBERSHIP_STATUS_CURRENT, c.MEMBERSHIP_STATUS_ADMIN]).count()

    @property
    def subscriber_count(self):
        """Returns the number of group subscribers"""
        return self.memberships.all().filter(is_subscribed=True).count()

    @property
    def admin_count(self):
        """Returns the number of group admins"""
        return self.memberships.all().filter(status=c.MEMBERSHIP_STATUS_ADMIN).count()

    @property
    def current_users(self):
        """Returns a queryset of users with pending memberships"""
        return User.objects.filter(pk__in=self.memberships.all().filter(status=c.MEMBERSHIP_STATUS_CURRENT).values_list('user', flat=True))

    @property
    def admin_users(self):
        """Returns a queryset of group admins"""
        return User.objects.filter(pk__in=self.memberships.all().filter(status=c.MEMBERSHIP_STATUS_ADMIN).values_list('user', flat=True))

    @property
    def pending_users(self):
        """Returns a queryset of users with pending memberships"""
        return User.objects.filter(pk__in=self.memberships.all().filter(status=c.MEMBERSHIP_STATUS_PENDING).values_list('user', flat=True))

    @property
    def short_description(self):
        """Returns the description in a format that is always 75 characters or less"""
        return (
            self.description
            if len(self.description) < 75
            else (self.description[:75] + "...")
        )

    @staticmethod
    def generate_slug(self) -> str:
        """Auto-generates unique slug function"""
        slug = slugify(self.name[:80])
        # Check it's unique, if it isn't, make it so
        if Group.objects.filter(slug=slug).count() > 0:
            slug = "%s-%s" % (slug, str(time.time()).replace(".", ""))
        return slug

    def save(self, *args, **kwargs) -> None:
        """
        Override save to:
        1) If adding, automate creation of slug
        2) If changing profile image, delete the old one from storage
        """

        # Use _state.adding to detect if first save
        if self._state.adding:
            self.slug = self.generate_slug(self)

        super(Group, self).save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        """We delete the profile image from storage"""
        self.profile_image.delete(save=False)
        super().delete()

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name_plural = "Groups"
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["name"]),
            models.Index(fields=["slug"]),
        ]
        ordering = ("created_at",)


class Membership(TimeStampedSoftDeleteBase):
    """
    Memberships are created when a user requests to join a group.
    They can be approved/denied by the administrators of the relevant group.
    """

    # # Default manager, unedited.
    objects = models.Manager()
    custom_manager = (
        # Custom manager with helper methods for filtering by status
        MembershipManager()
    )

    user = models.ForeignKey(
        "users.User",
        on_delete=models.SET(get_sentinel_user),
        related_name="memberships",
    )

    group = models.ForeignKey(
        "Group",
        on_delete=models.CASCADE,
        related_name="memberships",
    )

    status = models.CharField(
        blank=True,
        choices=c.MEMBERSHIP_STATUS_CHOICES,
        default=c.MEMBERSHIP_STATUS_PENDING,
        help_text="The status of the membership",
        max_length=100,
    )

    is_subscribed = models.BooleanField(
        help_text="Whether the user gets email updates",
        default=False,
    )

    updated_by = models.ForeignKey(
        "users.User",
        help_text="User who handled the request",
        on_delete=models.CASCADE,
        related_name="memberships_updated",
        blank=True,
        null=True,
    )

    class Meta:
        unique_together = ("user", "group")
        verbose_name_plural = "Memberships"
        ordering = ("-created_at", "-updated_at")

    def __str__(self):
        return f"[{self.status}] {self.user.first_name}"


class GroupAnnouncement(TimeStampedSoftDeleteBase):
    """
    Announcements are important communications made by admins, and displayed atop the Groups page, for all to see

    An example could be that the group is not accepting new members right now, or a clarification of group rules
    """

    user = models.ForeignKey(
        "users.User",
        help_text="User who wrote the announcement",
        on_delete=models.SET(get_sentinel_user),
        related_name="group_announcements",
    )

    group = models.ForeignKey(
        "groups.Group",
        help_text="The group where the announcement was written",
        on_delete=models.CASCADE,
        related_name="group_announcements",
    )

    title = models.TextField(help_text="The title of the announcement")

    body = models.TextField(help_text="The announcement itself")

    def __str__(self):
        return f"{self.group}'s announcement: '{self.title}'"

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Group Announcements"

        indexes = [
            models.Index(fields=["group"]),
            models.Index(fields=["created_at"]),
        ]
