# Basico P/S - Automation Orchestrator

<p align="center">
  <img src="/images/login_page.png">
</p>

The Automation Orchestrator allows you to run a local [Django Web Application](https://www.djangoproject.com/) to administrate and orchestrate automation scripts such as Nintex RPA botflows but you may also orchestrate other automation such as Python scripts, batch files, and other RPA tools.
The Automation Orchestrator is tested with and supports Nintex RPA version <= 15.1.

## Table of contents

-   [Introduction](#introduction)
-   [Installation](#installation)
-   [Server](#server)
-   [Common Issues](#common-issues)
-   [Setup](#setup)
-   [Notes](#notes)
-   [Copyrights](#copyrights)
-   [Contact](#contact)

## Introduction

As described on the official Django project site, it <i>"is a high-level Python Web framework that encourages rapid development and clean, pragmatic design. Built by experienced developers, it takes care of much of the hassle of Web development, so you can focus on writing your app without needing to reinvent the wheel. It’s free and open source."</i>

Some of the biggest web platforms and brands like [Instagram and Pinterest use the Django Framework](https://www.djangoproject.com/start/overview/) due to its leading security features and ability to scale.

The purpose of the Automation Orchestrator is to offer a well-functioning, fully customizable web server application to trigger and schedule scripts. The Automation Orchestrator can run as a fully local server only available on the local host accessible via a browser or as a server available in your protected internal network accessible via a browser.

Feature highlights out-of-the-box:

-   Authentication & Authorization
    -   Groups
    -   Users
-   Setup
    -   Bots
    -   Apps
    -   Botflows
-   Notifications
    -   SMTP accounts
-   Triggers
    -   API Triggers
    -   Email IMAP Triggers
    -   Email Outlook Triggers
    -   File Triggers
    -   Schedule Triggers
-   Botflow Execution Log
    -   Queue Functionality with License Awareness and Botflow Priorities
-   Native Script Support
    -   Python
    -   Nintex Foxtrot RPA
    -   UiPath
    -   VBScript
    -   Any other tools that can be executed as a command with: "application_path.exe" "file_path.abc"
-   Dashboard
    -   Graphic Execution Overview
    -   Calendar View of Execution History

## Installation

We highly recommend that the Automation Orchestrator is installed and setup only by people experienced with both Python and Nintex RPA. You are always welcome to contact us for assistance via: robotics@basico.dk

Out-of-the-box, the Automation Orchestrator can trigger and schedule scripts on the same machine and user running the server. In case you wish to do either of the following two things, you need to utilize the [Automation Orchestrator Executor](https://github.com/Basico-PS/AutomationOrchestratorExecutor) add-on:

-   Run the Automation Orchestrator on one machine but execute the scripts on a different machine, or
-   Run the Automation Orchestrator on a machine (for example, a Windows Terminal Server) with multiple users that are supposed to execute scripts

For the Automation Orchestrator to work, you need to install Python. Make sure to install the latest [![Python 3](https://img.shields.io/badge/python-3-blue.svg)](https://www.python.org/ftp/python/3.8.3/python-3.8.3-amd64.exe) 64-bit version. If you are in any doubts on how to correctly install Python, follow [this guide](https://www.mbalslow.com/blog/article/how-to-install-python/) or [contact us](#contact).

After installing Python, you are now ready to install the Automation Orchestrator. Follow these steps precisely:

1. Create a folder called "AutomationOrchestrator" on your machine, for example, directly on the C: drive or in the "Program Files" folder. So, your path should be similar to "C:\AutomationOrchestrator" or "C:\Program Files\AutomationOrchestrator".

2. Navigate to the [list of releases](https://github.com/Basico-PS/AutomationOrchestrator/releases) and download the source code (ZIP) of the latest version.

3. Unzip the folder in your created "AutomationOrchestrator" folder. So, your path could be similar to "C:\AutomationOrchestrator\AutomationOrchestrator-0.3.0" or "C:\Program Files\AutomationOrchestrator\AutomationOrchestrator-0.3.0".

4. After unzipping the folder, run the "INSTALL.bat" [file](https://github.com/Basico-PS/AutomationOrchestrator/blob/master/INSTALL.bat) for an automated installation process. Remember to run the batch file (or commands manually) as an administrator.

5. The last command of the installation process will prompt you to create an account, a super user with full permissions to the Automation Orchestrator. After creating the super user, the installation process is complete.

## Server

After a successful installation, you are now ready to run the Automation Orchestrator, the web server. You can run the Automation Orchestrator either locally or in your protected internal network. Which of the two options to choose depends on whether you intend to use and access the Automation Orchestrator only on the host machine or not. You can always switch between the two options.

Run the "SETUP_RUN_SERVER.bat" [file](https://github.com/Basico-PS/AutomationOrchestrator/blob/master/SETUP_RUN_SERVER.bat), which will create a scheduled job called AutomationOrchestratorRunServer in the Windows Task Scheduler. The created job will run every minute to make sure that the Automation Orchestrator is always running. Remember to run the batch file (or commands manually) as an administrator.

<p align="center">
  <img src="/images/run_server.png">
</p>

As long as you see this window running, the Automation Orchestrator is actively running on your machine. You can always minimize it.

IMPORTANT: If you wish to stop the server, <u>you MUST click the shortcut ctrl+c</u> in the server window to see the confirmation that the server is stopped before closing the window. Make sure to NOT close the server while any executions are running. Sometimes you need to hit the keys a couple of times before it is registered by the server. Also, remember to disable the job AutomationOrchestratorRunServer in the Windows Task Scheduler if you wish to make sure that it does not restart after one minute.

<p align="center">
  <img src="/images/close_server.png">
</p>

## Common Issues

This section contains a list of common issues and a description on how to solve them. In case the explained solution does not solve the issue or you experience issues not listen below, please report it [here](https://github.com/Basico-PS/AutomationOrchestrator/issues/new).

### During Installation

-   If the process of downloading and installing the Python packages fail with a Proxy Error, you need to you must define the your proxy settings before performing the "pip install" command. This can be done either by adjusting the INSTALL.bat file or performing the installation process (the commands of the INSTALL.bat) manually using the CMD. This means that you need to run the following commands before running the "pip install -r requirements.txt --no-cache-dir" command (make sure to replace the placeholder values):
    -   set "http_proxy=http://USERNAME:PASSWORD@PROXY_ADRESS:PORT"
    -   set "https_proxy=https://USERNAME:PASSWORD@PROXY_ADRESS:PORT"

### Running Automation Orchestrator

-   After a successful installation (no errors during the process), if you experience that you are not able to access the Automation Orchestrator in the browser, make sure to restart the machine. In case that does not help, check the following point.

-   The Automation Orchestrator will fail to run if the user does not have permissions to execute Python. Make sure to allow the user to execute the global install of Python (python.exe and pythonw.exe) and hereafter the Python (python.exe and pythonw.exe) installed in the virtual environment of the Automation Orchestrator ("./venv/scripts/python.exe" and "./venv/scripts/pythonw.exe").

-   If you either experience that you are unable to access the Automation Orchestrator in the browser or you get a "OperationalError at /login/ - attempt to write a readonly database", make sure that the user has full read and write permissions to the folder where Automation Orchestrator is installed. Right-click on the main "AutomationOrchestrator" folder and give the specific if not all users full permissions.

-   If you have selected to run the Automation Orchestrator in your protected internal network but are unable to access the application in a browser from another computer in your domain, you need to make sure that your Python instance is allowed to communicate through the firewall of your domain. To fix this, you can go to "Allow an app through Windows Firewall" and click "Allow another app...". First, make sure to add the global install of Python (python.exe and pythonw.exe) and hereafter the Python (python.exe and pythonw.exe) installed in the virtual environment of the Automation Orchestrator ("./venv/scripts/python.exe" and "./venv/scripts/pythonw.exe").

## Setup

You are now ready to access the Automation Orchestrator via a browser and get started. As long as the Automation Orchestrator is running, you can access it in your browser. The URL is specified in the window of the server running. Begin by signing in to the Automation Orchestrator using the super user that you created during the installation process. You should now see the home page.

<p align="center">
  <img src="/images/home_page_1.png">
</p>
<p align="center">
  <img src="/images/home_page_2.png">
</p>

After signing in, you can begin to set up the Automation Orchestrator. This is the order of the setup:

1. Add a Bot: This is the computer name and username to run the automation. Begin by adding the current computer and user, which will be the default values of the first Bot you add.

<p align="center">
  <img src="/images/add_bot.png">
</p>

2. Add an App: This is the Apps you wish to use for automation. The path of the App must be the path on the computer and user to run the automation. For example, this could be name "Foxtrot" and path "C:\Program Files (x86)\Foxtrot Suite\Foxtrot\Foxtrot.exe"

<p align="center">
  <img src="/images/add_app.png">
</p>

3. Add a Botflow: This is the Botflows you wish to run with your Apps. The path of the Botflow must be the path on the computer and user to run the automation. For example, this could be name "Invoicing Process" and path "C:\Users\mbalslow\Downloads\Invoicing Process.rpa"

<p align="center">
  <img src="/images/add_botflow_1.png">
</p>
<p align="center">
  <img src="/images/add_botflow_2.png">
</p>

4. Set up Triggers: The Triggers will be what is activating the automation. The simplest Triggers are File Triggers and Schedule Triggers.

<p align="center">
  <img src="/images/add_file_trigger.png">
</p>

-   For testing purposes, and if you ever need to start an automation manually, you can always manually activate the Triggers by selecting them in the list and use the action in the dropdown to activate them.

<p align="center">
  <img src="/images/test_trigger.png">
</p>

5. Follow the Botflow Executions: When Triggers are activated, a record is added to Botflow Executions. The different statusses are:
    - Pending
    - Running
    - Completed
    - Error
    - Cancelled

<p align="center">
  <img src="/images/executions.png">
</p>

6. Get Email Notifications: If you wish to receive Email Notifications, you can set up an SMTP Account.

<p align="center">
  <img src="/images/add_smtp_account.png">
</p>

-   After setting up the SMTP Account, you can test it to make sure that the settings are correct by selecting it in the list and use the action in the dropdown to test it.

<p align="center">
  <img src="/images/test_smtp_account_1.png">
</p>
<p align="center">
  <img src="/images/test_smtp_account_2.png">
</p>

-   Now, go to your Botflows and add the recipients for each of the Botflow Execution events.

<p align="center">
  <img src="/images/add_botflow_3.png">
</p>

You have now set up the Automation Orchestrator!

## Notes

The Automation Orchestrator runs with the ["DEBUG" flag set to "True"](https://docs.djangoproject.com/en/3.0/ref/settings/#debug), which is not recommended in a cloud production environment, since the Automation Orchestrator should only be used to run fully locally or shared in your protected internal network. If you wish to deploy the Automation Orchestrator in the open cloud, there are [many additional steps](https://docs.djangoproject.com/en/3.0/howto/deployment/) to consider and implement.

## Copyrights

Starting from v0.0.17 Basico P/S - Automation Orchestrator is distributed under the [BSD 3-clause license](https://github.com/Basico-PS/AutomationOrchestrator/blob/master/LICENSE). Basico P/S - Automation Orchestrator v0.0.16 and before was distributed under the MIT license.

(c) Basico P/S, Mathias Balsløw 2019-2020

## Contact

For contact or support, please write to us at: robotics@basico.dk
