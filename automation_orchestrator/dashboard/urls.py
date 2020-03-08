from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path
from .views import redirect_overview, overview


urlpatterns = [
    path('', redirect_overview),
    path('overview/', overview, name='dashboard-overview'),
]

urlpatterns += staticfiles_urlpatterns()
