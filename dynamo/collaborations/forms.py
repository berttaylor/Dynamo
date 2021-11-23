from django.forms import ModelForm, HiddenInput, CharField, DateInput, ChoiceField, RadioSelect, ModelChoiceField

from collaborations.models import CollaborationMilestone, CollaborationTask


class TaskForm(ModelForm):
    # We hide the collaboration section, as this is set by the view

    collaboration = CharField(widget=HiddenInput(), required=False)
    assigned_to = ModelChoiceField(queryset=None, required=False)

    def __init__(self, *args, **kwargs):
        """
        We override init to grab the collaboration, and use it to populate the assigned_to with the group members,
        so that they can be selected
        """
        super(TaskForm, self).__init__(*args, **kwargs)
        collaboration = kwargs['initial']['collaboration']
        group_members = collaboration.related_group.members.all()
        self.fields['assigned_to'].queryset = group_members

    class Meta:
        model = CollaborationTask
        fields = ["name", "description", "collaboration", "assigned_to"]


class DateInputLocal(DateInput):
    input_type = 'datetime-local'


class MilestoneForm(ModelForm):
    # We hide the collaboration section, as this is set by the view
    collaboration = CharField(widget=HiddenInput(), required=False)

    class Meta:
        model = CollaborationMilestone
        fields = ["name", "target_date", "collaboration"]
        widgets = {
            'target_date': DateInputLocal()
        }
