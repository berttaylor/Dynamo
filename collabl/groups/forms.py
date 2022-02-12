from django.forms import ModelForm, Textarea, TextInput, FileInput
from groups.models import Group, GroupAnnouncement


class GroupForm(ModelForm):
    """Main form for 'Group' creation/updates"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"

    class Meta:
        model = Group
        fields = [
            "name",
            "description",
        ]
        widgets = {
            "description": Textarea(
                attrs={
                    "class": "validate form-control",
                    "rows": 4,
                    "cols": 5,
                }
            ),
        }


class GroupImageForm(ModelForm):
    """
    form used for adding/updating Group images
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"

    class Meta:
        model = Group
        fields = [
            "profile_image",
        ]
        widgets = {
            "profile_image": FileInput(),
        }


class GroupAnnouncementForm(ModelForm):
    """
    form used for adding/updating Announcements
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"

    class Meta:
        model = GroupAnnouncement
        fields = ["title", "body"]

        widgets = {
            "title": TextInput(
                attrs={
                    "class": "validate form-control",
                    "rows": 1,
                    "cols": 5,
                }
            ),
            "body": Textarea(
                attrs={
                    "class": "validate form-control",
                    "rows": 4,
                    "cols": 5,
                }
            ),
        }
