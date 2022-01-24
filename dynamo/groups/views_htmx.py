from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

import groups.constants as c
from groups.forms import GroupForm, GroupImageForm, GroupAnnouncementForm
from groups.models import Group, Membership, GroupAnnouncement
from groups.utils import get_membership_level, get_filtered_collaborations
from groups.views import get_membership_count


@login_required()
def group_update_view(request, slug):
    """
    HTMX VIEW - Allows group updates with no reload
    Sends back "app/group/partials/header/main.html", to replace the content in #group_page_header
    If "group_update_modal": True is in the context (and the form), a modal will be rendered
    (with error messages, if appropriate)
    """

    group = get_object_or_404(Group, slug=slug)

    form = GroupForm(request.POST or None, instance=group)

    if request.user.is_authenticated:
        membership_level = get_membership_level(request.user, group)
    else:
        membership_level = None

    if request.method == "POST" and form.is_valid():
        form.save()
        return render(request,
                      "app/group/partials/header/main.html", {
                          "group": group,
                          "membership_level": membership_level,
                          "membership_count": get_membership_count(group),
                      })

    return render(request,
                  "app/group/partials/header/main.html", {
                      "group": group,
                      "membership_level": membership_level,
                      "membership_count": get_membership_count(group),
                      "group_update_modal": True,
                      "form": form,
                  })


@login_required()
def group_image_view(request, slug):
    """
    HTMX VIEW - Allows group image updates with no reload
    Sends back "app/group/partials/header/main.html", to replace the content in #group_page_header
    If "group_image_modal": True is in the context (and the form), a modal will be rendered
    (with error messages, if appropriate)
    """

    group = get_object_or_404(Group, slug=slug)

    form = GroupImageForm(request.POST or None, request.FILES or None, instance=group)

    if request.user.is_authenticated:
        membership_level = get_membership_level(request.user, group)
    else:
        membership_level = None

    if request.method == "POST" and form.is_valid():
        form.save()
        return render(request,
                      "app/group/partials/header/main.html", {
                          "group": group,
                          "membership_level": membership_level,
                          "membership_count": get_membership_count(group),
                      })

    return render(request,
                  "app/group/partials/header/main.html", {
                      "group": group,
                      "membership_level": membership_level,
                      "membership_count": get_membership_count(group),
                      "group_image_modal": True,
                      "form": form,
                  })


@login_required()
def group_membership_view(request, slug):
    """
    HTMX VIEW - Populates list of memberships of the specified type - set by select object on front end
    """

    # if the filter is not set, we send back only pending membership requests
    membership_filter = request.GET.get('membership_filter', c.MEMBERSHIP_STATUS_PENDING)
    group = get_object_or_404(Group, slug=slug)

    # Clear the session, if it is being used
    if request.session.get('selected_memberships', None):
        del request.session['selected_memberships']

    if membership_filter in c.MEMBERSHIP_FILTERS:
        return render(request,
                      "app/group/partials/memberships/list.html",
                      {
                          "membership_list": Membership.objects.filter(
                              group__slug=slug, status=membership_filter
                          ),
                          "membership_filter": membership_filter,
                          "group": group,
                          "membership_count": get_membership_count(group),
                      })
    else:
        return HttpResponse()


@login_required()
def group_membership_selector_view(request, slug, pk, membership_filter):
    """
    HTMX VIEW - Allows admins to select memberships in order to process in bulk

    The same view is used for adding/removing - there is no point where a user would want to add an select
    twice so we can assume that if the request id received is stored in session, the user wants to remove it.

    The view responds with an HTML partial (either the action bar, or nothing in its place),
    which is appended to the bottom of the requests list.
    """

    # Grab the current list, or create one - an empty list
    selected_memberships = request.session.get('selected_memberships', [])
    group = get_object_or_404(Group, slug=slug)

    # CASE 1: Removing an agency - Update the shortlist (in session), render the response
    if pk in selected_memberships:
        selected_memberships.remove(pk)
        if len(selected_memberships) == 0:
            del request.session['selected_memberships']
            return HttpResponse()
        else:
            request.session['selected_memberships'] = selected_memberships
            return render(request,
                          "app/group/partials/memberships/action_bar.html", {
                              "selected_memberships": len(selected_memberships),
                              "membership_filter": membership_filter,
                              "group": group,
                          })

    # CASE 2: Adding an agency to the shortlist - Update the shortlist (in session), render the response
    else:
        selected_memberships.append(pk)
        request.session['selected_memberships'] = selected_memberships
        return render(request,
                      "app/group/partials/memberships/action_bar.html", {
                          "selected_memberships": len(selected_memberships),
                          "membership_filter": membership_filter,
                          "group": group,
                      })


@login_required()
def group_membership_handler_view(request, slug, action, membership_filter):
    """
    HTMX VIEW - Allows admins process memberships stored in session

    The same view is used for approving/ignoring/clearing/removing - the method is provided in the htmx attributes on
    the template

    The view responds with a partial that contains javascript update state on the front end. (eg. update member
    count or check/uncheck boxes)
    """

    # Grab the current list, or return None is there isn't one
    if not (selected_memberships := request.session.get('selected_memberships', None)):
        return None

    group = get_object_or_404(Group, slug=slug)

    if action == c.MEMBERSHIP_ACTION_CLEAR_SELECTION:
        # Get the ids (so that we can 'uncheck' the checkboxes on front end)
        check_box_ids = [f"checkbox_for_{membership_id}" for membership_id in request.session['selected_memberships']]

        # Remove the list from session
        del request.session['selected_memberships']

        return render(request,
                      "app/group/partials/memberships/template_js/uncheck_membership_tickboxes.html",
                      {"check_box_ids": check_box_ids})

    elif action == c.MEMBERSHIP_ACTION_APPROVE:
        # Get the memberships and mark them as approved
        Membership.objects.filter(id__in=selected_memberships).update(
            status=c.MEMBERSHIP_STATUS_CURRENT,
            updated_by=request.user,
        )

    elif action == c.MEMBERSHIP_ACTION_IGNORE:
        # Get the memberships and mark them as ignored
        Membership.objects.filter(id__in=selected_memberships).update(
            status=c.MEMBERSHIP_STATUS_IGNORED,
            updated_by=request.user,
        )

    elif action == c.MEMBERSHIP_ACTION_MAKE_ADMIN:
        # Get the memberships and make admin
        Membership.objects.filter(id__in=selected_memberships).update(
            status=c.MEMBERSHIP_STATUS_ADMIN,
            updated_by=request.user,
        )

    elif action == c.MEMBERSHIP_ACTION_REMOVE:
        # Get the memberships and delete them
        Membership.objects.filter(id__in=selected_memberships).delete()

    # Remove the list from session
    del request.session['selected_memberships']

    if membership_filter in c.MEMBERSHIP_FILTERS:
        membership_list = Membership.objects.filter(
            group=group, status=membership_filter
        )
    else:
        membership_list = Membership.objects.none()

    return render(request, "app/group/partials/memberships/main.html",
                  {
                      "group": group,
                      "membership_list": membership_list,
                      "membership_filter": membership_filter,
                      "membership_count": get_membership_count(group),
                  })


@login_required()
def group_collaboration_list(request, slug):
    """
    HTMX VIEW - Populates the list of collaborations - either All, Planning, ongoing,
    """

    # Get group
    group = get_object_or_404(Group, slug=slug)

    # Get filter parameter - if not set, send back a 'hidden' response (Empty HTML string)
    collaboration_list_filter = request.GET.get('collaboration_list_filter', 'HIDE')
    if collaboration_list_filter == 'HIDE':
        return HttpResponse()

    collaborations = get_filtered_collaborations(group, collaboration_list_filter)

    return render(request,
                  "app/group/partials/collaborations/list.html", {
                      "collaboration_list": collaborations,
                      "group": group
                  })


@login_required()
def group_announcement_list(request, slug):
    """
    HTMX VIEW - Populates the list of announcements - either Latest, All, or None
    """

    # if the filter is not set, we hide the announcements
    announcement_list_filter = request.GET.get('announcement_list_filter', 'HIDE')
    group = get_object_or_404(Group, slug=slug)

    if announcement_list_filter == 'HIDE':
        return HttpResponse()

    match announcement_list_filter:
        case c.ANNOUNCEMENTS_FILTER_LATEST:
            announcements = GroupAnnouncement.objects.filter(group=group)[:1]
        case c.ANNOUNCEMENTS_FILTER_ALL:
            announcements = GroupAnnouncement.objects.filter(group=group)
        case _:
            announcements = GroupAnnouncement.objects.none()

    return render(request,
                  "app/group/partials/announcements/list.html", {
                      "group": group,
                      "announcement_list": announcements
                  })


@login_required()
def group_announcement_delete(request, slug, pk):
    """
    HTMX VIEW - Allows announcement updates with no reload
    Sends back "app/group/partials/announcements/list.html", to replace the content in #list_of_announcements
    If "announcement_delete_modal": True is in the context (and the form), a modal will be rendered
    (with error messages, if appropriate)
    """

    group = get_object_or_404(Group, slug=slug)
    announcement = get_object_or_404(GroupAnnouncement, pk=pk)

    if request.method == "POST":
        announcement.delete()
        return render(request,
                      "app/group/partials/announcements/list.html", {
                          "announcement_list": GroupAnnouncement.objects.filter(group=group)[:1],
                          "group": group,
                      })

    return render(request,
                  "app/group/partials/announcements/list.html", {
                      "announcement_list": GroupAnnouncement.objects.filter(group=group)[:1],
                      "group": group,
                      "announcement_delete_modal": True,
                      "announcement": announcement,
                  })


@login_required()
def group_announcement_create(request, slug):
    """
    HTMX VIEW - Allows new announcements with no reload
    Sends back "app/group/partials/announcements/list.html", to replace the content in #list_of_announcements
    If "announcement_create_modal": True is in the context (and the form), a modal will be rendered
    (with error messages, if appropriate)
    """

    group = get_object_or_404(Group, slug=slug)

    form = GroupAnnouncementForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        announcement = form.save(commit=False)
        announcement.group = group
        announcement.user = request.user
        announcement.save()
        return render(request,
                      "app/group/partials/announcements/list.html", {
                          "announcement_list": GroupAnnouncement.objects.filter(group=group)[:1],
                          "group": group,
                      })

    return render(request,
                  "app/group/partials/announcements/list.html", {
                      "announcement_list": GroupAnnouncement.objects.filter(group=group)[:1],
                      "group": group,
                      "announcement_create_modal": True,
                      "form": form,
                  })


@login_required()
def group_announcement_update(request, slug, pk):
    """
    HTMX VIEW - Allows announcement updates with no reload
    Sends back "app/group/partials/announcements/list.html", to replace the content in #list_of_announcements
    If "announcement_update_modal": True is in the context (and the form), a modal will be rendered
    (with error messages, if appropriate)
    """

    group = get_object_or_404(Group, slug=slug)
    group_announcement = get_object_or_404(GroupAnnouncement, pk=pk)

    form = GroupAnnouncementForm(request.POST or None, instance=group_announcement)

    if request.method == "POST" and form.is_valid():
        form.save()
        return render(request,
                      "app/group/partials/announcements/list.html", {
                          "announcement_list": GroupAnnouncement.objects.filter(group=group)[:1],
                          "group": group,
                      })

    return render(request,
                  "app/group/partials/announcements/list.html", {
                      "announcement_list": GroupAnnouncement.objects.filter(group=group)[:1],
                      "group": group,
                      "announcement_update_modal": True,
                      "announcement": group_announcement,
                      "form": form,
                  })
