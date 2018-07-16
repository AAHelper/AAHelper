from django.urls import path

from . import views

app_name = 'aafinder'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('area/<int:pk>/', views.AreaDetailView.as_view(), name='area_detail'),
    # path('search/', views.MeetingFilter.as_view(), name='search'),
    # path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    # path('<int:question_id>/vote/', views.vote, name='vote'),
]
