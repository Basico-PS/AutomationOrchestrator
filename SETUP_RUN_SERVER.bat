@echo off

CALL CD %~dp0

:CreateJob

echo It is recommended to run the server in your network.
CALL SET /P server=Would you like to run the server locally or in your network (L/N)?

IF NOT %server% == N (
	IF NOT %server% == n (
		IF NOT %server% == L (
			IF NOT %server% == l (
				Echo
				Echo
				GOTO CreateJob
				Echo
				Echo
			)
		)
	)
)

echo It is recommended NOT to run with highest privileges unless it is necessary for the command to be executed.
CALL SET /P privileges=Would you like to run the server with highest privileges (Y/N)?

IF %server% == L (
    CALL SET batchfile="%CD%\run_server\RUN_SERVER_LOCALLY.bat"
) else (
    IF %server% == l (
        CALL SET batchfile="%CD%\run_server\RUN_SERVER_LOCALLY.bat"
    ) else (
        CALL SET batchfile="%CD%\run_server\RUN_SERVER_NETWORK.bat"
    )
)

IF %privileges% == Y (
    CALL SET level=HIGHEST
) else (
    IF %privileges% == y (
        CALL SET level=HIGHEST
    ) else (
        CALL SET level=LIMITED
    )
)

CALL SCHTASKS /CREATE /SC DAILY /TN "AutomationOrchestratorRunServer" /TR %batchfile% /ST 00:00 /RI 1 /DU 23:59 /RL %level% /F
TIMEOUT 15