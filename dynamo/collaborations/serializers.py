from collections import OrderedDict
from string import capwords

from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.fields import SerializerMethodField, DateTimeField, ReadOnlyField
from rest_framework.relations import StringRelatedField, RelatedField
from rest_framework.serializers import ModelSerializer

from chat.models import Message
from collaborations import constants as c
from collaborations.models import Collaboration, CollaborationFile, CollaborationElement
from groups.models import Group
from users.models import User


class CollaborationSerializer(ModelSerializer):
    created_by = StringRelatedField(read_only=True)
    related_group = StringRelatedField(read_only=True)
    elements = StringRelatedField(read_only=True, many=True)

    class Meta:
        model = Collaboration
        lookup_field = 'slug'
        fields = (
            "name",
            "slug",
            "description",
            "created_by",
            "related_group",
            "status",
            "percent_completed",
            "elements"
        )

    @staticmethod
    def get_number_of_messages(obj):
        """
        Returns the number of messages linked to this collaboration - Not used in current version
        """
        return Message.objects.filter(collaboration=obj).count()

    @staticmethod
    def get_number_of_tasks(obj):
        """
        Returns the number of tasks linked to this collaboration - Not used in current version
        """
        return CollaborationElement.objects.filter(collaboration=obj, type=c.COLLABORATION_ELEMENT_TYPE_TASK).count()

    @staticmethod
    def get_number_of_milestones(obj):
        """
        Returns the number of milestones linked to this collaboration - Not used in current version
        """
        return CollaborationElement.objects.filter(collaboration=obj,
                                                   type=c.COLLABORATION_ELEMENT_TYPE_MILESTONE).count()

    def create(self, validated_data):
        """
        We override the create method to add the user and group to the object
        This is not RESTful, but allows for a smoother user experience, as fewer details are needed in POST.
        """

        # 1. Get variables
        request = self.context['request']
        user = request.user
        group_slug = request.query_params.get('group')
        group = Group.objects.get(slug=group_slug)

        # 2. Check that the user has the rights to add a collaboration to this group,
        # - PermissionDenied if not, or proceed and add them as the created_by user if they do
        if user not in group.admins.all():
            raise PermissionDenied(detail="Become an admin of the group to add new collaborations.")
        else:
            validated_data["created_by"] = user
            validated_data["related_group"] = group
            return super(CollaborationSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        """
        We override the create method to check permissions
        """

        # 1. Get variables
        user = self.context['request'].user
        group = instance.related_group

        # 2. Check that the user has the rights to edit the collaboration,
        # - PermissionDenied if not, or proceed and add them as the created_by user if they do
        if user not in group.admins.all():
            raise PermissionDenied(detail="You do not have permission to edit this collaboration")
        else:
            return super(CollaborationSerializer, self).update(instance, validated_data)

    def to_representation(self, instance):
        """Remove fields that dont contain relevant info"""
        representation = super(CollaborationSerializer, self).to_representation(instance)
        if not representation["description"]:
            representation.pop("description")
        return representation


class CollaborationFileSerializer(ModelSerializer):
    class Meta:
        model = CollaborationFile
        fields = (
            "collaboration",
            "name",
            "format",
        )


class UserRelatedField(RelatedField):
    """
    This field allows us to use str representation of a user in the serializer,
    and still have it as a writeable field.

    It is necessary for clean representation of assigned_to - as StringRelatedField is read_only.
    """

    def display_value(self, instance):
        return instance

    def to_representation(self, value):
        return capwords(str(value))

    def to_internal_value(self, data):
        return User.objects.get(username__iexact=data)  # Case insensitive


class TaskRelatedField(RelatedField):
    """
    This field allows us to use a string representation of 'prerequisites' in the serializer,
    which displays specific information about its completion, and the users assigned to it.

    It is also a writeable field, for which we use the task reference e.g "TASK-T4LWF"
    """

    def display_value(self, instance):
        return instance

    def to_representation(self, value):
        return str(value) + f" ({value.reference})"

    def to_internal_value(self, data):
        return CollaborationElement.objects.get(reference__iexact=data)  # Case insensitive


class CollaborationElementSerializer(ModelSerializer):
    """
    Main CollaborationElement Serializer - complex in nature, due to the data model, and the response options desired.

    A CollaborationElement can be either a "task" or a
    """
    assigned_to = UserRelatedField(required=False, queryset=User.objects.all())
    prerequisites = TaskRelatedField(required=False, queryset=CollaborationElement.objects.all(), many=True)
    completed_by = StringRelatedField(read_only=True)
    target_date = DateTimeField(
        format="%d/%b/%y",
        input_formats=["%d/%m/%y"],
        required=False,
    )
    completion_notes = ReadOnlyField()
    completed_at = DateTimeField(
        format="%d/%b/%y",
        read_only=True,
        required=False,
    )

    # Shorten responses
    # Removes keys from response where 'Null' values exist - easier to read in  a list, but possibly less REST-ful,
    # and doesnt make it clear which extra fields are available for storing data.
    # If used, extended_guidance is recommended
    shorten_responses = True

    # Extended guidance
    # Extended guidance provides additional feedback when adding tasks/milestones as to which optional fields
    # are available for storing information. With this on, the APi response will show missing fields that are optional,
    # as well as missing fields that as required.
    extended_guidance = True

    class Meta:
        model = CollaborationElement
        fields = (
            "position",
            "type",
            "name",
            "description",
            "assigned_to",
            "prerequisites",
            "target_date",
            "status",
            "completed_at",
            "completed_by",
            "reference",
            "completion_notes",
        )
        extra_kwargs = {
            'position': {'required': False},
            'name': {'required': False},
            'type': {'required': True},
        }

    def validate(self, attrs):
        """
        We have to write the validation ourselves, as the required fields depends entirely on whether the
        object is a task or a milestone.

        We can assume that every element that reaches this point will have a 'type' of either "Task" or "Milestone"
        - This is because the 'type' field is required by the serializer and has already been validated
        against the text choices, which are kept in constants.
        """

        if attrs["type"] == c.COLLABORATION_ELEMENT_TYPE_TASK:

            # Set all required fields for a task
            required_fields = (
                "type",
                "name",
            )

            optional_fields = (
                "description",
                "assigned_to",
                "prerequisites",
                "completed_at",
                "completed_by",
            )

        else:
            # Set all required fields for a Milestone
            required_fields = (
                "type",
                "name",
                "target_date",
            )

            optional_fields = ()

        # Get list of missing fields, so we can create useful error messages
        missing_required_fields = [field for field in required_fields if field not in attrs]
        missing_optional_fields = [field for field in optional_fields if field not in attrs]

        if missing_required_fields:

            # We use list comprehension to make a dictionary marking all the required fields (as keys) with the
            # value 'self.error_messages["required"]'
            message = {field: self.error_messages["required"] for field in missing_required_fields}

            # If extended guidance is selected, We use list comprehension to make a dictionary marking
            # all the optional fields (as keys) with the value "This field is optional"
            if self.extended_guidance:
                message.update({field: "This field is optional" for field in missing_optional_fields})

            # Raise the errors
            raise ValidationError(message)

        return attrs

    def create(self, validated_data):
        """
        We override the create method to add the user and group to the object
        This is not very RESTful, but allows for a smoother user experience, as fewer details are needed in POST.
        """

        # 1. Get variables
        request = self.context['request']
        user = request.user
        collaboration_slug = request.query_params.get('collaboration')
        collaboration = Collaboration.objects.get(slug=collaboration_slug)

        # 2. Check that the user has the rights to add a task to a collaboration in this group,
        # - PermissionDenied if not, or proceed and add them as the created_by user if they do
        if user not in collaboration.related_group.admins.all():
            raise PermissionDenied(detail="Become a member of the group to add new tasks and milestones.")

        # 3. Calculate position of element
        if not (tasks_milestones := collaboration.elements.all()):
            # If no other elements exist, set this one as the first
            position = 1
        else:
            # Otherwise, get the highest numbered 'position' from the elements, and add one.
            position = tasks_milestones.order_by('-position')[0].position + 1

        # 4. Add data to dictionary and call the create function
        validated_data["collaboration"] = collaboration
        validated_data["position"] = int(position)

        return super(CollaborationElementSerializer, self).create(validated_data)

    def to_representation(self, instance):
        """Remove fields that don't contain relevant info to the element type"""
        # Get variables
        representation = super(CollaborationElementSerializer, self).to_representation(instance)
        element_type = representation["type"]

        # If the element type is 'Task", remove all fields related to Milestones.
        if element_type == c.COLLABORATION_ELEMENT_TYPE_TASK:
            representation.pop("target_date")
            representation.pop("status")

        # If the element type is 'Milestone", remove all fields related to Tasks, and any blank descriptions.
        else:
            representation.pop("description")
            representation.pop("assigned_to")
            representation.pop("completed_at")
            representation.pop("completed_by")

        # If shorten responses is selected, we clean the data of any null values before making the response.
        if not self.shorten_responses:
            return representation
        else:
            # First remove prerequisites, if none have been specified.
            if not representation["prerequisites"]:
                representation.pop("prerequisites")
            # Next, we create a new dictionary of all of the keys/values where the value is not None.
            non_null_representation = OrderedDict(
                [(key, representation[key]) for key in representation if representation[key] is not None]
            )
            return non_null_representation
