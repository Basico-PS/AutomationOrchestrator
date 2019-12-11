CALL CD %~dp0
CALL venv\scripts\activate
python automation_orchestrator\run_server.py --locally=false