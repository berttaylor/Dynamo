import constants as c


def get_membership_level(user, group):
    """
    Simple utility function that return that status of the membership, if one exists.
    Used to render relevant sections on front end.
    """
    if not (membership := group.memberships.filter(user=user, group=group).first()):
        return None

    return membership.status


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
