import datetime
from django import forms
from django.forms.fields import DateField, TimeField
from django.core.exceptions import ValidationError
from django.forms.utils import from_current_timezone, to_current_timezone
from aafinder.models import Meeting, MeetingArea
from django.utils.translation import gettext_lazy as _
from aafinder.utils import now, get_now_time, get_now_date, get_now_and_offset

AREAS = None

class MeetingForm(forms.ModelForm):
    class Meta:
        model = Meeting
        fields = ['area', 'codes', 'types']

        labels = {
            'types': _('Day'),
            'codes': _('Meeting Type'),
        }


def get_meeting_area_choices():
    global AREAS
    if AREAS is None:
        AREAS = [('All', 'All'), ] + [(
            c.id, c.area) for c in MeetingArea.objects.all().order_by("area")]
    # areas = areas + [('All', 'All'), ]
    
    return AREAS


class MeetingSearchForm(forms.Form):
    date_and_time = forms.SplitDateTimeField(initial=now)
    hours_from_start = forms.IntegerField(initial=3, max_value=24)
    area = forms.ChoiceField(choices=get_meeting_area_choices)
    # end_time = forms.TimeField(initial=get_date_offset, input_formats=['%H:%M', ])
    # widgets


