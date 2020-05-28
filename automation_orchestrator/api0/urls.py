from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from rest_framework import routers
from rest_framework.documentation import include_docs_urls
from .views import ApiTriggerView, BotflowExecutionView, PythonFunctionView, PythonFunctionExecutionView


router = routers.DefaultRouter()
router.register('apitrigger', ApiTriggerView, basename='api_trigger')
router.register('botflowexecution', BotflowExecutionView)
router.register('pythonfunction', PythonFunctionView, basename='python_function')
router.register('pythonfunctionexecution', PythonFunctionExecutionView)

urlpatterns = [
    path('', include(router.urls)),
    path('docs/', include_docs_urls(title='Automation Orchestrator',
                                    description="",
                                    public=True))
]

urlpatterns += staticfiles_urlpatterns()
