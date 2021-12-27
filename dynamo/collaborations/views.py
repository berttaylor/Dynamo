from itertools import chain

from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.db.models import Value, CharField
from django.db.models.expressions import Window
from django.db.models.functions import Rank
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DetailView, ListView
from django.views.generic.edit import FormMixin, UpdateView, DeleteView

from chat.forms import CollaborationMessageForm
from chat.models import Message
from collaborations.forms import MilestoneForm, TaskForm
from collaborations.models import Collaboration, CollaborationTask, CollaborationMilestone
from groups.models import Group
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


@method_decorator(login_required, name="dispatch")
class CollaborationCreateView(CreateView):
    """
    Allows users to create a new collaboration
    """

    template_name = "dashboard/collaborations/collaboration_create.html"
    model = Collaboration
    fields = (
        "name",
        "description",
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
        form.instance.created_by = user

        form.instance.related_group = Group.objects.get(
            slug=self.kwargs.get("group_slug")
        )

        return super(CollaborationCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "collaboration-detail",
            kwargs={"slug": self.object.slug},
        )


class CollaborationDetailView(FormMixin, DetailView):
    """
    Shows all information regarding a collaboration, as well as
        - Chat Messages
        - Tasks /Milestones
    """

    template_name = "dashboard/collaborations/collaboration_detail.html"
    model = Collaboration
    form_class = CollaborationMessageForm

    def get_context_data(self, **kwargs):
        """
        We override get_context_data to populate the search field choices
        """

        context = super(CollaborationDetailView, self).get_context_data(**kwargs)

        collaboration = self.get_object()

        context.update(
            {
                "chat_messages": Message.objects.filter(collaboration=collaboration),
                "chat_form": CollaborationMessageForm(
                    initial={"collaboration": collaboration}
                ),
                "task_form": TaskForm(
                    initial={"collaboration": collaboration},
                ),
                "milestone_form": MilestoneForm(
                    initial={"collaboration": collaboration}
                ),
                "elements": get_all_elements(collaboration)
            },
        )

        return context


class CollaborationListView(ListView):
    """
    Shows all collaborations, adn acts as dashboard home
    """

    template_name = "dashboard/collaborations/collaboration_list.html"
    model = Collaboration


@method_decorator(login_required, name="dispatch")
class CollaborationUpdateView(UpdateView):
    """
    Allows the user to update multiple fields on a collaboration which they are the admin/creator of.
    """

    template_name = "dashboard/collaborations/collaboration_update.html"
    model = Collaboration
    fields = [
        "name",
        "description",
    ]

    def get_success_url(self):
        return reverse_lazy(
            "collaboration-detail",
            kwargs={"slug": self.object.slug},
        )


@method_decorator(login_required, name="dispatch")
class CollaborationDeleteView(DeleteView):
    template_name = "dashboard/collaborations/collaboration_delete.html"
    model = Collaboration

    def get_success_url(self):
        return reverse_lazy(
            "group-detail",
            kwargs={"slug": self.object.related_group.slug},
        )


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
                  "dashboard/collaborations/partials/collaboration_elements.html", {
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
                  "dashboard/collaborations/partials/collaboration_elements.html", {
                      "task_form": TaskForm(
                          initial={"collaboration": collaboration},
                      ),
                      "milestone_form": MilestoneForm(
                          initial={"collaboration": collaboration}
                      ),
                      "elements": get_all_elements(collaboration),
                      "collaboration": collaboration,
                  })


@method_decorator(login_required, name="dispatch")
class TaskUpdateView(UpdateView):
    """
    Allows the user to update tasks on a collaboration which they are the admin/creator of.
    """

    template_name = "dashboard/collaborations/collaboration_task_update.html"
    model = CollaborationTask
    fields = [
        "position",
        "name",
        "description",
        "assigned_to",
        "prerequisites",
        "tags",
        "completed_at",
        "completion_notes"
    ]

    def get_success_url(self):
        return reverse_lazy(
            "collaboration-detail",
            kwargs={"slug": self.object.collaboration.slug},
        )


@method_decorator(login_required, name="dispatch")
class MilestoneUpdateView(UpdateView):
    """
    Allows the user to update milestones on a collaboration which they are the admin/creator of.
    """

    template_name = "dashboard/collaborations/collaboration_milestone_update.html"
    model = CollaborationMilestone
    fields = [
        "position",
        "name",
        "target_date",
    ]

    def get_success_url(self):
        return reverse_lazy(
            "collaboration-detail",
            kwargs={"slug": self.object.collaboration.slug},
        )


@login_required()
def task_delete_view(request, pk):
    """
    HTMX VIEW - Allows delete without refresh
    """

    task = CollaborationTask.objects.filter(pk=pk, collaboration__related_group__admins=request.user).first()

    collaboration = task.collaboration

    task.delete()

    return render(request,
                  "dashboard/collaborations/partials/collaboration_elements.html", {
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
                  "dashboard/collaborations/partials/collaboration_elements.html", {
                      "task_form": TaskForm(
                          initial={"collaboration": collaboration},
                      ),
                      "milestone_form": MilestoneForm(
                          initial={"collaboration": collaboration}
                      ),
                      "elements": get_all_elements(collaboration),
                      "collaboration": collaboration,
                  })
