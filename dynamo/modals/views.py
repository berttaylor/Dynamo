from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy

from collaborations.forms import TaskForm
from collaborations.models import CollaborationTask, Collaboration
from collaborations.utils import get_all_elements
from modals.forms import TaskCompleteForm
from modals.utils import get_repr, get_field

TASK_COMPLETION_NOTES_MODAL = "Task Completion Notes Modal"
TASK_CREATION_MODAL = "Task Creation Modal"

MODAL_SETTINGS = {
    TASK_COMPLETION_NOTES_MODAL: {
        'model': CollaborationTask,
        'template': 'app/collaborations/partials/elements/modals/task_completion_notes_modal.html',
        'form': TaskCompleteForm,
        'success_url_redirect': "htmx-get-element-list",
        'success_url_required_key': "collaboration_pk",
        'success_url_required_value_path': 'collaboration.id'
    },
    TASK_CREATION_MODAL: {
        'model': CollaborationTask,
        'parent_model': Collaboration,
        'template': 'app/collaborations/partials/elements/modals/task_creation_modal.html',
        'form': TaskForm,
        'success_url_redirect': "htmx-get-element-list",
        'success_url_required_key': "collaboration_pk",
        'success_url_required_value_path': 'collaboration.id'
    }
}


@login_required()
def update_from_modal_view(request, modal, instance_pk):
    """
    HTMX VIEW - Allows modal submission with state update and no reload
    """

    model = MODAL_SETTINGS[modal]['model']
    form = MODAL_SETTINGS[modal]['form']

    instance = get_object_or_404(model, pk=instance_pk)
    form = form(request.POST, request.FILES, instance=instance)

    success_url_required_value_path = MODAL_SETTINGS[modal]['success_url_required_value_path']
    success_url_required_value = get_repr(get_field(instance, success_url_required_value_path))

    if form.is_valid():
        form.save()

    return HttpResponseRedirect(
        reverse_lazy(
            MODAL_SETTINGS[modal]['success_url_redirect'],
            kwargs={MODAL_SETTINGS[modal]['success_url_required_key']: success_url_required_value},
        )
    )


@login_required()
def task_creation_modal_view(request, collaboration_id):
    """
    HTMX VIEW - Allows modal submission with state update and no reload
    """

    collaboration = get_object_or_404(Collaboration, pk=collaboration_id)

    if request.method == "POST":

        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.collaboration = collaboration
            task.save()

            return render(request,
                          "app/collaborations/partials/elements/list/main.html", {
                              "elements": get_all_elements(collaboration),
                              "completion_percentage": collaboration.percent_completed,
                              "completion_status": collaboration.status,
                              "collaboration": collaboration,
                              "completion_percentage_update": True,
                          })

    return render(request,
                  "app/collaborations/partials/elements/list/main.html", {
                      "elements": get_all_elements(collaboration),
                      "completion_percentage": collaboration.percent_completed,
                      "completion_status": collaboration.status,
                      "collaboration": collaboration,
                      "task_creation_modal": True,
                      "task_form": TaskForm(
                          initial={"collaboration": collaboration},
                      ),
                  })