"""automation_orchestrator URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from orchestrator.monitoring import file_trigger_monitor, schedule_trigger_monitor, outlook_trigger_monitor, execution_monitor
import os
import threading


def start_file_trigger_monitor():
    t = threading.Thread(target=file_trigger_monitor)
    t.setDaemon(True)
    t.start()


def start_schedule_trigger_monitor():
    t = threading.Thread(target=schedule_trigger_monitor)
    t.setDaemon(True)
    t.start()


def start_outlook_trigger_monitor():
    t = threading.Thread(target=outlook_trigger_monitor)
    t.setDaemon(True)
    t.start()


def start_execution_monitor():
    t = threading.Thread(target=execution_monitor)
    t.setDaemon(True)
    t.start()
    

urlpatterns = [
    path('', admin.site.urls),
    path('api/0/', include('orchestrator.urls')),
    ]

if os.path.exists('logs\\error_log.txt'):
    os.remove('logs\\error_log.txt')

start_file_trigger_monitor()
start_schedule_trigger_monitor()
start_outlook_trigger_monitor()
start_execution_monitor()
