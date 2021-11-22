from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy

from chat.models import Message
from groups.models import Group


@login_required()
def GroupMessageCreateView(request, group_uuid):
    """
    FUNCTIONAL VIEW - Allows chat messages to be added
    """
    # TODO: Secure and set methods

    # Get  variables
    message = str(request.POST["message"])

    user = request.user
    group = Group.objects.get(id=group_uuid)

    Message.objects.create(group=group, user=user, message=message)

    return HttpResponseRedirect(
        reverse_lazy(
            "group-detail",
            kwargs={"slug": group.slug},
        )
    )
