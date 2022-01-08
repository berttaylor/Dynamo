from itertools import chain

from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.db.models import Value, CharField
from django.db.models.expressions import Window
from django.db.models.functions import Rank
from django.shortcuts import render

from collaborations.forms import MilestoneForm, TaskForm
from collaborations.models import Collaboration, CollaborationTask, CollaborationMilestone
from users.models import User


def get_all_elements(collaboration):
    """
    This function works in three steps to produce a combined, ordered list of Tasks & Milestones
    """

    # 1. Get all Tasks, and annotate them with the type ('Task'), and their task number - which is determined by their
    # position in relation to the other tasks, rather than by their 'position' field, which orders them according to
    # position with milestones also (and is zero indexed.)
    tasks = CollaborationTask.objects.filter(collaboration=collaboration).annotate(
        type=Value('Task', output_field=CharField()), number=Window(
            expression=Rank(),
            order_by=F('position').asc()
        ))

    # 2. Get all Milestones, and annotate them with the type ('Milestone')
    milestones = CollaborationMilestone.objects.filter(collaboration=collaboration).annotate(
        type=Value('Milestone', output_field=CharField()))

    # 3. Chain the lists together, and sort them by their position field (in reverse)
    element_list = sorted(
        chain(tasks, milestones),
        key=lambda element: element.position)
    return element_list


@login_required()
def task_create_view(request, collaboration_uuid):
    """
    HTMX VIEW - Allows task messages to be added
    """
    # TODO: Secure and set methods

    # Get  variables
    name = str(request.POST["name"])
    assigned_to_id = str(request.POST["assigned_to"])

    collaboration = Collaboration.objects.get(id=collaboration_uuid)
    assigned_to = User.objects.get(id=assigned_to_id)

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
def milestone_create_view(request, collaboration_uuid):
    """
    HTMX VIEW - Allows task messages to be added
    """
    # TODO: Secure and set methods

    # Get  variables
    name = str(request.POST["name"])
    target_date = str(request.POST["target_date"])

    collaboration = Collaboration.objects.get(id=collaboration_uuid)

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

    task = CollaborationTask.objects.filter(pk=pk, collaboration__related_group__admins=request.user).first()

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
    milestone = CollaborationMilestone.objects.filter(pk=pk, collaboration__related_group__admins=request.user).first()

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
