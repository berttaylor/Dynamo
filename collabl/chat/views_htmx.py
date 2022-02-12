from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from chat.forms import CollaborationMessageForm, GroupMessageForm, GroupMessageUpdateForm, \
    CollaborationMessageUpdateForm
from chat.models import Message
from collaborations.models import Collaboration
from groups.models import Group
from groups.views import get_membership_level


@login_required()
def group_message_create_view(request, slug):
    """
    HTMX VIEW - Allows chat messages to be added
    """
    # TODO: Secure and set methods

    # Get  variables
    message = str(request.POST["message"])

    user = request.user
    group = Group.objects.get(slug=slug)

    Message.objects.create(group=group, user=user, message=message)
    messages = Message.objects.filter(group=group)
    membership_level = get_membership_level(request.user, group)

    return render(request, "app/group/partials/chat/main.html", {
        'membership_level': membership_level,
        "chat_messages": messages,
        "group": group,
        "chat_form": GroupMessageForm(
            initial={"group": group}
        )})


@login_required()
def group_message_update_view(request, slug, pk):
    """
    HTMX VIEW - Allows message updates with no reload
    Sends back "app/group/partials/chat/main.html", to replace the content in #group_chat
    If "message_update_modal": True is in the context (and the form), a modal will be rendered
    (with error messages, if appropriate)
    """

    # Get  variables
    message = Message.objects.get(pk=pk)
    group = message.group
    form = GroupMessageUpdateForm(request.POST or None, instance=message)

    if request.method == "POST" and form.is_valid():
        form.save()
        return render(request, "app/group/partials/chat/main.html", {
            'membership_level': get_membership_level(request.user, group),
            "chat_messages": Message.objects.filter(group=group),
            "group": group,
            "chat_form": GroupMessageForm(
                initial={"group": group}
            )})

    return render(request, "app/group/partials/chat/main.html", {
        'membership_level': get_membership_level(request.user, group),
        'message': message,
        "chat_messages": Message.objects.filter(group=group),
        'message_update_modal': True,
        "group": group,
        "form": form,
        "chat_form": GroupMessageForm(
            initial={"group": group}
        )})


@login_required()
def group_message_delete_view(request, slug, pk):
    """
    HTMX VIEW - Allows message deletion
    Sends back "app/group/partials/chat/main.html", to replace the content in #group_chat
    If "message_delete_modal": True is in the context (and the form), a modal will be rendered
    (with error messages, if appropriate)
    """

    # Get  variables
    message = Message.objects.get(pk=pk)
    group = message.group

    if request.method == "POST":
        message.delete()
        return render(request, "app/group/partials/chat/main.html", {
            'membership_level': get_membership_level(request.user, group),
            "chat_messages": Message.objects.filter(group=group),
            "group": group,
            "chat_form": GroupMessageForm(
                initial={"group": group}
            )})

    return render(request, "app/group/partials/chat/main.html", {
        'membership_level': get_membership_level(request.user, group),
        'message': message,
        "chat_messages": Message.objects.filter(group=group),
        'message_delete_modal': True,
        "group": group,
        "chat_form": GroupMessageForm(
            initial={"group": group}
        )})


@login_required()
def collaboration_message_create_view(request, slug):
    """
    HTMX VIEW - Allows chat messages to be added
    """
    # TODO: Secure and set methods

    # Get  variables
    message = str(request.POST["message"])
    user = request.user
    collaboration = Collaboration.objects.get(slug=slug)
    Message.objects.create(collaboration=collaboration, user=user, message=message)

    return render(request, "app/collaborations/partials/chat/main.html", {
        'membership_level': get_membership_level(request.user, collaboration.related_group),
        "chat_messages": Message.objects.filter(collaboration=collaboration),
        "collaboration": collaboration,
        "chat_form": CollaborationMessageForm(
            initial={"collaboration": collaboration}
        )})


@login_required()
def collaboration_message_delete_view(request, slug, pk):
    """
    HTMX VIEW - Allows chat messages to be deleted

    Sends back "app/collaborations/partials/chat/main.html", to replace the content in
    #collaboration_chat. If "message_delete_modal": True is in the context (and the form), a modal will be rendered
    (with error messages, if appropriate)
    """

    # Get  variables
    message = Message.objects.get(pk=pk)
    collaboration = message.collaboration

    if request.method == "POST":
        message.delete()
        return render(request, "app/collaborations/partials/chat/main.html", {
            'membership_level': get_membership_level(request.user, collaboration.related_group),
            "chat_messages": Message.objects.filter(collaboration=collaboration),
            "collaboration": collaboration,
            "chat_form": CollaborationMessageForm(
                initial={"collaboration": collaboration}
            )})

    return render(request, "app/collaborations/partials/chat/main.html", {
        'membership_level': get_membership_level(request.user, collaboration.related_group),
        'message': message,
        "chat_messages": Message.objects.filter(collaboration=collaboration),
        'message_delete_modal': True,
        "collaboration": collaboration,
        "chat_form": CollaborationMessageForm(
            initial={"collaboration": collaboration}
        )})


@login_required()
def collaboration_message_update_view(request, slug, pk):
    """
    HTMX VIEW - Allows chat messages to be deleted

    Sends back "app/collaborations/partials/chat/main.html", to replace the content in
    #collaboration_chat. If "message_delete_modal": True is in the context (and the form), a modal will be rendered
    (with error messages, if appropriate)
    """

    # Get  variables
    message = Message.objects.get(pk=pk)
    collaboration = message.collaboration
    form = CollaborationMessageUpdateForm(request.POST or None, instance=message)

    if request.method == "POST" and form.is_valid():
        form.save()
        return render(request, "app/collaborations/partials/chat/main.html", {
            'membership_level': get_membership_level(request.user, collaboration.related_group),
            "chat_messages": Message.objects.filter(collaboration=collaboration),
            "collaboration": collaboration,
            "chat_form": CollaborationMessageForm(
                initial={"collaboration": collaboration}
            )})

    return render(request, "app/collaborations/partials/chat/main.html", {
        'membership_level': get_membership_level(request.user, collaboration.related_group),
        'message': message,
        "chat_messages": Message.objects.filter(collaboration=collaboration),
        'message_update_modal': True,
        "collaboration": collaboration,
        "form": form,
        "chat_form": CollaborationMessageForm(
            initial={"collaboration": collaboration}
        )})

