call cd %~dp0
call venv\scripts\activate
call python automation_orchestrator/manage.py runserver
REM call python automation_orchestrator/manage.py runserver 0.0.0.0:8000
