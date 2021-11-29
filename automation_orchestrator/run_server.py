import os
import sys
import django
import requests
import sqlite3
from socket import gethostname, gethostbyname_ex
from django.db.models import Q
from subprocess import Popen
from time import sleep
from datetime import datetime
from infi.systray import SysTrayIcon
from automation_orchestrator.settings import DATABASE_DIR, DATABASE_NAME


INFO_LOG_PATH = "logs\\info_log.txt"
SERVER_LOG_PATH = "logs\\server_log.txt"
ERROR_LOG_PATH = "logs\\error_log.txt"
MANAGE_SERVER_PATH = "automation_orchestrator\\manage.py"
SHUT_DOWN = False


sys.path.append('automation_orchestrator')
os.environ['DJANGO_SETTINGS_MODULE'] = 'automation_orchestrator.settings'
django.setup()


from orchestrator.models import BotflowExecution, PythonFunctionExecution


def database_backup():
    try:
        db_path = os.path.join(DATABASE_DIR, DATABASE_NAME)
        db_backup_path = os.path.join(DATABASE_DIR, "backup", datetime.now().strftime("%Y%m%d_") + DATABASE_NAME)

        print(f"{datetime.now()}: Performing a backup of the database...")

        db = sqlite3.connect(db_path)
        db_backup = sqlite3.connect(db_backup_path)

        with db_backup:
            db.backup(db_backup)

        print(f"{datetime.now()}: Backup of database complete!")

    except Exception:
        print(f"{datetime.now()}: ERROR! Failed to perform a backup of the database...")

    finally:
        try:
            db.close()
        except Exception:
            pass

        try:
            db_backup.close()
        except Exception:
            pass


def main():
    global SHUT_DOWN

    program_runtime = 7200
    server_runtime = 1800
    sleep_time = 10
    restart_time = 2
    error_count = 0
    error_count_max = 5

    if not os.path.exists(MANAGE_SERVER_PATH):
        print(f"{datetime.now()}: ERROR! The 'manage.py' file was not found, closing down...")
        sleep(sleep_time)
        sys.exit()

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

    start_time_loop = datetime.now()

    database_backup()

    with open(SERVER_LOG_PATH, "w") as log_file:
        with Popen(cmd, stdout=log_file, stderr=log_file) as p:
            try:
                print(f"{datetime.now()}: The server is now running on: {url}")
                print(f"{datetime.now()}: The server will automatically restart in {str(server_runtime / 60)} minutes...")

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

                    if (datetime.now() - start_time_loop).seconds >= server_runtime or os.path.exists(ERROR_LOG_PATH) or not server_responded or SHUT_DOWN:
                        if not BotflowExecution.objects.filter(Q(status="Pending") | Q(status="Running")).exists() and not PythonFunctionExecution.objects.filter(time_end__isnull=True).exists():
                            if os.path.exists(ERROR_LOG_PATH):
                                error_count += 1

                                with open(ERROR_LOG_PATH) as error_file:
                                    error_message = error_file.read()

                                print(f"{datetime.now()}: ERROR OCCURRED: {error_message}")

                            elif not server_responded:
                                print(f"{datetime.now()}: ERROR OCCURRED: The server does not respond...")

                            break

            except Exception:
                print(f"{datetime.now()}: Server interrupted!")
                SHUT_DOWN = True

            else:
                if (datetime.now() - start_time_program).seconds >= program_runtime:
                    print(f"{datetime.now()}: Restarting the program!")
                    SHUT_DOWN = True

                elif not SHUT_DOWN:
                    print(f"{datetime.now()}: Restarting the server!")

            finally:
                print(f"{datetime.now()}: Stopping the server...")

                p.terminate()
                p.wait()

                sleep(restart_time)

                print(f"{datetime.now()}: Server stopped!")

                sleep(restart_time)


def on_quit_callback(systray):
    global SHUT_DOWN
    if not SHUT_DOWN:
        SHUT_DOWN = True

        print(f"{datetime.now()}: Request to quit the server received!")


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    start_time_program = datetime.now()

    with SysTrayIcon("automation_orchestrator\\static\\admin\\favicon.ico", "Automation Orchestrator", on_quit=on_quit_callback) as systray:
        while 1:
            main()

            if SHUT_DOWN:
                break
