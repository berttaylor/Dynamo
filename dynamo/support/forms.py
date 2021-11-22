from django.forms import ModelForm, Select, Textarea, TextInput

from .models import SupportMessage


class SupportMessageForm(ModelForm):
    class Meta:
        model = SupportMessage
        fields = [
            "name",
            "email",
            "subject",
            "message",
        ]
