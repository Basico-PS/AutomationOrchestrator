import os
import sys
import django
import requests
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
    restart_time = 2
    error_count = 0
    
    if not os.path.exists("automation_orchestrator\\manage.py"):
        print(f"{datetime.now()}: ERROR! The 'manage.py' file was not found, closing down...")
        sleep(restart_time)
        return None
    
    if os.path.exists('venv\\scripts\\python.exe'):
        python = 'venv\\scripts\\python.exe'
    else:
        python = 'python.exe'
    
    if str(sys.argv[-1]).lower() == '--locally=true':
        url = "http://127.0.0.1:8000/"
        cmd = [python, 'automation_orchestrator\\manage.py', 'runserver', '--noreload']
    else:
        url = gethostbyname_ex(gethostname())[-1][-1]
        url = f"http://{url}:8000/"
        cmd = [python, 'automation_orchestrator\\manage.py', 'runserver', '0.0.0.0:8000', '--noreload']

    while True:
        start_time_loop = datetime.now()
        
        with open("logs\\server_log.txt", "w") as log_file:
            with Popen(cmd, stdout=log_file, stderr=log_file) as p:
                try:
                    print(f"{datetime.now()}: The server is now running on: {url}")
                    print(f"{datetime.now()}: The server will automatically restart in {str(server_runtime)} seconds...")
                    
                    while True:
                        sleep(sleep_time)
                        
                        try:
                            requests.get(url, timeout=restart_time)
                            server_responded = True
                        except requests.exceptions.Timeout:
                            server_responded = False
                        
                        if (datetime.now() - start_time_loop).seconds >= server_runtime or os.path.exists("logs\\error_log.txt") or not server_responded:
                            if not Execution.objects.filter(Q(status="Pending") | Q(status="Running")).exists():
                                if os.path.exists("logs\\error_log.txt"):
                                    error_count += 1
                                    
                                    with open("logs\\error_log.txt") as error_file:
                                        error_message = error_file.read()
                                        
                                    print(f"{datetime.now()}: ERROR OCCURRED: {error_message}")
                                    
                                elif not server_responded:
                                    print(f"{datetime.now()}: ERROR OCCURRED: The server does not respond...")
                                    
                                print(f"{datetime.now()}: Stopping the server...")
                                
                                p.terminate()
                                p.wait()
                                
                                print(f"{datetime.now()}: Server stopped!")
                                break
                            
                            else:
                                print(f"{datetime.now()}: Waiting to restart as something is either 'Pending' or 'Running'...")
                                
                except:
                    print(f"{datetime.now()}: Stopping the server...")
                    
                    p.terminate()
                    p.wait()
                    
                    print(f"{datetime.now()}: Server stopped!")
                    break
        
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
