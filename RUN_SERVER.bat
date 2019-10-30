call cd %~dp0
call venv\scripts\activate
python automation_orchestrator/manage.py runserver --noreload
REM python automation_orchestrator/manage.py runserver 0.0.0.0:8000 --noreload
