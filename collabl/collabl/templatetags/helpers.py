import re
from django import template

register = template.Library()


@register.simple_tag
def active_link(request, url_pattern):
    """
    Sets provides additional class attributes when the request link matched the url pattern provided
    """
    if re.search(url_pattern, request.path):
        # Note: This is a 'contains' rather than a match on equality
        return "bg-tertiary"
    return ""
