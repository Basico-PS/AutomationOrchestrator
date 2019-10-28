import os
import glob
import pytz
import shutil
import datetime
import traceback
import subprocess
import time as t
from .models import App, Botflow, FileTrigger, ScheduleTrigger, Execution


trigger_sleep = 2
queue_sleep = 3


def calculate_next_execution(run_start, frequency, run_every, run_after, run_until, run_on_week_days, run_on_weekend_days):    
    for i in range(5256000):
        if frequency == "MI":
            time = run_start + datetime.timedelta(minutes=int(run_every) * i)
            
        elif frequency == "HO":
            time = run_start + datetime.timedelta(hours=int(run_every) * i)
            
        elif frequency == "DA":
            time = run_start + datetime.timedelta(days=int(run_every) * i)
            
        elif frequency == "WE":
            time = run_start + datetime.timedelta(weeks=int(run_every) * i)
        
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
        
        if os.path.exists("error.txt"):
            break
        
        try:
            file_trigger_monitor_evaluate()
            
        except:
            with open("error.txt", 'a') as f:
                try:
                    f.write(traceback.format_exc())
                    print(traceback.format_exc())
                except:
                    pass
            break


def file_trigger_monitor_evaluate():
    items = FileTrigger.objects.filter(activated=True)
    
    for item in items:
        if not os.path.isdir(item.path_in) or not os.path.isdir(item.path_out):
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
        
        files = [file for file in glob.glob(item.path_in + r"\*") if os.path.isfile(file)]
        files.sort(key=os.path.getctime)

        for file in files:
            file_path = os.path.dirname(file)
            file_name = os.path.basename(file)
            
            file_name, file_extension = os.path.splitext(file_name)

            try:
                path_destination = os.path.join(item.path_out, file_name + '' + file_extension)
                
                shutil.move(file, item.path_out)

            except shutil.Error:
                index = 0

                while True:
                    index += 1

                    path_destination = os.path.join(item.path_out, file_name + f'_{index}' + file_extension)

                    if not os.path.isfile(path_destination):
                        shutil.move(file, path_destination)
                    else:
                        continue
                    break
            
            execution = Execution(app=App.objects.get(pk=item.app.pk).path, 
                                  botflow=Botflow.objects.get(pk=item.botflow.pk).path,
                                  trigger=path_destination,
                                  timeout_minutes=Botflow.objects.get(pk=item.botflow.pk).timeout_minutes,
                                  timeout_kill_processes=Botflow.objects.get(pk=item.botflow.pk).timeout_kill_processes,
                                  computer_name=item.computer_name,
                                  user_name=item.user_name,
                                  priority=item.priority,
                                  status="Pending")
            
            execution.save()


def schedule_trigger_monitor():
    while True:
        range(10000)
        t.sleep(trigger_sleep)
        
        if os.path.exists("error.txt"):
            break
        
        try:
            schedule_trigger_monitor_evaluate()
            
        except:
            with open("error.txt", 'a') as f:
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
            execution = Execution(app=App.objects.get(pk=item.app.pk).path, 
                                  botflow=Botflow.objects.get(pk=item.botflow.pk).path,
                                  trigger=datetime.datetime.now(pytz.timezone('Europe/Copenhagen')).strftime("%Y-%m-%d %H:%M"),
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
        
        elif datetime.datetime.strptime(item.next_execution, "%Y-%m-%d %H:%M") < now:
            run_start = now.replace(tzinfo=pytz.timezone('UTC'))
            item.next_execution = calculate_next_execution(run_start, item.frequency, item.run_every, run_after, run_until, item.run_on_week_days, item.run_on_weekend_days)
            item.past_settings = settings
            item.save()


def execution_monitor():
    while True:
        range(10000)
        t.sleep(queue_sleep)
        
        if os.path.exists("error.txt"):
            break
        
        try:
            execution_monitor_evaluate()
            
        except:
            with open("error.txt", 'a') as f:
                try:
                    f.write(traceback.format_exc())
                    print(traceback.format_exc())
                except:
                    pass
            break
        

def execution_monitor_evaluate():
    items = Execution.objects.filter(status="Pending", computer_name__iexact=os.environ['COMPUTERNAME'], user_name__iexact=os.environ['USERNAME']).order_by('-priority', 'time_queued')
    
    for item in items:
        while True:
            if not any(item.app.split("\\")[-1].lower() in process.lower() for process in subprocess.run(["wmic", "process", "get", "description,executablepath"], stdout=subprocess.PIPE, text=True).stdout.split('\n')):
                break
            range(10000)
            t.sleep(queue_sleep)
            
        item.time_start = datetime.datetime.now(pytz.timezone('Europe/Copenhagen')).strftime(f"%Y-%m-%dT%H:%M:%S+0{str(int(datetime.datetime.now(pytz.timezone('Europe/Copenhagen')).utcoffset().seconds / 60 / 60))}00")
        item.status = "Running"
        item.save()
        
        status = "Completed"
        
        if os.path.isfile(item.botflow):
            if not [{'botflow': x.botflow, 'trigger': x.trigger} for x in items if x.status == 'Completed'].count({'botflow': item.botflow, 'trigger': item.trigger}) >= 1:
                try:
                    if 'foxtrot' or 'foxbot' in item.app.lower():
                        subprocess.run([item.app, r'/Open', item.botflow, r'/Run', r'/Close', r'/Exit'], timeout=(item.timeout_minutes * 60))
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
