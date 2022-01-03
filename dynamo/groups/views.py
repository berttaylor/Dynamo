from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
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
from groups.models import Group, GroupAnnouncement, Membership


class GroupListView(ListView):
    """
    List of all groups, allowing a user to search, and find causes that appeal to them
    """

    model = Group
    template_name = "dashboard/group/group_search.html"
    paginate_by = 30


class GroupDetailView(FormMixin, DetailView):
    """
    Shows all information regarding a group, as well as
        - Chat Messages
        - Join Requests
        - Collaborations
    """

    template_name = "dashboard/group/group_detail.html"
    model = Group
    form_class = GroupMessageForm

    def get_context_data(self, **kwargs):
        """
        We override get_context_data to populate the search field choices
        """

        context = super(GroupDetailView, self).get_context_data(**kwargs)

        group = self.get_object()
        user_is_admin = True if group.memberships.filter(user=self.request.user, group=group, is_admin=True) else False

        context.update(
            {

                "chat_messages": Message.objects.filter(group=group),
                "collaborations": Collaboration.objects.filter(related_group=group),
                "chat_form": GroupMessageForm(initial={"group": group}),
                "announcements": GroupAnnouncement.objects.filter(group=group),
                "membership_list_view": c.MEMBERSHIP_STATUS_PENDING,
                "membership_list": group.memberships.filter(status=c.MEMBERSHIP_STATUS_PENDING),
                "user_is_admin": user_is_admin,
                "member_count": Membership.custom_manager.current().filter(group=group).count(),
                "admin_count": Membership.custom_manager.admin().filter(group=group).count(),
                "subscriber_count": Membership.custom_manager.subscribers().filter(group=group).count()
            },
        )

        # Clear the session, if it is being used
        if self.request.session.get('selected_memberships', None):
            del self.request.session['selected_memberships']

        return context


@method_decorator(login_required, name="dispatch")
class GroupCreateView(CreateView):
    """
    Allows users to create a new group
    """

    template_name = "dashboard/group/group_create.html"
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
        # TODO: ned to add through defaults
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

    template_name = "dashboard/group/group_update.html"
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
    template_name = "dashboard/group/group_delete.html"
    model = Group

    def get_success_url(self):
        return reverse("group-list")


@login_required()
def group_join_view(request, slug):
    """
    FUNCTIONAL VIEW - Allows users to request to join groups.
    """

    # Get  variables
    user, group = request.user, Group.objects.get(slug=slug)

    # If the user is already a member, send an error
    if user in group.members.all().exclude(status=c.MEMBERSHIP_STATUS_LEFT):
        messages.error(request, "Membership object already exists")
        return HttpResponseRedirect(
            reverse_lazy(
                "group-detail",
                kwargs={"slug": group.slug},
            )
        )

    else:
        # If they have previously been in the group, we reactivate their membership
        if Membership.objects.filter(user=user, group=group).exists():
            Membership.objects.filter(user=user, group=group).update(status=c.MEMBERSHIP_STATUS_PENDING)
        else:
            Membership.objects.create(user=user, group=group)

        messages.success(
            request, "Membership Requested: Awaiting confirmation from group admin"
        )

        return HttpResponseRedirect(
            reverse_lazy(
                "group-detail",
                kwargs={"slug": group.slug},
            )
        )


@login_required()
def group_leave_view(request, slug):
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

    else:
        # get membership
        membership = Membership.objects.get(user=user, group=group)

        # If the user is last admin of the group, send error
        if membership.is_admin and not group.memberships.filter(is_admin=True).exclude(pk=membership.pk).exists():
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
            membership.update(status=c.MEMBERSHIP_STATUS_LEFT, is_admin=False, is_subscribed=False)
            messages.success(request, "You have left the group")
            return HttpResponseRedirect(
                reverse_lazy(
                    "group-detail",
                    kwargs={"slug": group.slug},
                )
            )
