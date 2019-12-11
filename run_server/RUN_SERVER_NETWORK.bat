CALL CD %~dp0
CALL CD ..
CALL venv\scripts\activate
python automation_orchestrator\run_server.py --locally=false