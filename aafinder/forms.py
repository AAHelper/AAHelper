from django.forms import ModelForm
from aafinder.models import Meeting
from django.utils.translation import gettext_lazy as _


class MeetingForm(ModelForm):
    class Meta:
        model = Meeting
        fields = ['area', 'codes', 'types']

        labels = {
            'types': _('Day'),
        }
