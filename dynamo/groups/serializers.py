from rest_framework.fields import SerializerMethodField, DateTimeField
from rest_framework.relations import HyperlinkedRelatedField, StringRelatedField
from rest_framework.reverse import reverse
from rest_framework.serializers import ModelSerializer

from chat.serializers import MessageSerializer
from collaborations.serializers import CollaborationSerializer
from dynamo.settings import SITE_PROTOCOL, SITE_DOMAIN
from groups.constants import REQUEST_STATUS_PENDING
from groups.models import Group, GroupJoinRequest


class GroupSerializer(ModelSerializer):
    """
    Main group serializer. Provides details and 'group-health' stats in the same place.
    """
    created_by = StringRelatedField(read_only=True)

    admin_list = SerializerMethodField(read_only=True)
    member_list = SerializerMethodField(read_only=True)
    subscriber_list = SerializerMethodField(read_only=True)

    current_user_is_admin = SerializerMethodField(read_only=True)
    current_user_is_member = SerializerMethodField(read_only=True)
    current_user_is_subscriber = SerializerMethodField(read_only=True)
    current_user_membership_pending = SerializerMethodField(read_only=True)

    class Meta:
        model = Group
        lookup_field = 'slug'
        fields = (
            "name",
            "slug",
            "description",
            "created_by",
            "admin_list",
            "member_list",
            "subscriber_list",
            "current_user_is_admin",
            "current_user_is_member",
            "current_user_is_subscriber",
            "current_user_membership_pending",
        )

    def create(self, validated_data):
        """
        We override the create method to add the created_by to the object
        We also add them to the admin, members and subscribers for the group
        """

        # 1. Get user
        request = self.context['request']
        user = request.user

        # 2. Create Group
        group = Group.objects.create(created_by=user, **validated_data)

        # 3. Add user to admin, members and subscribers
        group.admins.add(user)
        group.members.add(user)
        group.subscribers.add(user)

        return group

    def get_admin_list(self, obj):
        """
        Returns list of admins
        """
        return [user.username for user in obj.admins.all()]

    def get_member_list(self, obj):
        """
        Returns list of members
        """
        return [user.username for user in obj.members.all()]

    def get_subscriber_list(self, obj):
        """
        Returns list of subscribers
        """
        return [user.username for user in obj.subscribers.all()]

    def get_current_user_is_admin(self, obj):
        """
        Returns 'True' if user is an admin in this group.
        """

        request = self.context['request']
        user = request.user
        if user.is_authenticated:
            if user in obj.admins.all():
                return True
        return False

    def get_current_user_is_member(self, obj):
        """
        Returns 'True' if user is a member of this group.
        """
        request = self.context['request']
        user = request.user
        if user.is_authenticated:
            if user in obj.members.all():
                return True
        return False

    def get_current_user_is_subscriber(self, obj):
        """
        Returns 'True' if user is a subscriber to this group.
        """
        request = self.context['request']
        user = request.user
        if user.is_authenticated:
            if user in obj.subscribers.all():
                return True
        return False

    def get_current_user_membership_pending(self, obj):
        """
        Returns 'True' if the user has an open membership request to this group
        """
        request = self.context['request']
        user = request.user

        # If user isn't logged in, return false
        if not user.is_authenticated:
            return False

        # If no request has been made, return false
        elif not GroupJoinRequest.objects.filter(user=user, group=obj).exists():
            return False

        # If the request is pending, return True
        elif GroupJoinRequest.objects.get(user=user, group=obj).status == REQUEST_STATUS_PENDING:
            return True

        # Otherwise, the request must have already been 'Approved' or 'Denied', so we return false
        return False


class GroupJoinRequestSerializer(ModelSerializer):
    user = StringRelatedField(read_only=True)
    approve_url = SerializerMethodField(read_only=True)
    deny_url = SerializerMethodField(read_only=True)
    url = HyperlinkedRelatedField

    class Meta:
        model = GroupJoinRequest
        fields = (
            "user",
            "status",
            "approve_url",
            "deny_url"
        )

    @staticmethod
    def get_approve_url(obj):
        """
        Generates URL that can be used to approve the request
        """
        url = reverse("groupjoinrequest-detail", kwargs={"pk": obj.pk})
        return SITE_PROTOCOL + SITE_DOMAIN + url + "/approve"

    @staticmethod
    def get_deny_url(obj):
        """
        Generates URL that can be used to deny the request
        """
        url = reverse("groupjoinrequest-detail", kwargs={"pk": obj.pk})
        return SITE_PROTOCOL + SITE_DOMAIN + url + "/deny"


class GroupDetailSerializer(GroupSerializer):
    """
    Added fields for the Group Detail view serializer. Uses nested serializers to provide the chat messages and collaborations
    which belong to each group.
    """
    chat_messages = StringRelatedField(read_only=True, many=True)
    join_requests = StringRelatedField(many=True, read_only=True)
    collaborations = CollaborationSerializer(many=True, read_only=True)

    class Meta(GroupSerializer.Meta):
        fields = GroupSerializer.Meta.fields + ('chat_messages', 'join_requests', 'collaborations')
