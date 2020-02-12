CALL CD %~dp0
CALL python -m venv venv
CALL venv\scripts\activate
CALL pip install -r requirements.txt --no-cache-dir
CALL python automation_orchestrator/manage.py migrate
CALL python automation_orchestrator/manage.py createsuperuser

CALL SET /P create_super_user=Would you like to create a super user (Y/N)?

IF %create_super_user% == Y (
	CALL python automation_orchestrator/manage.py createsuperuser
)

echo The installation is now complete!
TIMEOUT 5
