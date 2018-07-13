from django.forms import ModelForm
from aafinder.models import Meeting


class MeetingForm(ModelForm):
    class Meta:
        model = Meeting
        fields = ['area', 'codes', 'types']
