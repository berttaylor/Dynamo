"""
Helpers for dealing with file uploads
"""


def group_based_upload_to(instance, filename):
    return "image/group/{}/{}".format(instance.slug, filename)
