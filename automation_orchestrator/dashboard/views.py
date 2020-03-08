import pytz
import json
from datetime import datetime, timedelta
from django.core import serializers
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from orchestrator.models import *


def redirect_overview(request):
    return redirect('dashboard-overview')


@login_required
def overview(request):

    today = datetime.now().date()

    bots = Bot.objects.all()
    apps = App.objects.all()
    botflows = Botflow.objects.all()

    botflow_executions = BotflowExecution.objects.all()

    botflow_executions_running = botflow_executions.filter(status='Running')
    botflow_executions_pending = botflow_executions.filter(status='Pending')
    botflow_executions_completed_today = botflow_executions.filter(status='Completed', time_end__date=today)
    botflow_executions_failed_today = botflow_executions.filter(time_end__date=today).exclude(status='Completed')

    botflow_executions = list(botflow_executions.values())
    for element in botflow_executions:
        element['time_queued'] = (element['time_queued'] + timedelta(hours=int(datetime.now(pytz.timezone('Europe/Copenhagen')).utcoffset().seconds / 60 / 60))).strftime(f"%Y-%m-%dT%H:%M:%S")

        try:
            element['time_start'] = (element['time_start'] + timedelta(hours=int(datetime.now(pytz.timezone('Europe/Copenhagen')).utcoffset().seconds / 60 / 60))).strftime(f"%Y-%m-%dT%H:%M:%S")
        except:
            element['time_start'] = ""

        try:
            element['time_end'] = (element['time_end'] + timedelta(hours=int(datetime.now(pytz.timezone('Europe/Copenhagen')).utcoffset().seconds / 60 / 60))).strftime(f"%Y-%m-%dT%H:%M:%S")
        except:
            element['time_end'] = ""

        if '\\' in element['app']:
            element['app'] = element['app'].split("\\")[-1]

        if '\\' in element['botflow']:
            element['botflow'] = element['botflow'].split("\\")[-1]

    botflow_executions_json = json.dumps(botflow_executions)

    python_functions = PythonFunction.objects.all()
    python_function_executions = PythonFunctionExecution.objects.all()

    context = {
        'bots': bots,
        'apps': apps,
        'botflows': botflows,
        'botflow_executions': botflow_executions,
        'botflow_executions_json': botflow_executions_json,
        'botflow_executions_running': botflow_executions_running,
        'botflow_executions_pending': botflow_executions_pending,
        'botflow_executions_completed_today': botflow_executions_completed_today,
        'botflow_executions_failed_today': botflow_executions_failed_today,
        'python_functions': python_functions,
        'python_function_executions': python_function_executions,
    }

    return render(request, 'dashboard/overview.html', context)
