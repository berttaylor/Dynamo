import random
from django.core.management.base import BaseCommand
from django.db import transaction
import names
from chat.models import Message
from collaborations.models import Collaboration
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
    Creates data for the groups in the system

    Announcements
    Messages
    Collaborations
    Generic tasks with randomly set complete/incomplete
    """

    def success(self, text):
        self.stdout.write(self.style.SUCCESS(text))

    def error(self, text):
        self.stdout.write(self.style.ERROR(text))

    def handle(self, *args, **options):

        with transaction.atomic():

            example_dialogue_1 = [
                "Hey Guys! Welcome to the new group",
                "Happy to be here",
                "What shall we do?"
                "I'd like to create something really special for the first project",
                "Check out the collaborations on the other groups, some of this stuff is really impressive.",
                "Do you think we could do something like that? A big scale project?"
                "This group is growing so fast, I cant help but believe we will....",
            ]

            example_announcements = [
                [
                    "Welcome to the Group!",
                    "Welcome to the new group. Make sure you have hit subscribe, because there are lots of fun activities incoming",
                ],
                [
                    "Looking for Members",
                    "Join up guys, and invite your friends. We have lots of plans for fun activities to do together that will help our community.",
                ],
                [
                    "New Members",
                    "If you have recently joined the group, be sure to drop a message in the chat at the bottom of the page to say hi.",
                ],
            ]

            example_collaborations = [
                [
                    "Charity Dog Walk",
                    "We are organising a dig dog walk for RSPCA. Help us plan it!",
                ],
                [
                    f"{names.get_first_name()}'s 40th Surprise",
                    "Lots of plans for fun activities to do together that will entertain",
                ],
                [
                    f"{names.get_first_name()}'s 40th Surprise",
                    "Lots of plans for fun activities to do together that will entertain",
                ],
                [
                    f"{names.get_first_name()}'s 40th Surprise",
                    "Lots of plans for fun activities to do together that will entertain",
                ],
                [
                    f"{names.get_first_name()}'s Birthday",
                    "Organising Fun activities to do together that will entertain",
                ],
                [
                    f"{names.get_first_name()}'s Birthday",
                    "Organising Fun activities to do together that will entertain",
                ],
                [
                    f"{names.get_first_name()}'s Birthday",
                    "Organising Fun activities to do together that will entertain",
                ],
                [
                    f"Running for {names.get_first_name()}",
                    "We're gonna show our support the best way we can!",
                ],
                [
                    f"Running for {names.get_first_name()}",
                    "We're gonna show our support the best way we can!",
                ],
                [
                    f"Running for {names.get_first_name()}",
                    "We're gonna show our support the best way we can!",
                ],
                [
                    f"{names.get_first_name()}'s Renovation project",
                    "Renovation will be done. Dreams will be made.",
                ],
                [
                    f"{names.get_first_name()}'s Renovation project",
                    "Renovation will be done. Dreams will be made.",
                ],
                [
                    f"{names.get_first_name()}'s Renovation project",
                    "Renovation will be done. Dreams will be made.",
                ],
                [
                    f"Cleaning up {names.get_last_name()} Avenue",
                    "We are going to make the street a nice place to live for all residents",
                ],
                [
                    f"Cleaning up {names.get_last_name()} Avenue",
                    "We are going to make the street a nice place to live for all residents",
                ],
                [
                    f"Cleaning up {names.get_last_name()} Avenue",
                    "We are going to make the street a nice place to live for all residents",
                ],
                [
                    "Renovating the school yard",
                    "We are going to make the school yard a nicer place be for the children",
                ],
                [
                    "Online Collaboration",
                    "We have some great tasks to share out for our biggest collaboration yet",
                ],
                [
                    "Zooming Home",
                    "Providing everyone with zoom capable machines to continue our work online",
                ],
                ["BigFest '23", "This is gonna be the biggest fest you've ever seen"],
                ["Quiz Night", "Organisation for the annual Pub Quiz night"],
                [
                    "Computer Upgrades",
                    "We need to plan who gets what, and when, order them, and collect them",
                ],
                [
                    "Bake Sale",
                    "Big Charity Bake sale, join up to hear about all the fun",
                ],
            ]

            for group in Group.objects.all().exclude(slug="barclays-eagle-labs"):

                if not group.memberships.filter(
                    status=MEMBERSHIP_STATUS_ADMIN
                ).exists():
                    print("creating admin")
                    new_admin = (
                        group.memberships.filter(status=MEMBERSHIP_STATUS_CURRENT)
                        .order_by("?")
                        .first()
                    )
                    new_admin.status = MEMBERSHIP_STATUS_ADMIN
                    new_admin.save()

                admins = User.objects.filter(
                    pk__in=group.memberships.all()
                    .filter(status=MEMBERSHIP_STATUS_ADMIN)
                    .values_list("user", flat=True)
                )
                print(admins)

                current_members = User.objects.filter(
                    pk__in=group.memberships.all()
                    .filter(status=MEMBERSHIP_STATUS_CURRENT)
                    .values_list("user", flat=True)
                )
                print(current_members)

                # Make Messages
                for message in example_dialogue_1:
                    Message.objects.create(
                        message=message,
                        group=group,
                        user=current_members.order_by("?").first(),
                    )

                # Make Announcements
                for announcement in example_announcements:
                    GroupAnnouncement.objects.create(
                        title=announcement[0],
                        body=announcement[1],
                        group=group,
                        user=admins.order_by("?")[0],
                    )

            # Make Collaborations
            section_of_groups = Group.objects.exclude(
                slug="barclays-eagle-labs"
            ).order_by("?")[:13]
            for collaboration in example_collaborations:
                group = section_of_groups.first()
                user = group.admin_users.order_by("?").first()
                Collaboration.objects.create(
                    name=collaboration[0],
                    description=collaboration[1],
                    related_group=group,
                    created_by=user,
                )

            self.success("Success")
