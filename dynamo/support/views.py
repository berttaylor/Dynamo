from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, TemplateView

from support.forms import SupportMessageForm
from support.models import FAQ, SupportMessage
from dynamo.settings import DEFAULT_SYSTEM_TO_EMAIL
from dynamo.tasks import send_email


class FAQListView(ListView):
    """
    Shows a list of Frequently Asked Questions
    """

    model = FAQ
    template_name = "support/faq_list.html"
    paginate_by = 30


class SupportMessageCreateView(CreateView):
    """
    Collects the data required and creates a new SupportMessage instance in the db.
    """

    model = SupportMessage
    form_class = SupportMessageForm
    template_name = "support/support_message_form.html"
    success_url = reverse_lazy("support-message-thanks")

    def get_initial(self):
        """
        Repopulates the form with user data.
        """
        initial = {}
        if self.request.user.is_authenticated:
            initial["user_name"] = (
                str(self.request.user.first_name)
                + " "
                + str(self.request.user.last_name)
            )

        return initial

    def form_valid(self, form):
        """
        We add the user before saving the SupportMessage
        """

        # 1. Add User, if logged in
        if self.request.user.is_authenticated:
            form.instance.related_user_account = self.request.user

        # 2. Create the SupportMessage
        response = super().form_valid(form)
        message = self.object

        # 3. Queue an email to the support team, informing them that action is needed
        send_email.delay(
            {
                "template": "admin_support_message.email",
                "recipients": (DEFAULT_SYSTEM_TO_EMAIL,),
                "additional_context": {
                    "subject": f"New Support Message Received from {message.name}",
                    "user": str(message.name),
                    "email": str(message.email),
                    "subject_line": str(message.subject),
                    "message_body": str(message.message),
                    "related_user": str(message.related_user_account.id),
                },
            }
        )

        return response


@method_decorator(login_required, name="dispatch")
class SupportMessageThanksView(TemplateView):
    """
    Confirms to the user that the message has been sent
    """

    template_name = "support/support_message_thanks.html"
