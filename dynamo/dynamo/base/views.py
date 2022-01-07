from django.http import HttpResponse

"""
Generic views needed for front end functionality are kept here.
"""


def empty_html_string(request):
    return HttpResponse('')
