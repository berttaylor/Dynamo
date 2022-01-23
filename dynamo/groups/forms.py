from django.forms import ModelForm, DateInput, ModelChoiceField, Textarea
from django.forms.widgets import Select

from collaborations.models import CollaborationMilestone, CollaborationTask, Collaboration
from groups.models import Group


class GroupForm(ModelForm):
    """Main form for 'Group' creation/updates"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = Group
        fields = ["name", "description", ]
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
            field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = Group
        fields = ["profile_image", ]
