from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views.generic import (
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
from groups.utils import get_membership_level, get_membership_count


class GroupDetailView(FormMixin, DetailView):
    """
    Shows all information regarding a group, as well as populating the initial state for the below page sections
    (which are then updated through htmx)
        - Message Board
        - Memberships
        - Announcements
        - Collaborations
    """

    template_name = "app/group/main.html"
    model = Group
    form_class = GroupMessageForm

    def get_context_data(self, **kwargs):
        """
        We override get_context_data to populate the search field choices
        """

        context = super(GroupDetailView, self).get_context_data(**kwargs)

        group = self.get_object()

        if self.request.user.is_authenticated:
            membership_level = get_membership_level(self.request.user, group)
        else:
            membership_level = None

        context.update(
            {
                "membership_level": membership_level,
                "membership_count": get_membership_count(group),
                "chat_form": GroupMessageForm(initial={"group": group}),
                "chat_messages": Message.objects.filter(group=group),
                "collaboration_filter": c.COLLABORATION_STATUS_ALL,
                "collaboration_list": Collaboration.objects.filter(related_group=group),
                "announcement_filter": c.ANNOUNCEMENTS_FILTER_LATEST,
                "announcement_list": GroupAnnouncement.objects.filter(group=group)[:1],
                "membership_filter": c.MEMBERSHIP_STATUS_PENDING,
                "membership_list": group.memberships.filter(status=c.MEMBERSHIP_STATUS_PENDING)
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

    template_name = "app/auxiliary/group/create.html"
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

        # 3. Add user as admin, members and subscribers
        Membership.objects.create(user=user, group=group, status=c.MEMBERSHIP_STATUS_ADMIN)

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

    template_name = "app/auxiliary/group/update.html"
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
    template_name = "app/auxiliary/group/delete.html"
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
    if Membership.objects.filter(user=user, group=group):
        messages.error(request, "Membership object already exists")
        return HttpResponseRedirect(
            reverse_lazy(
                "group-detail",
                kwargs={"slug": group.slug},
            )
        )

    # Otherwise, create the membership
    Membership.objects.create(user=user, group=group, status=c.MEMBERSHIP_STATUS_PENDING)

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
        if membership.status==c.MEMBERSHIP_STATUS_ADMIN and not group.memberships.filter(status=c.MEMBERSHIP_STATUS_ADMIN).exclude(pk=membership.pk).exists():
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
            membership.delete()
            messages.success(request, "You have left the group")
            return HttpResponseRedirect(
                reverse_lazy(
                    "group-detail",
                    kwargs={"slug": group.slug},
                )
            )


@method_decorator(login_required, name="dispatch")
class AnnouncementCreateView(CreateView):
    """
    Allows users to create a new announcement
    """

    template_name = "app/auxiliary/announcement/create.html"
    model = GroupAnnouncement
    fields = (
        "title",
        "body",
    )

    def get_initial(self):
        group = Group.objects.get(slug=self.kwargs.get("group_slug"))
        return {"related_group": group}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["group"] = Group.objects.get(slug=self.kwargs.get("group_slug"))
        return context

    def form_valid(self, form):
        """
        We override the form valid to add the user as admin and creator
        """

        # 1. Get user
        user = self.request.user
        if not user.is_authenticated:
            raise PermissionError

        form.instance.user = user
        form.instance.group = Group.objects.get(
            slug=self.kwargs.get("group_slug")
        )

        return super(AnnouncementCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "group-detail",
            kwargs={"slug": self.object.group.slug},
        )
