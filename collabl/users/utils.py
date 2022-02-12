from django.contrib.auth import get_user_model
from django.db.models import Count, When, Case, IntegerField
from collaborations.models import Collaboration
import collaborations.constants as collaboration_constants


def get_sentinel_user():
    """
    We use this function to set a user named "deleted" as the foreign key when a user who has
    foreign key relationships with another models is deleted
    """
    return get_user_model().objects.get_or_create(email="deleted@deleted.com")[0]


def get_users_filtered_collaborations(user, collaboration_list_filter):
    """
    We use this function to filter a users collaborations by their current status
    The possible filters are listed below (taken from constants):
        COLLABORATION_STATUS_PLANNING: str = "Planning"
        COLLABORATION_STATUS_ONGOING: str = "Ongoing"
        COLLABORATION_STATUS_COMPLETED: str = "Completed"
        COLLABORATION_STATUS_ALL: str = "All"  # Used for filtering
    """

    # Annotate the user's groups' collaborations with the number of complete/incomplete tasks,
    unfiltered_collaborations = (
        Collaboration.objects.filter(
            related_group__members=user,
        )
        .annotate(
            tasks_complete=Count(
                Case(
                    When(tasks__completed_at__isnull=False, then=1),
                    output_field=IntegerField(),
                )
            ),
            tasks_incomplete=Count(
                Case(
                    When(tasks__completed_at__isnull=True, then=1),
                    output_field=IntegerField(),
                )
            ),
        )
        .order_by("-created_at")
    )

    # Filter the collaborations, depending on the filter parameter chosen
    match collaboration_list_filter:
        case collaboration_constants.COLLABORATION_STATUS_ALL:
            collaborations = unfiltered_collaborations
        case collaboration_constants.COLLABORATION_STATUS_PLANNING:
            collaborations = unfiltered_collaborations.filter(tasks_complete=0)
        case collaboration_constants.COLLABORATION_STATUS_ONGOING:
            collaborations = unfiltered_collaborations.filter(
                tasks_incomplete__gt=0
            ).exclude(tasks_complete=0)
        case collaboration_constants.COLLABORATION_STATUS_COMPLETED:
            collaborations = unfiltered_collaborations.filter(
                tasks_incomplete=0
            ).exclude(tasks_complete=0)
        case _:
            collaborations = Collaboration.objects.none()

    return collaborations
