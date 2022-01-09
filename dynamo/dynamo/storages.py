"""
Helpers for dealing with file uploads
"""


def group_based_upload_to(instance, filename):
    return "groups/images/{}/{}".format(instance.slug, filename)


def collaboration_based_upload_to(instance, filename):
    return "collaboration/images/{}/{}".format(instance.slug, filename)
