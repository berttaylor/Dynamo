from django import forms
from django.forms import ModelForm, Select, Textarea, TextInput

from .models import SupportMessage


class SupportMessageForm(ModelForm):

    class Meta:
        model = SupportMessage
        fields = [
            "name",
            "email",
            "message",
        ]

        widgets = {
            "message": Textarea(
                attrs={
                    "class": "validate form-control",
                    "rows": "7",
                    "cols": 5,
                    "placeholder": "How can we help?",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super(SupportMessageForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'