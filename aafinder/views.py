import datetime
from django.views import generic
# from django.http import Http404
# from django.utils.translation import gettext as _

from .models import Meeting, MeetingArea
from .forms import MeetingSearchForm, MeetingForm, get_meeting_area_choices
from .utils import get_now_time, get_now_date, get_now_and_offset, now

class InitialFormMixin:
    form_class = MeetingSearchForm
    initial = {}
    prefix = None

    def get_initial(self):
        """Return the initial data to use for forms on this view."""
        initial_data = {
            # 'date': get_now_date(),
            # 'start_time': get_now_time(),
            'area': 'all',
            'date_and_time': now,
            'hours_from_start': 3,
        }
        return initial_data

    def get_prefix(self):
        """Return the prefix to use for forms."""
        return self.prefix

    def get_form_class(self):
        """Return the form class to use."""
        return self.form_class

    def get_form(self, form_class=None):
        """Return an instance of the form to be used in this view."""
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(**self.get_form_kwargs())

    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = {
            'initial': self.get_initial(),
            'prefix': self.get_prefix(),
        }

        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        return kwargs

    def get_filter_values(self, form):
        now, hours_from_now = get_now_and_offset()
        day_word = now.strftime("%A")
        area = "All"

        if form.is_valid():
            now = form.cleaned_data['date_and_time']
            hours_from_now = now + datetime.timedelta(hours=form.cleaned_data['hours_from_start'])
            day_word = now.strftime("%A")
            area = form.cleaned_data['area']

        if area == 'All' or not area.isnumeric():
            area = MeetingArea(area=area)
        else:
            area = MeetingArea.objects.get(pk=area)

        return now, hours_from_now, day_word, area

class IndexView(InitialFormMixin, generic.ListView):
    template_name = 'aasandiego/index.html'
    context_object_name = 'latest_meeting_list'
    

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()

        context = self.get_context_data()
        return self.render_to_response(context)

    def get_queryset(self):
        """Return the last five published questions."""
        form = self.get_form()
        now, hours_from_now, day_word, area = self.get_filter_values(form)

        qs = Meeting.objects.filter(
            types__type=day_word,
            time__gte=now.time(),
            time__lte=hours_from_now,
            ).select_related('area').order_by('time')

        if area.id:
            qs = qs.filter(area=area)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = self.get_form()

        now, hours_from_now, day_word, area = self.get_filter_values(form)

        context['today'] = day_word
        context['now'] = now
        context['hours_from'] = hours_from_now
        context['area'] = area

        context['form'] = form
        return context


class DetailView(generic.DetailView):
    model = Meeting
    template_name = 'aasandiego/detail.html'

class AreaDetailView(InitialFormMixin, generic.DetailView):
    model = MeetingArea
    template_name = 'aasandiego/area_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = self.get_form()

        now, hours_from_now, day_word, area = self.get_filter_values(form)

        context['today'] = day_word
        context['now'] = now
        context['hours_from'] = hours_from_now
        context['area'] = area

        context['form'] = form
        return context


# class MeetingFilter(IndexView, edit.FormView):
#     template_name = 'contact.html'
#     form_class = MeetingSearchForm

#     def form_valid(self, form):
#         # This method is called when valid form data has been POSTed.
#         # It should return an HttpResponse.
#         qs = form.get_queryset()
#         return super().form_valid(form)
