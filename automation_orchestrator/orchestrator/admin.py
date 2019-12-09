from django import forms
from django.contrib import admin, messages
from django.contrib.auth.models import Group
from django.http import HttpResponse
from .models import Bot, App, Botflow, FileTrigger, ScheduleTrigger, EmailImapTrigger, EmailOutlookTrigger, Execution, SmtpAccount
from .monitoring import add_execution_object
import csv
import os


admin.site.site_header = 'Basico P/S - Automation Orchestrator'
admin.site.site_title = 'Basico P/S - Automation Orchestrator'
admin.site.index_title = 'Orchestrate amazing automation'


def queue_item(item, trigger):
    add_execution_object(item, trigger)
    

def activate_selected_file_triggers(modeladmin, request, queryset):
    for item in queryset:
        queue_item(item, "File Trigger: Activated Manually")
    

def activate_selected_schedule_triggers(modeladmin, request, queryset):
    for item in queryset:
        queue_item(item, "Schedule Trigger: Activated Manually")
    

def activate_selected_email_imap_triggers(modeladmin, request, queryset):
    for item in queryset:
        queue_item(item, "Email IMAP Trigger: Activated Manually")
    

def activate_selected_email_outlook_triggers(modeladmin, request, queryset):
    for item in queryset:
        queue_item(item, "Email Outlook Trigger: Activated Manually")


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


def export_selected_email_imap_triggers(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="email_imap_triggers.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['pk', 'bot', 'app', 'botflow', 
                     'email', 'server', 'port', 'tls',
                     'folder_in', 'folder_out',
                     'activated',
                     'run_after', 'run_until', 'run_on_week_days', 'run_on_weekend_days',])
    
    email_imap_triggers = queryset.values_list('pk', 'bot', 'app', 'botflow',
                                               'email', 'server', 'port', 'tls',
                                               'folder_in', 'folder_out',
                                               'activated',
                                               'run_after', 'run_until', 'run_on_week_days', 'run_on_weekend_days',)
    
    for email_imap_trigger in email_imap_triggers:
        writer.writerow(email_imap_trigger)
        
    return response


def export_selected_email_outlook_triggers(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="email_outlook_triggers.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['pk', 'bot', 'app', 'botflow',
                     'email',
                     'folder_in', 'folder_out',
                     'activated',
                     'run_after', 'run_until', 'run_on_week_days', 'run_on_weekend_days',])
    
    email_outlook_triggers = queryset.values_list('pk', 'bot', 'app', 'botflow',
                                                  'email',
                                                  'folder_in', 'folder_out',
                                                  'activated',
                                                  'run_after', 'run_until', 'run_on_week_days', 'run_on_weekend_days',)
    
    for email_outlook_trigger in email_outlook_triggers:
        writer.writerow(email_outlook_trigger)
        
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
    

def test_selected_file_triggers_triggers(modeladmin, request, queryset):
    import glob
    
    for item in queryset:
        try:
            if not os.path.isdir(item.folder_in):
                messages.error(request, f"Failed to find the incoming folder: {item.folder_in}")
                continue
            
            elif not os.path.isdir(item.folder_out):
                messages.error(request, f"Failed to find the outgoing folder: {item.folder_out}")
                continue
        
            files = []
            for filter in item.filter.split(","):
                files = files + [file for file in glob.glob(item.folder_in + "\\" + filter.strip()) if os.path.isfile(file)]
                
            messages.success(request, f"Successfully retrieved {str(len(files))} file(s) in the incoming folder: {item.folder_in}")
                
        except:
            messages.error(request, f"Failed to retrieve files from the incoming folder: {item.folder_in}")
    

def test_selected_email_imap_triggers(modeladmin, request, queryset):
    from imaplib import IMAP4, IMAP4_SSL
    
    for item in queryset:
        try:
            if item.tls:
                server = IMAP4_SSL(item.server, item.port)                    
            else:
                server = IMAP4(item.server, item.port)
                
            server.login(item.email, item.password)
            
            server.select('INBOX')
            server.select('INBOX/' + item.folder_in)
            server.select('INBOX/' + item.folder_out)
        
            emails = server.select('INBOX/' + item.folder_in, readonly=True)[-1][-1]
                
            messages.success(request, f"Successfully connected to email {item.email}! Number of messages detected in the 'INBOX/{item.folder_in}' folder: {str(emails, 'utf-8', 'ignore')}")
                
        except:
            messages.error(request, f"Failed to connect to email {item.email}!")
            
        finally:
            try:
                server.logout()
            except:
                pass
            
            server = None
            del server
    

def test_selected_email_outlook_triggers(modeladmin, request, queryset):
    import win32com.client as win32
    
    email_outlook = win32.dynamic.Dispatch('Outlook.Application')
    
    for item in queryset:
        try:
            accounts = email_outlook.Session.Accounts
            accounts_list = [account.DisplayName for account in accounts]
            
            if item.email == "Default":
                namespace = email_outlook.GetNamespace("MAPI")
                
            else:
                if not item.email in accounts_list:
                    continue
                
                namespace = None
                
                for account in accounts:
                    if str(item.email).upper() == str(account.DisplayName).upper():
                        namespace = account.DeliveryStore
                        break
            
            inbox = namespace.GetDefaultFolder(6)
        
            folder_in = inbox
            folder_out = inbox
            
            for folder in item.folder_in.split("/"):
                folder_in = folder_in.Folders[folder]
            
            for folder in item.folder_out.split("/"):
                folder_out = folder_out.Folders[folder]
                
            emails = folder_in.Items
                
            messages.success(request, f"Successfully connected to email {item.email}! Number of messages detected in the 'INBOX/{item.folder_in}' folder: {str(len(emails))}")
            
        except:
            pass
        
        finally:
            accounts, accounts_list, namespace, inbox, folder_in, folder_out, emails = None, None, None, None, None, None, None
            del accounts, accounts_list, namespace, inbox, folder_in, folder_out, emails
            
    try:
        email_outlook.Application.Quit()
    except:
        pass
    
    email_outlook = None
    del email_outlook
    

def test_selected_smtp_accounts(modeladmin, request, queryset):
    from smtplib import SMTP, SMTP_SSL
    from email.message import EmailMessage
    
    for item in queryset:
        try:
            msg = EmailMessage()
            msg['Subject'] = "[TEST] Basico P/S Automation Orchestrator"
            msg['From'] = item.email
            msg['To'] = item.email

            with SMTP(item.server, item.port) as server:
                if item.tls:
                    server.starttls()
                server.login(item.email, item.password)
                server.send_message(msg)
                
            messages.success(request, f"Successfully sent an email with {item.email}!")
                
        except:
            if item.tls:
                try:
                    msg = EmailMessage()
                    msg['Subject'] = "[TEST] Basico P/S Automation Orchestrator"
                    msg['From'] = item.email
                    msg['To'] = item.email
                    
                    with SMTP_SSL(item.server, item.port) as server:
                        server.login(item.email, item.password)
                        server.send_message(msg)
                        
                    messages.success(request, f"Successfully sent an email with {item.email}!")
                    continue
                
                except:
                    pass
            
            messages.error(request, f"Failed to send email with {item.email}!")


class BotAdmin(admin.ModelAdmin):
    fieldsets = (
        ('General', {
            'fields': ('name', 'computer_name', 'user_name',),
        }),
        ('Nintex RPA', {
            'classes': ('collapse',),
            'fields': ('nintex_rpa_license_path', 'nintex_rpa_available_foxtrot_licenses', 'nintex_rpa_available_foxbot_licenses',),
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
    
    actions = [activate_selected_file_triggers, export_selected_file_triggers, test_selected_file_triggers_triggers]


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
    
    actions = [activate_selected_schedule_triggers, export_selected_schedule_triggers,]


class EmailImapTriggerForm(forms.ModelForm):    
    class Meta:
        model = EmailImapTrigger
        fields = '__all__'
        widgets = {
            'password': forms.PasswordInput(),
        }


class EmailImapTriggerAdmin(admin.ModelAdmin):
    form = EmailImapTriggerForm
    
    fieldsets = (
        ('General', {
            'fields': ('bot', 'app', 'botflow',),
        }),
        ('Email', {
            'fields': ('email', 'password',),
        }),
        ('Connection', {
            'fields': ('server', 'port', 'tls',),
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
    
    actions = [activate_selected_email_imap_triggers, export_selected_email_imap_triggers, test_selected_email_imap_triggers,]


class EmailOutlookTriggerAdmin(admin.ModelAdmin):
    fieldsets = (
        ('General', {
            'fields': ('bot', 'app', 'botflow',),
        }),
        ('Email', {
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
    
    actions = [activate_selected_email_outlook_triggers, export_selected_email_outlook_triggers, test_selected_email_outlook_triggers,]


class ExecutionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'time_queued',
                    'computer_name', 'user_name',
                    'app', 'botflow',
                    'trigger', 
                    'priority',
                    'status', 
                    'time_start', 'time_end',)
    list_display_links = ['pk']
    list_filter = ('computer_name', 'user_name', 'app', 'botflow', 'status',)
    readonly_fields = [field.name for field in Execution._meta.get_fields() if field.name != 'status']
    
    actions = [export_selected_executions,]

    def get_ordering(self, request):
        return ['-time_queued']


class SmtpAccountForm(forms.ModelForm):    
    class Meta:
        model = SmtpAccount
        fields = '__all__'
        widgets = {
            'password': forms.PasswordInput(),
        }
        

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
admin.site.register(EmailImapTrigger, EmailImapTriggerAdmin)
admin.site.register(EmailOutlookTrigger, EmailOutlookTriggerAdmin)
admin.site.register(Execution, ExecutionAdmin)
admin.site.register(SmtpAccount, SmtpAccountAdmin)
