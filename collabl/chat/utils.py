from groups.constants import MEMBERSHIP_STATUS_ADMIN
from groups.utils import get_membership_level


def user_is_message_owner(user, message):
    """Check that the users is the owner of the message"""

    return message.user == user


def get_message_group(message):
    """Gets the group that a message belongs to"""

    if hasattr(message, "group"):
        return message.group
    elif hasattr(message, "collaboration"):
        return message.collaboration.related_group
    return None


def user_is_message_owner_or_admin(user, message):
    """Check that the users is either the owner of the message, or a group admin"""

    if user_is_message_owner(user, message):
        return True
    else:
        return (
            get_membership_level(user, get_message_group(message))
            == MEMBERSHIP_STATUS_ADMIN
        )
