from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.views.generic.edit import FormMixin

import groups.constants as c
from chat.forms import GroupMessageForm
from chat.models import Message
from collaborations.models import Collaboration
from groups.models import Group, GroupJoinRequest
from django.utils import timezone


class GroupListView(ListView):
    """
    List of all groups, allowing a user to search, and find causes that appeal to them
    """

    model = Group
    template_name = "groups/group_search.html"
    paginate_by = 30


class GroupDetailView(FormMixin, DetailView):
    """
    Shows all information regarding a group, as well as
        - Chat Messages
        - Join Requests
        - Collaborations
    """

    template_name = "groups/group_detail.html"
    model = Group
    form_class = GroupMessageForm

    def get_context_data(self, **kwargs):
        """
        We override get_context_data to populate the search field choices
        """

        context = super(GroupDetailView, self).get_context_data(**kwargs)

        group = self.get_object()

        context.update(
            {
                "join_requests": GroupJoinRequest.objects.filter(
                    group=group, status=c.REQUEST_STATUS_PENDING
                ),
                "chat_messages": Message.objects.filter(group=group),
                "collaborations": Collaboration.objects.filter(related_group=group),
                "chat_form": GroupMessageForm(initial={"group": group}),
            },
        )

        return context


@method_decorator(login_required, name="dispatch")
class GroupCreateView(CreateView):
    """
    Allows users to create a new group
    """

    template_name = "groups/group_create.html"
    model = Group
    fields = (
        "name",
        "description",
    )

    def form_valid(self, form):
        """
        We override the form valid to add the user as admin and creator
        """

        # 1. Get user (if logged in)
        user = self.request.user
        if not user.is_authenticated:
            raise PermissionError
        form.instance.created_by = user

        # 2. Create group in db
        response = super(GroupCreateView, self).form_valid(form)
        group = self.object

        # 3. Add user to admin, members and subscribers
        group.admins.add(user)
        group.members.add(user)
        group.subscribers.add(user)
        group.save()

        return response

    def get_success_url(self):
        return reverse_lazy(
            "group-detail",
            kwargs={"slug": self.object.slug},
        )


@method_decorator(login_required, name="dispatch")
class GroupUpdateView(UpdateView):
    """
    Allows the user to update multiple fields on a group which they are the admin/creator of.
    """

    template_name = "groups/group_update.html"
    model = Group
    fields = [
        "name",
        "description",
    ]

    def get_success_url(self):
        return reverse_lazy(
            "group-detail",
            kwargs={"slug": self.object.slug},
        )


@method_decorator(login_required, name="dispatch")
class GroupDeleteView(DeleteView):
    template_name = "groups/group_delete.html"
    model = Group

    def get_success_url(self):
        return reverse("group-list")


@login_required()
def GroupJoinView(request, slug):
    """
    FUNCTIONAL VIEW - Allows users to request to join groups.
    """

    # Get  variables
    user, group = request.user, Group.objects.get(slug=slug)

    # If the user is already a member, send an error
    if user in group.members.all():
        messages.error(request, "You are already a member of this group")
        return HttpResponseRedirect(
            reverse_lazy(
                "group-detail",
                kwargs={"slug": group.slug},
            )
        )
    # If the user has already requested to join, send an error
    elif (
        GroupJoinRequest.objects.filter(user=user, group=group)
        .exclude(status=c.REQUEST_STATUS_APPROVED)
        .exists()
    ):
        messages.error(request, "You have an outstanding request to join this group")
        return HttpResponseRedirect(
            reverse_lazy(
                "group-detail",
                kwargs={"slug": group.slug},
            )
        )
    # If the user isn't in the group, and no outstanding request exists, create one.
    else:
        messages.success(
            request, "Membership Requested: Awaiting confirmation from group admin"
        )
        GroupJoinRequest.objects.create(user=user, group=group)
        return HttpResponseRedirect(
            reverse_lazy(
                "group-detail",
                kwargs={"slug": group.slug},
            )
        )


@login_required()
def GroupLeaveView(request, slug):
    """
    FUNCTIONAL VIEW - Allows users to leave groups
    """

    # Get  variables
    user, group = request.user, Group.objects.get(slug=slug)

    # If the user is not in the group , send an error
    if user not in group.members.all():
        messages.error(request, "You are not a member of this group")
        return HttpResponseRedirect(
            reverse_lazy(
                "group-detail",
                kwargs={"slug": group.slug},
            )
        )
    # If the user is last admin of the group, send error
    elif user in group.admins.all() and group.admins.all().count() == 1:
        messages.error(
            request, "You are the last admin. Assign another to leave the group"
        )
        return HttpResponseRedirect(
            reverse_lazy(
                "group-detail",
                kwargs={"slug": group.slug},
            )
        )
    # If the user is in the group, and isn't the last admin, let them leave.
    else:
        group.admins.remove(user)
        group.members.remove(user)
        group.subscribers.remove(user)

        messages.success(request, "You have left the group")

        return HttpResponseRedirect(
            reverse_lazy(
                "group-detail",
                kwargs={"slug": group.slug},
            )
        )


@login_required()
def GroupRequestApproveView(request, uuid):
    """
    FUNCTIONAL VIEW - Allows admins to approve join requests
    """

    # Get  variables
    handling_user = request.user
    join_request = GroupJoinRequest.objects.get(id=uuid)
    requesting_user = join_request.user

    # Check user permissions
    if handling_user not in join_request.group.admins.all():
        raise PermissionError

    # If all checks out, approve the request and redirect to detail page
    else:
        # update the request
        join_request.status = c.REQUEST_STATUS_APPROVED
        join_request.handled_by = handling_user
        join_request.handled_date = timezone.now()
        join_request.save()

        # add them to the group the request
        join_request.group.members.add(requesting_user)
        join_request.group.subscribers.add(requesting_user)
        messages.success(
            request,
            f"'{requesting_user}''s request to join '{join_request.group}' was approved",
        )
        return HttpResponseRedirect(
            reverse_lazy(
                "group-detail",
                kwargs={"slug": join_request.group.slug},
            )
        )


@login_required()
def GroupRequestDenyView(request, uuid):
    """
    FUNCTIONAL VIEW - Allows admins to deny join requests
    """

    # Get  variables
    handling_user = request.user
    join_request = GroupJoinRequest.objects.get(id=uuid)
    requesting_user = join_request.user

    # Check user permissions
    if handling_user not in join_request.group.admins.all():
        raise PermissionError

    # If all checks out, deny the request and redirect to detail page
    else:
        join_request.status = c.REQUEST_STATUS_DENIED
        join_request.handled_by = handling_user
        join_request.handled_date = timezone.now()
        join_request.save()
        messages.success(
            request,
            f"'{requesting_user}''s request to join '{join_request.group}' was denied",
        )
        return HttpResponseRedirect(
            reverse_lazy(
                "group-detail",
                kwargs={"slug": join_request.group.slug},
            )
        )
