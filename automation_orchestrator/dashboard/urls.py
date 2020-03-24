from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path
from .views import redirect_overview, overview, calendar_view


urlpatterns = [
    path('', redirect_overview),
    path('overview/', overview, name='dashboard-overview'),
    path('calendar-view/', calendar_view, name='dashboard-calendar-view'),
]

urlpatterns += staticfiles_urlpatterns()
