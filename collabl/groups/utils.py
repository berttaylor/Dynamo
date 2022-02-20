from django.db.models import Count, Case, When, Q, IntegerField

import groups.constants as c
from collaborations.models import Collaboration


def get_membership_level(user, group):
    """
    Simple utility function that return that status of the membership, if one exists.
    Used to render relevant sections on front end.
    """

    if user.is_authenticated:
        if membership := group.memberships.filter(user=user, group=group).first():
            return membership.status
    return None


def user_has_active_membership(user, group):
    """Check that the users membership is of the correct level"""

    active_membership_levels: list = [
        c.MEMBERSHIP_STATUS_ADMIN,
        c.MEMBERSHIP_STATUS_CURRENT,
    ]

    membership_level = get_membership_level(user, group)

    return membership_level in active_membership_levels


def user_is_admin(user, group):
    """Check that the users membership is of admin level"""
    return get_membership_level(user, group) == c.MEMBERSHIP_STATUS_ADMIN


def get_membership_count(group):
    """
    Counts memberships by type in order to provide as context to front end
    """

    memberships = group.memberships.all()

    admin_count = memberships.filter(status=c.MEMBERSHIP_STATUS_ADMIN).count()
    member_count = memberships.filter(status=c.MEMBERSHIP_STATUS_CURRENT).count()
    ignored_count = memberships.filter(status=c.MEMBERSHIP_STATUS_IGNORED).count()
    pending_count = memberships.filter(status=c.MEMBERSHIP_STATUS_PENDING).count()
    subscriber_count = memberships.filter(is_subscribed=True).count()

    return {
        "admin": admin_count,
        "member": member_count,
        "ignored": ignored_count,
        "pending": pending_count,
        "subscriber": subscriber_count,
    }


def get_filtered_collaborations(group, collaboration_list_filter):
    # Annotate the group's collaborations with the number of complete/incomplete tasks,
    group_collaborations = (
        Collaboration.objects.filter(
            related_group=group,
        )
        .annotate(
            tasks_complete=Count(
                Case(
                    When(Q(tasks__completed_at__isnull=False), then=1),
                    output_field=IntegerField(),
                )
            ),
            tasks_incomplete=Count(
                Case(
                    When(Q(tasks__completed_at__isnull=True), then=1),
                    output_field=IntegerField(),
                )
            ),
        )
        .order_by("-created_at")
    )

    # Filter the collaborations, depending on the filter parameter chosen
    match collaboration_list_filter:
        case c.COLLABORATION_STATUS_ALL:
            collaborations = group_collaborations
        case c.COLLABORATION_STATUS_PLANNING:
            collaborations = group_collaborations.filter(tasks_complete=0)
        case c.COLLABORATION_STATUS_ONGOING:
            collaborations = group_collaborations.filter(
                tasks_incomplete__gt=0
            ).exclude(tasks_complete=0)
        case c.COLLABORATION_STATUS_COMPLETED:
            collaborations = group_collaborations.filter(tasks_incomplete=0).exclude(
                tasks_complete=0
            )
        case _:
            collaborations = Collaboration.objects.none()

    return collaborations
