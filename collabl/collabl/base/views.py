from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import RedirectView

"""
Generic views needed for front end functionality are kept here.
"""


def empty_string(request):
    return HttpResponse()


class HomepageRedirectView(RedirectView):
    """
    This view directs the user to the correct 'home' location, depending on whether they are logged in or not
    """

    def get_redirect_url(self, *args, **kwargs):
        user = self.request.user
        match user.is_authenticated:
            # if logged_in, direct to the dashboard
            case True:
                return reverse_lazy("user-group-list")

            # if unauthenticated, redirect to agency directory
            case _:
                return reverse_lazy("landing")
