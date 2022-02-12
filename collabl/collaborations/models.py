import random
import string
import time

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import F
from django.template.defaultfilters import slugify
from django.utils import timezone

from collaborations import constants as c
from collabl.base.models import TimeStampedSoftDeleteBase
from collabl.storages import collaboration_based_upload_to, collaboration_file_upload_to


def get_sentinel_user():
    """
    We use this function to set a user named "deleted" as the foreign key when a user who has
    foreign key relationships with another models is deleted
    """
    return get_user_model().objects.get_or_create(email="deleted@deleted.com")[0]


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

    image = models.FileField(
        upload_to=collaboration_based_upload_to,
        help_text="Image for the collaboration. Please aim to keep this below 1mb in size.",
        null=True,
        blank=True,
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
    def number_of_tasks(self) -> int:
        """
        Gets the total number of tasks
        """
        return CollaborationTask.objects.filter(collaboration=self).count()

    @property
    def number_of_tasks_completed(self) -> int:
        """
        Gets the total number of tasks completed
        """
        return CollaborationTask.objects.filter(
            collaboration=self, completed_at__isnull=False
        ).count()

    @property
    def number_of_milestones(self) -> int:
        """
        Gets the total number of milestones
        """
        return CollaborationMilestone.objects.filter(collaboration=self).count()

    @property
    def number_of_elements(self) -> int:
        """
        Gets the total number of tasks and milestones
        IMPORTANT: Used for ordering
        """
        return self.number_of_tasks + self.number_of_milestones

    @property
    def percent_completed(self) -> int:
        """
        Returns the completion percentage, according to how many tasks have been completed,
        and how many remain
        """
        tasks = CollaborationTask.objects.filter(collaboration=self)
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
        ordering = ["-created_at"]


class CollaborationTask(TimeStampedSoftDeleteBase):
    """
    A Task is a step which needs to be taken in order to reach the collaboration's goal.
    """

    def __init__(self, *args, **kwargs):
        """
        We override the init method to store a copy of the position when the class is instantiated
        This allows us to easily check whether the user's request is changing the position, and then take
        the actions required to ensure that all related objects in the db are updated.
        """
        super().__init__(*args, **kwargs)
        self.__original_position = self.position

    position = models.PositiveSmallIntegerField(
        help_text="The position of the element (1 = 1st)", blank=True
    )

    __original_position = None

    reference = models.CharField(
        default="REF",
        null=False,
        max_length=255,
        help_text="An auto-generated task reference, used to assign task as prerequisites",
    )

    collaboration = models.ForeignKey(
        "Collaboration",
        help_text="The Collaboration this element belongs to",
        on_delete=models.CASCADE,
        related_name="tasks",
    )

    name = models.CharField(
        help_text="A name for the task e.g. 'Make Contact with the Town Council'",
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
        "CollaborationTask",
        help_text="Tasks that must be completed before this task",
        related_name="dependant_tasks",
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

    file = models.FileField(
        upload_to=collaboration_file_upload_to,
        help_text="File related to the task. Please aim to keep this below 5mb in size.",
        null=True,
        blank=True,
    )

    prompt_for_details_on_completion = models.BooleanField(
        help_text="Whether the user who completes the task should be prompted to enter further details",
        default=False,
    )

    @staticmethod
    def generate_ref(length) -> str:
        """Unique reference auto-generation function"""
        chars = string.ascii_uppercase + string.digits
        ref_prefix = "TASK-"
        ref_code = "".join(random.choice(chars) for _ in range(length))
        return ref_prefix + ref_code

    @property
    def next_milestone(self):
        """Gets the next milestone"""
        if CollaborationMilestone.objects.filter(
            collaboration=self.collaboration, position__gt=self.position
        ).exists():
            return CollaborationMilestone.objects.filter(
                collaboration=self.collaboration, position__gt=self.position
            ).order_by("position")[0]
        else:
            return None

    def insert(self):
        """
        If the task has been added in between other elements, then we will need to reorder everything
        afterwards, by adding 1 to their position. We use an F expression, rather than looping,
        as this results in a single db query.
        """
        CollaborationTask.objects.filter(
            collaboration=self.collaboration, position__gte=self.position
        ).update(position=F("position") + 1)
        CollaborationMilestone.objects.filter(
            collaboration=self.collaboration, position__gte=self.position
        ).update(position=F("position") + 1)
        return

    def reposition(self):
        """
        If moving to a higher position, we target all elements with a position greater than the
        '__original_position' of this task, but less than or equal to the new position of this task. from this
        queryset, we subtract '1' from the position column, making room for our task, and keeping the rest in order.
        We use an F expression, rather than looping, as this results in a single db query.
        """

        if self.position > self.__original_position:
            CollaborationTask.objects.filter(
                collaboration=self.collaboration,
                position__gt=self.__original_position,
                position__lte=self.position,
            ).update(position=F("position") - 1)
            CollaborationMilestone.objects.filter(
                collaboration=self.collaboration,
                position__gt=self.__original_position,
                position__lte=self.position,
            ).update(position=F("position") - 1)

        """
        If moving to a lower position, we target all elements with a position lower than the
        '__original_position' of this task, but greater than or equal to the new position of this task. from
        this queryset, we add '1' to the position column, making room for our task, and keeping the rest in
        order. We use an F expression, rather than looping, as this results in a single db query.
        """

        if self.position < self.__original_position:
            CollaborationTask.objects.filter(
                collaboration=self.collaboration,
                position__lt=self.__original_position,
                position__gte=self.position,
            ).update(position=F("position") + 1)
            CollaborationMilestone.objects.filter(
                collaboration=self.collaboration,
                position__lt=self.__original_position,
                position__gte=self.position,
            ).update(position=F("position") + 1)

        return

    def remove(self):
        """
        When removing an element from a collaboration, we must also update the position of the other elements to
        reflect the change
        """

        CollaborationTask.objects.filter(
            collaboration=self.collaboration,
            position__gt=self.position,
        ).update(position=F("position") - 1)
        CollaborationMilestone.objects.filter(
            collaboration=self.collaboration,
            position__gt=self.position,
        ).update(position=F("position") - 1)

        self.delete()

        return

    def save(self, *args, **kwargs) -> None:

        """
        On save, we need to call some extra functions to ensure the adding/re-ordering of tasks also updates the
        positions of those around them, and on the milestones which log them.
        """

        # FOR CREATION
        if self._state.adding:

            # 1: Generate Reference & position (if not given)
            self.reference = self.generate_ref(5)
            if not self.position:
                self.position = self.collaboration.number_of_elements

            # 2: If there is a milestone ahead, add this task to the prerequisites
            if next_milestone := self.next_milestone:
                next_milestone.set_prerequisites()

            # 3: If the task has been added in between other elements, then we will need to reorder everything
            # NOTE: This section only gets called if the new task is not placed at the end
            if self.position < self.collaboration.number_of_elements:
                self.insert()

            return super(CollaborationTask, self).save(*args, **kwargs)

        # FOR EDITING
        else:

            # IF REPOSITIONING
            if self.position != self.__original_position:

                # Move the other elements
                self.reposition()

                # Update the instance
                response = super(CollaborationTask, self).save(*args, **kwargs)

                # Update the prerequisites on the milestones
                for milestone in self.collaboration.milestones.all():
                    milestone.set_prerequisites()

                # Return response
                return response

            # For simple edits (no reordering), we just return super().save
            return super(CollaborationTask, self).save(*args, **kwargs)

    def is_complete(self, *args, **kwargs) -> bool:
        """
        Checks if task is complete
        """
        return bool(self.completed_at)

    def __str__(self):
        """
        We have quite a detailed str representation, to avoid needing to do anything more on the front end.
        That said, we may be able to find more efficient ways of doing this in terms of database queries
        """
        # Check if task/milestone has been completed
        complete = True if self.completed_at else False

        # Tasks
        # If complete, give a string
        if complete:
            if self.completion_notes:
                return f" ☒ {self.name} (notes)"
            return f" ☒ {self.name}"

        # If not, check if assigned to anyone, and return an appropriate string.
        assigned_to = (
            string.capwords(self.assigned_to.first_name) if self.assigned_to else None
        )
        if assigned_to:
            return f" ☐ {self.name} ({assigned_to})"
        else:
            return f" ☐ {self.name}"

    class Meta:
        verbose_name_plural = "Tasks"
        indexes = [
            models.Index(fields=["collaboration", "position"]),
            models.Index(fields=["collaboration", "-position"]),
            models.Index(fields=["collaboration"]),
            models.Index(fields=["position"]),
            models.Index(fields=["-position"]),
        ]
        ordering = ["collaboration", "position"]


class CollaborationMilestone(TimeStampedSoftDeleteBase):
    """
    A Milestone is placed and displayed amongst the tasks at points where significant progress
    is made towards the end goal e.g. “Stage 1 Initial testing complete!”

    We store a list of prerequisite tasks in a many to many, rather than computing on then fly.
    This is in order to somewhat the number and complexity of database queries on simple read operations,
    and, in turn, avoid substantial slowdowns as the database grows.
    """

    def __init__(self, *args, **kwargs):
        """
        We override the init method to store a copy of the position when the class is instantiated
        This allows us to easily check whether the user's request is changing the position, and then take
        the actions required to ensure that all related objects in the db are updated.
        """
        super().__init__(*args, **kwargs)
        self.__original_position = self.position

    position = models.PositiveSmallIntegerField(
        help_text="The position of the element (1 = 1st)", blank=True
    )

    __original_position = None

    reference = models.CharField(
        default="REF",
        null=False,
        max_length=255,
        help_text="An auto-generated task reference, used to assign task as prerequisites",
    )

    collaboration = models.ForeignKey(
        "Collaboration",
        help_text="The Collaboration this element belongs to",
        on_delete=models.CASCADE,
        related_name="milestones",
    )

    name = models.CharField(
        help_text="A name for the milestone e.g. 'Stage 1 Preparations complete!'",
        max_length=100,
    )

    target_date = models.DateTimeField(
        help_text="A date by which the group should aim to reach this milestone",
        null=True,
        blank=True,
    )

    prerequisites = models.ManyToManyField(
        "CollaborationTask",
        help_text="Tasks that must be completed to each this milestones",
        related_name="milestone",
        blank=True,
    )

    @staticmethod
    def generate_ref(length) -> str:
        """Unique reference auto-generation function"""
        chars = string.ascii_uppercase + string.digits
        ref_prefix = "MILE-"
        ref_code = "".join(random.choice(chars) for _ in range(length))
        return ref_prefix + ref_code

    @property
    def status(self) -> str | None:
        """Determines a milestones status"""
        if all(task.completed_at for task in self.prerequisites.all()):
            return c.MILESTONE_STATUS_REACHED
        elif self.target_date and self.target_date < timezone.now():
            return c.MILESTONE_STATUS_BEHIND_TARGET
        else:
            return c.MILESTONE_STATUS_ON_TARGET

    @property
    def next_milestone(self):
        """Gets the next milestone"""
        if CollaborationMilestone.objects.filter(
            collaboration=self.collaboration, position__gt=self.position
        ).exists():
            return CollaborationMilestone.objects.filter(
                collaboration=self.collaboration, position__gt=self.position
            ).order_by("position")[0]
        else:
            return None

    def set_prerequisites(self, *args, **kwargs) -> None:
        """
        Logic to set all of the prerequisites required to meet a milestone,
        and mark the milestone as reached (completed), if they are all complete.
        """
        # Check if there are another other milestones before this one
        if CollaborationMilestone.objects.filter(
            collaboration=self.collaboration, position__lt=self.position
        ).exists():
            previous_milestone_position = (
                CollaborationMilestone.objects.filter(
                    collaboration=self.collaboration, position__lt=self.position
                )
                .order_by("-position")[0]
                .position
            )
        else:
            previous_milestone_position = 0

        tasks = CollaborationTask.objects.filter(
            collaboration=self.collaboration,
            position__lt=self.position,
            position__gte=previous_milestone_position,
        ).order_by("position")

        self.prerequisites.set(tasks)

        return

    def tasks_outstanding(self, *args, **kwargs) -> None:
        """
        Logic to count the number of tasks remaining
        """

        return self.prerequisites.filter(completed_at__isnull=True).count()

    def tasks_completed(self, *args, **kwargs) -> None:
        """
        Logic to count the number of tasks completed
        """

        return self.prerequisites.filter(completed_at__isnull=False).count()

    def is_complete(self, *args, **kwargs) -> bool:
        """
        Checks if milestone is reached
        """
        return self.status == c.MILESTONE_STATUS_REACHED

    def update_next_milestone(self):
        """
        If there is another milestone after this one, then it will now have some duplicate prerequisite tasks,
        We need to reset these
        """
        if next_milestone := self.next_milestone:
            next_milestone.set_prerequisites()
        return

    def insert(self):
        """
        If a milestone has been added in between other elements, then we will need to reorder everything
        afterwards, by adding 1 to their position. We use an F expression, rather than looping,
        as this results in a single db query.
        NOTE: This section only gets called if the new milestone is not placed at the end
        """
        if (
            self.position < self.collaboration.number_of_elements - 1
        ):  # minus this milestone
            CollaborationTask.objects.filter(
                collaboration=self.collaboration, position__gte=self.position
            ).update(position=F("position") + 1)
            CollaborationMilestone.objects.filter(
                collaboration=self.collaboration, position__gte=self.position
            ).update(position=F("position") + 1)
        return

    def reposition(self):
        """
        If moving to a higher position, we target all elements with a position greater than the
        '__original_position' of this milestone, but less than or equal to the new position of this milestone.
        from this queryset, we subtract '1' from the position column, making room for this milestone, and
        keeping the rest in order. We use an F expression, rather than looping,
        as this results in a single db query.
        """
        if self.position > self.__original_position:
            CollaborationTask.objects.filter(
                collaboration=self.collaboration,
                position__gt=self.__original_position,
                position__lte=self.position,
            ).update(position=F("position") - 1)
            CollaborationMilestone.objects.filter(
                collaboration=self.collaboration,
                position__gt=self.__original_position,
                position__lte=self.position,
            ).update(position=F("position") - 1)

        """
        If moving to a lower position, we target all elements with a position lower than the
        '__original_position' of this milestone, but greater than or equal to the new position of this
        milestone. from this queryset, we add '1' to the position column, making room for our milestone,
        and keeping the rest in order. We use an F expression, rather than looping,
        as this results in a single db query.
        """

        if self.position < self.__original_position:
            CollaborationTask.objects.filter(
                collaboration=self.collaboration,
                position__lt=self.__original_position,
                position__gte=self.position,
            ).update(position=F("position") + 1)
            CollaborationMilestone.objects.filter(
                collaboration=self.collaboration,
                position__lt=self.__original_position,
                position__gte=self.position,
            ).update(position=F("position") + 1)

        return

    def remove(self):
        """
        When removing an element from a collaboration, we must also update the position of the other elements to
        reflect the change
        """

        CollaborationTask.objects.filter(
            collaboration=self.collaboration,
            position__gt=self.position,
        ).update(position=F("position") - 1)
        CollaborationMilestone.objects.filter(
            collaboration=self.collaboration,
            position__gt=self.position,
        ).update(position=F("position") - 1)

        self.delete()

        return

    def save(self, *args, **kwargs) -> None:
        """
        On save, we need to add a reference, attach the prerequisite tasks by many-to-many and call some extra functions
        to ensure the adding/re-ordering of tasks also updates the positions of those around them,
        and on the milestones which log them.
        """

        # FOR CREATION
        if self._state.adding:

            # 1: Generate Reference & position (if not given)
            self.reference = self.generate_ref(5)
            if not self.position:
                self.position = self.collaboration.number_of_elements

            # 2: Save item
            response = super(CollaborationMilestone, self).save(*args, **kwargs)

            # 3: Set the prerequisite tasks for completion of this milestone
            self.set_prerequisites()

            # 4: Move the other elements (if required)
            self.insert()

            # 5: Update the prerequisite tasks for the next milestone (if required)
            self.update_next_milestone()

            return response

        # FOR EDITING
        else:

            # IF REPOSITIONING
            if self.position != self.__original_position:

                # Move the other elements (if required)
                self.reposition()

                # Update the instance
                response = super(CollaborationMilestone, self).save(*args, **kwargs)

                # Update the prerequisites on the milestones
                for milestone in self.collaboration.milestones.all():
                    milestone.set_prerequisites()

                # Return response
                return response

            # For simple edits (no reordering), we just return super().save
            return super(CollaborationMilestone, self).save(*args, **kwargs)

    def __str__(self):
        """
        We have quite a detailed str representation, to avoid needing to do anything more on the front end.
        That said, we may be able to find more efficient ways of doing this in terms of database queries
        """

        prerequisite_tasks = self.prerequisites.all()

        completed_prerequisite_tasks = prerequisite_tasks.filter(
            completed_at__isnull=False
        )

        return f"Milestone - {self.name} ({completed_prerequisite_tasks.count()} of {prerequisite_tasks.count()} complete)"

    class Meta:
        verbose_name_plural = "Milestones"
        indexes = [
            models.Index(fields=["collaboration", "position"]),
            models.Index(fields=["collaboration", "-position"]),
            models.Index(fields=["collaboration"]),
            models.Index(fields=["position"]),
            models.Index(fields=["-position"]),
        ]
        ordering = ["collaboration", "position"]
