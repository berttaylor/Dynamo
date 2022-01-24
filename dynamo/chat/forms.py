from django.forms import ModelForm, HiddenInput, CharField, TextInput, Textarea


from chat.models import Message


class GroupMessageForm(ModelForm):
    # We hide the group section, as this is set by the view
    group = CharField(widget=HiddenInput(), required=False)

    class Meta:
        model = Message
        fields = ["message", "group"]

        widgets = {
            "message": TextInput(
                attrs={
                    "class": "form-control",
                    "id": "message",
                    "rows": "1",
                    "placeholder": "Your Message",
                    "required": True
                }
            ),
        }


class GroupMessageUpdateForm(ModelForm):
    """
    Different form for update, as this render in the modal
    """

    class Meta:
        model = Message
        fields = ["message", ]

        widgets = {
            "message": Textarea(
                attrs={
                    "class": "validate form-control",
                    "rows": "5",
                    "cols": 5,
                },
            )
        }


class CollaborationMessageForm(ModelForm):
    # We hide the collaboration section, as this is set by the view
    collaboration = CharField(widget=HiddenInput(), required=False)

    class Meta:
        model = Message
        fields = ["message", "collaboration"]

        widgets = {
            "message": TextInput(
                attrs={
                    "class": "form-control",
                    "id": "message",
                    "rows": "1",
                    "placeholder": "Your Message",
                    "required": True
                }
            ),
        }


class CollaborationMessageUpdateForm(ModelForm):
    """
    Different form for update, as this render in the modal
    """

    class Meta:
        model = Message
        fields = ["message", ]

        widgets = {
            "message": Textarea(
                attrs={
                    "class": "validate form-control",
                    "rows": "5",
                    "cols": 5,
                },
            )
        }
