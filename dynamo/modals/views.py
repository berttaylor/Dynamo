from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy

from collaborations.models import CollaborationTask
from modals.forms import TaskCompleteForm
from modals.utils import get_repr, get_field

TASK_COMPLETION_NOTES_MODAL = "Task Completion Notes Modal"

MODAL_SETTINGS = {
    TASK_COMPLETION_NOTES_MODAL: {
        'model': CollaborationTask,
        'template': 'app/collaborations/partials/elements/modals/task_completion_notes_modal.html',
        'form': TaskCompleteForm,
        'success_url_redirect': "htmx-get-element-list",
        'success_url_required_key': "collaboration_pk",
        'target_element': "collaboration_pk",
        'success_url_required_value_path': 'collaboration.id'
    }
}


@login_required()
def update_from_modal_view(request, modal, instance_pk):
    """
    HTMX VIEW - Allows completion of tasks with one click and no reload
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



