from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from rest_framework.fields import SerializerMethodField, DateTimeField
from rest_framework.relations import StringRelatedField
from rest_framework.serializers import ModelSerializer

from chat.models import Message
from collaborations.models import Collaboration
from groups.models import Group


class MessageSerializer(ModelSerializer):
    current_user_is_owner = SerializerMethodField(read_only=True)
    user = StringRelatedField(read_only=True)
    created_at = DateTimeField(read_only=True, format="%I:%M%p (%d %b '%y)")

    class Meta:
        model = Message
        fields = (
            "message",
            "user",
            "created_at",
            "current_user_is_owner",
        )

    def get_current_user_is_owner(self, obj):
        """
        Returns 'True' if user is the creator of the chat message
        """
        request = self.context['request']
        user = request.user
        if user.is_authenticated:
            if obj.user == user:
                return True
        return False

    def create(self, validated_data):
        """
        We override the create method to add the user, adn teh group/collaboration to the object
        """

        # 1. Get user
        request = self.context['request']
        user = request.user

        # 2. If a group is specified, create a group message
        if group_slug := request.query_params.get('group'):
            try:
                group = Group.objects.get(slug=group_slug)
            except ObjectDoesNotExist:
                raise NotFound(detail="collaboration not found")
            else:
                # Check permissions, and deliver the information
                if user not in group.members.all():
                    raise PermissionDenied(detail="Join the group to send messages")
                message = Message.objects.create(user=user, group=group, **validated_data)
                return message

        # 2. Else, If a collaboration is specified, create a collaboration message
        elif collaboration_slug := request.query_params.get('collaboration'):
            try:
                collaboration = Collaboration.objects.get(slug=collaboration_slug)
            except ObjectDoesNotExist:
                raise NotFound(detail="collaboration not found")
            else:
                # Check permissions, and deliver the information
                if user not in collaboration.related_group.members.all():
                    raise PermissionDenied(detail="Join the collaboration's group to send messages")
                message = Message.objects.create(user=user, collaboration=collaboration, **validated_data)
                return message

        # 3. If neither is specified, return error
        else:
            raise ValidationError(detail="Please specify a group, or collaboration - e.g '?group=the-creek'")

