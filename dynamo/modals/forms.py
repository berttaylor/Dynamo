from django.forms import ModelForm, Textarea

from collaborations.models import CollaborationTask


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