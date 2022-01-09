import random
import string
import time

from collaborations import constants as c
from django.db import models
from django.db.models import F
from django.template.defaultfilters import slugify
from django.utils import timezone

from dynamo.storages import collaboration_based_upload_to
from users.utils import get_sentinel_user

from dynamo.base.models import TimeStampedSoftDeleteBase


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
        return CollaborationTask.objects.filter(collaboration=self, completed_at__isnull=False).count()

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
        ordering = ["name"]


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
        help_text="The position of the element (1 = 1st)",
        blank=True,
        null=False
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

    tags = models.ManyToManyField(
        "CollaborationTaskTag",
        help_text="Tags showing certain properties that relate to multiple tasks e.g. 'Admin Task'",
        related_name="tasks",
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
            # afterwards, by adding 1 to their position. We use an F expression, rather than looping,
            # as this results in a single db query.
            # NOTE: This section only gets called if the new task is not placed at the end
            if self.position < self.collaboration.number_of_elements:
                CollaborationTask.objects.filter(
                    collaboration=self.collaboration, position__gte=self.position
                ).update(position=F("position") + 1)
                CollaborationMilestone.objects.filter(
                    collaboration=self.collaboration, position__gte=self.position
                ).update(position=F("position") + 1)

            return super(CollaborationTask, self).save(*args, **kwargs)

        # FOR EDITING
        else:
            # IF REPOSITIONING
            if self.position != self.__original_position:

                # If moving to a higher position, we target all elements with a position greater than the
                # '__original_position' of this task, but less than or equal to the new position of this task. from this
                # queryset, we subtract '1' from the position column, making room for our task, and keeping the rest in order.
                # We use an F expression, rather than looping, as this results in a single db query.

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

                # If moving to a lower position, we target all elements with a position lower than the
                # '__original_position' of this task, but greater than or equal to the new position of this task. from
                # this queryset, we add '1' to the position column, making room for our task, and keeping the rest in
                # order. We use an F expression, rather than looping, as this results in a single db query.

                else:
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

                # Update the instance
                response = super(CollaborationTask, self).save(*args, **kwargs)

                # Update the prerequisites on the milestones
                # First we get the next milestone from the old position (if one exists),
                # and remove the task from its list of prerequisites
                # TODO - Which one is faster? version 1 (below) - or version 2 (below that)
                if old_ms := self.collaboration.milestones.filter(
                        position__gt=self.__original_position
                ).order_by("position")[0]:
                    old_ms.prerequisites.remove(self)
                # Next, we get the milestone from the new position (if one exists),
                # and add this task to its list of prerequisites
                if new_ms := self.collaboration.milestones.filter(
                        position__gt=self.position
                ).order_by("position")[0]:
                    new_ms.prerequisites.add(self)

                # version 2
                # old_ms = self.collaboration.milestones.filter(position__gt=self.__original_position).order_by(
                #         'position')[0]
                # new_ms = self.collaboration.milestones.filter(position__gt=self.position).order_by('position')[0]
                # # If the milestone has changed:
                # if old_ms != new_ms:
                #     if old_ms:
                #         # we remove this task from the old one (if it exists)
                #         old_ms.prerequisites.remove(self)
                #     if new_ms:
                #         # and add it to the new one (if it exists)
                #         new_ms.prerequisites.add(self)

                # Return response
                return response

            # For simple edits (no reordering), we just return super().save
            return super(CollaborationTask, self).save(*args, **kwargs)

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
        assigned_to = string.capwords(self.assigned_to.username) if self.assigned_to else None
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
        help_text="The position of the element (1 = 1st)",
        blank=True,
        null=False
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
        elif self.target_date > timezone.now():
            return c.MILESTONE_STATUS_ON_TARGET
        else:
            return c.MILESTONE_STATUS_BEHIND_TARGET

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

            # 2: Set the prerequisite tasks for completion of this milestone
            response = super(CollaborationMilestone, self).save(*args, **kwargs)

            # 3: Set the prerequisite tasks for completion of this milestone
            self.set_prerequisites()

            # 4: If the milestone has been added in between other elements, then we will need to reorder everything
            # afterwards, by adding 1 to their position. We use an F expression, rather than looping,
            # as this results in a single db query.
            # NOTE: This section only gets called if the new milestone is not placed at the end
            if self.position < self.collaboration.number_of_elements - 1:  # minus this milestone
                CollaborationTask.objects.filter(
                    collaboration=self.collaboration, position__gte=self.position
                ).update(position=F("position") + 1)
                CollaborationMilestone.objects.filter(
                    collaboration=self.collaboration, position__gte=self.position
                ).update(position=F("position") + 1)

                # 5: If there is another milestone after this one, then it will now have some duplicate prerequisite tasks,
                # We need to reset these.
                if next_milestone := self.next_milestone:
                    next_milestone.set_prerequisites()

            return response

        # FOR EDITING
        else:
            # IF REPOSITIONING
            if self.position != self.__original_position:

                # If moving to a higher position, we target all elements with a position greater than the
                # '__original_position' of this milestone, but less than or equal to the new position of this milestone.
                # from this queryset, we subtract '1' from the position column, making room for this milestone, and
                # keeping the rest in order. We use an F expression, rather than looping,
                # as this results in a single db query.

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

                # If moving to a lower position, we target all elements with a position lower than the
                # '__original_position' of this milestone, but greater than or equal to the new position of this
                # milestone. from this queryset, we add '1' to the position column, making room for our milestone,
                # and keeping the rest in order. We use an F expression, rather than looping,
                # as this results in a single db query.

                else:
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
