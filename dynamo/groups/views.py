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
from groups.models import Group, GroupAnnouncement, GroupJoinRequest
from django.utils import timezone

from users.models import User


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

        context.update(
            {

                "chat_messages": Message.objects.filter(group=group),
                "collaborations": Collaboration.objects.filter(related_group=group),
                "chat_form": GroupMessageForm(initial={"group": group}),
                "announcements": GroupAnnouncement.objects.filter(group=group),
                "membership_list": GroupJoinRequest.objects.filter(
                    group=group, status=c.REQUEST_STATUS_PENDING
                ),
                "membership_list_view": "PENDING",
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


@login_required()
def htmx_membership_view_handler(request, group_id):
    """
    HTMX VIEW - Sends back list of memberships of the specified type - set by select object on front end
    """

    # if not status is set, we send back only pending membership requests
    membership_list_view = request.GET.get('membership_list_view', 'PENDING')

    # Clear the session, if it is being used
    if request.session.get('selected_memberships', None):
        del request.session['selected_memberships']

    match membership_list_view:
        case "PENDING":
            return render(request,
                          "dashboard/group/memberships/group_members_list.html",
                          {
                              "membership_list": GroupJoinRequest.objects.filter(
                                  group_id=group_id, status=c.REQUEST_STATUS_PENDING
                              ),
                              "membership_list_view": membership_list_view,
                              "group_id": group_id,
                          })

        case "MEMBERS":
            return render(request,
                          "dashboard/group/memberships/group_members_list.html",
                          {
                              "membership_list": GroupJoinRequest.objects.filter(
                                  group_id=group_id, status=c.REQUEST_STATUS_APPROVED
                              ),
                              "membership_list_view": membership_list_view,
                              "group_id": group_id,
                          })

        case "DENIED":
            return render(request,
                          "dashboard/group/memberships/group_members_list.html",
                          {
                              "membership_list": GroupJoinRequest.objects.filter(
                                  group_id=group_id, status=c.REQUEST_STATUS_DENIED
                              ),
                              "membership_list_view": membership_list_view,
                              "group_id": group_id,
                          })

        case "HIDE":
            return HttpResponse("")


@login_required()
def htmx_membership_selector(request, group_id, membership_id, membership_list_view):
    """
    HTMX VIEW - Allows admins to select memberships in order to process in bulk

    The same view is used for adding/removing - there is no point where a user would want to add an select
    twice so we can assume that if the request id received is stored in session, the user wants to remove it.

    The view responds with an HTML partial (either the action bar, or nothing in its place),
    which is appended to the bottom of the requests list.
    """

    # Grab the current list, or create one - an empty list
    selected_memberships = request.session.get('selected_memberships', [])

    # CASE 1: Removing an agency - Update the shortlist (in session), render the response
    if membership_id in selected_memberships:
        selected_memberships.remove(membership_id)
        request.session['selected_memberships'] = selected_memberships
        if len(selected_memberships) > 0:
            print(selected_memberships)
            return render(request,
                          "dashboard/group/memberships/group_members_action_bar.html", {
                              "selected_memberships": len(selected_memberships),
                              "membership_list_view": membership_list_view,
                              "group_id": group_id,
                          })
        else:
            print(selected_memberships)
            return HttpResponse("")

    # CASE 2: Adding an agency to the shortlist - Update the shortlist (in session), render the response
    else:
        selected_memberships.append(membership_id)
        request.session['selected_memberships'] = selected_memberships
        print(selected_memberships)
        return render(request,
                      "dashboard/group/memberships/group_members_action_bar.html", {
                          "selected_memberships": len(selected_memberships),
                          "membership_list_view": membership_list_view,
                          "group_id": group_id,
                      })


@login_required()
def htmx_membership_handler(request, group_id, action, membership_list_view):
    """
    HTMX VIEW - Allows admins process memberships stored in session

    The same view is used for approving/ignoring/clearing - the method is provided in the htmx attributes on
    the template

    The view responds with a partial that contains javascript update state on the front end. (eg. update member
    count or check/uncheck boxes)
    """

    # TODO - Transaction atomic

    # Grab the current list, or return None is there isnt one
    if not (selected_memberships := request.session.get('selected_memberships', None)):
        return None

    group = Group.objects.get(pk=group_id)

    if action == "CLEAR":
        # Get the ids (so that we can 'uncheck' the checkboxes on front end)
        check_box_ids = [f"checkbox_for_{membership_id}" for membership_id in request.session['selected_memberships']]

        # Remove the list from session
        del request.session['selected_memberships']

        return render(request,
                      "dashboard/group/memberships/template_js/uncheck_membership_tickboxes.html",
                      {"check_box_ids": check_box_ids})

    elif action == "APPROVE":
        # Get the memberships and mark them as approved
        GroupJoinRequest.objects.filter(id__in=selected_memberships).update(
            status=c.REQUEST_STATUS_APPROVED,
            handled_by=request.user,
            handled_date=timezone.now()
        )

        # Add the users to the group
        users = User.objects.filter(group_join_requests_made__in=selected_memberships)

        for user in users:
            group.members.add(user)

        # Remove the list from session
        del request.session['selected_memberships']

        # Get new queryset
        match membership_list_view:
            case "PENDING":
                membership_list = GroupJoinRequest.objects.filter(
                    group_id=group_id, status=c.REQUEST_STATUS_PENDING
                )
            case "MEMBERS":
                membership_list = GroupJoinRequest.objects.filter(
                    group_id=group_id, status=c.REQUEST_STATUS_APPROVED
                )

            case "DENIED":
                membership_list = GroupJoinRequest.objects.filter(
                    group_id=group_id, status=c.REQUEST_STATUS_DENIED
                )

            case _:
                membership_list = GroupJoinRequest.objects.none()

        return render(request, "dashboard/group/memberships/group_members_list.html",
                      {
                          "membership_list": membership_list,
                          "membership_list_view": membership_list_view,
                          "group_id": group_id,
                          "new_member_count": group.members.all().count(),
                          "new_subscriber_count": group.subscribers.all().count(),
                          "new_admin_count": group.admins.all().count(),
                      })

    elif action == "IGNORE":
        # Get the memberships and mark them as ignored
        GroupJoinRequest.objects.filter(id__in=selected_memberships).update(
            status=c.REQUEST_STATUS_DENIED,
            handled_by=request.user,
            handled_date=timezone.now()
        )

        # Remove the list from session
        del request.session['selected_memberships']

        # Get new queryset
        match membership_list_view:
            case "PENDING":
                membership_list = GroupJoinRequest.objects.filter(
                    group_id=group_id, status=c.REQUEST_STATUS_PENDING
                )
            case "MEMBERS":
                membership_list = GroupJoinRequest.objects.filter(
                    group_id=group_id, status=c.REQUEST_STATUS_APPROVED
                )

            case "DENIED":
                membership_list = GroupJoinRequest.objects.filter(
                    group_id=group_id, status=c.REQUEST_STATUS_DENIED
                )

            case _:
                membership_list = GroupJoinRequest.objects.none()

        return render(request, "dashboard/group/memberships/group_members_list.html",
                      {
                          "membership_list": membership_list,
                          "membership_list_view": membership_list_view,
                          "group_id": group_id,
                      })

    elif action == "REMOVE":
        # Get the memberships and mark them as ignored
        GroupJoinRequest.objects.filter(id__in=selected_memberships).update(
            status=c.REQUEST_STATUS_DENIED,
            handled_by=request.user,
            handled_date=timezone.now()
        )

        # Add the users to the group
        users = User.objects.filter(group_join_requests_made__in=selected_memberships)

        for user in users:
            group.members.remove(user)

        # Remove the list from session
        del request.session['selected_memberships']

        # Get new queryset
        match membership_list_view:
            case "PENDING":
                membership_list = GroupJoinRequest.objects.filter(
                    group_id=group_id, status=c.REQUEST_STATUS_PENDING
                )
            case "MEMBERS":
                membership_list = GroupJoinRequest.objects.filter(
                    group_id=group_id, status=c.REQUEST_STATUS_APPROVED
                )

            case "DENIED":
                membership_list = GroupJoinRequest.objects.filter(
                    group_id=group_id, status=c.REQUEST_STATUS_DENIED
                )

            case _:
                membership_list = GroupJoinRequest.objects.none()

        return render(request, "dashboard/group/memberships/group_members_list.html",
                      {
                          "membership_list": membership_list,
                          "membership_list_view": membership_list_view,
                          "group_id": group_id,
                          "new_member_count": group.members.all().count(),
                          "new_subscriber_count": group.subscribers.all().count(),
                          "new_admin_count": group.admins.all().count(),
                      })
