import os
import sys
import django
from socket import gethostname, gethostbyname_ex
from django.db.models import Q
from subprocess import Popen, PIPE
from time import sleep
from datetime import datetime


sys.path.append('automation_orchestrator')
os.environ['DJANGO_SETTINGS_MODULE'] = 'automation_orchestrator.settings'
django.setup()


from orchestrator.models import Execution


def main():
    start_time_main = datetime.now()
    
    max_runtime = 10800
    server_runtime = 1800
    sleep_time = 10
    restart_time = 10
    error_count = 0
    
    if not os.path.exists("automation_orchestrator\\manage.py"):
        print(f"{datetime.now()}: ERROR! The 'manage.py' file was not found, closing down...")
        sleep(restart_time)
        return None
    
    if str(sys.argv[-1]).lower() == '--locally=true':
        url = "http://127.0.0.1:8000/"
        cmd = ['python', 'automation_orchestrator\\manage.py', 'runserver', '--noreload']
    else:
        url = gethostbyname_ex(gethostname())[-1][-1]
        url = f"http://{url}:8000/"
        cmd = ['python', 'automation_orchestrator\\manage.py', 'runserver', '0.0.0.0:8000', '--noreload']

    while True:
        start_time_loop = datetime.now()
        
        with Popen(cmd, stdout=PIPE, stderr=PIPE) as p:
            print(f"{datetime.now()}: The server is now running on: {url}")
            print(f"{datetime.now()}: The server will automatically restart in {str(server_runtime)} seconds...")
            
            while True:
                sleep(sleep_time)
                
                if (datetime.now() - start_time_loop).seconds >= server_runtime or os.path.exists("error.txt"):
                    executions = Execution.objects.filter(Q(status="Pending") | Q(status="Running"))
                            
                    if len(executions) == 0:
                        if os.path.exists("error.txt"):
                            error_count += 1
                            with open("error.txt") as f:
                                error_message = f.read()
                                
                            print(f"{datetime.now()}: ERROR OCCURRED: {error_message}")
                            
                        print(f"{datetime.now()}: Stopping the server...")
                        
                        p.kill()
                        break
                    
                    else:
                        print(f"{datetime.now()}: Waiting to restart as something is either 'Pending' or 'Running'...")
        
        if error_count >= 3:
            print(f"{datetime.now()}: NOT restarting the server after {str(error_count)} encountered errors!")
            sleep(restart_time)
            break
        
        if (datetime.now() - start_time_main).seconds >= max_runtime:
            print(f"{datetime.now()}: The server has now been running for more than {str(max_runtime)} seconds and is closing down completely...")
            sleep(restart_time)
            break
        
        print(f"{datetime.now()}: Restarting the server in {str(restart_time)} seconds...")
        sleep(restart_time)


if __name__ == '__main__':
    main()
