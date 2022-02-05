from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView, ListView

from collaborations.models import Collaboration
from groups.constants import MEMBERSHIP_STATUS_CURRENT, MEMBERSHIP_STATUS_ADMIN
from groups.models import Group, Membership
from users.forms import SignUpForm, UserDetailUpdateForm
from users.utils import get_users_filtered_collaborations


def sign_up_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get("email")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(
                email=email, password=raw_password, request=request
            )
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
    success_url = reverse_lazy('user-update')

    def get_object(self, queryset=None):
        return self.request.user


@method_decorator(login_required, name="dispatch")
class UserGroupListView(ListView):
    """
    Shows all of the users groups
    """

    template_name = "app/home/user_groups.html"
    model = Group
    context_object_name = 'groups'

    def get_queryset(self):
        memberships = Membership.objects.filter(
            user=self.request.user,
            status__in=[MEMBERSHIP_STATUS_CURRENT, MEMBERSHIP_STATUS_ADMIN]
        ).values_list('group', flat=True)
        return Group.objects.filter(pk__in=memberships)


@method_decorator(login_required, name="dispatch")
class UserCollaborationListView(ListView):
    """
    Shows all of the users Collaborations, serving both full page and htmx requests
    """

    template_name = "app/home/user_collaborations.html"
    model = Collaboration

    def get_template_names(self):
        """
        If this is an HTMX request, we return a partial,
        rather than the entire page
        """
        if self.request.htmx:
            return "app/home/partials/collaboration_list.html"
        return "app/home/user_collaborations.html"

    def get_queryset(self):
        """
        If a filter is specified, we send back a subset of the users groups, rather than all of them.
        """
        # Get filter parameter
        if collaboration_list_filter := self.request.GET.get('collaboration_list_filter', None):
            return get_users_filtered_collaborations(self.request.user, collaboration_list_filter)

        return Collaboration.objects.filter(related_group__members=self.request.user)



