:CreateJob

CALL SET /P server=Would you like to run the server locally or in your network (L/N)?

IF %server% == L (
	CALL SCHTASKS /CREATE /SC DAILY /TN "AutomationOrchestratorRunServer" /TR %CD%"\RUN_SERVER_LOCALLY.bat" /ST 01:00 /RI 1 /DU 23:59 /RL HIGHEST /F
) 
IF %server% == N (
	CALL SCHTASKS /CREATE /SC DAILY /TN "AutomationOrchestratorRunServer" /TR %CD%"\RUN_SERVER_NETWORK.bat" /ST 01:00 /RI 1 /DU 23:59 /RL HIGHEST /F
)

IF NOT %server% == N (
	IF NOT %server% == L (
		GOTO CreateJob
	)
)