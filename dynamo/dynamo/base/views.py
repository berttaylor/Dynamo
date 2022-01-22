from django.http import HttpResponse

"""
Generic views needed for front end functionality are kept here.
"""


def htmx_empty_string(request):
    return HttpResponse()
