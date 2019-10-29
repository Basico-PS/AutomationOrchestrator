call cd %~dp0
call venv\scripts\activate
call python automation_orchestrator/manage.py runserver
