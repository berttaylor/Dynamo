import random
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from chat.models import Message
from collaborations.models import (
    Collaboration,
    CollaborationTask,
    CollaborationMilestone,
)
from groups.constants import (
    MEMBERSHIP_STATUS_CURRENT,
    MEMBERSHIP_STATUS_ADMIN,
    MEMBERSHIP_STATUS_IGNORED,
    MEMBERSHIP_STATUS_PENDING,
)
from groups.models import Group, Membership, GroupAnnouncement
from users.models import User


class Command(BaseCommand):
    """
    Creates data for the task in each collaboration
    """

    def success(self, text):
        self.stdout.write(self.style.SUCCESS(text))

    def error(self, text):
        self.stdout.write(self.style.ERROR(text))

    def handle(self, *args, **options):

        with transaction.atomic():

            example_tasks = [
                [
                    "Make the posters",
                    "This will need a creative touch, Maybe {} is best to handle this",
                ],
                [
                    "Newsletter",
                    "We will have to contact the users - {}, Can you send out a newsletter?",
                ],
                [
                    "Book the Zone",
                    "If it hasn't been done, someone will need to book the zone out for the day, how about {}?",
                ],
                [
                    "Film Instructional Video",
                    "All members will be asked to help setting up their own equipment, {} will film the video ",
                ],
            ]

            more_example_tasks = [
                [
                    "Move the equipment",
                    "We'll need {}'s strong hands to carry the equipment into place",
                ],
                [
                    "Get it done",
                    "Once the preparations are complete, {} will contact you and we can complete the collaboration!",
                ],
            ]

            section_of_collaborations = Collaboration.objects.filter().order_by("?")[
                :17
            ]

            for collaboration in section_of_collaborations:
                if not collaboration.number_of_tasks:
                    for task in example_tasks:
                        assigned_to = (
                            collaboration.related_group.current_users.order_by(
                                "?"
                            ).first()
                        )
                        completed_at = None
                        completed_by = None
                        if random.getrandbits(1):
                            completed_at = timezone.now()
                            completed_by = assigned_to
                        description = task[1].format(assigned_to.first_name)
                        CollaborationTask.objects.create(
                            collaboration=collaboration,
                            name=task[0],
                            description=description,
                            assigned_to=assigned_to,
                            completed_by=completed_by,
                            completed_at=completed_at,
                        )

                    CollaborationMilestone.objects.create(
                        collaboration=collaboration, name="All Preparations Complete!"
                    )

                    for task in more_example_tasks:
                        assigned_to = (
                            collaboration.related_group.current_users.order_by(
                                "?"
                            ).first()
                        )
                        completed_at = None
                        completed_by = None
                        if random.getrandbits(1):
                            completed_at = timezone.now()
                            completed_by = assigned_to
                        description = task[1].format(assigned_to.first_name)
                        CollaborationTask.objects.create(
                            collaboration=collaboration,
                            name=task[0],
                            description=description,
                            assigned_to=assigned_to,
                            completed_by=completed_by,
                            completed_at=completed_at,
                        )

            self.success("Success")
