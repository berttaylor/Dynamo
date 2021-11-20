import string
import time
import random
from django.utils import timezone

from django.db import models
from django.template.defaultfilters import slugify

from collaborations import constants as c
from dynamo.base.models import TimeStampedSoftDeleteBase
from users.utils import get_sentinel_user


class Collaboration(TimeStampedSoftDeleteBase):
    """
    Collaborations are the projects which belong to a group
    e.g. ‘Turning the Old Schoolyard into a Safe Space for Teenagers’
    """

    name = models.CharField(
        help_text="Give the Collaboration a name e.g. 'Charity Bake Sale'",
        max_length=100,
    )

    slug = models.SlugField(
        blank=True,
        help_text="Auto-generated slug for the Collaboration",
        max_length=150,
    )

    description = models.TextField(
        blank=True,
        help_text="Further details can be provided here",
        max_length=500,
        null=True,
    )

    created_by = models.ForeignKey(
        "users.User",
        help_text="User who created the collaboration",
        on_delete=models.SET(get_sentinel_user),
        related_name="collaborations_created",
    )

    related_group = models.ForeignKey(
        "groups.Group",
        help_text="The Group this collaboration belongs to",
        on_delete=models.CASCADE,
        related_name="collaborations",
    )

    @property
    def status(self) -> str | None:
        """Determines a collaborations status"""
        if self.percent_completed == 0:
            return c.COLLABORATION_STATUS_PLANNING
        elif self.percent_completed == 100:
            return c.COLLABORATION_STATUS_COMPLETED
        else:
            return c.COLLABORATION_STATUS_ONGOING

    @property
    def percent_completed(self) -> int:
        """
        Returns the completion percentage, according to how many tasks have been completed,
        and how many remain
        """
        tasks = CollaborationElement.objects.filter(collaboration=self, type=c.COLLABORATION_ELEMENT_TYPE_TASK)
        if not tasks:
            return 0
        completed_tasks = tasks.filter(completed_at__isnull=False)
        return int(completed_tasks.count() / tasks.count() * 100)

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
        if Collaboration.objects.filter(slug=slug).count() > 0:
            slug = "%s-%s" % (slug, str(time.time()).replace(".", ""))
        return slug

    def save(self, *args, **kwargs) -> None:
        """Override save to automate creation of some fields"""
        # Use _state.adding to detect if first save
        if self._state.adding:
            self.slug = self.generate_slug(self)
        super(Collaboration, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name_plural = "Collaborations"
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["name"]),
            models.Index(fields=["slug"]),
        ]


class CollaborationElement(TimeStampedSoftDeleteBase):
    """
    A CollaborationElement is either a Task or a Milestone. We use this table to simplify the joining
    of the two items into one list that shows both types of object together, ordered by their position.
    These can then be serialised/ordered/updated in a quick, and database-query-light way.

    A Task is a step which needs to be taken in order to reach the collaboration's goal.
    A Milestone is placed and displayed amongst the tasks at points where significant progress
    is made towards the end goal e.g. “Stage 1 Initial testing complete!”
    """

    reference = models.CharField(
        default="REF",
        null=False,
        max_length=255,
        help_text="An auto-generated task reference, used to assign task as prerequisates"
    )

    collaboration = models.ForeignKey(
        "Collaboration",
        help_text="The Collaboration this element belongs to",
        on_delete=models.CASCADE,
        related_name="elements",
    )

    position = models.PositiveSmallIntegerField(
        help_text="The position of the element (1 = 1st)",
    )

    type = models.CharField(
        choices=c.COLLABORATION_ELEMENT_TYPE_CHOICES,
        default=c.COLLABORATION_ELEMENT_TYPE_TASK,
        help_text="The type of the element",
        max_length=50,
    )

    name = models.CharField(
        help_text="A name for the task/milestone e.g. 'Make Contact with the Town Council / Stage 1 complete'",
        max_length=100,
    )

    description = models.TextField(
        blank=True,
        null=True,
        help_text="A further description of the task and what is required",
        max_length=500,
    )

    assigned_to = models.ForeignKey(
        "users.User",
        help_text="User who should complete the task",
        on_delete=models.SET(get_sentinel_user),
        related_name="tasks_assigned",
        blank=True,
        null=True,
    )

    prerequisites = models.ManyToManyField(
        "CollaborationElement",
        help_text="Tasks that must be completed before this task",
        related_name="dependant_tasks",
        blank=True,
    )

    tags = models.ManyToManyField(
        "CollaborationTaskTag",
        help_text="Tags showing certain properties that relate to multiple tasks e.g. 'Admin Task'",
        related_name="tasks",
        blank=True,
    )

    target_date = models.DateTimeField(
        help_text="A date by which the group should aim to reach this milestone",
        null=True,
        blank=True,
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp of when this task was completed.",
    )

    completed_by = models.ForeignKey(
        "users.User",
        help_text="User who completed the task/reached the milestone",
        on_delete=models.SET(get_sentinel_user),
        related_name="tasks_completed",
        blank=True,
        null=True,
    )

    completion_notes = models.TextField(
        blank=True,
        null=True,
        help_text="Any information relevant to the completion of this task. ",
        max_length=500,
    )

    @staticmethod
    def generate_ref(length, element_type) -> str:
        """Unique reference auto-generation function"""
        chars = string.ascii_uppercase + string.digits
        if element_type == c.COLLABORATION_ELEMENT_TYPE_TASK:
            ref_prefix = "TASK-"
        else:
            ref_prefix = "MILE-"
        ref_code = "".join(random.choice(chars) for _ in range(length))
        return ref_prefix + ref_code

    @property
    def status(self) -> str | None:
        """Determines a milestones status"""
        if self.type != c.COLLABORATION_ELEMENT_TYPE_MILESTONE:
            return None
        elif all(task.completed_at for task in self.prerequisites.all()):
            return c.MILESTONE_STATUS_REACHED
        elif self.target_date > timezone.now():
            return c.MILESTONE_STATUS_ON_TARGET
        else:
            return c.MILESTONE_STATUS_BEHIND_TARGET

    def set_prerequisites(self, *args, **kwargs) -> None:
        """
        Logic to set all of the prerequisites required to meet a milestone,
        and mark the milestone as reached (completed), if they are all complete.
        """
        # Check if there are another other milestones before this one
        if CollaborationElement.objects.filter(
                collaboration=self.collaboration,
                type=c.COLLABORATION_ELEMENT_TYPE_MILESTONE,
                position__lt=self.position
        ).exists():
            previous_milestone_position = CollaborationElement.objects.filter(
                collaboration=self.collaboration,
                type=c.COLLABORATION_ELEMENT_TYPE_MILESTONE,
                position__lt=self.position
            ).order_by('-position')[0].position
        else:
            previous_milestone_position = 0

        tasks = CollaborationElement.objects.filter(
            collaboration=self.collaboration,
            position__lt=self.position,
            position__gt=previous_milestone_position)\
            .order_by('position')

        self.prerequisites.set(tasks)

        return

    def save(self, *args, **kwargs) -> None:
        """
        Logic to update
        """
        # Add a reference number when a CollaborationElement is created
        if self._state.adding:
            self.reference = self.generate_ref(5, self.type)

        response = super(CollaborationElement, self).save(*args, **kwargs)

        if self.type == c.COLLABORATION_ELEMENT_TYPE_MILESTONE:
            self.set_prerequisites(self)
        else:
            # Check next milestone and mark as complete is needed
            pass

        return response

    def __str__(self):
        # Check if task/milestone has been completed
        complete = True if self.completed_at else False

        if self.type == c.COLLABORATION_ELEMENT_TYPE_TASK:
            # Tasks
            # If complete, give a string with the date
            if complete:
                if self.completion_notes:
                    return f" ☒ {self.name} (notes)"
                return f" ☒ {self.name}"

            # If not, check if assigned to anyone, and return an appropriate string.
            assigned_to = string.capwords(self.assigned_to.username) if self.assigned_to else None
            if assigned_to:
                return f" ☐ {self.name} ({assigned_to})"
            else:
                return f" ☐ {self.name}"
        else:
            # Milestones
            # Return a string presenting the number of tasks/complete and remaining
            prerequisite_tasks = self.prerequisites.filter(type=c.COLLABORATION_ELEMENT_TYPE_TASK)

            completed_prerequisite_tasks = prerequisite_tasks.filter(completed_at__isnull=False)

            return f"Milestone - {self.name} ({completed_prerequisite_tasks.count()} of {prerequisite_tasks.count()} complete)"

    class Meta:
        verbose_name_plural = "Elements"
        indexes = [
            models.Index(fields=["collaboration", "position"]),
            models.Index(fields=["collaboration"]),
            models.Index(fields=["position"]),
        ]
        ordering = ["collaboration", "-position"]


class CollaborationTaskTag(TimeStampedSoftDeleteBase):
    """
    A CollaborationTaskTag is a marker that can be placed on tasks with certain properties
    e.g. ‘Difficult’, 'Urgent', 'Needs Car'
    """

    name = models.CharField(
        help_text="A name for the Tag e.g. 'Task for Admin'",
        max_length=50,
    )

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name_plural = "Task Tags"
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["name"]),
        ]


class CollaborationFile(TimeStampedSoftDeleteBase):
    """
    A CollaborationFile is created for any files that are deemed useful for the collaboration.
    An example may be uploading a PDF once 'Design a poster for school concert' has been completed,
    allowing other users to see the end result. once uploaded, these can also be foreign key'ed to
    the relevant task, if appropriate
    """

    collaboration = models.ForeignKey(
        "Collaboration",
        help_text="The Collaboration this file belongs to",
        on_delete=models.CASCADE,
        related_name="files",
    )

    name = models.CharField(
        help_text="A name for the file e.g 'A4 Poster V1'",
        max_length=50,
    )

    format = models.CharField(
        help_text="The format of the file",
        choices=c.FILE_FORMAT_CHOICES,
        max_length=50,
    )

    # TODO : sort file uploads
    #  related_file = models.FileField(
    #     # The PrivateAssetStorage class extends the S3Boto with some overrides
    #     # (Sends to a private, separate DO space)
    #     storage=PrivateAssetStorage(),
    #     upload_to=build_image_storage_path,
    #     help_text="The file of the image. Please aim to keep this below 1mb in size.",
    #     )

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name_plural = "Files"
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["collaboration"]),
            models.Index(fields=["name"]),
        ]
