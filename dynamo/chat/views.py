from django.core.exceptions import ObjectDoesNotExist

# Create your views here.
from rest_framework import viewsets
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated

from chat.models import Message
from chat.serializers import MessageSerializer
from collaborations.models import Collaboration
from groups.models import Group


class MessageViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows chat message to be viewed
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        If no group/collaboration is supplied in the parameters, we send back nothing.
        If a group is supplied, we send back messages from that group (but not from its collaborations)
        If a collaboration is supplied, we send back messages from that collaboration (but not from its group)
        """

        # 1. If a group is specified, grab the slug
        if group_slug := self.request.query_params.get('group'):
            # Get group and check it exists
            try:
                group = Group.objects.get(slug=group_slug)
            except ObjectDoesNotExist:
                raise NotFound(detail="collaboration not found")
            else:
                # Check permissions, and deliver the information
                if self.request.user not in group.members.all():
                    raise PermissionDenied(detail="Join the group to see the chat")
                return Message.objects.filter(group=group).order_by('created_at')

        # 2. Else, If a collaboration is specified, grab the slug
        elif collaboration_slug := self.request.query_params.get('collaboration'):
            # Get collaboration and check it exists
            try:
                collaboration = Collaboration.objects.get(slug=collaboration_slug)
            except ObjectDoesNotExist:
                raise NotFound(detail="collaboration not found")
            else:
                # Check permissions, and deliver the information
                if self.request.user not in collaboration.related_group.members.all():
                    raise PermissionDenied(detail="Join this collaboration's group to see the chat")
                return Message.objects.filter(collaboration=collaboration).order_by('created_at')

        # 3. If neither is specified, return error
        else:
            raise ValidationError(detail="Please specify a group, or collaboration - e.g '?group=the-creek'")

    def get_serializer_context(self):
        """
        We override this to grab the group from the parameters before passing to the
        serializer
        """
        context = super().get_serializer_context()
        if group_slug := self.request.query_params.get('group'):
            context["group"] = group_slug
        return context