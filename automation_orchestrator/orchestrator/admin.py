from django import forms
from django.db import models
from django.contrib import admin, messages
from django.http import HttpResponse
from django.utils.html import format_html
from simple_history.admin import SimpleHistoryAdmin
from .models import Bot, App, Botflow, FileTrigger, PythonFunction, ScheduleTrigger, EmailImapTrigger, EmailOutlookTrigger, ApiTrigger, BotflowExecution, SmtpAccount, PythonFunction, PythonFunctionExecution
from .monitoring import add_botflow_execution_object
import subprocess
import csv
import os


admin.site.site_header = 'Basico P/S - Automation Orchestrator'
admin.site.site_title = 'Basico P/S - Automation Orchestrator'
admin.site.index_title = 'Orchestrate amazing automation'


def queue_item(item, trigger):
    add_botflow_execution_object(bot_pk=item.bot.pk, app_pk=item.app.pk, botflow_pk=item.botflow.pk, trigger=trigger)


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


def activate_selected_api_triggers(modeladmin, request, queryset):
    for item in queryset:
        queue_item(item, "API Trigger: Activated Manually")


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


def export_selected_api_triggers(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="api_triggers.csv"'

    writer = csv.writer(response)
    writer.writerow(['pk', 'bot', 'app', 'botflow',
                     'activated',])

    api_triggers = queryset.values_list('pk', 'bot', 'app', 'botflow',
                                        'activated',)

    for api_trigger in api_triggers:
        writer.writerow(api_trigger)

    return response


def export_selected_botflow_executions(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="botflow_executions.csv"'

    writer = csv.writer(response)
    writer.writerow(['pk', 'time_queued',
                     'computer_name', 'user_name',
                     'app', 'botflow', 'trigger',
                     'priority', 'timeout_minutes',
                     'status', 'time_start', 'time_end'])

    botflow_executions  = queryset.values_list('pk', 'time_queued',
                                               'computer_name', 'user_name',
                                               'app', 'botflow', 'trigger',
                                               'priority', 'timeout_minutes',
                                               'status', 'time_start', 'time_end')

    for botflow_execution in botflow_executions:
        writer.writerow(botflow_execution)

    return response


def test_selected_bots(modeladmin, request, queryset):
    for item in queryset:
        try:
            computer_name = item.computer_name
            user_name = item.user_name

            if str(computer_name).lower() != os.environ['COMPUTERNAME'].lower():
                psexec_path = os.path.abspath(".\\automation_orchestrator\\tools\\psexec\\psexec.exe")

                if not os.path.isfile(psexec_path):
                    messages.error(request, f"Unable to test the bot as the psexec tool cannot be located: {psexec_path}")

                    if item.status != "Unknown":
                        item.status = "Unknown"
                        item.save()

                    continue

                sessions = subprocess.run([psexec_path, f"\\\\{computer_name}", "query", "session"], stdout=subprocess.PIPE, text=True).stdout.split("\n")

            else:
                sessions = subprocess.run(["query", "session"], stdout=subprocess.PIPE, text=True).stdout.split("\n")

            if not "SESSIONNAME" in str(sessions):
                messages.error(request, f"Failed to connect to computer: {computer_name}")

                if item.status != "ERROR":
                    item.status = "ERROR"
                    item.save()

                continue

            active = False
            for session in sessions:
                if f" {user_name.lower()} " in session.lower() and " Active " in session:
                    active = True
                    break

            if active:
                messages.success(request, f"Successfully connected to computer '{computer_name}' and identified an active session for user: {user_name}")

                if item.status != "Working":
                    item.status = "Working"
                    item.save()

            else:
                messages.error(request, f"Successfully connected to computer '{computer_name}', however, no active session identified for user: {user_name}")

                if item.status != "ERROR":
                    item.status = "ERROR"
                    item.save()

        except:
            messages.error(request, f"Fatal error when attempting to test computer '{computer_name}' and user: {user_name}")

            if item.status != "Unknown":
                item.status = "Unknown"
                item.save()


def test_selected_botflows(modeladmin, request, queryset):
    for item in queryset:
        if os.path.isfile(item.path):
            messages.success(request, f"Successfully located the '{item.name}' Botflow file: {item.path}")
        else:
            messages.error(request, f"Failed to locate the '{item.name}' Botflow file: {item.path}")


def test_selected_file_triggers(modeladmin, request, queryset):
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

            if item.status != "Working":
                item.status = "Working"
                item.save()

        except:
            messages.error(request, f"Failed to retrieve files from the incoming folder: {item.folder_in}")

            item.status = "ERROR"
            item.save()


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

            emails_folder_in = server.select('INBOX/' + item.folder_in, readonly=True)[-1][-1]
            emails_folder_in = str(emails_folder_in, 'utf-8', 'ignore')
            emails_folder_out = server.select('INBOX/' + item.folder_out, readonly=True)[-1][-1]
            emails_folder_out = str(emails_folder_out, 'utf-8', 'ignore')
            
            if "doesn't exist" in emails_folder_in or "doesn't exist" in emails_folder_out:
                messages.error(request, f"Failed to connect to email {item.email}!")

                item.status = "ERROR"
                item.save()
                
            else:
                messages.success(request, f"Successfully connected to email {item.email}! Number of messages detected in the 'INBOX/{item.folder_in}' folder: {emails_folder_in}")

                if item.status != "Working":
                    item.status = "Working"
                    item.save()

        except:
            messages.error(request, f"Failed to connect to email {item.email}!")

            item.status = "ERROR"
            item.save()

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

            if item.status != "Working":
                item.status = "Working"
                item.save()

        except:
            item.status = "ERROR"
            item.save()

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

            if item.status != "Working":
                item.status = "Working"
                item.save()

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

            item.status = "ERROR"
            item.save()


class BotAdmin(SimpleHistoryAdmin):
    fieldsets = (
        ('General', {
            'fields': ('name', 'computer_name', 'user_name',),
        }),
        ('Nintex RPA', {
            'classes': ('collapse',),
            'fields': ('nintex_rpa_license_path', 'nintex_rpa_available_foxtrot_licenses', 'nintex_rpa_available_foxbot_licenses',),
        }),
    )

    list_display = ('pk', 'name', 'computer_name', 'user_name', 'status',
                    'update_record',)
    list_editable = ('name', 'computer_name', 'user_name',)
    list_display_links = ['pk']

    actions = [test_selected_bots,]

    def update_record(self, obj):
        return format_html('<a type="submit" class="default" href="/orchestrator/bot/{}/change/">EDIT</a>', obj.id)


class AppAdmin(SimpleHistoryAdmin):
    fieldsets = (
        ('General', {
            'fields': ('name', 'path',),
        }),
    )

    list_display = ('pk', 'name', 'path',
                    'update_record')
    list_editable = ('name', 'path',)
    list_display_links = ['pk']

    def update_record(self, obj):
        return format_html('<a type="submit" class="default" href="/orchestrator/app/{}/change/">EDIT</a>', obj.id)




class BotflowAdmin(SimpleHistoryAdmin):
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
                    'priority',
                    'update_record',)
    list_editable = ('name', 'path',
                     'queue_if_already_running',
                     'priority',)
    list_display_links = ['pk']

    actions = [test_selected_botflows,]

    def update_record(self, obj):
        return format_html('<a type="submit" class="default" href="/orchestrator/botflow/{}/change/">EDIT</a>', obj.id)


class FileTriggerAdmin(SimpleHistoryAdmin):
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
                    'folder_in', 'folder_out', 'filter',
                    'activated', 'status',
                    'update_record',)
    list_editable = ('bot', 'app', 'botflow',
                    'folder_in', 'folder_out', 'filter', 'activated',)
    list_display_links = ['pk']

    actions = [activate_selected_file_triggers, export_selected_file_triggers, test_selected_file_triggers,]

    def update_record(self, obj):
        return format_html('<a type="submit" class="default" href="/orchestrator/filetrigger/{}/change/">EDIT</a>', obj.id)


class ScheduleTriggerAdmin(SimpleHistoryAdmin):
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
                    'frequency', 'run_every', 'run_start',
                    'activated', 'status',
                    'update_record',)
    list_editable = ('bot', 'app', 'botflow',
                    'frequency', 'run_every', 'run_start', 'activated',)
    list_display_links = ['pk']
    exclude = ('past_settings',)
    readonly_fields = ('next_execution',)

    actions = [activate_selected_schedule_triggers, export_selected_schedule_triggers,]

    def update_record(self, obj):
        return format_html('<a type="submit" class="default" href="/orchestrator/scheduletrigger/{}/change/">EDIT</a>', obj.id)


class EmailImapTriggerForm(forms.ModelForm):
    class Meta:
        model = EmailImapTrigger
        fields = '__all__'
        widgets = {
            'password': forms.PasswordInput(),
        }


class EmailImapTriggerAdmin(SimpleHistoryAdmin):
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
                    'folder_in', 'folder_out',
                    'activated', 'status',
                    'update_record',)
    list_editable = ('bot', 'app', 'botflow',
                     'email',
                     'folder_in', 'folder_out', 'activated',)
    list_display_links = ['pk']

    activate_selected_email_imap_triggers.short_description = "Activate selected email IMAP triggers"
    export_selected_email_imap_triggers.short_description = "Export selected email IMAP triggers"
    test_selected_email_imap_triggers.short_description = "Test selected email IMAP triggers"

    actions = [activate_selected_email_imap_triggers, export_selected_email_imap_triggers, test_selected_email_imap_triggers,]

    def update_record(self, obj):
        return format_html('<a type="submit" class="default" href="/orchestrator/emailimaptrigger/{}/change/">EDIT</a>', obj.id)


class EmailOutlookTriggerAdmin(SimpleHistoryAdmin):
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
                    'folder_in', 'folder_out',
                    'activated', 'status',
                    'update_record',)
    list_editable = ('bot', 'app', 'botflow',
                     'email',
                     'folder_in', 'folder_out', 'activated',)
    list_display_links = ['pk']

    activate_selected_email_outlook_triggers.short_description = "Activate selected email Outlook triggers"
    export_selected_email_outlook_triggers.short_description = "Export selected email Outlook triggers"
    test_selected_email_outlook_triggers.short_description = "Test selected email Outlook triggers"

    actions = [activate_selected_email_outlook_triggers, export_selected_email_outlook_triggers,]

    def update_record(self, obj):
        return format_html('<a type="submit" class="default" href="/orchestrator/emailoutlooktrigger/{}/change/">EDIT</a>', obj.id)


class ApiTriggerAdmin(SimpleHistoryAdmin):
    fieldsets = (
        ('General', {
            'fields': ('bot', 'app', 'botflow',),
        }),
        ('Activate', {
            'fields': ('activated',),
        }),
    )

    list_display = ('pk', 'bot', 'app', 'botflow',
                    'activated', 'status',
                    'update_record',)
    list_editable = ('bot', 'app', 'botflow',
                     'activated',)
    list_display_links = ['pk']

    activate_selected_api_triggers.short_description = "Activate selected API triggers"
    export_selected_api_triggers.short_description = "Export selected API triggers"

    actions = [activate_selected_api_triggers, export_selected_api_triggers,]

    def update_record(self, obj):
        return format_html('<a type="submit" class="default" href="/orchestrator/apitrigger/{}/change/">EDIT</a>', obj.id)


class BotflowExecutionAdmin(SimpleHistoryAdmin):
    list_display = ('pk', 'time_queued',
                    'computer_name', 'user_name',
                    'app', 'botflow',
                    'trigger',
                    'priority',
                    'status',
                    'time_start', 'time_end',)
    list_display_links = ['pk']
    list_filter = ('computer_name', 'user_name', 'app', 'botflow', 'status',)
    readonly_fields = [field.name for field in BotflowExecution._meta.get_fields() if field.name != 'status']

    actions = [export_selected_botflow_executions,]

    def get_ordering(self, request):
        return ['-time_queued']

    def has_add_permission(self, request, obj=None):
        return False


class SmtpAccountForm(forms.ModelForm):
    class Meta:
        model = SmtpAccount
        fields = '__all__'
        widgets = {
            'password': forms.PasswordInput(),
        }


class SmtpAccountAdmin(SimpleHistoryAdmin):
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
                    'activated', 'status',
                    'update_record',)
    list_editable = ('server', 'port', 'tls',
                     'activated',)
    list_display_links = ['pk']

    test_selected_smtp_accounts.short_description = "Test selected SMTP accounts"

    actions = [test_selected_smtp_accounts, ]

    def get_ordering(self, request):
        return ['-activated']

    def update_record(self, obj):
        return format_html('<a type="submit" class="default" href="/orchestrator/smtpaccount/{}/change/">EDIT</a>', obj.id)


class PythonFunctionForm(forms.ModelForm):
    class Meta:
        model = PythonFunction
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 10, 'cols': 150}),
            'encrypted_value_1': forms.PasswordInput(),
            'encrypted_value_2': forms.PasswordInput(),
            'encrypted_value_3': forms.PasswordInput(),
            'encrypted_value_4': forms.PasswordInput(),
            'encrypted_value_5': forms.PasswordInput(),
            'code': forms.Textarea(attrs={'rows': 30, 'cols': 150}),
        }


class PythonFunctionAdmin(SimpleHistoryAdmin):
    form = PythonFunctionForm

    fieldsets = (
        ('General', {
            'fields': ('name', 'description',),
        }),
        ('Encrypted values', {
            'fields': ('encrypted_value_1', 'encrypted_value_2', 'encrypted_value_3', 'encrypted_value_4', 'encrypted_value_5',),
        }),
        ('Code', {
            'fields': ('code',),
        }),
        ('Activate', {
            'fields': ('activated',),
        }),
    )

    list_display = ('pk', 'name', 'description',
                    'activated', 'update_record',)
    list_editable = ('name',
                     'activated',)
    list_display_links = ['pk']

    def update_record(self, obj):
        return format_html('<a type="submit" class="default" href="/orchestrator/pythonfunction/{}/change/">EDIT</a>', obj.id)


class PythonFunctionExecutionAdmin(SimpleHistoryAdmin):
    list_display = ('pk', 'python_function',
                    'request_user', 'request_ip',
                    'time_start', 'time_end',)
    list_display_links = ['pk']
    list_filter = ('python_function', 'request_user', 'request_ip',)
    readonly_fields = [field.name for field in PythonFunctionExecution._meta.get_fields()]

    def get_ordering(self, request):
        return ['-time_start']

    def has_add_permission(self, request, obj=None):
        return False


admin.site.register(Bot, BotAdmin)
admin.site.register(App, AppAdmin)
admin.site.register(Botflow, BotflowAdmin)
admin.site.register(FileTrigger, FileTriggerAdmin)
admin.site.register(ScheduleTrigger, ScheduleTriggerAdmin)
admin.site.register(EmailImapTrigger, EmailImapTriggerAdmin)
admin.site.register(EmailOutlookTrigger, EmailOutlookTriggerAdmin)
admin.site.register(ApiTrigger, ApiTriggerAdmin)
admin.site.register(BotflowExecution, BotflowExecutionAdmin)
admin.site.register(SmtpAccount, SmtpAccountAdmin)
admin.site.register(PythonFunction, PythonFunctionAdmin)
admin.site.register(PythonFunctionExecution, PythonFunctionExecutionAdmin)
