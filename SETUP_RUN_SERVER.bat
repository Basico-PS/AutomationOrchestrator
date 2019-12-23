CALL CD %~dp0

:CreateJob

CALL SET /P server=Would you like to run the server locally or in your network (L/N)?

IF %server% == L (
	CALL SCHTASKS /CREATE /SC DAILY /TN "AutomationOrchestratorRunServer" /TR "%CD%\run_server\RUN_SERVER_LOCALLY.bat" /ST 00:00 /RI 1 /DU 23:59 /RL HIGHEST /F
	TIMEOUT 15

) 
IF %server% == N (
	CALL SCHTASKS /CREATE /SC DAILY /TN "AutomationOrchestratorRunServer" /TR "%CD%\run_server\RUN_SERVER_NETWORK.bat" /ST 00:00 /RI 1 /DU 23:59 /RL HIGHEST /F
	TIMEOUT 15
)

IF NOT %server% == N (
	IF NOT %server% == L (
		Echo
		Echo
		GOTO CreateJob
	)
)
