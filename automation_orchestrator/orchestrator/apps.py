from django.apps import AppConfig


class OrchestratorConfig(AppConfig):
    name = 'orchestrator'

    def ready(self):
        import orchestrator.signals
