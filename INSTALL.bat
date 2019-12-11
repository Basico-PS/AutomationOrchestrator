CALL CD %~dp0
CALL python -m venv venv
CALL venv\scripts\activate
CALL pip install -r requirements.txt --no-cache-dir
CALL python automation_orchestrator/manage.py makemigrations
CALL python automation_orchestrator/manage.py migrate
CALL python automation_orchestrator/manage.py createsuperuser