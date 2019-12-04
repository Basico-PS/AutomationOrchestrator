call cd %~dp0
call python -m venv venv
call venv\scripts\activate
call pip install -r requirements.txt --no-cache-dir
call python automation_orchestrator/manage.py makemigrations
call python automation_orchestrator/manage.py migrate
call python automation_orchestrator/manage.py createsuperuser
