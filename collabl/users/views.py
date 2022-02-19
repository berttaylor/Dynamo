from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.views.generic import UpdateView, ListView

from collaborations.models import Collaboration
from groups.constants import (
    MEMBERSHIP_STATUS_CURRENT,
    MEMBERSHIP_STATUS_ADMIN,
    MEMBERSHIP_STATUS_PENDING,
)
from groups.models import Group, Membership
from users.forms import SignUpForm, UserDetailUpdateForm
from users.utils import get_users_filtered_collaborations


@require_http_methods(["GET", "POST"])
def sign_up_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get("email")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(email=email, password=raw_password, request=request)
            login(request, user)
            return redirect("login")
    else:
        form = SignUpForm()
    return render(request, "landing/registration/signup.html", {"form": form})


@method_decorator(login_required, name="dispatch")
class UserUpdateView(UpdateView):
    """
    Allows users to update their details
    """

    template_name = "app/home/user_details.html"
    form_class = UserDetailUpdateForm
    success_url = reverse_lazy("user-update")
    http_method_names = ['get', 'post']

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
    http_method_names = ['get',]

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
    http_method_names = ['get',]

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
