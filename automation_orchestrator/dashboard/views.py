import pytz
import json
from datetime import datetime, timedelta
from django.core import serializers
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from orchestrator.models import *


def redirect_overview(request):
    return redirect('dashboard-overview')


def format_botflow_executions(botflow_executions):
    botflow_executions_overview = []
    botflow_executions_calendar = []

    for element in botflow_executions:
        record_overview = {}
        record_calendar = {}

        record_overview['id'] = element.id

        record_overview['time_queued'] = element.time_queued

        record_overview['computer_name'] = element.computer_name
        record_overview['user_name'] = element.user_name

        record_overview['app'] = element.app
        if '\\' in record_overview['app']:
            record_overview['app_formatted'] = record_overview['app'].split("\\")[-1]
        else:
            record_overview['app_formatted'] = record_overview['app']

        record_overview['botflow'] = element.botflow
        if '\\' in record_overview['botflow']:
            record_overview['botflow_formatted'] = record_overview['botflow'].split("\\")[-1]
        else:
            record_overview['botflow_formatted'] = record_overview['botflow']

        record_overview['trigger'] = element.trigger
        if '\\' in record_overview['trigger']:
            record_overview['trigger_formatted'] = record_overview['trigger'][:(record_overview['trigger'].find(":")+2)] + record_overview['trigger'].split("\\")[-1]
        else:
            record_overview['trigger_formatted'] = record_overview['trigger']

        record_overview['priority'] = element.priority
        record_overview['status'] = element.status

        record_overview['custom_progress'] = element.custom_progress
        record_overview['custom_progress'] = str(record_overview['custom_progress']).replace('.00', '') + '%'
        record_overview['custom_status'] = element.custom_status

        record_overview['time_start'] = element.time_start
        record_overview['time_end'] = element.time_end
        record_overview['time_updated'] = element.time_updated

        record_calendar['computer_name'] = record_overview['computer_name']
        record_calendar['user_name'] = record_overview['user_name']
        record_calendar['botflow'] = record_overview['botflow']
        record_calendar['botflow_formatted'] = record_overview['botflow_formatted']
        record_calendar['status'] = record_overview['status']

        try:
            record_calendar['time_start'] = (record_overview['time_start'] + timedelta(hours=int(datetime.now(pytz.timezone('Europe/Copenhagen')).utcoffset().seconds / 60 / 60))).strftime(f"%Y-%m-%dT%H:%M:%S")
        except:
            record_calendar['time_start'] = ""

        try:
            record_calendar['time_end'] = (record_overview['time_end'] + timedelta(hours=int(datetime.now(pytz.timezone('Europe/Copenhagen')).utcoffset().seconds / 60 / 60))).strftime(f"%Y-%m-%dT%H:%M:%S")
        except:
            record_calendar['time_end'] = ""

        botflow_executions_overview.append(record_overview)
        botflow_executions_calendar.append(record_calendar)

    return botflow_executions_overview, botflow_executions_calendar


def get_context():
    today = datetime.now().date()

    bots = Bot.objects.all()
    bots = [
        {
            'id': bot['id'],
            'name': bot['name'],
            'computer_name': bot['computer_name'],
            'user_name': bot['user_name']
        } for bot in list(bots.values())
    ]

    apps = App.objects.all()
    apps = [
        {
            'id': app['id'],
            'name': app['name'],
            'path': app['path'],
        } for app in list(apps.values())
    ]

    botflows = Botflow.objects.all()
    botflows = [
        {
            'id': botflow['id'],
            'name': botflow['name'],
            'path': botflow['path'],
        } for botflow in list(botflows.values())
    ]

    botflow_executions = BotflowExecution.objects.all()

    botflow_executions_running = botflow_executions.filter(status='Running', time_end__isnull=True)
    botflow_executions_pending = botflow_executions.filter(status='Pending')
    botflow_executions_completed_today = botflow_executions.filter(status='Completed', time_end__date=today)
    botflow_executions_failed_today = botflow_executions.filter(time_end__date=today).exclude(status='Completed')

    python_functions = PythonFunction.objects.all()
    python_function_executions = PythonFunctionExecution.objects.all()

    botflow_executions_overview, botflow_executions_calendar = format_botflow_executions(botflow_executions)

    context = {
        'bots': json.dumps(bots),
        'apps': json.dumps(apps),
        'botflows': json.dumps(botflows),
        'botflow_executions_overview': botflow_executions_overview,
        'botflow_executions_calendar': json.dumps(botflow_executions_calendar),
        'botflow_executions_running': botflow_executions_running,
        'botflow_executions_pending': botflow_executions_pending,
        'botflow_executions_completed_today': botflow_executions_completed_today,
        'botflow_executions_failed_today': botflow_executions_failed_today,
        'python_functions': python_functions,
        'python_function_executions': python_function_executions,
    }

    return context


@login_required
def overview(request):
    return render(request, 'dashboard/overview.html', get_context())


@login_required
def calendar_view(request):
    return render(request, 'dashboard/calendar_view.html', get_context())
