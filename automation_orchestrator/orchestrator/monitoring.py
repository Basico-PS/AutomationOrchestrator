import re
import os
import glob
import pytz
import email
import shutil
import datetime
import calendar
import traceback
import subprocess
import time as t
import win32com.client as win32
from imaplib import IMAP4, IMAP4_SSL
from .models import Bot, App, Botflow, FileTrigger, ScheduleTrigger, EmailImapTrigger, EmailOutlookTrigger, BotflowExecution
from django.db.models import Q
from dateutil.relativedelta import relativedelta
from pythoncom import CoInitialize, CoUninitialize


trigger_sleep = 10
email_imap_sleep = 15
email_outlook_sleep = 15
queue_sleep = 10


class EmailOutlookDispatchException(Exception):
    # Exception to be used when the connection to the dispatched Email Outlook object is lost.
    pass


def add_botflow_execution_object(bot_pk, app_pk, botflow_pk, trigger):
    bot_object = Bot.objects.get(pk=bot_pk)
    app_object = App.objects.get(pk=app_pk)
    botflow_object = Botflow.objects.get(pk=botflow_pk)

    botflow_execution = BotflowExecution(app=app_object.path,
                                         botflow=botflow_object.path,
                                         trigger=trigger[:250],
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
                                         error_notification = botflow_object.error_notification,
                                         nintex_rpa_license_path = bot_object.nintex_rpa_license_path,
                                         nintex_rpa_available_foxtrot_licenses = bot_object.nintex_rpa_available_foxtrot_licenses,
                                         nintex_rpa_available_foxbot_licenses = bot_object.nintex_rpa_available_foxbot_licenses)
    botflow_execution.save()

    bot_object, app_object, botflow_object = None, None, None
    del bot_object, app_object, botflow_object


def calculate_next_botflow_execution(run_start, frequency, run_every, run_after, run_until, run_on_week_days, run_on_weekend_days):
    for i in range(5256000):
        if frequency == "MIN":
            time = run_start + datetime.timedelta(minutes=int(run_every) * i)

        elif frequency == "HOU":
            time = run_start + datetime.timedelta(hours=int(run_every) * i)

        elif frequency == "DAY":
            time = run_start + datetime.timedelta(days=int(run_every) * i)

        elif frequency == "WEE":
            time = run_start + datetime.timedelta(weeks=int(run_every) * i)

        elif frequency == "MON":
            time = run_start + relativedelta(months=int(run_every) * i)

        elif frequency == "FWK":
            time = run_start + relativedelta(months=int(run_every) * i)
            time = time.replace(day=1)

            time_temp = time

            for ii in range(7):
                if time.weekday() >= 5:
                    time = time_temp + datetime.timedelta(days=ii)
                else:
                    break

        elif frequency == "FWD":
            time = run_start + relativedelta(months=int(run_every) * i)
            time = time.replace(day=1)

            time_temp = time

            for ii in range(7):
                if time.weekday() <= 4:
                    time = time_temp + datetime.timedelta(days=ii)
                else:
                    break

        elif frequency == "LWK":
            time = run_start + relativedelta(months=int(run_every) * i)
            time = time.replace(day=calendar.monthrange(time.year, time.month)[1])

            time_temp = time

            for ii in range(7):
                if time.weekday() >= 5:
                    time = time_temp - datetime.timedelta(days=ii)
                else:
                    break

        elif frequency == "LWD":
            time = run_start + relativedelta(months=int(run_every) * i)
            time = time.replace(day=calendar.monthrange(time.year, time.month)[1])

            time_temp = time

            for ii in range(7):
                if time.weekday() <= 4:
                    time = time_temp - datetime.timedelta(days=ii)
                else:
                    break

        else:
            continue

        if time >= datetime.datetime.now(pytz.timezone('UTC')):
            time_timedelta = datetime.timedelta(hours=time.hour, minutes=time.minute)

            if run_after < run_until:
                if time_timedelta < run_after:
                    continue
                if time_timedelta >= run_until:
                    continue
            else:
                if time_timedelta >= run_after or time_timedelta < run_until:
                    pass
                else:
                    continue

            if not run_on_week_days:
                if 0 <= time.weekday() <= 4:
                    continue
            if not run_on_weekend_days:
                if 5 <= time.weekday() <= 6:
                    continue

            return time.strftime("%Y-%m-%d %H:%M")

    return ""


def file_trigger_monitor():
    while True:
        range(10000)
        t.sleep(trigger_sleep)

        if os.path.exists("logs\\error_log.txt"):
            break

        try:
            file_trigger_monitor_evaluate()

        except:
            with open("logs\\error_log.txt", 'a') as f:
                try:
                    f.write(traceback.format_exc())
                    print(traceback.format_exc())
                except:
                    pass
            break


def file_trigger_monitor_evaluate():
    items = FileTrigger.objects.filter(activated=True)

    for item in items:
        if not os.path.isdir(item.folder_in) or not os.path.isdir(item.folder_out):
            item.status = "ERROR"
            item.save()
            continue

        if not item.run_on_week_days:
            if 0 <= datetime.datetime.now(pytz.timezone('Europe/Copenhagen')).weekday() <= 4:
                continue
        if not item.run_on_weekend_days:
            if 5 <= datetime.datetime.now(pytz.timezone('Europe/Copenhagen')).weekday() <= 6:
                continue

        if item.run_after is not None:
            run_after = datetime.timedelta(hours=item.run_after.hour, minutes=item.run_after.minute) - datetime.datetime.now(pytz.timezone('Europe/Copenhagen')).utcoffset()
        else:
            run_after = datetime.timedelta(hours=0, minutes=0)

        if item.run_until is not None:
            run_until = datetime.timedelta(hours=item.run_until.hour, minutes=item.run_until.minute) - datetime.datetime.now(pytz.timezone('Europe/Copenhagen')).utcoffset()
        else:
            run_until = datetime.timedelta(hours=0, minutes=0)

        time_timedelta = datetime.timedelta(hours=datetime.datetime.now(pytz.timezone('UTC')).hour, minutes=datetime.datetime.now(pytz.timezone('UTC')).minute)

        if run_after < run_until:
            if time_timedelta < run_after:
                continue
            if time_timedelta >= run_until:
                continue
        else:
            if time_timedelta >= run_after or time_timedelta < run_until:
                pass
            else:
                continue

        files = []
        for filter in item.filter.split(","):
            files = files + [file for file in glob.glob(item.folder_in + "\\" + filter.strip()) if os.path.isfile(file)]

        files = list(dict.fromkeys(files))
        files.sort(key=os.path.getctime)

        for file in files:
            file_path = os.path.dirname(file)
            file_name = os.path.basename(file)

            file_name, file_extension = os.path.splitext(file_name)

            try:
                path_destination = os.path.join(item.folder_out, file_name + '' + file_extension)

                shutil.move(file, item.folder_out)

            except shutil.Error:
                index = 0

                while True:
                    index += 1

                    path_destination = os.path.join(item.folder_out, file_name + f'_{index}' + file_extension)

                    if not os.path.isfile(path_destination):
                        shutil.move(file, path_destination)
                    else:
                        continue
                    break

            if not Botflow.objects.get(pk=item.botflow.pk).queue_if_already_running:
                if BotflowExecution.objects.filter(Q(status="Pending") | Q(status="Running"), botflow=Botflow.objects.get(pk=item.botflow.pk).path).exists():
                    add_botflow_execution = False
                else:
                    add_botflow_execution = True
            else:
                add_botflow_execution = True

            if add_botflow_execution:
                add_botflow_execution_object(bot_pk=item.bot.pk, app_pk=item.app.pk, botflow_pk=item.botflow.pk, trigger=f"File Trigger: {path_destination}")

        if item.status != "Working":
            item.status = "Working"
            item.save()

    items = None
    del items


def schedule_trigger_monitor():
    while True:
        range(10000)
        t.sleep(trigger_sleep)

        if os.path.exists("logs\\error_log.txt"):
            break

        try:
            schedule_trigger_monitor_evaluate()

        except:
            with open("logs\\error_log.txt", 'a') as f:
                try:
                    f.write(traceback.format_exc())
                    print(traceback.format_exc())
                except:
                    pass
            break


def schedule_trigger_monitor_evaluate():
    items = ScheduleTrigger.objects.filter(activated=True)

    for item in items:
        now = datetime.datetime.now(pytz.timezone('UTC'))
        now = datetime.datetime.strptime(f"{now.year}-{now.month}-{now.day} {now.hour}:{now.minute}", "%Y-%m-%d %H:%M")

        if item.run_after is not None:
            run_after = datetime.timedelta(hours=item.run_after.hour, minutes=item.run_after.minute) - datetime.datetime.now(pytz.timezone('Europe/Copenhagen')).utcoffset()
        else:
            run_after = datetime.timedelta(hours=0, minutes=0)

        if item.run_until is not None:
            run_until = datetime.timedelta(hours=item.run_until.hour, minutes=item.run_until.minute) - datetime.datetime.now(pytz.timezone('Europe/Copenhagen')).utcoffset()
        else:
            run_until = datetime.timedelta(hours=0, minutes=0)

        settings = f"{item.frequency},{item.run_every},{item.run_start},{item.run_after},{item.run_until},{item.run_on_week_days},{item.run_on_weekend_days}"

        if item.next_execution == "":
            run_start = item.run_start.replace(tzinfo=pytz.timezone('UTC'))
            item.next_execution = calculate_next_botflow_execution(run_start, item.frequency, item.run_every, run_after, run_until, item.run_on_week_days, item.run_on_weekend_days)
            item.past_settings = settings
            item.save()

        elif item.past_settings != settings:
            run_start = item.run_start.replace(tzinfo=pytz.timezone('UTC'))
            item.next_execution = calculate_next_botflow_execution(run_start, item.frequency, item.run_every, run_after, run_until, item.run_on_week_days, item.run_on_weekend_days)
            item.past_settings = settings
            item.save()

        if datetime.datetime.strptime(item.next_execution, "%Y-%m-%d %H:%M") == now:
            if not Botflow.objects.get(pk=item.botflow.pk).queue_if_already_running:
                if BotflowExecution.objects.filter(Q(status="Pending") | Q(status="Running"), botflow=Botflow.objects.get(pk=item.botflow.pk).path).exists():
                    add_botflow_execution = False
                else:
                    add_botflow_execution = True
            else:
                add_botflow_execution = True

            if add_botflow_execution:
                time_trigger = datetime.datetime.now(pytz.timezone('Europe/Copenhagen')).strftime("%Y-%m-%d %H:%M")
                add_botflow_execution_object(bot_pk=item.bot.pk, app_pk=item.app.pk, botflow_pk=item.botflow.pk, trigger=f"Schedule Trigger: {time_trigger}")

            run_start = now.replace(tzinfo=pytz.timezone('UTC'))
            item.next_execution = calculate_next_botflow_execution(run_start, item.frequency, item.run_every, run_after, run_until, item.run_on_week_days, item.run_on_weekend_days)
            item.past_settings = settings
            item.save()

        elif datetime.datetime.strptime(item.next_execution, "%Y-%m-%d %H:%M") < now:
            run_start = datetime.datetime.strptime(item.next_execution, "%Y-%m-%d %H:%M").replace(tzinfo=pytz.timezone('UTC'))
            item.next_execution = calculate_next_botflow_execution(run_start, item.frequency, item.run_every, run_after, run_until, item.run_on_week_days, item.run_on_weekend_days)
            item.past_settings = settings
            item.save()

        if item.status != "Working":
            item.status = "Working"
            item.save()

    items = None
    del items


def email_imap_trigger_monitor():
    while True:
        range(10000)
        t.sleep(email_imap_sleep)

        if os.path.exists("logs\\error_log.txt"):
            break

        try:
            email_imap_trigger_monitor_evaluate()

        except:
            with open("logs\\error_log.txt", 'a') as f:
                try:
                    f.write(traceback.format_exc())
                    print(traceback.format_exc())
                except:
                    pass
            break


def email_imap_trigger_monitor_evaluate():
    pattern_uid = re.compile(r'\d+ \(UID (?P<uid>\d+)\)')

    items = EmailImapTrigger.objects.filter(activated=True)

    for item in items:
        if not item.run_on_week_days:
            if 0 <= datetime.datetime.now(pytz.timezone('Europe/Copenhagen')).weekday() <= 4:
                continue
        if not item.run_on_weekend_days:
            if 5 <= datetime.datetime.now(pytz.timezone('Europe/Copenhagen')).weekday() <= 6:
                continue

        if item.run_after is not None:
            run_after = datetime.timedelta(hours=item.run_after.hour, minutes=item.run_after.minute) - datetime.datetime.now(pytz.timezone('Europe/Copenhagen')).utcoffset()
        else:
            run_after = datetime.timedelta(hours=0, minutes=0)

        if item.run_until is not None:
            run_until = datetime.timedelta(hours=item.run_until.hour, minutes=item.run_until.minute) - datetime.datetime.now(pytz.timezone('Europe/Copenhagen')).utcoffset()
        else:
            run_until = datetime.timedelta(hours=0, minutes=0)

        time_timedelta = datetime.timedelta(hours=datetime.datetime.now(pytz.timezone('UTC')).hour, minutes=datetime.datetime.now(pytz.timezone('UTC')).minute)

        if run_after < run_until:
            if time_timedelta < run_after:
                continue
            if time_timedelta >= run_until:
                continue
        else:
            if time_timedelta >= run_after or time_timedelta < run_until:
                pass
            else:
                continue

        try:
            if item.tls:
                server = IMAP4_SSL(item.server, item.port)
            else:
                server = IMAP4(item.server, item.port)

            server.login(item.email, item.password)

            server.select('INBOX')
            server.select('INBOX/' + item.folder_in)
            server.select('INBOX/' + item.folder_out)

            server.select('INBOX/' + item.folder_in)
            _, emails = server.search(None, 'All')
            emails = emails[0].split()
            email_id = emails[-1]

            email_data = server.fetch(email_id, '(RFC822)')

            email_subject = ""
            for email_data_part in email_data[1]:
                if isinstance(email_data_part, tuple):
                    email_subject = email.message_from_string(email_data_part[1].decode())['subject']
                    break

            email_uid = server.fetch(email_id, '(UID)')
            email_uid = str(email_uid[-1][0], 'utf-8', 'ignore')
            email_uid = pattern_uid.match(email_uid).group('uid')

            email_copy_response = server.uid('COPY', email_uid, 'INBOX/' + item.folder_out)

            if email_copy_response[0] == 'OK':
                server.uid('STORE', email_uid , '+FLAGS', r'(\Deleted)')
                server.expunge()

            if not Botflow.objects.get(pk=item.botflow.pk).queue_if_already_running:
                if BotflowExecution.objects.filter(Q(status="Pending") | Q(status="Running"), botflow=Botflow.objects.get(pk=item.botflow.pk).path).exists():
                    add_botflow_execution = False
                else:
                    add_botflow_execution = True
            else:
                add_botflow_execution = True

            if add_botflow_execution:
                add_botflow_execution_object(bot_pk=item.bot.pk, app_pk=item.app.pk, botflow_pk=item.botflow.pk, trigger=f"Email IMAP Trigger: {email_subject}")

        except:
            item.status = "ERROR"
            item.save()

        finally:
            try:
                server.logout()
            except:
                pass

            server = None
            del server

    items, pattern_uid = None, None
    del items, pattern_uid


def email_outlook_trigger_monitor():
    while True:
        range(10000)
        t.sleep(email_outlook_sleep)

        if EmailOutlookTrigger.objects.filter(activated=True).exists():
            break

    CoInitialize()
    email_outlook = win32.dynamic.Dispatch('Outlook.Application')

    while True:
        range(10000)
        t.sleep(email_outlook_sleep)

        if os.path.exists("logs\\error_log.txt"):
            break

        try:
            email_outlook_trigger_monitor_evaluate(email_outlook)

        except EmailOutlookDispatchException:
            print("Connection to Outlook lost, attempting to restart monitoring...")

            try:
                email_outlook.Application.Quit()
            except:
                pass

            email_outlook = None
            del email_outlook

            CoUninitialize()

            email_outlook_trigger_monitor()

        except:
            with open("logs\\error_log.txt", 'a') as f:
                try:
                    f.write(traceback.format_exc())
                    print(traceback.format_exc())
                except:
                    pass
            break

        if not EmailOutlookTrigger.objects.filter(activated=True).exists():
            try:
                email_outlook.Application.Quit()
            except:
                pass

            email_outlook = None
            del email_outlook

            CoUninitialize()

            email_outlook_trigger_monitor()

    try:
        email_outlook.Application.Quit()
    except:
        pass

    email_outlook = None
    del email_outlook

    CoUninitialize()


def email_outlook_trigger_monitor_evaluate(email_outlook):
    items = EmailOutlookTrigger.objects.filter(activated=True)

    for item in items:
        if not item.run_on_week_days:
            if 0 <= datetime.datetime.now(pytz.timezone('Europe/Copenhagen')).weekday() <= 4:
                continue
        if not item.run_on_weekend_days:
            if 5 <= datetime.datetime.now(pytz.timezone('Europe/Copenhagen')).weekday() <= 6:
                continue

        if item.run_after is not None:
            run_after = datetime.timedelta(hours=item.run_after.hour, minutes=item.run_after.minute) - datetime.datetime.now(pytz.timezone('Europe/Copenhagen')).utcoffset()
        else:
            run_after = datetime.timedelta(hours=0, minutes=0)

        if item.run_until is not None:
            run_until = datetime.timedelta(hours=item.run_until.hour, minutes=item.run_until.minute) - datetime.datetime.now(pytz.timezone('Europe/Copenhagen')).utcoffset()
        else:
            run_until = datetime.timedelta(hours=0, minutes=0)

        time_timedelta = datetime.timedelta(hours=datetime.datetime.now(pytz.timezone('UTC')).hour, minutes=datetime.datetime.now(pytz.timezone('UTC')).minute)

        if run_after < run_until:
            if time_timedelta < run_after:
                continue
            if time_timedelta >= run_until:
                continue

        else:
            if time_timedelta >= run_after or time_timedelta < run_until:
                pass
            else:
                continue
        try:
            accounts = email_outlook.Session.Accounts
            accounts_list = [account.DisplayName for account in accounts]

            if item.email == "Default":
                namespace = email_outlook.GetNamespace("MAPI")

            else:
                if not item.email in accounts_list:
                    item.status = "ERROR"
                    item.save()
                    continue

                namespace = None

                for account in accounts:
                    if str(item.email).upper() == str(account.DisplayName).upper():
                        namespace = account.DeliveryStore
                        break

            inbox = namespace.GetDefaultFolder(6)

        except:
            item.status = "ERROR"
            item.save()

            items, accounts, accounts_list, namespace, inbox, folder_in, folder_out, emails = None, None, None, None, None, None, None, None
            del items, accounts, accounts_list, namespace, inbox, folder_in, folder_out, emails

            raise EmailOutlookDispatchException

        folder_in = inbox
        folder_out = inbox

        for folder in item.folder_in.split("/"):
            folder_in = folder_in.Folders[folder]

        for folder in item.folder_out.split("/"):
            folder_out = folder_out.Folders[folder]

        emails = folder_in.Items

        for email in emails:
            email.Move(folder_out)

            if not Botflow.objects.get(pk=item.botflow.pk).queue_if_already_running:
                if BotflowExecution.objects.filter(Q(status="Pending") | Q(status="Running"), botflow=Botflow.objects.get(pk=item.botflow.pk).path).exists():
                    add_botflow_execution = False
                else:
                    add_botflow_execution = True
            else:
                add_botflow_execution = True

            if add_botflow_execution:
                add_botflow_execution_object(bot_pk=item.bot.pk, app_pk=item.app.pk, botflow_pk=item.botflow.pk, trigger=f"Email Outlook Trigger: {email.Subject}")

        if item.status != "Working":
            item.status = "Working"
            item.save()

        accounts, accounts_list, namespace, inbox, folder_in, folder_out, emails = None, None, None, None, None, None, None
        del accounts, accounts_list, namespace, inbox, folder_in, folder_out, emails

    items = None
    del items


def botflow_execution_monitor():
    while True:
        range(10000)
        t.sleep(queue_sleep)

        if os.path.exists("logs\\error_log.txt"):
            break

        try:
            botflow_execution_monitor_evaluate()

        except:
            with open("logs\\error_log.txt", 'a') as f:
                try:
                    f.write(traceback.format_exc())
                    print(traceback.format_exc())
                except:
                    pass
            break


def botflow_execution_monitor_evaluate():
    items = BotflowExecution.objects.filter(status="Pending", computer_name__iexact=os.environ['COMPUTERNAME'], user_name__iexact=os.environ['USERNAME']).order_by('priority', 'time_queued')

    for item in items:
        app = item.app.split("\\")[-1].lower()

        if app == "foxbot.exe" or app == "foxtrot.exe":
            processes = subprocess.run(["wmic", "process", "where", f"name='{app}'", "call", "GetOwner"], stdout=subprocess.PIPE, text=True).stdout.split('\n')

            username = os.environ['USERNAME'].lower()

            if any(str(f'\tuser = "{username}";') in user.lower() for user in processes):
                continue

            if item.nintex_rpa_license_path != "":
                nintex_rpa_license_path = item.nintex_rpa_license_path

                if os.path.exists(nintex_rpa_license_path):
                    nintex_rpa_license_path = os.path.join(item.nintex_rpa_license_path, "System")

                    if os.path.exists(nintex_rpa_license_path):
                        if app == "foxbot.exe":
                            if item.nintex_rpa_available_foxbot_licenses <= len([file for file in os.listdir(nintex_rpa_license_path) if file.startswith("RPA") and file.endswith(".net")]):
                                continue

                        elif app == "foxtrot.exe":
                            if item.nintex_rpa_available_foxtrot_licenses <= len([file for file in os.listdir(nintex_rpa_license_path) if file.startswith("FTE") and file.endswith(".net")]):
                                continue

        item.time_start = datetime.datetime.now(pytz.timezone('Europe/Copenhagen')).strftime(f"%Y-%m-%dT%H:%M:%S+0{str(int(datetime.datetime.now(pytz.timezone('Europe/Copenhagen')).utcoffset().seconds / 60 / 60))}00")
        item.status = "Running"
        item.save()

        status = "Completed"

        if os.path.isfile(item.botflow):
            if not [{'botflow': x.botflow, 'trigger': x.trigger} for x in items if x.status == 'Completed'].count({'botflow': item.botflow, 'trigger': item.trigger}) >= 1:
                try:
                    if app == "foxbot.exe" or app == "foxtrot.exe":
                        if item.close_bot_automatically:
                            subprocess.run([item.app, '/Open', item.botflow, '/Run', '/Close', '/Exit'], timeout=(item.timeout_minutes * 60))
                        else:
                            subprocess.run([item.app, '/Open', item.botflow, '/Run'], timeout=(item.timeout_minutes * 60))
                    else:
                        subprocess.run([item.app, item.botflow], timeout=(item.timeout_minutes * 60))

                except subprocess.TimeoutExpired:
                    status = "Error - Botflow Timeout"

                    try:
                        if app == "foxbot.exe" or app == "foxtrot.exe":
                            os.system('taskkill /f /im foxtrot64.exe')
                    except:
                        pass

                    timeout_kill_processes = [str(process).strip() for process in item.timeout_kill_processes.split(",")]

                    for process in timeout_kill_processes:
                        try:
                            os.system(f'taskkill /f /im {process}')
                        except:
                            pass

            else:
                status = "Skipped - Duplicate Queue Items Detected"

        else:
            status = "Error - Botflow Missing"

        item.time_end = datetime.datetime.now(pytz.timezone('Europe/Copenhagen')).strftime(f"%Y-%m-%dT%H:%M:%S+0{str(int(datetime.datetime.now(pytz.timezone('Europe/Copenhagen')).utcoffset().seconds / 60 / 60))}00")
        item.status = status
        item.save()

        break

    items = None
    del items
