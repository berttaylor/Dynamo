from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from chat.forms import CollaborationMessageForm, GroupMessageForm
from chat.models import Message
from collaborations.models import Collaboration
from groups.models import Group
from groups.views import get_membership_level


@login_required()
def group_message_create_view(request, group_uuid):
    """
    HTMX VIEW - Allows chat messages to be added
    """
    # TODO: Secure and set methods

    # Get  variables
    message = str(request.POST["message"])

    user = request.user
    group = Group.objects.get(id=group_uuid)

    Message.objects.create(group=group, user=user, message=message)
    messages = Message.objects.filter(group=group)
    membership_level = get_membership_level(request.user, group)

    return render(request, "dashboard/group/partials/group_chat.html", {
        'membership_level': membership_level,
        "chat_messages": messages,
        "group": group,
        "chat_form": GroupMessageForm(
            initial={"group": group}
        )})


@login_required()
def group_message_delete_view(request, message_id):
    """
    HTMX VIEW - Allows chat messages to be deleted
    """

    # TODO: Secure and set methods

    # Get  variables
    message = Message.objects.get(pk=message_id)
    user = request.user

    group = message.group
    message.delete()
    messages = Message.objects.filter(group=group)

    membership_level = get_membership_level(request.user, group)

    return render(request, "dashboard/group/partials/group_chat.html", {
        'membership_level': membership_level,
        "chat_messages": messages,
        "group": group,
        "chat_form": GroupMessageForm(
            initial={"group": group}
        )})


@login_required()
def collaboration_message_create_view(request, collaboration_uuid):
    """
    HTMX VIEW - Allows chat messages to be added
    """
    # TODO: Secure and set methods

    # Get  variables
    message = str(request.POST["message"])

    user = request.user
    collaboration = Collaboration.objects.get(id=collaboration_uuid)

    Message.objects.create(collaboration=collaboration, user=user, message=message)
    messages = Message.objects.filter(collaboration=collaboration)

    membership_level = get_membership_level(request.user, collaboration.related_group)

    return render(request, "dashboard/collaborations/partials/collaboration_chat.html", {
        'membership_level': membership_level,
        "chat_messages": messages,
        "collaboration": collaboration,
        "chat_form": CollaborationMessageForm(
            initial={"collaboration": collaboration}
        )})


@login_required()
def collaboration_message_delete_view(request, message_id):
    """
    HTMX VIEW - Allows chat messages to be deleted
    """

    # TODO: Secure and set methods

    # Get  variables
    message = Message.objects.get(pk=message_id)
    user = request.user

    collaboration = message.collaboration
    message.delete()
    messages = Message.objects.filter(collaboration=collaboration)

    membership_level = get_membership_level(request.user, collaboration.related_group)

    return render(request, "dashboard/collaborations/partials/collaboration_chat.html", {
        'membership_level': membership_level,
        "chat_messages": messages,
        "collaboration": collaboration,
        "chat_form": CollaborationMessageForm(
            initial={"collaboration": collaboration}
        )})
