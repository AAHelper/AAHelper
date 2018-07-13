# from django.http import HttpResponseRedirect
# from django.shortcuts import get_object_or_404, render
# from django.urls import reverse
import datetime
from django.views import generic

from .models import Meeting
from .forms import MeetingForm


class IndexView(generic.ListView):
    template_name = 'aasandiego/index.html'
    context_object_name = 'latest_meeting_list'

    def get_queryset(self):
        """Return the last five published questions."""

        now = datetime.datetime.now()
        day_word = now.strftime("%A")
        # now = now - datetime.timedelta(hours=1)

        hours_from_now = now + datetime.timedelta(hours=2)

        return Meeting.objects.filter(
            types__type=day_word,
            time__gte=now,
            time__lte=hours_from_now,
            ).distinct().order_by('time')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['today'] = datetime.date.today().strftime("%A")
        context['now'] = datetime.datetime.now()
        context['hours_from_now'] = context['now'] + datetime.timedelta(hours=2)

        context['form'] = MeetingForm()
        return context


class DetailView(generic.DetailView):
    model = Meeting
    template_name = 'aasandiego/detail.html'

