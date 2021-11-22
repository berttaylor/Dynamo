from django.forms import ModelForm, IntegerField, HiddenInput, CharField

from chat.models import Message


class GroupMessageForm(ModelForm):
    # We hide the group section, as this is set by the view
    group = CharField(widget=HiddenInput(), required=False)

    class Meta:
        model = Message
        fields = ["message", "group"]


class CollaborationMessageForm(ModelForm):
    # We hide the collaboration section, as this is set by the view
    collaboration = CharField(widget=HiddenInput(), required=False)

    class Meta:
        model = Message
        fields = ["message", "collaboration"]
