import datetime
from django import forms
from django.forms.fields import DateField, TimeField
from django.core.exceptions import ValidationError
from django.forms.utils import from_current_timezone, to_current_timezone
from aafinder.models import Meeting, MeetingArea, MeetingType
from django.utils.translation import gettext_lazy as _
from aafinder.utils import now

AREAS = None
MEETING_TYPES = None


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


def get_types_choices():
    global MEETING_TYPES
    if MEETING_TYPES:
        return MEETING_TYPES

    today = datetime.date.today()
    sunday = today - datetime.timedelta(today.weekday()+1)

    MEETING_TYPES = []

    for i in range(7):
        tmp_date = sunday + datetime.timedelta(i)
        weekday = tmp_date.strftime('%A')
        MEETING_TYPES.append(
            (
                MeetingType.objects.only('pk').get(type=weekday).pk,
                weekday
            )
        )

    return MEETING_TYPES

class MeetingSearchForm(forms.Form):
    day = forms.ChoiceField(choices=get_types_choices)
    time = forms.TimeField(initial=now)
    hours_from_start = forms.IntegerField(initial=3, max_value=24)
    area = forms.ChoiceField(choices=get_meeting_area_choices)
    # end_time = forms.TimeField(initial=get_date_offset, input_formats=['%H:%M', ])
    # widgets


