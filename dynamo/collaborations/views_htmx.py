from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy

import collaborations.constants as c
from collaborations.forms import MilestoneForm, TaskForm
from collaborations.models import Collaboration, CollaborationTask, CollaborationMilestone
from collaborations.utils import get_all_elements
from modals.forms import TaskCompleteForm
from users.models import User


@login_required()
def task_create_view(request, collaboration_id):
    """
    HTMX VIEW - Allows tasks to be added
    """
    # TODO: Secure and set methods

    # Get  variables
    name = str(request.POST["name"])
    assigned_to_id = str(request.POST["assigned_to"])

    collaboration = get_object_or_404(Collaboration, pk=collaboration_id)
    assigned_to = get_object_or_404(User, pk=assigned_to_id)

    CollaborationTask.objects.create(collaboration=collaboration, name=name, assigned_to=assigned_to)

    return render(request,
                  "app/collaborations/partials/elements/main.html", {
                      "task_form": TaskForm(
                          initial={"collaboration": collaboration},
                      ),
                      "milestone_form": MilestoneForm(
                          initial={"collaboration": collaboration}
                      ),
                      "elements": get_all_elements(collaboration),
                      "collaboration": collaboration,
                  })


@login_required()
def milestone_create_view(request, collaboration_id):
    """
    HTMX VIEW - Allows task messages to be added
    """
    # TODO: Secure and set methods

    # Get  variables
    name = str(request.POST["name"])
    target_date = str(request.POST["target_date"])

    collaboration = get_object_or_404(Collaboration, pk=collaboration_id)

    CollaborationMilestone.objects.create(collaboration=collaboration, name=name, target_date=target_date)

    return render(request,
                  "app/collaborations/partials/elements/main.html", {
                      "task_form": TaskForm(
                          initial={"collaboration": collaboration},
                      ),
                      "milestone_form": MilestoneForm(
                          initial={"collaboration": collaboration}
                      ),
                      "elements": get_all_elements(collaboration),
                      "collaboration": collaboration,
                  })


@login_required()
def task_delete_view(request, pk):
    """
    HTMX VIEW - Allows delete without refresh
    """

    task = get_object_or_404(CollaborationTask, pk=pk)

    collaboration = task.collaboration

    task.delete()

    return render(request,
                  "app/collaborations/partials/elements/main.html", {
                      "task_form": TaskForm(
                          initial={"collaboration": collaboration},
                      ),
                      "milestone_form": MilestoneForm(
                          initial={"collaboration": collaboration}
                      ),
                      "elements": get_all_elements(collaboration),
                      "collaboration": collaboration,
                  })


@login_required()
def milestone_delete_view(request, pk):
    """
    HTMX VIEW - Allows delete without refresh
    """
    milestone = get_object_or_404(CollaborationMilestone, pk=pk)

    collaboration = milestone.collaboration

    milestone.delete()

    return render(request,
                  "app/collaborations/partials/elements/main.html", {
                      "task_form": TaskForm(
                          initial={"collaboration": collaboration},
                      ),
                      "milestone_form": MilestoneForm(
                          initial={"collaboration": collaboration}
                      ),
                      "elements": get_all_elements(collaboration),
                      "collaboration": collaboration,
                  })


@login_required()
def htmx_task_status_update_view(request, pk, action):
    """
    HTMX VIEW - Allows completion of tasks with one click and no reload
    """

    task = get_object_or_404(CollaborationTask, pk=pk)

    collaboration = task.collaboration

    match action:
        case c.COMPLETE_TASK:
            task.completed_at = datetime.now()
            task.completed_by = request.user
            task.save()
        case c.UNDO_COMPLETE_TASK:
            task.completed_at = None
            task.completed_by = None
            task.save()
        case _:
            pass

    return render(request,
                  "app/collaborations/partials/elements/list/main.html", {
                      "elements": get_all_elements(collaboration),
                      "completion_percentage": collaboration.percent_completed,
                      "completion_percentage_update": True,
                      "task_completion_notes_required": True if task.completed_at and task.prompt_for_details_on_completion else False,
                      "form": TaskCompleteForm(instance=task),
                  })


@login_required()
def htmx_get_element_list_view(request, collaboration_pk):
    """
    HTMX VIEW - Sends back html list of elements
    """

    collaboration = get_object_or_404(Collaboration, pk=collaboration_pk)

    return render(request,
                  "app/collaborations/partials/elements/list/main.html", {
                      "elements": get_all_elements(collaboration),
                      "completion_percentage": collaboration.percent_completed,
                  })


@login_required()
def htmx_task_move_view(request, pk, position):
    """
    HTMX VIEW - Allows reordering of tasks.
    """

    task = get_object_or_404(CollaborationTask, pk=pk)

    if 0 <= int(position) < task.collaboration.number_of_elements:
        task.position = int(position)
        task.save()

    return HttpResponseRedirect(
        reverse_lazy('htmx-get-element-list',
                     kwargs={'collaboration_pk': task.collaboration.pk},
                     )
    )
