from django.contrib import admin
from django.contrib.auth.models import Group
from django.http import HttpResponse
from .models import App, Botflow, FileTrigger, ScheduleTrigger, OutlookTrigger, Execution
import csv


admin.site.site_header = 'Basico P/S - Automation Orchestrator'


def export_selected_file_triggers(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="file_triggers.csv"'
    writer = csv.writer(response)
    writer.writerow(['pk', 'app', 'botflow', 
                     'folder_in', 'folder_out',
                     'activated',
                     'priority',
                     'run_after', 'run_until', 'run_on_week_days', 'run_on_weekend_days',
                     'computer_name', 'user_name'])
    file_triggers = queryset.values_list('pk', 'app', 'botflow', 
                                         'folder_in', 'folder_out',
                                         'activated',
                                         'priority',
                                         'run_after', 'run_until', 'run_on_week_days', 'run_on_weekend_days',
                                         'computer_name', 'user_name')
    for file_trigger in file_triggers:
        writer.writerow(file_trigger)
    return response


def export_selected_schedule_triggers(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="schedule_triggers.csv"'
    writer = csv.writer(response)
    writer.writerow(['pk', 'app', 'botflow', 
                     'frequency', 'run_every', 'run_start',
                     'activated',
                     'priority',
                     'run_after', 'run_until', 'run_on_week_days', 'run_on_weekend_days',
                     'computer_name', 'user_name'])
    schedule_triggers = queryset.values_list('pk', 'app', 'botflow', 
                                             'frequency', 'run_every', 'run_start',
                                             'activated',
                                             'priority',
                                             'run_after', 'run_until', 'run_on_week_days', 'run_on_weekend_days',
                                             'computer_name', 'user_name')
    
    for schedule_trigger in schedule_triggers:
        writer.writerow(schedule_trigger)
    return response


def export_selected_outlook_triggers(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="outlook_triggers.csv"'
    writer = csv.writer(response)
    writer.writerow(['pk', 'app', 'botflow', 
                     'folder_in', 'folder_out',
                     'activated',
                     'priority',
                     'run_after', 'run_until', 'run_on_week_days', 'run_on_weekend_days',
                     'computer_name', 'user_name'])
    outlook_triggers = queryset.values_list('pk', 'app', 'botflow', 
                                            'folder_in', 'folder_out',
                                            'activated',
                                            'priority',
                                            'run_after', 'run_until', 'run_on_week_days', 'run_on_weekend_days',
                                            'computer_name', 'user_name')
    for outlook_trigger in outlook_triggers:
        writer.writerow(outlook_trigger)
    return response


def export_selected_executions(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="executions.csv"'
    writer = csv.writer(response)
    writer.writerow(['pk', 'time_queued', 'app', 'botflow', 'trigger', 
                     'computer_name', 'user_name', 'priority', 'timeout_minutes',
                     'status', 'time_start', 'time_end'])
    executions = queryset.values_list('pk', 'time_queued', 'app', 'botflow', 'trigger', 
                                      'computer_name', 'user_name', 'priority', 'timeout_minutes',
                                      'status', 'time_start', 'time_end')
    for execution in executions:
        writer.writerow(execution)
    return response


class AppAdmin(admin.ModelAdmin):
    fieldsets = (
        ('General', {
            'fields': ('name', 'path',),
        }),
    )
    list_display = ('pk', 'name', 'path',)
    list_editable = ('name', 'path',)
    list_display_links = ['pk']


class BotflowAdmin(admin.ModelAdmin):
    fieldsets = (
        ('General', {
            'fields': ('name', 'path',),
        }),
        ('Queueing', {
            'fields': ('queue_if_already_running',),
        }),
        ('Timeout', {
            'fields': ('timeout_minutes', 'timeout_kill_processes',),
        }),
        ('Nintex RPA', {
            'classes': ('collapse',),
            'fields': ('close_bot_automatically',),
        }),
    )
    list_display = ('pk', 'name', 'path',
                    'queue_if_already_running',
                    'close_bot_automatically',
                    'timeout_minutes', 'timeout_kill_processes',)
    list_editable = ('name', 'path',
                     'queue_if_already_running',
                     'close_bot_automatically',
                     'timeout_minutes', 'timeout_kill_processes',)
    list_display_links = ['pk']


class FileTriggerAdmin(admin.ModelAdmin):
    fieldsets = (
        ('General', {
            'fields': ('app', 'botflow',),
        }),
        ('Folders', {
            'fields': ('folder_in', 'folder_out',),
        }),
        ('Activate', {
            'fields': ('activated',),
        }),
        ('Prioritization', {
            'classes': ('collapse',),
            'fields': ('priority',),
        }),
        ('Time Filter', {
            'classes': ('collapse',),
            'fields': ('run_after', 'run_until', 'run_on_week_days', 'run_on_weekend_days',),
        }),
        ('Computer and User Settings', {
            'classes': ('collapse',),
            'fields': ('computer_name', 'user_name',),
        }),
    )
    
    list_display = ('pk', 'app', 'botflow', 
                    'folder_in', 'folder_out', 'activated')
    list_editable = ('app', 'botflow', 
                    'folder_in', 'folder_out', 'activated')
    list_display_links = ['pk']
    
    actions = [export_selected_file_triggers, ]


class ScheduleTriggerAdmin(admin.ModelAdmin):
    fieldsets = (
        ('General', {
            'fields': ('app', 'botflow'),
        }),
        ('Recurrence', {
            'fields': ('frequency', 'run_every', 'run_start',),
        }),
        ('Activate', {
            'fields': ('activated',),
        }),
        ('Prioritization', {
            'classes': ('collapse',),
            'fields': ('priority',),
        }),
        ('Time Filter', {
            'classes': ('collapse',),
            'fields': ('run_after', 'run_until', 'run_on_week_days', 'run_on_weekend_days'),
        }),
        ('Computer and User Settings', {
            'classes': ('collapse',),
            'fields': ('computer_name', 'user_name',),
        }),
    )
    
    list_display = ('pk', 'app', 'botflow', 
                    'frequency', 'run_every', 'run_start', 'activated',)
    list_editable = ('app', 'botflow', 
                    'frequency', 'run_every', 'run_start', 'activated',)
    list_display_links = ['pk']
    exclude = ('next_execution', 'past_settings')
    
    actions = [export_selected_schedule_triggers, ]


class OutlookTriggerAdmin(admin.ModelAdmin):
    fieldsets = (
        ('General', {
            'fields': ('app', 'botflow',),
        }),
        ('Outlook', {
            'fields': ('email',),
        }),
        ('Folders', {
            'fields': ('folder_in', 'folder_out',),
        }),
        ('Activate', {
            'fields': ('activated',),
        }),
        ('Prioritization', {
            'classes': ('collapse',),
            'fields': ('priority',),
        }),
        ('Time Filter', {
            'classes': ('collapse',),
            'fields': ('run_after', 'run_until', 'run_on_week_days', 'run_on_weekend_days',),
        }),
        ('Computer and User Settings', {
            'classes': ('collapse',),
            'fields': ('computer_name', 'user_name',),
        }),
    )
    
    list_display = ('pk', 'app', 'botflow', 
                    'email',
                    'folder_in', 'folder_out', 'activated')
    list_editable = ('app', 'botflow', 
                    'email',
                    'folder_in', 'folder_out', 'activated')
    list_display_links = ['pk']
    
    actions = [export_selected_outlook_triggers, ]


class ExecutionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'time_queued', 'app', 'botflow', 
                    'trigger', 
                    'computer_name', 'user_name', 'priority', 'timeout_minutes',
                    'status', 'time_start', 'time_end',)
    list_display_links = ['pk']
    list_filter = ('app', 'botflow', 'computer_name', 'user_name', 'status',)
    
    actions = [export_selected_executions, ]

    def get_ordering(self, request):
        return ['-time_queued']


admin.site.register(App, AppAdmin)
admin.site.register(Botflow, BotflowAdmin)
admin.site.register(FileTrigger, FileTriggerAdmin)
admin.site.register(ScheduleTrigger, ScheduleTriggerAdmin)
admin.site.register(OutlookTrigger, OutlookTriggerAdmin)
admin.site.register(Execution, ExecutionAdmin)
