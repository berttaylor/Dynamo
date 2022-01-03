
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

import groups.constants as c
from groups.models import Group, Membership


@login_required()
def htmx_membership_list(request, group_id):
    """
    HTMX VIEW - Sends back list of memberships of the specified type - set by select object on front end
    """

    # if the filter is not set, we send back only pending membership requests
    membership_list_view = request.GET.get('membership_list_view', c.MEMBERSHIP_STATUS_PENDING)

    # Clear the session, if it is being used
    if request.session.get('selected_memberships', None):
        del request.session['selected_memberships']

    if membership_list_view in c.MEMBERSHIP_STATUS_CHOICES_DICT:
        return render(request,
                      "dashboard/group/memberships/group_members_list.html",
                      {
                          "membership_list": Membership.objects.filter(
                              group_id=group_id, status=membership_list_view
                          ),
                          "membership_list_view": membership_list_view,
                          "group_id": group_id,
                      })
    else:
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
        if len(selected_memberships) == 0:
            print(selected_memberships)
            del request.session['selected_memberships']
            return HttpResponse("")
        else:
            print(selected_memberships)
            request.session['selected_memberships'] = selected_memberships
            return render(request,
                          "dashboard/group/memberships/group_members_action_bar.html", {
                              "selected_memberships": len(selected_memberships),
                              "membership_list_view": membership_list_view,
                              "group_id": group_id,
                          })

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

    The same view is used for approving/ignoring/clearing/removing - the method is provided in the htmx attributes on
    the template

    The view responds with a partial that contains javascript update state on the front end. (eg. update member
    count or check/uncheck boxes)
    """

    # Grab the current list, or return None is there isn't one
    if not (selected_memberships := request.session.get('selected_memberships', None)):
        return None

    group = Group.objects.get(pk=group_id)

    if action == c.MEMBERSHIP_ACTION_CLEAR_SELECTION:
        # Get the ids (so that we can 'uncheck' the checkboxes on front end)
        check_box_ids = [f"checkbox_for_{membership_id}" for membership_id in request.session['selected_memberships']]

        # Remove the list from session
        del request.session['selected_memberships']

        return render(request,
                      "dashboard/group/memberships/template_js/uncheck_membership_tickboxes.html",
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

    elif action == c.MEMBERSHIP_ACTION_REMOVE:
        # Get the memberships and mark them as removed
        Membership.objects.filter(id__in=selected_memberships).update(
            status=c.MEMBERSHIP_STATUS_REMOVED,
            updated_by=request.user,
        )

    # Remove the list from session
    del request.session['selected_memberships']

    if membership_list_view in c.MEMBERSHIP_STATUS_CHOICES_DICT:
        membership_list = Membership.objects.filter(
            group_id=group_id, status=membership_list_view
        )
    else:
        membership_list = Membership.objects.none()

    return render(request, "dashboard/group/memberships/group_members_list.html",
                  {
                      "membership_list": membership_list,
                      "membership_list_view": membership_list_view,
                      "group_id": group_id,
                      "new_member_count": group.memberships.all().filter(status=c.MEMBERSHIP_STATUS_CURRENT).count(),
                      "new_subscriber_count": group.memberships.all().filter(is_subscribed=True).count(),
                      "new_admin_count": group.memberships.all().filter(is_admin=True).count(),
                  })
