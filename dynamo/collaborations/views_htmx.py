from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic.list import BaseListView

import collaborations.constants as c
from collaborations.forms import MilestoneForm, TaskForm, TaskUpdateForm, TaskCompleteForm, CollaborationForm, \
    CollaborationImageForm, CollaborationCreateFormWithGroupSelection
from collaborations.models import Collaboration, CollaborationTask, CollaborationMilestone
from collaborations.utils import get_all_elements
from dynamo.settings import SITE_PROTOCOL, SITE_DOMAIN
from groups.constants import MEMBERSHIP_STATUS_ADMIN
from groups.models import Group
from groups.utils import get_filtered_collaborations


@login_required()
def group_collaboration_create_view(request, slug):
    """
    HTMX VIEW - Allows collaboration creation
    Sends back app/group/partials/collaborations/list.html, to replace the content in #list_of_collaborations
    If "collaboration_creation_modal": True is in the context (and the form), a modal will be rendered (with error messages, if appropriate)
    """

    form = CollaborationForm(request.POST or None)
    group = get_object_or_404(Group, slug=slug)

    if request.method == "POST":
        if form.is_valid():
            collaboration = form.save(commit=False)
            collaboration.related_group = group
            collaboration.created_by = request.user
            collaboration.created_at = datetime.now()
            collaboration.save()
            success_url = SITE_PROTOCOL + SITE_DOMAIN + reverse_lazy(
                "collaboration-detail",
                kwargs={"slug": collaboration.slug},
            )

            # Get filter parameter - if not set, send back a 'hidden' response (Empty HTML string)
            collaboration_list_filter = request.GET.get('collaboration_list_filter', None)
            if not collaboration_list_filter:
                collaboration_list_filter = request.POST.get('collaboration_list_filter', 'HIDE')

            return render(request,
                          "app/group/partials/collaborations/list.html", {
                              "group": group,
                              "collaboration_list": get_filtered_collaborations(group, collaboration_list_filter),
                              "collaboration_list_filter": collaboration_list_filter,
                              "form": form,
                              "success_url": success_url,
                          })

    return render(request,
                  "app/group/partials/modals/collaboration_create.html", {
                      "group": group,
                      "form": form,
                  })


@login_required()
def collaboration_delete_view(request, slug):
    """
    HTMX VIEW - Allows deletion of collaborations
    a get request will send back the confirmation modal (containing a delete link),
    to be appended to #collaboration_header
    If "task_delete_modal": True is in the context, a modal will be rendered
    """

    collaboration = get_object_or_404(Collaboration, slug=slug)

    if request.method == "POST":
        group = collaboration.related_group
        collaboration.delete()
        messages.success(request, "Collaboration Removed")
        return HttpResponseRedirect(
            reverse_lazy(
                "group-detail",
                kwargs={"slug": group.slug},
            )
        )

    return render(request,
                  "app/collaborations/partials/header/modals/collaboration_delete.html", {
                      "collaboration": collaboration,
                  })


@login_required()
def collaboration_update_view(request, slug):
    """
    HTMX VIEW - Allows collaborations to be updated without reload
    Sends back app/collaborations/partials/header/main.html, to replace the content in #collaboration_header
    If "collaboration_update_modal": True is in the context (and the form), a modal will be rendered (with error
    messages, if appropriate)
    """

    collaboration = get_object_or_404(Collaboration, slug=slug)

    form = CollaborationForm(request.POST or None, instance=collaboration)

    if request.method == "POST":
        if form.is_valid():
            form.save()
        return render(request,
                      "app/collaborations/partials/header/main.html", {
                          "collaboration": collaboration,
                      })

    return render(request,
                  "app/collaborations/partials/header/modals/collaboration_update.html", {
                      "collaboration": collaboration,
                      "form": form,
                  })


@login_required()
def collaboration_image_view(request, slug):
    """
    HTMX VIEW - Allows collaborations images to be updated without reload
    Sends back app/collaborations/partials/header/main.html, to replace the content in #collaboration_header
    If "collaboration_image_modal": True is in the context (and the form), a modal will be rendered (with error
    messages, if appropriate)
    """

    collaboration = get_object_or_404(Collaboration, slug=slug)

    form = CollaborationImageForm(request.POST or None, request.FILES or None, instance=collaboration)

    if request.method == "POST":
        if form.is_valid():
            form.save()
        return render(request,
                      "app/collaborations/partials/header/main.html", {
                          "collaboration": collaboration,
                      })

    return render(request,
                  'app/collaborations/partials/header/modals/collaboration_image_update.html', {
                      "collaboration": collaboration,
                      "form": form,
                  })


@login_required()
def collaboration_task_create_view(request, slug):
    """
    HTMX VIEW - Allows task creation with update and no reload
    Sends back a list of elements, to replace the content in #element_list
    If "task_creation_modal": True is in the context (and the form), a modal will be rendered (with error messages, if appropriate)
    """

    collaboration = get_object_or_404(Collaboration, slug=slug)
    form = TaskForm(request.POST or None, initial={"collaboration": collaboration})

    if request.method == "POST" and form.is_valid():
        task = form.save(commit=False)
        task.collaboration = collaboration
        task.save()

        return render(request,
                      "app/collaborations/partials/elements/list/main.html", {
                          "elements": get_all_elements(collaboration),
                          "collaboration": collaboration,
                      })

    return render(request,
                  "app/collaborations/partials/elements/list/main.html", {
                      "elements": get_all_elements(collaboration),
                      "collaboration": collaboration,
                      "task_creation_modal": True,
                      "form": form,
                  })


@login_required()
def collaboration_task_update_view(request, slug, pk):
    """
    HTMX VIEW - Allows task updates with update and no reload
    Sends back a list of elements, to replace the content in #element_list
    If "task_update_modal": True is in the context (and the form), a modal will be rendered (with error messages, if appropriate)
    """

    collaboration = get_object_or_404(Collaboration, slug=slug)
    task = get_object_or_404(CollaborationTask, pk=pk)

    form = TaskUpdateForm(request.POST or None, initial={"collaboration": collaboration}, instance=task)

    if request.method == "POST" and form.is_valid():
        form.save()
        return render(request,
                      "app/collaborations/partials/elements/list/main.html", {
                          "elements": get_all_elements(collaboration),
                          "collaboration": collaboration,
                      })

    return render(request,
                  "app/collaborations/partials/elements/list/main.html", {
                      "elements": get_all_elements(collaboration),
                      "collaboration": collaboration,
                      "task_update_modal": True,
                      "task": task,
                      "form": form,
                  })


@login_required()
def collaboration_task_notes_view(request, slug, pk):
    """
    HTMX VIEW - Allows task notes to be given with update and no reload
    Sends back a list of elements, to replace the content in #element_list
    If "task_completion_notes_modal": True is in the context (and the form), a modal will be
    rendered (with error messages, if appropriate)
    """

    collaboration = get_object_or_404(Collaboration, slug=slug)
    task = get_object_or_404(CollaborationTask, pk=pk)

    form = TaskCompleteForm(request.POST, request.FILES, instance=task)

    if request.method == "POST" and form.is_valid():
        form.save()
        return render(request,
                      "app/collaborations/partials/elements/list/main.html", {
                          "elements": get_all_elements(collaboration),
                          "collaboration": collaboration,
                      })

    return render(request,
                  "app/collaborations/partials/elements/list/main.html", {
                      "elements": get_all_elements(collaboration),
                      "collaboration": collaboration,
                      "task_completion_notes_modal": True,
                      "task": task,
                      "form": TaskCompleteForm(instance=task),
                  })


@login_required()
def collaboration_task_toggle_view(request, slug, pk, status):
    """
    HTMX VIEW - Allows completion of tasks with one click and no reload
    """

    task = get_object_or_404(CollaborationTask, pk=pk)

    collaboration = task.collaboration

    match status:
        case c.COMPLETE_TASK:
            task.completed_at = datetime.now()
            task.completed_by = request.user
            task.save()
        case c.UNDO_COMPLETE_TASK:
            task.completed_at = None
            task.completed_by = None
            task.file = None
            task.completion_notes = None
            task.save()
        case _:
            pass

    return render(request,
                  "app/collaborations/partials/elements/list/main.html", {
                      "elements": get_all_elements(collaboration),
                      "task_completion_notes_modal": True if task.completed_at and task.prompt_for_details_on_completion else False,
                      "form": TaskCompleteForm(instance=task),
                      "task": task,
                      "collaboration": collaboration,
                  })


@login_required()
def collaboration_task_delete_view(request, slug, pk):
    """
    HTMX VIEW - Allows deletion of tasks with reordering of elements
    Sends back a list of elements, to replace the content in #element_list
    If "task_delete_modal": True is in the context, a modal will be rendered
    """

    collaboration = get_object_or_404(Collaboration, slug=slug)
    task = get_object_or_404(CollaborationTask, pk=pk)

    if request.method == "POST":
        task.remove()
        return render(request,
                      "app/collaborations/partials/elements/list/main.html", {
                          "elements": get_all_elements(collaboration),
                          "collaboration": collaboration,
                      })

    return render(request,
                  "app/collaborations/partials/elements/list/main.html", {
                      "elements": get_all_elements(collaboration),
                      "collaboration": collaboration,
                      "task_delete_modal": True,
                      "task": task,
                  })


@login_required()
def collaboration_milestone_create_view(request, slug):
    """
    HTMX VIEW - Allows milestone creation with update and no reload
    Sends back a list of elements, to replace the content in #element_list
    If "milestone_creation_modal": True is in the context (and the form), a modal will be rendered (with error messages, if appropriate)
    """

    collaboration = get_object_or_404(Collaboration, slug=slug)
    form = MilestoneForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        milestone = form.save(commit=False)
        milestone.collaboration = collaboration
        milestone.save()

        return render(request,
                      "app/collaborations/partials/elements/list/main.html", {
                          "elements": get_all_elements(collaboration),
                          "collaboration": collaboration,
                      })

    return render(request,
                  "app/collaborations/partials/elements/list/main.html", {
                      "elements": get_all_elements(collaboration),
                      "collaboration": collaboration,
                      "milestone_creation_modal": True,
                      "form": form,
                  })


@login_required()
def collaboration_milestone_update_view(request, slug, pk):
    """
    HTMX VIEW - Allows milestone updates with update and no reload
    Sends back a list of elements, to replace the content in #element_list
    If "task_update_modal": True is in the context (and the form), a modal will be rendered (with error messages, if appropriate)
    """

    collaboration = get_object_or_404(Collaboration, slug=slug)
    milestone = get_object_or_404(CollaborationMilestone, pk=pk)

    form = MilestoneForm(request.POST or None, initial={"collaboration": collaboration}, instance=milestone)

    if request.method == "POST" and form.is_valid():
        form.save()
        return render(request,
                      "app/collaborations/partials/elements/list/main.html", {
                          "elements": get_all_elements(collaboration),
                          "collaboration": collaboration,
                      })

    return render(request,
                  "app/collaborations/partials/elements/list/main.html", {
                      "elements": get_all_elements(collaboration),
                      "collaboration": collaboration,
                      "milestone_update_modal": True,
                      "milestone": milestone,
                      "form": form,
                  })


@login_required()
def collaboration_milestone_delete_view(request, slug, pk):
    """
    HTMX VIEW - Allows deletion of milestones with reordering of elements
    Sends back a list of elements, to replace the content in #element_list
    If "task_delete_modal": True is in the context, a modal will be rendered
    """

    collaboration = get_object_or_404(Collaboration, slug=slug)
    milestone = get_object_or_404(CollaborationMilestone, pk=pk)

    if request.method == "POST":
        milestone.remove()
        return render(request,
                      "app/collaborations/partials/elements/list/main.html", {
                          "elements": get_all_elements(collaboration),
                          "collaboration": collaboration,
                      })

    return render(request,
                  "app/collaborations/partials/elements/list/main.html", {
                      "elements": get_all_elements(collaboration),
                      "collaboration": collaboration,
                      "milestone_delete_modal": True,
                      "milestone": milestone,
                  })


@login_required()
def collaboration_elements_list_view(request, slug):
    """
    HTMX VIEW - Sends back html list of elements
    """

    collaboration = get_object_or_404(Collaboration, slug=slug)

    return render(request,
                  "app/collaborations/partials/elements/list/main.html", {
                      "elements": get_all_elements(collaboration),
                      "collaboration": collaboration,
                  })


@login_required()
def collaboration_task_move_view(request, slug, pk, position):
    """
    HTMX VIEW - Allows reordering of tasks.
    """

    task = get_object_or_404(CollaborationTask, pk=pk)

    if 0 <= int(position) < task.collaboration.number_of_elements:
        task.position = int(position)
        task.save()

    return HttpResponseRedirect(
        reverse_lazy('collaboration-elements-list',
                     kwargs={'slug': task.collaboration.slug},
                     )
    )


@login_required()
def collaboration_milestone_move_view(request, slug, pk, position):
    """
    HTMX VIEW - Allows reordering of milestones
    """

    milestone = get_object_or_404(CollaborationMilestone, pk=pk)

    if 0 <= int(position) < milestone.collaboration.number_of_elements:
        milestone.position = int(position)
        milestone.save()

    return HttpResponseRedirect(
        reverse_lazy('collaboration-elements-list',
                     kwargs={'slug': milestone.collaboration.slug},
                     )
    )


@login_required()
def user_collaboration_create_view(request, slug):
    """
    HTMX VIEW - Allows milestone creation with update and no reload
    Sends back a list of elements, to replace the content in #element_list
    If "milestone_creation_modal": True is in the context (and the form), a modal will be rendered (with error messages, if appropriate)
    """

    collaboration = get_object_or_404(Collaboration, slug=slug)
    form = MilestoneForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        milestone = form.save(commit=False)
        milestone.collaboration = collaboration
        milestone.save()

        return render(request,
                      "app/collaborations/partials/elements/list/main.html", {
                          "elements": get_all_elements(collaboration),
                          "collaboration": collaboration,
                      })

    return render(request,
                  "app/collaborations/partials/elements/list/main.html", {
                      "elements": get_all_elements(collaboration),
                      "collaboration": collaboration,
                      "milestone_creation_modal": True,
                      "form": form,
                  })


@login_required()
def user_collaboration_create_view(request):
    """
    HTMX VIEW - Allows collaboration creation from the user-collaboration list view
    This is different to creating a collaboration from within a group page, as we need to confirm with the user which
    group the collaboration should belong to before we create it.
    Sends back the modal app/home/modals/collaboration_create.html, which is appended do the modal div.
    on successful submission, sends back a JS/htmx redirect to the new group page.
    """

    if not request.user.memberships.filter(status=MEMBERSHIP_STATUS_ADMIN):
        return render(request,
                      "app/home/modals/join_or_make_a_group.html", {
                      })

    form = CollaborationCreateFormWithGroupSelection(request.user, request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            collaboration = form.save(commit=False)
            collaboration.created_by = request.user
            collaboration.save()
            success_url = SITE_PROTOCOL + SITE_DOMAIN + reverse_lazy(
                "collaboration-detail",
                kwargs={"slug": collaboration.slug},
            )

            return render(request,
                          "app/snippets/js_redirect.html", {
                              "url": success_url,
                          })

    return render(request,
                  "app/home/modals/collaboration_create.html", {
                      "form": form,
                  })
