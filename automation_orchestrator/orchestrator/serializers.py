from rest_framework import serializers
from .models import ApiTrigger, BotflowExecution, PythonFunction, PythonFunctionExecution


class ApiTriggerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApiTrigger
        fields = '__all__'
        read_only_fields = [field.name for field in ApiTrigger._meta.get_fields()]


class BotflowExecutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BotflowExecution
        fields = '__all__'
        read_only_fields = [field.name for field in BotflowExecution._meta.get_fields() if field.name != 'status' and field.name != 'time_start' and field.name != 'time_end']


class PythonFunctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PythonFunction
        fields = [field.name for field in PythonFunction._meta.get_fields() if field.name != 'code' and not 'encrypted' in field.name]
        read_only_fields = [field.name for field in PythonFunction._meta.get_fields()]


class PythonFunctionExecutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PythonFunctionExecution
        fields = [field.name for field in PythonFunctionExecution._meta.get_fields() if field.name != 'code']
        read_only_fields = [field.name for field in PythonFunctionExecution._meta.get_fields()]
