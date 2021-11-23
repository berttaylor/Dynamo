from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy

from chat.models import Message
from collaborations.models import Collaboration
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


@login_required()
def CollaborationMessageCreateView(request, collaboration_uuid):
    """
    FUNCTIONAL VIEW - Allows chat messages to be added
    """
    # TODO: Secure and set methods

    # Get  variables
    message = str(request.POST["message"])

    user = request.user
    collaboration = Collaboration.objects.get(id=collaboration_uuid)

    Message.objects.create(collaboration=collaboration, user=user, message=message)

    return HttpResponseRedirect(
        reverse_lazy(
            "collaboration-detail",
            kwargs={"slug": collaboration.slug},
        )
    )
