from rest_framework import viewsets
from .models import Execution
from .serializers import ExecutionSerializer


class ExecutionView(viewsets.ModelViewSet):
    """
    retrieve:
    Return the given execution record.

    list:
    Return a list of all the existing execution records.

    create:
    Create a new execution record instance.

    update:
    Update the execution record instance.

    partial_update:
    Partially update the execution record instance.

    delete:
    Delete the execution record instance.
    """
    queryset = Execution.objects.exclude(status="Completed")
    serializer_class = ExecutionSerializer
    throttle_scope = 'execution'
    http_method_names = ['get', 'patch']
