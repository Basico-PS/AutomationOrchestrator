import os
import csv
import pytz
import datetime
import subprocess
from tzlocal import get_localzone
from django import forms
from django.db import models
from django.contrib import admin, messages
from django.http import HttpResponse
from django.utils.html import format_html
from simple_history.admin import SimpleHistoryAdmin
from .models import Bot, App, Botflow, FileTrigger, PythonFunction, ScheduleTrigger, EmailImapTrigger, EmailOutlookTrigger, ApiTrigger, BotflowExecution, SmtpAccount, PythonFunction, PythonFunctionExecution
from .monitoring import add_botflow_execution_object, determine_execution_bot
from automation_orchestrator.settings import VERSION


admin.site.site_header = 'Automation Orchestrator'
admin.site.site_title = f'Automation Orchestrator {VERSION}'
admin.site.index_title = 'Orchestrate Amazing Automation'


def queue_item(item, trigger):
    add_botflow_execution_object(
        bot_pk=determine_execution_bot(item).pk,
        app_pk=item.app.pk,
        botflow_pk=item.botflow.pk,
        trigger=trigger,
        custom_status=item.botflow_execution_custom_status
    )


def run_selected_triggers(modeladmin, request, queryset):
    for item in queryset:
        queue_item(item, "No Trigger: Activated Manually")


def run_selected_file_triggers(modeladmin, request, queryset):
    run_selected_triggers(modeladmin, request, queryset)


def run_selected_schedule_triggers(modeladmin, request, queryset):
    run_selected_triggers(modeladmin, request, queryset)


def run_selected_email_imap_triggers(modeladmin, request, queryset):
    run_selected_triggers(modeladmin, request, queryset)


def run_selected_email_outlook_triggers(modeladmin, request, queryset):
    run_selected_triggers(modeladmin, request, queryset)


def run_selected_api_triggers(modeladmin, request, queryset):
    run_selected_triggers(modeladmin, request, queryset)


def cancel_selected_botflow_executions(modeladmin, request, queryset):
    time_zone = str(get_localzone())

    time_now = datetime.datetime.now(pytz.timezone(time_zone)).strftime(f"%Y-%m-%dT%H:%M:%S+0{str(int(datetime.datetime.now(pytz.timezone(time_zone)).utcoffset().seconds / 60 / 60))}00")

    for item in queryset:
        if item.time_start == None or item.time_end == None or item.status == "Running":
            item.status = "Cancelled"
            if item.time_start == None:
                item.time_start = time_now
            if item.time_end == None:
                item.time_end = time_now
            item.save()


def copy_selected_file_triggers(modeladmin, request, queryset):
    for item in queryset:
        bots = item.bots.all()

        item_new = item
        item_new.pk = None
        item_new.date_created = None
        item_new.date_updated = None
        item_new.activated = False

        item_new.save()

        item_new.bots.set([x.id for x in bots])
        item_new.save()


def copy_selected_schedule_triggers(modeladmin, request, queryset):
    for item in queryset:
        bots = item.bots.all()

        item_new = item
        item_new.pk = None
        item_new.date_created = None
        item_new.date_updated = None
        item_new.activated = False

        item_new.next_execution = None

        item_new.save()

        item_new.bots.set([x.id for x in bots])
        item_new.save()


def copy_selected_email_imap_triggers(modeladmin, request, queryset):
    for item in queryset:
        bots = item.bots.all()

        item_new = item
        item_new.pk = None
        item_new.date_created = None
        item_new.date_updated = None
        item_new.activated = False

        item_new.save()

        item_new.bots.set([x.id for x in bots])
        item_new.save()


def copy_selected_email_outlook_triggers(modeladmin, request, queryset):
    for item in queryset:
        bots = item.bots.all()

        item_new = item
        item_new.pk = None
        item_new.date_created = None
        item_new.date_updated = None
        item_new.activated = False

        item_new.save()

        item_new.bots.set([x.id for x in bots])
        item_new.save()


def copy_selected_api_triggers(modeladmin, request, queryset):
    for item in queryset:
        bots = item.bots.all()

        item_new = item
        item_new.pk = None
        item_new.date_created = None
        item_new.date_updated = None
        item_new.activated = False

        item_new.save()

        item_new.bots.set([x.id for x in bots])
        item_new.save()


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


def refresh_selected_bots(modeladmin, request, queryset):
    for item in queryset:
        try:
            computer_name = item.computer_name
            user_name = item.user_name

            if str(computer_name).lower() == os.environ['COMPUTERNAME'].lower():
                sessions = subprocess.run(["query", "session"], stdout=subprocess.PIPE, text=True).stdout.split("\n")

                if not "SESSIONNAME" in str(sessions):
                    if item.status != "Unknown":
                        item.status = "Unknown"
                        item.save_without_historical_record()

                active = False
                for session in sessions:
                    if f" {user_name.lower()} " in session.lower() and " Active " in session:
                        active = True
                        break

                if active:
                    if item.status != "Active" and item.status != "Running":
                        item.status = "Active"
                        item.save_without_historical_record()

                else:
                    if item.status != "ERROR":
                        item.status = "ERROR"
                        item.save_without_historical_record()

            else:
                if item.status != "Running":
                    if (pytz.utc.localize(datetime.datetime.utcnow()) - item.date_updated).seconds > 300:
                        if item.status != "Unknown":
                            item.status = "Unknown"
                            item.save_without_historical_record()

        except:
            if item.status != "Unknown":
                item.status = "Unknown"
                item.save_without_historical_record()


def test_selected_apps(modeladmin, request, queryset):
    for item in queryset:
        if os.path.isfile(item.path):
            messages.success(request, f"Successfully located the '{item.name}' App file: {item.path}")
        else:
            messages.error(request, f"Failed to locate the '{item.name}' App file: {item.path}")


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

            if item.status != "Active":
                item.status = "Active"
                item.save_without_historical_record()

        except:
            messages.error(request, f"Failed to retrieve files from the incoming folder: {item.folder_in}")

            if item.status != "ERROR":
                item.status = "ERROR"
                item.save_without_historical_record()


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

                if item.status != "ERROR":
                    item.status = "ERROR"
                    item.save_without_historical_record()

            else:
                messages.success(request, f"Successfully connected to email {item.email}! Number of messages detected in the 'INBOX/{item.folder_in}' folder: {emails_folder_in}")

                if item.status != "Active":
                    item.status = "Active"
                    item.save_without_historical_record()

        except:
            messages.error(request, f"Failed to connect to email {item.email}!")

            if item.status != "ERROR":
                item.status = "ERROR"
                item.save_without_historical_record()

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

            if item.status != "Active":
                item.status = "Active"
                item.save_without_historical_record()

        except:
            if item.status != "ERROR":
                item.status = "ERROR"
                item.save_without_historical_record()

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
            msg['Subject'] = "[TEST] Automation Orchestrator"
            msg['From'] = item.email
            msg['To'] = item.email

            with SMTP(item.server, item.port) as server:
                if item.tls:
                    server.starttls()
                if item.password != "":
                    server.login(item.email, item.password)
                server.send_message(msg)

            messages.success(request, f"Successfully sent an email with {item.email}!")

            if item.status != "Active":
                item.status = "Active"
                item.save_without_historical_record()

        except:
            if item.tls:
                try:
                    msg = EmailMessage()
                    msg['Subject'] = "[TEST] Automation Orchestrator"
                    msg['From'] = item.email
                    msg['To'] = item.email

                    with SMTP_SSL(item.server, item.port) as server:
                        if item.password != "":
                            server.login(item.email, item.password)
                        server.send_message(msg)

                    messages.success(request, f"Successfully sent an email with {item.email}!")
                    continue

                except:
                    pass

            messages.error(request, f"Failed to send email with {item.email}!")

            if item.status != "ERROR":
                item.status = "ERROR"
                item.save_without_historical_record()


class BotAdmin(SimpleHistoryAdmin):
    def update_record(self, obj):
        return format_html('<a type="submit" class="default" href="/orchestrator/bot/{}/change/">EDIT</a>', obj.id)

    def pk_formatted(self, obj):
        return obj.pk

    fieldsets = (
        ('General', {
            'fields': ('name', 'computer_name', 'user_name',),
        }),
        ('Time Filter', {
            'classes': ('collapse',),
            'fields': ('run_after', 'run_until', 'run_on_week_days', 'run_on_weekend_days'),
        }),
        ('Nintex RPA', {
            'classes': ('collapse',),
            'fields': ('nintex_rpa_license_path', 'nintex_rpa_available_foxtrot_licenses', 'nintex_rpa_available_foxbot_licenses',),
        }),
    )

    list_display = ('pk_formatted', 'name', 'computer_name', 'user_name', 'status',
                    'update_record',)
    list_editable = ('name', 'computer_name', 'user_name',)
    list_display_links = ['pk_formatted']

    pk_formatted.admin_order_field = 'pk'
    pk_formatted.short_description = 'ID'

    actions = [refresh_selected_bots,]


class AppAdmin(SimpleHistoryAdmin):
    def update_record(self, obj):
        return format_html('<a type="submit" class="default" href="/orchestrator/app/{}/change/">EDIT</a>', obj.id)

    def pk_formatted(self, obj):
        return obj.pk

    fieldsets = (
        ('General', {
            'fields': ('name', 'path',),
        }),
    )

    list_display = ('pk_formatted', 'name', 'path',
                    'update_record')
    list_editable = ('name', 'path',)
    list_display_links = ['pk_formatted']

    pk_formatted.admin_order_field = 'pk'
    pk_formatted.short_description = 'ID'

    actions = [test_selected_apps,]


class BotflowAdmin(SimpleHistoryAdmin):
    def update_record(self, obj):
        return format_html('<a type="submit" class="default" href="/orchestrator/botflow/{}/change/">EDIT</a>', obj.id)

    def pk_formatted(self, obj):
        return obj.pk
    pk_formatted.admin_order_field = 'pk'
    pk_formatted.short_description = 'ID'

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

    list_display = ('pk_formatted', 'name', 'path',
                    'queue_if_already_running',
                    'priority',
                    'update_record',)
    list_editable = ('name', 'path',
                     'queue_if_already_running',
                     'priority',)
    list_display_links = ['pk_formatted']

    actions = [test_selected_botflows,]


class FileTriggerAdmin(SimpleHistoryAdmin):
    def update_record(self, obj):
        return format_html('<a type="submit" class="default" href="/orchestrator/filetrigger/{}/change/">EDIT</a>', obj.id)

    def pk_formatted(self, obj):
        return obj.pk

    fieldsets = (
        ('General', {
            'fields': ('bots', 'app', 'botflow',),
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
        ('Botflow Execution Note', {
            'classes': ('collapse',),
            'fields': ('botflow_execution_custom_status',),
        })
    )

    list_display = ('pk_formatted', 'assigned_bots', 'app', 'botflow',
                    'folder_in', 'folder_out', 'filter',
                    'activated', 'status',
                    'update_record',)
    list_editable = ('app', 'botflow',
                    'folder_in', 'folder_out', 'filter', 'activated',)
    list_display_links = ['pk_formatted']

    pk_formatted.short_description = 'ID'
    run_selected_file_triggers.short_description = "Run selected file triggers"

    pk_formatted.admin_order_field = 'pk'

    actions = [copy_selected_file_triggers, export_selected_file_triggers, test_selected_file_triggers, run_selected_file_triggers]


class ScheduleTriggerAdmin(SimpleHistoryAdmin):
    def update_record(self, obj):
        return format_html('<a type="submit" class="default" href="/orchestrator/scheduletrigger/{}/change/">EDIT</a>', obj.id)

    def pk_formatted(self, obj):
        return obj.pk

    def next_execution_formatted(self, obj):
        time = obj.next_execution
        if time != None and time != "":
            time = time.astimezone().strftime("%Y-%m-%d %H:%M")
        return time

    fieldsets = (
        ('General', {
            'fields': ('bots', 'app', 'botflow'),
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
        ('Botflow Execution Note', {
            'classes': ('collapse',),
            'fields': ('botflow_execution_custom_status',),
        }),
        ('Next Execution', {
            'classes': ('collapse',),
            'fields': ('next_execution',),
        }),
    )

    list_display = ('pk_formatted', 'assigned_bots', 'app', 'botflow',
                    'frequency', 'run_every', 'run_start',
                    'activated', 'status',
                    'next_execution_formatted',
                    'update_record',)
    list_editable = ('app', 'botflow',
                    'frequency', 'run_every', 'run_start', 'activated',)
    list_display_links = ['pk_formatted']
    exclude = ('past_settings',)
    readonly_fields = ('next_execution',)

    pk_formatted.short_description = 'ID'
    run_selected_schedule_triggers.short_description = "Run selected schedule triggers"
    next_execution_formatted.short_description = 'Next Execution'

    pk_formatted.admin_order_field = 'pk'
    next_execution_formatted.admin_order_field = 'next_execution'

    actions = [copy_selected_schedule_triggers, export_selected_schedule_triggers, run_selected_schedule_triggers]


class EmailImapTriggerForm(forms.ModelForm):
    class Meta:
        model = EmailImapTrigger
        fields = '__all__'
        widgets = {
            'password': forms.PasswordInput(),
        }


class EmailImapTriggerAdmin(SimpleHistoryAdmin):
    def update_record(self, obj):
        return format_html('<a type="submit" class="default" href="/orchestrator/emailimaptrigger/{}/change/">EDIT</a>', obj.id)

    def pk_formatted(self, obj):
        return obj.pk

    fieldsets = (
        ('General', {
            'fields': ('bots', 'app', 'botflow',),
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
        ('Botflow Execution Note', {
            'classes': ('collapse',),
            'fields': ('botflow_execution_custom_status',),
        })
    )

    list_display = ('pk_formatted', 'assigned_bots', 'app', 'botflow',
                    'email',
                    'folder_in', 'folder_out',
                    'activated', 'status',
                    'update_record',)
    list_editable = ('app', 'botflow',
                     'email',
                     'folder_in', 'folder_out', 'activated',)
    list_display_links = ['pk_formatted']

    pk_formatted.short_description = 'ID'
    copy_selected_email_imap_triggers.short_description = "Copy selected email IMAP triggers"
    export_selected_email_imap_triggers.short_description = "Export selected email IMAP triggers"
    run_selected_email_imap_triggers.short_description = "Activate selected email IMAP triggers"
    test_selected_email_imap_triggers.short_description = "Test selected email IMAP triggers"

    pk_formatted.admin_order_field = 'pk'

    actions = [copy_selected_email_imap_triggers, export_selected_email_imap_triggers, test_selected_email_imap_triggers, run_selected_email_imap_triggers]

    form = EmailImapTriggerForm


class EmailOutlookTriggerAdmin(SimpleHistoryAdmin):
    def update_record(self, obj):
        return format_html('<a type="submit" class="default" href="/orchestrator/emailoutlooktrigger/{}/change/">EDIT</a>', obj.id)

    def pk_formatted(self, obj):
        return obj.pk

    fieldsets = (
        ('General', {
            'fields': ('bots', 'app', 'botflow',),
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
        ('Botflow Execution Note', {
            'classes': ('collapse',),
            'fields': ('botflow_execution_custom_status',),
        })
    )

    list_display = ('pk_formatted', 'assigned_bots', 'app', 'botflow',
                    'email',
                    'folder_in', 'folder_out',
                    'activated', 'status',
                    'update_record',)
    list_editable = ('app', 'botflow',
                     'email',
                     'folder_in', 'folder_out', 'activated',)
    list_display_links = ['pk_formatted']

    pk_formatted.short_description = 'ID'
    copy_selected_email_outlook_triggers.short_description = "Copy selected email Outlook triggers"
    export_selected_email_outlook_triggers.short_description = "Export selected email Outlook triggers"
    run_selected_email_outlook_triggers.short_description = "Run selected email Outlook triggers"
    test_selected_email_outlook_triggers.short_description = "Test selected email Outlook triggers"

    pk_formatted.admin_order_field = 'pk'

    actions = [copy_selected_email_outlook_triggers, export_selected_email_outlook_triggers, run_selected_email_outlook_triggers]


class ApiTriggerAdmin(SimpleHistoryAdmin):
    def update_record(self, obj):
        return format_html('<a type="submit" class="default" href="/orchestrator/apitrigger/{}/change/">EDIT</a>', obj.id)

    def pk_formatted(self, obj):
        return obj.pk

    fieldsets = (
        ('General', {
            'fields': ('bots', 'app', 'botflow',),
        }),
        ('Activate', {
            'fields': ('activated',),
        }),
        ('Botflow Execution Note', {
            'classes': ('collapse',),
            'fields': ('botflow_execution_custom_status',),
        })
    )

    list_display = ('pk_formatted', 'assigned_bots', 'app', 'botflow',
                    'activated', 'status',
                    'update_record',)
    list_editable = ('app', 'botflow',
                     'activated',)
    list_display_links = ['pk_formatted']

    pk_formatted.short_description = 'ID'
    copy_selected_api_triggers.short_description = "Copy selected API triggers"
    export_selected_api_triggers.short_description = "Export selected API triggers"
    run_selected_api_triggers.short_description = "Run selected API triggers"

    pk_formatted.admin_order_field = 'pk'

    actions = [copy_selected_api_triggers, export_selected_api_triggers, run_selected_api_triggers]


class BotflowExecutionAdmin(SimpleHistoryAdmin):
    def get_ordering(self, request):
        return ['-time_queued']

    def has_add_permission(self, request, obj=None):
        return False

    def pk_formatted(self, obj):
        return obj.pk

    def time_queued_formatted(self, obj):
        time = obj.time_queued
        if time != None:
            time = time.astimezone().strftime("%Y-%m-%d %H:%M:%S")
        return time

    def time_start_formatted(self, obj):
        time = obj.time_start
        if time != None:
            time = time.astimezone().strftime("%Y-%m-%d %H:%M:%S")
        return time

    def time_end_formatted(self, obj):
        time = obj.time_end
        if time != None:
            time = time.astimezone().strftime("%Y-%m-%d %H:%M:%S")
        return time

    def time_updated_formatted(self, obj):
        time = obj.time_updated
        if time != None:
            time = time.astimezone().strftime("%Y-%m-%d %H:%M:%S")
        return time

    def app_formatted(self, obj):
        return os.path.basename(obj.app)

    def bot_formatted(self, obj):
        return f"{obj.computer_name} - {obj.user_name}"

    def botflow_formatted(self, obj):
        return os.path.basename(obj.botflow)

    def trigger_formatted(self, obj):
        trigger = obj.trigger
        trigger_file = "File Trigger: "
        if trigger.startswith(trigger_file):
            if not "Activated Manually" in trigger:
                return trigger_file + os.path.basename(trigger[len(trigger_file):])
        return trigger

    def custom_progress_formatted(self, obj):
        progress = str(obj.custom_progress)
        progress = progress.replace('.00', '') + "%"
        return progress

    def custom_status_formatted(self, obj):
        note = str(obj.custom_status)
        return note

    list_display = ('pk_formatted',
                    'time_queued_formatted',
                    'bot_formatted',
                    'app_formatted',
                    'botflow_formatted',
                    'trigger_formatted',
                    'priority',
                    'status',
                    'custom_progress_formatted',
                    'time_start_formatted',
                    'time_end_formatted',
                    'time_updated_formatted',
                    'custom_status_formatted',)
    list_display_links = ['pk_formatted']
    list_filter = ('computer_name', 'user_name', 'app', 'botflow', 'status',)
    readonly_fields = [field.name for field in BotflowExecution._meta.get_fields() if field.name != 'custom_status']

    time_queued_formatted.short_description = 'Time Queued'
    time_start_formatted.short_description = 'Time Start'
    time_end_formatted.short_description = 'Time End'
    time_updated_formatted.short_description = 'Time Updated'
    app_formatted.short_description = 'App'
    bot_formatted.short_description = 'Bot'
    botflow_formatted.short_description = 'Botflow'
    trigger_formatted.short_description = 'Trigger'
    custom_progress_formatted.short_description = 'Progress'
    custom_status_formatted.short_description = 'Note'
    pk_formatted.short_description = 'ID'

    time_queued_formatted.admin_order_field = 'time_queued'
    time_start_formatted.admin_order_field = 'time_start'
    time_end_formatted.admin_order_field = 'time_end'
    time_updated_formatted.admin_order_field = 'time_updated'
    app_formatted.admin_order_field = 'app'
    bot_formatted.admin_order_field = 'computer_name'
    botflow_formatted.admin_order_field = 'botflow'
    trigger_formatted.admin_order_field = 'trigger'
    custom_progress_formatted.admin_order_field = 'custom_progress'
    custom_status_formatted.admin_order_field = 'custom_status'
    pk_formatted.admin_order_field = 'pk'

    actions = [cancel_selected_botflow_executions, export_selected_botflow_executions,]

    list_per_page = 20


class SmtpAccountForm(forms.ModelForm):
    class Meta:
        model = SmtpAccount
        fields = '__all__'
        widgets = {
            'password': forms.PasswordInput(),
        }


class SmtpAccountAdmin(SimpleHistoryAdmin):
    def get_ordering(self, request):
        return ['-activated']

    def update_record(self, obj):
        return format_html('<a type="submit" class="default" href="/orchestrator/smtpaccount/{}/change/">EDIT</a>', obj.id)

    def pk_formatted(self, obj):
        return obj.pk

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

    list_display = ('pk_formatted', 'email',
                    'server', 'port', 'tls',
                    'activated', 'status',
                    'update_record',)
    list_editable = ('server', 'port', 'tls',
                     'activated',)
    list_display_links = ['pk_formatted']

    pk_formatted.short_description = 'ID'
    test_selected_smtp_accounts.short_description = "Test selected SMTP accounts"

    pk_formatted.admin_order_field = 'pk'

    actions = [test_selected_smtp_accounts, ]

    form = SmtpAccountForm


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
    def update_record(self, obj):
        return format_html('<a type="submit" class="default" href="/orchestrator/pythonfunction/{}/change/">EDIT</a>', obj.id)

    def pk_formatted(self, obj):
        return obj.pk

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

    list_display = ('pk_formatted', 'name', 'description',
                    'activated', 'update_record',)
    list_editable = ('name',
                     'activated',)
    list_display_links = ['pk_formatted']

    pk_formatted.admin_order_field = 'pk'
    pk_formatted.short_description = 'ID'

    form = PythonFunctionForm


class PythonFunctionExecutionAdmin(SimpleHistoryAdmin):
    def get_ordering(self, request):
        return ['-time_start']

    def has_add_permission(self, request, obj=None):
        return False

    def pk_formatted(self, obj):
        return obj.pk

    list_display = ('pk_formatted', 'python_function',
                    'request_user', 'request_ip',
                    'time_start', 'time_end',)
    list_display_links = ['pk_formatted']
    list_filter = ('python_function', 'request_user', 'request_ip',)

    readonly_fields = [field.name for field in PythonFunctionExecution._meta.get_fields()]

    pk_formatted.admin_order_field = 'pk'
    pk_formatted.short_description = 'ID'

    list_per_page = 20


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
