from collaborations.constants import COLLABORATION_STATUS_PLANNING, COLLABORATION_STATUS_ONGOING, \
    COLLABORATION_STATUS_COMPLETED, COLLABORATION_STATUS_ALL

"""GROUP ANNOUNCEMENTS"""

ANNOUNCEMENTS_LIST_VIEW_LATEST: str = "Latest"
ANNOUNCEMENTS_LIST_VIEW_ALL: str = "All"

ANNOUNCEMENTS_LIST_VIEWS: dict = {
    ANNOUNCEMENTS_LIST_VIEW_LATEST: "Latest",
    ANNOUNCEMENTS_LIST_VIEW_ALL: "All",
}

"""GROUP COLLABORATIONS"""

# Note: These are set in collaborations.constants and imported here for use as a view filter

COLLABORATION_LIST_VIEWS: dict = {
    COLLABORATION_STATUS_PLANNING: "Planning",
    COLLABORATION_STATUS_ONGOING: "Ongoing",
    COLLABORATION_STATUS_COMPLETED: "Completed",
    COLLABORATION_STATUS_ALL: "All",
}

"""GROUP MEMBERSHIPS"""
MEMBERSHIP_STATUS_ADMIN: str = "Admin"
MEMBERSHIP_STATUS_PENDING: str = "Pending"
MEMBERSHIP_STATUS_CURRENT: str = "Current"
MEMBERSHIP_STATUS_IGNORED: str = "Ignored"

# One version in a tuple form - to be used as the 'choices' for a text field
MEMBERSHIP_STATUS_CHOICES: tuple = (
    (MEMBERSHIP_STATUS_ADMIN, "Admin"),
    (MEMBERSHIP_STATUS_PENDING, "Pending"),
    (MEMBERSHIP_STATUS_CURRENT, "Current"),
    (MEMBERSHIP_STATUS_IGNORED, "Ignored"),
)

# We use an extra version, in dictionary form, which to greatly simplifies the view logic - see use in .views_htmx.py
MEMBERSHIP_LIST_VIEWS: dict = {
    MEMBERSHIP_STATUS_ADMIN: "Admin",
    MEMBERSHIP_STATUS_PENDING: "Pending",
    MEMBERSHIP_STATUS_CURRENT: "Current",
    MEMBERSHIP_STATUS_IGNORED: "Ignored",
}

MEMBERSHIP_ACTION_APPROVE: str = "Approve"
MEMBERSHIP_ACTION_IGNORE: str = "Ignore"
MEMBERSHIP_ACTION_REMOVE: str = "Remove"
MEMBERSHIP_ACTION_MAKE_ADMIN: str = "Make Admin"
MEMBERSHIP_ACTION_CLEAR_SELECTION: str = "Clear Selection"

