import os
import glob
import pytz
import shutil
import datetime
import calendar
import traceback
import subprocess
import pythoncom
import time as t
import win32com.client as win32
from .models import App, Botflow, FileTrigger, ScheduleTrigger, OutlookTrigger, Execution
from django.db.models import Q
from dateutil.relativedelta import relativedelta


trigger_sleep = 2
outlook_sleep = 2
queue_sleep = 3


class OutlookDispatchException(Exception):
    # Exception to be used when the connection to the dispatched Outlook object is lost.
    pass


def calculate_next_execution(run_start, frequency, run_every, run_after, run_until, run_on_week_days, run_on_weekend_days):    
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
                    
            if run_on_week_days == False:
                if 0 <= time.weekday() <= 4:
                    continue
            if run_on_weekend_days == False:
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
            continue
                    
        if item.run_on_week_days == False:
            if 0 <= datetime.datetime.now(pytz.timezone('Europe/Copenhagen')).weekday() <= 4:
                continue
        if item.run_on_weekend_days == False:
            if 5 <= datetime.datetime.now(pytz.timezone('Europe/Copenhagen')).weekday() <= 6:
                continue
        
        if item.run_after != None:
            run_after = datetime.timedelta(hours=item.run_after.hour, minutes=item.run_after.minute) - datetime.datetime.now(pytz.timezone('Europe/Copenhagen')).utcoffset()
        else:
            run_after = datetime.timedelta(hours=0, minutes=0)
            
        if item.run_until != None:
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
            
            if Botflow.objects.get(pk=item.botflow.pk).queue_if_already_running == False:
                already_running = Execution.objects.filter(Q(status="Pending") | Q(status="Running"), botflow=Botflow.objects.get(pk=item.botflow.pk).path)
            else:
                already_running = []
            
            if len(already_running) < 1:
                execution = Execution(app=App.objects.get(pk=item.app.pk).path, 
                                    botflow=Botflow.objects.get(pk=item.botflow.pk).path,
                                    trigger=f"File Trigger: {path_destination}",
                                    close_bot_automatically=Botflow.objects.get(pk=item.botflow.pk).close_bot_automatically,
                                    timeout_minutes=Botflow.objects.get(pk=item.botflow.pk).timeout_minutes,
                                    timeout_kill_processes=Botflow.objects.get(pk=item.botflow.pk).timeout_kill_processes,
                                    computer_name=item.computer_name,
                                    user_name=item.user_name,
                                    priority=item.priority,
                                    status="Pending")
                
                execution.save()
        
            already_running = None
            del already_running
        
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
        
        if item.run_after != None:
            run_after = datetime.timedelta(hours=item.run_after.hour, minutes=item.run_after.minute) - datetime.datetime.now(pytz.timezone('Europe/Copenhagen')).utcoffset()
        else:
            run_after = datetime.timedelta(hours=0, minutes=0)
            
        if item.run_until != None:
            run_until = datetime.timedelta(hours=item.run_until.hour, minutes=item.run_until.minute) - datetime.datetime.now(pytz.timezone('Europe/Copenhagen')).utcoffset()
        else:
            run_until = datetime.timedelta(hours=0, minutes=0)
            
        settings = f"{item.frequency},{item.run_every},{item.run_start},{item.run_after},{item.run_until},{item.run_on_week_days},{item.run_on_weekend_days}"
            
        if item.next_execution == "":
            run_start = item.run_start.replace(tzinfo=pytz.timezone('UTC'))
            item.next_execution = calculate_next_execution(run_start, item.frequency, item.run_every, run_after, run_until, item.run_on_week_days, item.run_on_weekend_days)
            item.past_settings = settings
            item.save()
            
        elif item.past_settings != settings:
            run_start = item.run_start.replace(tzinfo=pytz.timezone('UTC'))
            item.next_execution = calculate_next_execution(run_start, item.frequency, item.run_every, run_after, run_until, item.run_on_week_days, item.run_on_weekend_days)
            item.past_settings = settings
            item.save()
            
        if datetime.datetime.strptime(item.next_execution, "%Y-%m-%d %H:%M") == now:
            if Botflow.objects.get(pk=item.botflow.pk).queue_if_already_running == False:
                already_running = Execution.objects.filter(Q(status="Pending") | Q(status="Running"), botflow=Botflow.objects.get(pk=item.botflow.pk).path)
            else:
                already_running = []
            
            if len(already_running) < 1:
                time_trigger = datetime.datetime.now(pytz.timezone('Europe/Copenhagen')).strftime("%Y-%m-%d %H:%M")
                
                execution = Execution(app=App.objects.get(pk=item.app.pk).path,
                                    botflow=Botflow.objects.get(pk=item.botflow.pk).path,
                                    trigger=f"Schedule Trigger: {time_trigger}",
                                    close_bot_automatically=Botflow.objects.get(pk=item.botflow.pk).close_bot_automatically,
                                    timeout_minutes=Botflow.objects.get(pk=item.botflow.pk).timeout_minutes,
                                    timeout_kill_processes=Botflow.objects.get(pk=item.botflow.pk).timeout_kill_processes,
                                    computer_name=item.computer_name,
                                    user_name=item.user_name,
                                    priority=item.priority,
                                    status="Pending")
                execution.save()
            
            run_start = now.replace(tzinfo=pytz.timezone('UTC'))
            item.next_execution = calculate_next_execution(run_start, item.frequency, item.run_every, run_after, run_until, item.run_on_week_days, item.run_on_weekend_days)
            item.past_settings = settings
            item.save()
        
            already_running = None
            del already_running
        
        elif datetime.datetime.strptime(item.next_execution, "%Y-%m-%d %H:%M") < now:
            run_start = datetime.datetime.strptime(item.next_execution, "%Y-%m-%d %H:%M").replace(tzinfo=pytz.timezone('UTC'))
            item.next_execution = calculate_next_execution(run_start, item.frequency, item.run_every, run_after, run_until, item.run_on_week_days, item.run_on_weekend_days)
            item.past_settings = settings
            item.save()
        
    items = None
    del items


def outlook_trigger_monitor():    
    while True:
        range(10000)
        t.sleep(outlook_sleep)
        
        if len(OutlookTrigger.objects.filter(activated=True)) >= 1:
            break
    
    
    pythoncom.CoInitialize()
    outlook = win32.dynamic.Dispatch('Outlook.Application')
    
    while True:
        range(10000)
        t.sleep(outlook_sleep)
        
        if os.path.exists("logs\\error_log.txt"):
            break
        
        try:
            outlook_trigger_monitor_evaluate(outlook)
            
        except OutlookDispatchException:
            print("Connection to Outlook lost, attempting to restart monitoring...")
            
            try:
                outlook.Application.Quit()
            except:
                pass
            outlook = None
            del outlook
            pythoncom.CoUninitialize()
    
            outlook_trigger_monitor()
        
        except:
            with open("logs\\error_log.txt", 'a') as f:
                try:
                    f.write(traceback.format_exc())
                    print(traceback.format_exc())
                except:
                    pass
            break
        
        if len(OutlookTrigger.objects.filter(activated=True)) == 0:
            try:
                outlook.Application.Quit()
            except:
                pass
            outlook = None
            del outlook
            pythoncom.CoUninitialize()
            
            outlook_trigger_monitor()

    try:
        outlook.Application.Quit()
    except:
        pass
    outlook = None
    del outlook
    pythoncom.CoUninitialize()


def outlook_trigger_monitor_evaluate(outlook):
    items = OutlookTrigger.objects.filter(activated=True)
    
    for item in items:        
        try:
            accounts = outlook.Session.Accounts
            accounts_list = [account.DisplayName for account in accounts]
            
            if item.email == "Default":
                namespace = outlook.GetNamespace("MAPI")
            else:
                if not item.email in accounts_list:
                    continue
                namespace = None
                for account in accounts:
                    if str(item.email).upper() == str(account.DisplayName).upper():
                        namespace = account.DeliveryStore
                        break
            
            inbox = namespace.GetDefaultFolder(6)
            
        except:
            items, accounts, accounts_list, namespace, inbox, folder_in, folder_out, emails = None, None, None, None, None, None, None, None
            del items
            del accounts
            del accounts_list
            del namespace
            del inbox
            del folder_in
            del folder_out
            del emails
            
            raise OutlookDispatchException
    
        if item.run_on_week_days == False:
            if 0 <= datetime.datetime.now(pytz.timezone('Europe/Copenhagen')).weekday() <= 4:
                continue
        if item.run_on_weekend_days == False:
            if 5 <= datetime.datetime.now(pytz.timezone('Europe/Copenhagen')).weekday() <= 6:
                continue
        
        if item.run_after != None:
            run_after = datetime.timedelta(hours=item.run_after.hour, minutes=item.run_after.minute) - datetime.datetime.now(pytz.timezone('Europe/Copenhagen')).utcoffset()
        else:
            run_after = datetime.timedelta(hours=0, minutes=0)
            
        if item.run_until != None:
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
        
        folder_in = inbox
        folder_out = inbox
        
        for folder in item.folder_in.split("\\"):
            folder_in = folder_in.Folders[folder]
        
        for folder in item.folder_out.split("\\"):
            folder_out = folder_out.Folders[folder]
            
        emails = folder_in.Items

        for email in emails:
            email.Move(folder_out)
            
            if Botflow.objects.get(pk=item.botflow.pk).queue_if_already_running == False:
                already_running = Execution.objects.filter(Q(status="Pending") | Q(status="Running"), botflow=Botflow.objects.get(pk=item.botflow.pk).path)
            else:
                already_running = []
            
            if len(already_running) < 1:
                execution = Execution(app=App.objects.get(pk=item.app.pk).path, 
                                        botflow=Botflow.objects.get(pk=item.botflow.pk).path,
                                        trigger=f"Outlook Trigger: {email.Subject}",
                                        close_bot_automatically=Botflow.objects.get(pk=item.botflow.pk).close_bot_automatically,
                                        timeout_minutes=Botflow.objects.get(pk=item.botflow.pk).timeout_minutes,
                                        timeout_kill_processes=Botflow.objects.get(pk=item.botflow.pk).timeout_kill_processes,
                                        computer_name=item.computer_name,
                                        user_name=item.user_name,
                                        priority=item.priority,
                                        status="Pending")
                
                execution.save()
        
            already_running = None
            del already_running
            
        accounts, accounts_list, namespace, inbox, folder_in, folder_out, emails = None, None, None, None, None, None, None
        del accounts
        del accounts_list
        del namespace
        del inbox
        del folder_in
        del folder_out
        del emails

    items = None
    del items


def execution_monitor():
    while True:
        range(10000)
        t.sleep(queue_sleep)
        
        if os.path.exists("logs\\error_log.txt"):
            break
        
        try:
            execution_monitor_evaluate()
            
        except:
            with open("logs\\error_log.txt", 'a') as f:
                try:
                    f.write(traceback.format_exc())
                    print(traceback.format_exc())
                except:
                    pass
            break
        

def execution_monitor_evaluate():
    items = Execution.objects.filter(status="Pending", computer_name__iexact=os.environ['COMPUTERNAME'], user_name__iexact=os.environ['USERNAME']).order_by('priority', 'time_queued')
    
    for item in items:
        app = item.app.split("\\")[-1].lower()
        username = os.environ['USERNAME'].lower()
        processes = subprocess.run(["wmic", "process", "where", f"name='{app}'", "call", "GetOwner"], stdout=subprocess.PIPE, text=True).stdout.split('\n')
        
        if any(str(f'\tuser = "{username}";') in user.lower() for user in processes):
            continue
            
        item.time_start = datetime.datetime.now(pytz.timezone('Europe/Copenhagen')).strftime(f"%Y-%m-%dT%H:%M:%S+0{str(int(datetime.datetime.now(pytz.timezone('Europe/Copenhagen')).utcoffset().seconds / 60 / 60))}00")
        item.status = "Running"
        item.save()
        
        status = "Completed"
        
        if os.path.isfile(item.botflow):
            if not [{'botflow': x.botflow, 'trigger': x.trigger} for x in items if x.status == 'Completed'].count({'botflow': item.botflow, 'trigger': item.trigger}) >= 1:
                try:
                    if 'foxtrot' or 'foxbot' in item.app.lower():
                        if item.close_bot_automatically == True:
                            subprocess.run([item.app, '/Open', item.botflow, '/Run', '/Close', '/Exit'], timeout=(item.timeout_minutes * 60))
                        else:
                            subprocess.run([item.app, '/Open', item.botflow, '/Run'], timeout=(item.timeout_minutes * 60))
                    else:
                        subprocess.run([item.app, item.botflow], timeout=(item.timeout_minutes * 60))
                    
                except subprocess.TimeoutExpired:
                    status = "Error - Botflow Timeout"
                    
                    try:
                        if 'foxtrot' or 'foxbot' in item.app.lower():
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
