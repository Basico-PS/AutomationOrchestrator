from django import forms
from django.contrib import admin, messages
from django.contrib.auth.models import Group
from django.http import HttpResponse
from .models import Bot, App, Botflow, FileTrigger, ScheduleTrigger, OutlookDesktopTrigger, Execution, SmtpAccount
import csv
import os


admin.site.site_header = 'Basico P/S - Automation Orchestrator'


def queue_item(item, trigger):
    bot_object = Bot.objects.get(pk=item.bot.pk)
    app_object = App.objects.get(pk=item.app.pk)
    botflow_object = Botflow.objects.get(pk=item.botflow.pk)
                
    execution = Execution(app=app_object.path, 
                          botflow=botflow_object.path,
                          trigger=trigger,
                          close_bot_automatically=botflow_object.close_bot_automatically,
                          timeout_minutes=botflow_object.timeout_minutes,
                          timeout_kill_processes=botflow_object.timeout_kill_processes,
                          computer_name=bot_object.computer_name,
                          user_name=bot_object.user_name,
                          priority=botflow_object.priority,
                          status="Pending",
                          queued_notification = botflow_object.queued_notification,
                          started_notification = botflow_object.started_notification,
                          completed_notification = botflow_object.completed_notification,
                          error_notification = botflow_object.error_notification)
    execution.save()
    

def activate_selected_file_triggers(modeladmin, request, queryset):
    for item in queryset:
        queue_item(item, "File Trigger: Activated Manually")
    

def activate_selected_schedule_triggers(modeladmin, request, queryset):
    for item in queryset:
        queue_item(item, "Schedule Trigger: Activated Manually")
    

def activate_selected_outlook_triggers(modeladmin, request, queryset):
    for item in queryset:
        queue_item(item, "Outlook Trigger: Activated Manually")


def export_selected_file_triggers(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="file_triggers.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['pk', 'bot', 'app', 'botflow', 
                     'folder_in', 'folder_out',
                     'activated',
                     'run_after', 'run_until', 'run_on_week_days', 'run_on_weekend_days',])
    
    file_triggers = queryset.values_list('pk', 'bot', 'app', 'botflow', 
                                         'folder_in', 'folder_out',
                                         'activated',
                                         'run_after', 'run_until', 'run_on_week_days', 'run_on_weekend_days',)
    for file_trigger in file_triggers:
        writer.writerow(file_trigger)
        
    return response


def export_selected_schedule_triggers(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="schedule_triggers.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['pk', 'bot', 'app', 'botflow', 
                     'frequency', 'run_every', 'run_start',
                     'activated',
                     'run_after', 'run_until', 'run_on_week_days', 'run_on_weekend_days',])
    
    schedule_triggers = queryset.values_list('pk', 'bot', 'app', 'botflow', 
                                             'frequency', 'run_every', 'run_start',
                                             'activated',
                                             'run_after', 'run_until', 'run_on_week_days', 'run_on_weekend_days',)
    
    for schedule_trigger in schedule_triggers:
        writer.writerow(schedule_trigger)
        
    return response


def export_selected_outlook_triggers(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="outlook_triggers.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['pk', 'bot', 'app', 'botflow', 
                     'folder_in', 'folder_out',
                     'activated',
                     'run_after', 'run_until', 'run_on_week_days', 'run_on_weekend_days',])
    
    outlook_triggers = queryset.values_list('pk', 'bot', 'app', 'botflow', 
                                            'folder_in', 'folder_out',
                                            'activated',
                                            'run_after', 'run_until', 'run_on_week_days', 'run_on_weekend_days',)
    
    for outlook_trigger in outlook_triggers:
        writer.writerow(outlook_trigger)
        
    return response


def export_selected_executions(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="executions.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['pk', 'time_queued',
                     'computer_name', 'user_name',
                     'app', 'botflow', 'trigger',
                     'priority', 'timeout_minutes',
                     'status', 'time_start', 'time_end'])
    
    executions = queryset.values_list('pk', 'time_queued',
                                      'computer_name', 'user_name',
                                      'app', 'botflow', 'trigger',
                                      'priority', 'timeout_minutes',
                                      'status', 'time_start', 'time_end')
    
    for execution in executions:
        writer.writerow(execution)
        
    return response
    

def test_selected_smtp_accounts(modeladmin, request, queryset):
    import smtplib
    from email.message import EmailMessage
    
    for item in queryset:
        try:
            msg = EmailMessage()
            msg['Subject'] = "[TEST] Basico P/S Automation Orchestrator"
            msg['From'] = item.email
            msg['To'] = item.email

            with smtplib.SMTP(item.server, item.port) as server:
                if item.tls:
                    server.starttls()
                server.login(item.email, item.password)
                server.send_message(msg)
                
            messages.success(request, f"Successfully sent an email with {item.email}!")
                
        except:
            messages.error(request, f"Failed to send email with {item.email}!")


class BotForm(forms.ModelForm):
    class Meta:
        model = Bot
        fields = '__all__'

    def clean(self):
        computer_name = self.cleaned_data.get('computer_name')
        user_name = self.cleaned_data.get('user_name')
        
        if Bot.objects.filter(computer_name=computer_name).filter(user_name=user_name).exists():
            raise forms.ValidationError('A bot with the same computer name and username already exist!')
        
        return self.cleaned_data


class BotAdmin(admin.ModelAdmin):
    form = BotForm
    
    fieldsets = (
        ('General', {
            'fields': ('name', 'computer_name', 'user_name',),
        }),
    )
    list_display = ('pk', 'name', 'computer_name', 'user_name',)
    list_editable = ('name', 'computer_name', 'user_name',)
    list_display_links = ['pk']


class AppForm(forms.ModelForm):
    class Meta:
        model = App
        fields = '__all__'

    def clean(self):
        path = self.cleaned_data.get('path')
        
        if not os.path.isfile(path):
            raise forms.ValidationError("The specified file in the path field does not exist!")
        
        return self.cleaned_data


class AppAdmin(admin.ModelAdmin):
    # form = AppForm
    
    fieldsets = (
        ('General', {
            'fields': ('name', 'path',),
        }),
    )
    list_display = ('pk', 'name', 'path',)
    list_editable = ('name', 'path',)
    list_display_links = ['pk']


class BotflowForm(forms.ModelForm):    
    class Meta:
        model = Botflow
        fields = '__all__'

    def clean(self):
        path = self.cleaned_data.get('path')
        
        if not os.path.isfile(path):
            raise forms.ValidationError("The specified file in the path field does not exist!")
        
        return self.cleaned_data


class BotflowAdmin(admin.ModelAdmin):
    # form = BotflowForm
    
    fieldsets = (
        ('General', {
            'fields': ('name', 'path',),
        }),
        ('Queueing', {
            'fields': ('queue_if_already_running',),
        }),
        ('Prioritization', {
            'classes': ('collapse',),
            'fields': ('priority',),
        }),
        ('Timeout', {
            'classes': ('collapse',),
            'fields': ('timeout_minutes', 'timeout_kill_processes',),
        }),
        ('Notifications', {
            'classes': ('collapse',),
            'fields': ('queued_notification', 'started_notification', 'completed_notification', 'error_notification',),
        }),
        ('Nintex RPA', {
            'classes': ('collapse',),
            'fields': ('close_bot_automatically',),
        }),
    )
    list_display = ('pk', 'name', 'path',
                    'queue_if_already_running',
                    'priority',)
    list_editable = ('name', 'path',
                     'queue_if_already_running',
                     'priority',)
    list_display_links = ['pk']


class FileTriggerAdmin(admin.ModelAdmin):
    fieldsets = (
        ('General', {
            'fields': ('bot', 'app', 'botflow',),
        }),
        ('Folders', {
            'fields': ('folder_in', 'folder_out',),
        }),
        ('Filter', {
            'fields': ('filter',),
        }),
        ('Activate', {
            'fields': ('activated',),
        }),
        ('Time Filter', {
            'classes': ('collapse',),
            'fields': ('run_after', 'run_until', 'run_on_week_days', 'run_on_weekend_days',),
        }),
    )
    
    list_display = ('pk', 'bot', 'app', 'botflow', 
                    'folder_in', 'folder_out', 'filter', 'activated')
    list_editable = ('bot', 'app', 'botflow', 
                    'folder_in', 'folder_out', 'filter', 'activated')
    list_display_links = ['pk']
    
    actions = [export_selected_file_triggers, activate_selected_file_triggers,]


class ScheduleTriggerAdmin(admin.ModelAdmin):
    fieldsets = (
        ('General', {
            'fields': ('bot', 'app', 'botflow'),
        }),
        ('Recurrence', {
            'fields': ('frequency', 'run_every', 'run_start',),
        }),
        ('Activate', {
            'fields': ('activated',),
        }),
        ('Time Filter', {
            'classes': ('collapse',),
            'fields': ('run_after', 'run_until', 'run_on_week_days', 'run_on_weekend_days'),
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('next_execution',),
        }),
    )
    
    list_display = ('pk', 'bot', 'app', 'botflow', 
                    'frequency', 'run_every', 'run_start', 'activated',)
    list_editable = ('bot', 'app', 'botflow', 
                    'frequency', 'run_every', 'run_start', 'activated',)
    list_display_links = ['pk']
    exclude = ('past_settings',)
    readonly_fields = ('next_execution',)
    
    actions = [export_selected_schedule_triggers, activate_selected_schedule_triggers,]


class OutlookDesktopTriggerAdmin(admin.ModelAdmin):
    fieldsets = (
        ('General', {
            'fields': ('bot', 'app', 'botflow',),
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
        ('Time Filter', {
            'classes': ('collapse',),
            'fields': ('run_after', 'run_until', 'run_on_week_days', 'run_on_weekend_days',),
        }),
    )
    
    list_display = ('pk', 'bot', 'app', 'botflow', 
                    'email',
                    'folder_in', 'folder_out', 'activated')
    list_editable = ('bot', 'app', 'botflow', 
                     'email',
                     'folder_in', 'folder_out', 'activated')
    list_display_links = ['pk']
    
    actions = [export_selected_outlook_triggers, activate_selected_outlook_triggers,]


class ExecutionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'time_queued',
                    'computer_name', 'user_name',
                    'app', 'botflow',
                    'trigger', 
                    'priority', 'timeout_minutes',
                    'status', 'time_start', 'time_end',)
    list_display_links = ['pk']
    list_filter = ('computer_name', 'user_name', 'app', 'botflow', 'status',)
    
    actions = [export_selected_executions, ]

    def get_ordering(self, request):
        return ['-time_queued']


class SmtpAccountForm(forms.ModelForm):    
    class Meta:
        model = SmtpAccount
        fields = '__all__'
        widgets = {
            'password': forms.PasswordInput(),
        }

    def clean(self):
        activated = self.cleaned_data.get('activated')
        
        if activated and SmtpAccount.objects.filter(activated=True).exists():
            raise forms.ValidationError("An activated SMTP account already exists! Make sure to not activate this account or deactivate the activated account.")
        
        return self.cleaned_data
        

class SmtpAccountAdmin(admin.ModelAdmin):
    form = SmtpAccountForm
    
    fieldsets = (
        ('General', {
            'fields': ('email', 'password',),
        }),
        ('Connection', {
            'fields': ('server', 'port', 'tls',),
        }),
        ('Activate', {
            'fields': ('activated',),
        }),
    )
    
    list_display = ('pk', 'email',
                    'server', 'port', 'tls',
                    'activated',)
    list_editable = ('server', 'port', 'tls',
                     'activated',)
    list_display_links = ['pk']
    
    actions = [test_selected_smtp_accounts, ]

    def get_ordering(self, request):
        return ['-activated']


admin.site.register(Bot, BotAdmin)
admin.site.register(App, AppAdmin)
admin.site.register(Botflow, BotflowAdmin)
admin.site.register(FileTrigger, FileTriggerAdmin)
admin.site.register(ScheduleTrigger, ScheduleTriggerAdmin)
admin.site.register(OutlookDesktopTrigger, OutlookDesktopTriggerAdmin)
admin.site.register(Execution, ExecutionAdmin)
admin.site.register(SmtpAccount, SmtpAccountAdmin)
