from django.forms import ModelForm, DateInput, ModelChoiceField, Textarea
from django.forms.widgets import Select

from collaborations.models import CollaborationMilestone, CollaborationTask, Collaboration


class DateInputLocal(DateInput):
    input_type = 'datetime-local'


class TaskForm(ModelForm):
    # We hide the collaboration section, as this is set by the view

    assigned_to = ModelChoiceField(queryset=None, required=False)

    def __init__(self, *args, **kwargs):
        """
        We override init to grab the collaboration, and use it to populate the assigned_to with the group members,
        so that they can be selected
        """
        super(TaskForm, self).__init__(*args, **kwargs)
        if kwargs.get('initial'):
            collaboration = kwargs['initial']['collaboration']
            group_members = collaboration.related_group.members.all()
            self.fields['assigned_to'].queryset = group_members
        for field_name, field in self.fields.items():
            if field_name != 'prompt_for_details_on_completion':
                field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = CollaborationTask
        fields = ["name", "description", "assigned_to", 'prompt_for_details_on_completion']
        widgets = {
            "assigned_to": Select(
                attrs={
                    "class": "form-control",
                    "id": "task_name",
                    "rows": "1",
                    "required": True
                }
            ),
            "description": Textarea(
                attrs={
                    "class": "validate form-control",
                    "rows": 4,
                    "cols": 5,
                }
            ),
        }


class TaskUpdateForm(ModelForm):
    # We hide the collaboration section, as this is set by the view

    assigned_to = ModelChoiceField(queryset=None, required=False)

    def __init__(self, *args, **kwargs):
        """
        We override init to grab the collaboration, and use it to populate the assigned_to with the group members,
        so that they can be selected
        """
        super().__init__(*args, **kwargs)
        if kwargs.get('initial'):
            collaboration = kwargs['initial']['collaboration']
            group_members = collaboration.related_group.members.all()
            self.fields['assigned_to'].queryset = group_members
        for field_name, field in self.fields.items():
            if field_name != 'prompt_for_details_on_completion':
                field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = CollaborationTask
        fields = ["name", "description", "assigned_to", 'prompt_for_details_on_completion']
        widgets = {
            "assigned_to": Select(
                attrs={
                    "class": "form-control",
                    "id": "task_name",
                    "rows": "1",
                    "required": True
                }
            ),
            "description": Textarea(
                attrs={
                    "class": "validate form-control",
                    "rows": 4,
                    "cols": 5,
                }
            ),
        }


class TaskCompleteForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(TaskCompleteForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = CollaborationTask
        fields = ["completion_notes", 'file']
        widgets = {
            "completion_notes": Textarea(
                attrs={
                    "rows": 3,
                    "cols": 5,
                }
            ),
        }


class MilestoneForm(ModelForm):
    """
    we use a custom form, so that we can add formatting, and widgets
    """

    class Meta:
        model = CollaborationMilestone
        fields = ["name"]

    def __init__(self, *args, **kwargs):
        super(MilestoneForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class CollaborationForm(ModelForm):
    """
    form used for adding/updating collaborations
    """

    def __init__(self, *args, **kwargs):
        """
        We override init to grab the collaboration, and use it to populate the assigned_to with the group members,
        so that they can be selected
        """
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = Collaboration
        fields = ["name", "description"]
        widgets = {
            "description": Textarea(
                attrs={
                    "class": "validate form-control",
                    "rows": 4,
                    "cols": 5,
                }
            ),
        }


class CollaborationImageForm(ModelForm):
    """
    form used for adding/updating collaboration images
    """

    def __init__(self, *args, **kwargs):
        """
        We override init to grab the collaboration, and use it to populate the assigned_to with the group members,
        so that they can be selected
        """
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = Collaboration
        fields = ["image",]
