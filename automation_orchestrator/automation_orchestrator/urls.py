import os
import threading
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
from orchestrator.monitoring import file_trigger_monitor, schedule_trigger_monitor, email_imap_trigger_monitor, email_outlook_trigger_monitor, botflow_execution_monitor


def start_file_trigger_monitor():
    t = threading.Thread(target=file_trigger_monitor)
    t.setDaemon(True)
    t.start()


def start_schedule_trigger_monitor():
    t = threading.Thread(target=schedule_trigger_monitor)
    t.setDaemon(True)
    t.start()


def start_email_imap_trigger_monitor():
    t = threading.Thread(target=email_imap_trigger_monitor)
    t.setDaemon(True)
    t.start()


def start_email_outlook_trigger_monitor():
    t = threading.Thread(target=email_outlook_trigger_monitor)
    t.setDaemon(True)
    t.start()


def start_botflow_execution_monitor():
    t = threading.Thread(target=botflow_execution_monitor)
    t.setDaemon(True)
    t.start()


urlpatterns = [
    path('api/0/', include('api0.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('', admin.site.urls),
]

if os.path.exists('logs\\error_log.txt'):
    os.remove('logs\\error_log.txt')

if os.path.exists('logs\\error_bot_status.txt'):
    os.remove('logs\\error_bot_status.txt')

start_file_trigger_monitor()
start_schedule_trigger_monitor()
start_email_imap_trigger_monitor()
start_email_outlook_trigger_monitor()
start_botflow_execution_monitor()
