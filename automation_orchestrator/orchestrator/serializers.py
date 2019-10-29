from rest_framework import serializers
from .models import Execution


class ExecutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Execution
        fields = '__all__'
        read_only_fields = [field.name for field in Execution._meta.get_fields() if field.name != 'status' and field.name != 'time_start' and field.name != 'time_end']
