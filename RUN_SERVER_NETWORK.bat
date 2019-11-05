call cd %~dp0
call venv\scripts\activate
python automation_orchestrator\run_server.py --locally=false