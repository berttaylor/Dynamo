from django.contrib.auth import get_user_model


def get_sentinel_user():
    """
    We use this function to set a user named "deleted" as the foreign key when a user who has
    foreign key relationships with another models is deleted
    """
    return get_user_model().objects.get_or_create(
        email="deleted@deleted.com"
    )[0]
