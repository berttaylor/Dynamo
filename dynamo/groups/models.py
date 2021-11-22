import time

from django.db import models
from django.template.defaultfilters import slugify
from groups import constants as c
from users.utils import get_sentinel_user

from dynamo.base.models import TimeStampedSoftDeleteBase


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

    admins = models.ManyToManyField(
        "users.User",
        help_text="Users with Administrative Rights",
        related_name="admin_positions",
        blank=True,
    )

    members = models.ManyToManyField(
        "users.User",
        help_text="Users who are members of the Group",
        related_name="memberships",
        blank=True,
    )

    subscribers = models.ManyToManyField(
        "users.User",
        help_text="Users who receive email updates from the Group",
        related_name="subscriptions",
        blank=True,
    )

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
        """Override save to automate creation of some fields"""
        # Use _state.adding to detect if first save
        if self._state.adding:
            self.slug = self.generate_slug(self)
        super(Group, self).save(*args, **kwargs)

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


class GroupJoinRequest(TimeStampedSoftDeleteBase):
    """
    GroupJoinRequest are created when a user requests to join a group.
    They can be approved/denied by the administrators of the relevant group.
    """

    user = models.ForeignKey(
        "users.User",
        help_text="The User who made the request",
        on_delete=models.SET(get_sentinel_user),
        related_name="group_join_requests_made",
    )

    group = models.ForeignKey(
        "Group",
        help_text="The Group which the User would like to join",
        on_delete=models.CASCADE,
        related_name="join_requests",
    )

    status = models.CharField(
        blank=True,
        choices=c.REQUEST_STATUS_CHOICES,
        default=c.REQUEST_STATUS_PENDING,
        help_text="The status of the request",
        max_length=100,
    )

    handled_by = models.ForeignKey(
        "users.User",
        help_text="User who handled the request",
        on_delete=models.CASCADE,
        related_name="group_join_requests_handled",
        blank=True,
        null=True,
    )

    handled_date = models.DateTimeField(
        blank=True,
        help_text="Timestamped when the request is handled",
        null=True,
    )

    class Meta:
        unique_together = ("user", "group")
        verbose_name_plural = "Join Requests"
        ordering = ("created_at",)

    def __str__(self):
        return f"[{self.status}] {self.user.username}"


class GroupProfileImage(TimeStampedSoftDeleteBase):
    """
    Images stored for the Groups' main profile page
    """

    # TODO : sort file uploads
    #  related_file = models.FileField(
    #     # The PrivateAssetStorage class extends the S3Boto with some overrides
    #     # (Sends to a private, separate DO space)
    #     storage=PrivateAssetStorage(),
    #     upload_to=build_image_storage_path,
    #     help_text="The file of the image. Please aim to keep this below 1mb in size.",
    #     )

    alt_text = models.CharField(
        null=False,
        max_length=100,
        help_text="The full alt text of the image for accessibility purposes.",
    )

    def __str__(self):
        return self.alt_text

    class Meta:
        verbose_name_plural = "Profile Images"
