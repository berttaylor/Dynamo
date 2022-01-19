from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DetailView
from django.views.generic.edit import FormMixin, UpdateView, DeleteView

from chat.forms import CollaborationMessageForm
from chat.models import Message
from collaborations.forms import MilestoneForm, TaskForm
from collaborations.models import Collaboration, CollaborationTask, CollaborationMilestone
from collaborations.utils import get_all_elements
from groups.models import Group
from groups.views import get_membership_level


@method_decorator(login_required, name="dispatch")
class CollaborationCreateView(CreateView):
    """
    Allows users to create a new collaboration
    """

    template_name = "app/auxiliary/collaboration/create.html"
    model = Collaboration
    fields = (
        "name",
        "description",
    )

    def get_initial(self):
        group = get_object_or_404(Group, slug=self.kwargs.get("group_slug"))
        return {"related_group": group}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["group"] = get_object_or_404(Group, slug=self.kwargs.get("group_slug"))
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

    template_name = "app/collaborations/main.html"
    model = Collaboration
    form_class = CollaborationMessageForm

    def get_context_data(self, **kwargs):
        """
        We override get_context_data to populate the search field choices
        """

        context = super(CollaborationDetailView, self).get_context_data(**kwargs)

        collaboration = self.get_object()

        group = collaboration.related_group

        if self.request.user.is_authenticated:
            membership_level = get_membership_level(self.request.user, group)
        else:
            membership_level = None

        context.update(
            {
                "membership_level": membership_level,
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
                "elements": get_all_elements(collaboration),
                "completion_status": collaboration.status,
            },
        )

        return context


@method_decorator(login_required, name="dispatch")
class CollaborationUpdateView(UpdateView):
    """
    Allows the user to update multiple fields on a collaboration which they are the admin/creator of.
    """

    template_name = "app/auxiliary/collaboration/update.html"
    model = Collaboration
    fields = [
        "name",
        "description",
        "image"
    ]

    def get_success_url(self):
        return reverse_lazy(
            "collaboration-detail",
            kwargs={"slug": self.object.slug},
        )


@method_decorator(login_required, name="dispatch")
class CollaborationDeleteView(DeleteView):
    template_name = "app/auxiliary/collaboration/delete.html"
    model = Collaboration

    def get_success_url(self):
        return reverse_lazy(
            "group-detail",
            kwargs={"slug": self.object.related_group.slug},
        )


@method_decorator(login_required, name="dispatch")
class TaskUpdateView(UpdateView):
    """
    Allows the user to update tasks on a collaboration which they are the admin/creator of.
    """

    template_name = "app/auxiliary/task/update.html"
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

    template_name = "app/auxiliary/milestone/update.html"
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
