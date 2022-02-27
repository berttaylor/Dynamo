import os

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views.decorators.http import require_http_methods
from django.views.generic import UpdateView, ListView

from users.models import User
from users.utils import account_activation_token
from collabl.tasks import send_email
from collaborations.models import Collaboration
from groups.constants import (
    MEMBERSHIP_STATUS_CURRENT,
    MEMBERSHIP_STATUS_ADMIN,
    MEMBERSHIP_STATUS_PENDING,
)
from groups.models import Group, Membership
from users.forms import SignUpForm, UserDetailUpdateForm
from users.utils import get_users_filtered_collaborations
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView


@require_http_methods(["GET", "POST"])
def sign_up_view(request):

    form = SignUpForm(request.POST or None)

    if request.method == "POST" and form.is_valid():

        # Set the user as inactive and create
        form.instance.is_active = False
        user = form.save()

        # Send activation email
        site_protocol = os.environ.get("SITE_PROTOCOL")
        site_domain = os.environ.get("SITE_DOMAIN")
        activation_url_section = reverse_lazy(
            "activate",
            kwargs={
                "encoded_pk": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": account_activation_token.make_token(user),
            },
        )
        full_activation_url = site_protocol + site_domain + activation_url_section
        send_email.delay(
            {
                "template": "activation.email",
                "recipients": (str(user.email),),
                "additional_context": {
                    "subject": "Activate Your Account",
                    "first_name": str(user.first_name),
                    "link": str(full_activation_url),
                },
            }
        )

        # Redirect to login page
        return redirect("login")

    # If get (or invalid data) render Signup form
    return render(request, "landing/registration/signup.html", {"form": form})


@require_http_methods(
    [
        "GET",
    ]
)
def account_activation_view(request, encoded_pk, token):
    """
    View that is linked to from account verification emails.
    """

    pk = force_text(urlsafe_base64_decode(encoded_pk))
    user = User.objects.get(pk=pk)

    # If the user is already active, we redirect to the login page
    if user.is_active:
        return redirect("login")

    # If there is no matching token, we redirect with a message
    if not account_activation_token.check_token(user, token):
        return redirect("login")

    # If everything matches, we mark the user as active, and send a confirmation email.
    user.is_active = True
    user.save()

    return redirect("login")


@method_decorator(login_required, name="dispatch")
class UserUpdateView(UpdateView):
    """
    Allows users to update their details
    """

    template_name = "app/home/user_details.html"
    form_class = UserDetailUpdateForm
    success_url = reverse_lazy("user-update")
    http_method_names = ["get", "post"]

    def get_object(self, queryset=None):
        return self.request.user


@method_decorator(login_required, name="dispatch")
class UserGroupListView(ListView):
    """
    Shows all of the users groups
    """

    model = Group
    context_object_name = "groups"
    template_name = "app/home/user_groups.html"
    partial_template_name = "app/home/partials/group_list.html"
    hx_target_id = "list_of_groups"
    http_method_names = [
        "get",
    ]

    def get_template_names(self):
        """
        If this is an HTMX request targeting a specific section of the page,
        we return a partial, rather than the entire page
        """
        if self.request.htmx.target == self.hx_target_id:
            return self.partial_template_name
        return self.template_name

    def get_queryset(self):
        # We override this function to check if any parameters have been added, before we get the queryset
        if self.request.GET.get("show_pending", None):
            pending_memberships = Membership.objects.filter(
                user=self.request.user, status=MEMBERSHIP_STATUS_PENDING
            ).values_list("group", flat=True)
            return Group.objects.filter(pk__in=pending_memberships)
        else:
            active_memberships = Membership.objects.filter(
                user=self.request.user,
                status__in=[MEMBERSHIP_STATUS_CURRENT, MEMBERSHIP_STATUS_ADMIN],
            ).values_list("group", flat=True)
            return Group.objects.filter(pk__in=active_memberships)


@method_decorator(login_required, name="dispatch")
class UserCollaborationListView(ListView):
    """
    Shows all of the users Collaborations, serving both full page and htmx requests
    """

    model = Collaboration
    template_name = "app/home/user_collaborations.html"
    partial_template_name = "app/home/partials/collaboration_list.html"
    hx_target_id = "list_of_collaborations"
    http_method_names = [
        "get",
    ]

    def get_template_names(self):
        """
        If this is an HTMX request targeting a specific section of tha page,
        we return a partial, rather than the entire page
        """
        if self.request.htmx.target == self.hx_target_id:
            return self.partial_template_name
        return self.template_name

    def get_queryset(self):
        """
        If a filter is specified, we send back a subset of the users groups, rather than all of them.
        """
        # Get filter parameter
        if collaboration_list_filter := self.request.GET.get(
            "collaboration_list_filter", None
        ):
            return get_users_filtered_collaborations(
                self.request.user, collaboration_list_filter
            )
        return Collaboration.objects.filter(related_group__members=self.request.user)
