"""MEMBERSHIP_STATUS"""

MEMBERSHIP_STATUS_PENDING: str = "Pending"
MEMBERSHIP_STATUS_CURRENT: str = "Current"
MEMBERSHIP_STATUS_IGNORED: str = "Ignored"
MEMBERSHIP_STATUS_REMOVED: str = "Removed"
MEMBERSHIP_STATUS_LEFT: str = "Left"

MEMBERSHIP_STATUS_CHOICES: tuple = (
    (MEMBERSHIP_STATUS_PENDING, "Pending"),
    (MEMBERSHIP_STATUS_CURRENT, "Current"),
    (MEMBERSHIP_STATUS_IGNORED, "Ignored"),
    (MEMBERSHIP_STATUS_REMOVED, "Removed"),
    (MEMBERSHIP_STATUS_LEFT, "Left"),
)

"""MEMBERSHIP_ACTIONS"""
MEMBERSHIP_ACTION_APPROVE: str = "Approve"
MEMBERSHIP_ACTION_IGNORE: str = "Ignore"
MEMBERSHIP_ACTION_REMOVE: str = "Remove"
MEMBERSHIP_ACTION_MAKE_ADMIN: str = "Make Admin"
MEMBERSHIP_ACTION_CLEAR_SELECTION: str = "Clear Selection"
