from django.urls import path, register_converter

from . import views


class TimeConverter:
    regex = '[0-9]{2}:[0-9]{2}'

    def to_python(self, value):
        return value

    def to_url(self, value):
        return value


register_converter(TimeConverter, 'time')


app_name = 'aafinder'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('details/<int:pk>/', views.DetailView.as_view(), name='meeting_detail'),
    path('area/<slug:slug>/', views.AreaDetailView.as_view(), name='area_detail'),
    path('location/<int:pk>/', views.LocationDetailView.as_view(), name='meetings_by_location'),
    path('code/<int:pk>/', views.CodeDetailView.as_view(), name='meetings_by_code'),
    # path('meeting/search/', views.MeetingSearch.as_view(), name='meeting_search'),
    # path('meeting/<slug:day>/<slug:area>/<time:time>/<int:hours_from_start>/', views.MeetingView.as_view(), name='meeting_redirect'),
    # path('search/', views.MeetingFilter.as_view(), name='search'),
    # path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    # path('<int:question_id>/vote/', views.vote, name='vote'),
]
