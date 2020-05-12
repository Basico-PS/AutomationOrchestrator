import os
import sys
import django
import requests
import sqlite3
from socket import gethostname, gethostbyname_ex
from django.db.models import Q
from subprocess import Popen, PIPE
from time import sleep
from datetime import datetime
from automation_orchestrator.settings import DATABASE_DIR, DATABASE_NAME


INFO_LOG_PATH = "logs\\info_log.txt"
SERVER_LOG_PATH = "logs\\server_log.txt"
ERROR_LOG_PATH = "logs\\error_log.txt"
MANAGE_SERVER_PATH = "automation_orchestrator\\manage.py"


sys.path.append('automation_orchestrator')
os.environ['DJANGO_SETTINGS_MODULE'] = 'automation_orchestrator.settings'
django.setup()


from orchestrator.models import BotflowExecution, PythonFunctionExecution


def database_backup():
    try:
        print(f"{datetime.now()}: Performing a backup of the database...")

        db = sqlite3.connect(os.path.join(DATABASE_DIR, DATABASE_NAME))
        db_backup = sqlite3.connect(os.path.join(DATABASE_DIR, "backup", datetime.now().strftime("%Y%m%d%H%M%S ") + DATABASE_NAME))

        with db_backup:
            db.backup(db_backup)

        print(f"{datetime.now()}: Backup of database complete!")

    except:
        print(f"{datetime.now()}: ERROR! Failed to perform a backup of the database...")

    finally:
        try:
            db.close()
        except:
            pass

        try:
            db_backup.close()
        except:
            pass


def main():
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    database_backup()

    start_time_main = datetime.now()

    max_runtime = 10800
    server_runtime = 1800
    sleep_time = 10
    restart_time = 2
    error_count = 0

    if not os.path.exists(MANAGE_SERVER_PATH):
        print(f"{datetime.now()}: ERROR! The 'manage.py' file was not found, closing down...")
        sleep(restart_time)
        return None

    python_exe = 'pythonw.exe'
    if os.path.exists(f'venv\\scripts\\{python_exe}'):
        python = f'venv\\scripts\\{python_exe}'
    else:
        python = python_exe

    if str(sys.argv[-1]).lower() == '--locally=true':
        url = "http://127.0.0.1:8000/"
        cmd = [python, MANAGE_SERVER_PATH, 'runserver', '--noreload']
    else:
        url = gethostbyname_ex(gethostname())[-1][-1]
        url = f"http://{url}:8000/"
        cmd = [python, MANAGE_SERVER_PATH, 'runserver', '0.0.0.0:8000', '--noreload']

    while True:
        start_time_loop = datetime.now()

        with open(SERVER_LOG_PATH, "w") as log_file:
            with Popen(cmd, stdout=log_file, stderr=log_file) as p:
                try:
                    print(f"{datetime.now()}: The server is now running on: {url}")
                    print(f"{datetime.now()}: The server will automatically restart in {str(server_runtime)} seconds...")

                    with open(INFO_LOG_PATH, "w") as file:
                        file.write(f"Url: {url}\n")

                    while True:
                        range(10000)
                        sleep(sleep_time)

                        try:
                            requests.get(url, timeout=restart_time)
                            server_responded = True
                        except requests.exceptions.Timeout:
                            server_responded = False

                        if (datetime.now() - start_time_loop).seconds >= server_runtime or os.path.exists(ERROR_LOG_PATH) or not server_responded:
                            if not BotflowExecution.objects.filter(Q(status="Pending") | Q(status="Running")).exists() and not PythonFunctionExecution.objects.filter(time_end__isnull=True).exists():
                                if os.path.exists(ERROR_LOG_PATH):
                                    error_count += 1

                                    with open(ERROR_LOG_PATH) as error_file:
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
