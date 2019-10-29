from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from rest_framework import routers
from rest_framework.documentation import include_docs_urls
from . import views


router = routers.DefaultRouter()
router.register('execution', views.ExecutionView)

urlpatterns = [
    path('', include(router.urls)),
    path('docs/', include_docs_urls(title='Basico P/S - Automation Orchestrator',
                                    description="",
                                    public=True))
    ]

urlpatterns += staticfiles_urlpatterns()
