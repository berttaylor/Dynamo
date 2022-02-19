from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render

from chat.forms import (
    CollaborationMessageForm,
    GroupMessageForm,
    GroupMessageUpdateForm,
    CollaborationMessageUpdateForm,
)
from chat.models import Message
from chat.utils import user_is_message_owner, user_is_message_owner_or_admin
from collaborations.models import Collaboration
from groups.models import Group
from groups.utils import user_has_active_membership
from groups.views import get_membership_level


@login_required()
def group_message_create_view(request, slug):
    """
    HTMX VIEW - Allows chat messages to be added
    """

    # Get data
    message = str(request.POST["message"])
    group = Group.objects.get(slug=slug)

    # Check Permissions
    if not user_has_active_membership(request.user, group):
        return HttpResponseForbidden()

    # Create Message
    Message.objects.create(group=group, user=request.user, message=message)
    messages = Message.objects.filter(group=group)

    # Return Response
    return render(
        request,
        "app/group/partials/chat/main.html",
        {
            "membership_level": get_membership_level(request.user, group),
            "chat_messages": messages,
            "group": group,
            "chat_form": GroupMessageForm(initial={"group": group}),
        },
    )


@login_required()
def group_message_update_view(request, slug, pk):
    """
    HTMX VIEW - Allows message updates with no reload
    Sends back "app/group/partials/chat/main.html", to replace the content in #group_chat
    If "message_update_modal": True is in the context (and the form), a modal will be rendered
    (with error messages, if appropriate)
    """

    # Get Data
    message = Message.objects.get(pk=pk)
    group = message.group
    form = GroupMessageUpdateForm(request.POST or None, instance=message)

    # Check Permissions
    if not user_is_message_owner(request.user, message):
        return HttpResponseForbidden()

    # If POST, update the message
    if request.method == "POST" and form.is_valid():
        form.save()
        return render(
            request,
            "app/group/partials/chat/main.html",
            {
                "membership_level": get_membership_level(request.user, group),
                "chat_messages": Message.objects.filter(group=group),
                "group": group,
                "chat_form": GroupMessageForm(initial={"group": group}),
            },
        )

    # If GET, (or invalid data is posted) send back the populated 'Update Message' Modal
    return render(
        request,
        "app/group/partials/chat/main.html",
        {
            "membership_level": get_membership_level(request.user, group),
            "message": message,
            "chat_messages": Message.objects.filter(group=group),
            "message_update_modal": True,
            "group": group,
            "form": form,
            "chat_form": GroupMessageForm(initial={"group": group}),
        },
    )


@login_required()
def group_message_delete_view(request, slug, pk):
    """
    HTMX VIEW - Allows message deletion
    Sends back "app/group/partials/chat/main.html", to replace the content in #group_chat
    If "message_delete_modal": True is in the context (and the form), a modal will be rendered
    (with error messages, if appropriate)
    """

    # Get Data
    message = Message.objects.get(pk=pk)
    group = message.group

    # Check Permissions
    if not user_is_message_owner_or_admin(request.user, message):
        return HttpResponseForbidden()

    # If POST, delete the message
    if request.method == "POST":
        message.delete()
        return render(
            request,
            "app/group/partials/chat/main.html",
            {
                "membership_level": get_membership_level(request.user, group),
                "chat_messages": Message.objects.filter(group=group),
                "group": group,
                "chat_form": GroupMessageForm(initial={"group": group}),
            },
        )

    # If GET, send back the populated 'Delete Message' Modal
    return render(
        request,
        "app/group/partials/chat/main.html",
        {
            "membership_level": get_membership_level(request.user, group),
            "message": message,
            "chat_messages": Message.objects.filter(group=group),
            "message_delete_modal": True,
            "group": group,
            "chat_form": GroupMessageForm(initial={"group": group}),
        },
    )


@login_required()
def collaboration_message_create_view(request, slug):
    """
    HTMX VIEW - Allows chat messages to be added
    """

    # Get Data
    message = str(request.POST["message"])
    collaboration = Collaboration.objects.get(slug=slug)

    # Check Permissions
    if not user_has_active_membership(request.user, collaboration.related_group):
        return HttpResponseForbidden()

    # Create Message
    Message.objects.create(collaboration=collaboration, user=request.user, message=message)

    # Return Response
    return render(
        request,
        "app/collaborations/partials/chat/main.html",
        {
            "membership_level": get_membership_level(
                request.user, collaboration.related_group
            ),
            "chat_messages": Message.objects.filter(collaboration=collaboration),
            "collaboration": collaboration,
            "chat_form": CollaborationMessageForm(
                initial={"collaboration": collaboration}
            ),
        },
    )


@login_required()
def collaboration_message_delete_view(request, slug, pk):
    """
    HTMX VIEW - Allows chat messages to be deleted

    Sends back "app/collaborations/partials/chat/main.html", to replace the content in
    #collaboration_chat. If "message_delete_modal": True is in the context (and the form), a modal will be rendered
    (with error messages, if appropriate)
    """

    # Get Data
    message = Message.objects.get(pk=pk)
    collaboration = message.collaboration

    # Check Permissions
    if not user_is_message_owner_or_admin(request.user, message):
        return HttpResponseForbidden()

    # If POST, delete the message
    if request.method == "POST":
        message.delete()
        return render(
            request,
            "app/collaborations/partials/chat/main.html",
            {
                "membership_level": get_membership_level(
                    request.user, collaboration.related_group
                ),
                "chat_messages": Message.objects.filter(collaboration=collaboration),
                "collaboration": collaboration,
                "chat_form": CollaborationMessageForm(
                    initial={"collaboration": collaboration}
                ),
            },
        )

    # If GET, send back the populated 'Delete Message' Modal
    return render(
        request,
        "app/collaborations/partials/chat/main.html",
        {
            "membership_level": get_membership_level(
                request.user, collaboration.related_group
            ),
            "message": message,
            "chat_messages": Message.objects.filter(collaboration=collaboration),
            "message_delete_modal": True,
            "collaboration": collaboration,
            "chat_form": CollaborationMessageForm(
                initial={"collaboration": collaboration}
            ),
        },
    )


@login_required()
def collaboration_message_update_view(request, slug, pk):
    """
    HTMX VIEW - Allows chat messages to be deleted

    Sends back "app/collaborations/partials/chat/main.html", to replace the content in
    #collaboration_chat. If "message_delete_modal": True is in the context (and the form), a modal will be rendered
    (with error messages, if appropriate)
    """

    # Get Data
    message = Message.objects.get(pk=pk)
    collaboration = message.collaboration
    form = CollaborationMessageUpdateForm(request.POST or None, instance=message)

    # Check Permissions
    if not user_is_message_owner(request.user, message):
        return HttpResponseForbidden()

    # If POST, update the message
    if request.method == "POST" and form.is_valid():
        form.save()
        return render(
            request,
            "app/collaborations/partials/chat/main.html",
            {
                "membership_level": get_membership_level(
                    request.user, collaboration.related_group
                ),
                "chat_messages": Message.objects.filter(collaboration=collaboration),
                "collaboration": collaboration,
                "chat_form": CollaborationMessageForm(
                    initial={"collaboration": collaboration}
                ),
            },
        )

    # If GET, (or invalid data is posted) send back the populated 'Update Message' Modal
    return render(
        request,
        "app/collaborations/partials/chat/main.html",
        {
            "membership_level": get_membership_level(
                request.user, collaboration.related_group
            ),
            "message": message,
            "chat_messages": Message.objects.filter(collaboration=collaboration),
            "message_update_modal": True,
            "collaboration": collaboration,
            "form": form,
            "chat_form": CollaborationMessageForm(
                initial={"collaboration": collaboration}
            ),
        },
    )
