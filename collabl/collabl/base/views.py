from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods
from django.views.generic import RedirectView

"""
Generic views needed for front end functionality are kept here.
"""


@login_required()
@require_http_methods(["GET"])
def empty_string(request):
    return HttpResponse()


class HomepageRedirectView(RedirectView):
    """
    This view directs the user to the correct 'home' location, depending on whether they are logged in or not
    """

    http_method_names = [
        "get",
    ]

    def get_redirect_url(self, *args, **kwargs):
        user = self.request.user
        match user.is_authenticated:
            # if logged_in, direct to the dashboard
            case True:
                return reverse_lazy("group-search")

            # if unauthenticated, redirect to agency directory
            case _:
                return reverse_lazy("landing")


def trigger_error(request):
    """Used for sentry debugging"""
    division_by_zero = 1 / 0
