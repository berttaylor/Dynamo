from django.views.generic import DetailView, ListView
from django.views.generic.edit import FormMixin

from chat.forms import CollaborationMessageForm
from chat.models import Message
from collaborations.models import Collaboration
from collaborations.utils import get_all_elements

from groups.views import get_membership_level


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
                "elements": get_all_elements(collaboration),
                "collaboration": collaboration,
            },
        )

        return context
