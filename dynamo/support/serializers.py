from rest_framework.relations import StringRelatedField
from rest_framework.serializers import ModelSerializer

from support.models import FAQ, SupportMessage


class FAQSerializer(ModelSerializer):
    """
    Serializes the FAQs so that they can be read through the API.
    NOTE: this is a read-only functionality - I will add the FAQs / FAQ Categories in the Django Admin
    We use the __str__ value of the FAQCategory to avoid over-complicating matters with nested serialization
    """
    category = StringRelatedField()

    class Meta:
        model = FAQ
        fields = (
            "category",
            "question",
            "answer",
            "position",
        )


class SupportMessageSerializer(ModelSerializer):
    """
    DE-Serializes the Support Messages so that they can be added to the DB.
    NOTE: this is a write-only functionality - I will read / respond to Support Messages using the Django Admin.
    """

    class Meta:
        model = SupportMessage
        fields = (
            "name",
            "email",
            "subject",
            "message",
        )

    def create(self, validated_data):
        """
        Additional logic, to link message to a users account, if they are logged in
        """
        if self.context['request'].user.is_authenticated:
            validated_data['related_user_account'] = self.context['request'].user

        return super(SupportMessageSerializer, self).create(validated_data)


