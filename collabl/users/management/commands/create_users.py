import random
import names
from django.core.management.base import BaseCommand
from django.db import transaction

from groups.constants import MEMBERSHIP_STATUS_CURRENT, MEMBERSHIP_STATUS_ADMIN, \
    MEMBERSHIP_STATUS_IGNORED, MEMBERSHIP_STATUS_PENDING
from groups.models import Group, Membership
from users.models import User

class Command(BaseCommand):
    """
    Creates a specified users, and uses them to populate the groups in the system.

    Groups
    Users
    Memberships
    Collaborations

    """

    def success(self, text):
        self.stdout.write(self.style.SUCCESS(text))

    def error(self, text):
        self.stdout.write(self.style.ERROR(text))

    def handle(self, *args, **options):

        with transaction.atomic():

            # # Make Users
            # users_created = 0
            # new_users_ids = []
            # while users_created < 300:
            #     first_name = names.get_first_name()
            #     last_name = names.get_last_name()
            #     email = f"{first_name}.{last_name}@gmail.com"
            #     user = User.objects.create(first_name=first_name, last_name=last_name, email=email)
            #     new_users_ids.append(user.pk)
            #     users_created += 1

            example_groups = [
                ['Cheshire Chess Club', 'A place for us to plan events and and tournaments.'],
                ['Hoxton Hockey Team', 'A welcoming group, ready for new members, and new collaborations!'],
                ['Burnley Bakers', 'We often charity hold events in store, which we could use some help with'],
                ['Southside Five-a-side Club', 'Projects are incoming, and we are going to need to pull together'],
                ['Brixton Bowling Team', 'All for one, and one for all.....'],
                ['Peppersfield Parents', 'A group of concerns parents, wanting to make a difference..'],
                ['St Ives Community', 'A group for the St. Ives community to plan events'],
                ['March Town Committee', 'We plan many small festivals and fairs throughout the year'],
                ['St Nicholas Church', 'Church related events and community projects'],
                ['Giger Art Appreciation', 'Collaborative art Projects that are based around the work of H.R. Giger'],
                ['Hard Rock Online Meetup', 'Music collabs, hard rock, adn beers!'],
                ['Online Art Community', 'Large sale Online Art projects for all abilities'],
                ['Secret Garden Party', 'Space for organisers of the festival entertainment'],
                ['Buntingford Festival Committee', 'Planning festivals and fairs since 1978'],
                ['Wool & Wine', 'Knitting (and drinking) projects.... '],
                ['Royston Town Council', 'Note: Not for official business, please contact the office for inquiries'],
                ['Dabapps devs',
                 'We design and build custom web and mobile applications that help our clients succeed.'],
                ['Wagtail Team', 'Wagtail is built by developers for developers....'],
                ['Torchbox',
                 'Torchbox is the agency partner for socially progressive organisations with ambitious digital ideas.'],
            ]

            # Make Groups
            groups_created = 0
            new_group_ids = []
            for group in example_groups:
                name, description, user = group[0], group[1], User.objects.order_by('?')[0]
                if not Group.objects.filter(name=name).exists():
                    created_group = Group.objects.create(name=name, description=description,created_by=user)
                    new_group_ids.append(created_group.pk)
                    groups_created += 1

            # Make Memberships
            memberships_created = 0
            for group in Group.objects.filter(id__in=new_group_ids):
                for user in User.objects.all():
                    if not Membership.objects.filter(group=group, user=user).exists() and random.getrandbits(1):
                        if random.getrandbits(1):
                            Membership.objects.create(group=group, user=user, status=MEMBERSHIP_STATUS_CURRENT)
                            memberships_created += 1
                        elif random.getrandbits(1):
                            if random.getrandbits(1):
                                Membership.objects.create(group=group, user=user, status=MEMBERSHIP_STATUS_PENDING)
                                memberships_created += 1
                            elif random.getrandbits(1):
                                if random.getrandbits(1) and random.getrandbits(1):
                                    Membership.objects.create(group=group, user=user, status=MEMBERSHIP_STATUS_ADMIN)
                                    memberships_created += 1
                                else:
                                    Membership.objects.create(group=group, user=user, status=MEMBERSHIP_STATUS_IGNORED)
                                    memberships_created += 1

            self.success(
                f"{groups_created} groups created. {memberships_created} memberships created."
            )
