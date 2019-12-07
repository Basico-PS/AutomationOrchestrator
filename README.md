# Basico P/S - Automation Orchestrator

<i>More documentation is underway...</i>

For support, please contact us: robotics@basico.dk

<p align="center">
  <img src="/images/login%20page.png">
</p>

The Automation Orchestrator allows you to run a local [Django Web Application](https://www.djangoproject.com/) to administrate and orchestrate automation scripts such as Nintex RPA botflows. Feature highlights out-of-the-box:
- Groups and User Setup
- File Triggers
- Schedule Triggers
- Email Outlook Triggers
- Queue Functionality
- Execution Log

As described on the official Django project site, it <i>"is a high-level Python Web framework that encourages rapid development and clean, pragmatic design. Built by experienced developers, it takes care of much of the hassle of Web development, so you can focus on writing your app without needing to reinvent the wheel. It’s free and open source."</i>

Some of the biggest web platforms and brands like [Instagram and Pinterest use the Django Framework](https://www.djangoproject.com/start/overview/) due to its leading security features and ability to scale.

The purpose of the Automation Orchestrator is to offer a well-functioning, fully customizable automation orchestrator application to trigger and schedule scripts. The Automation Orchestrator can run as a fully local server only available on the local host accessible via a browser or as a server available in your protected internal network accessible via a browser. 

Out-of-the-box, the Automation Orchestrator can trigger and schedule scripts on the same machine and user running the server. In case you wish to do either of the two things below, you need to utilize the [Automation Orchestrator Executor add-on](https://github.com/Basico-PS/AutomationOrchestratorExecutor):
- Run the Automation Orchestrator on one machine but execute the scripts on a different machine, or
- Run the Automation Orchestrator on a machine (for example, a Windows Terminal Server) with multiple users that are supposed to execute scripts

IMPORTANT: For the Automation Orchestrator to work, you need to run the server in your protected internal network by using the "RUN_SERVER_NETWORK.bat" [file](https://github.com/Basico-PS/AutomationOrchestrator/blob/master/RUN_SERVER_NETWORK.bat).

IMPORTANT: The Automation Orchestrator runs with the ["DEBUG" flag set to "True"](https://docs.djangoproject.com/en/2.2/ref/settings/#debug), which is not recommended in a cloud production environment, since the Automation Orchestrator should only be used to run fully locally or shared in your protected internal network. If you wish to deploy the Automation Orchestrator in the open cloud, there are [many additional steps](https://docs.djangoproject.com/en/2.2/howto/deployment/) to consider and implement.

## Installation

For the Automation Orchestrator to work, you need to install [Python](https://www.python.org/). The Automation Orchestrator is tested with Python 3.7 and 3.8.

1. Download the [latest version](https://github.com/Basico-PS/AutomationOrchestrator/archive/v0.0.16.zip).
2. Create a folder called "Automation Orchestrator" somewhere convenient, for example, directly on the C: drive or in the "Program Files" folder.
3. Unzip the folder in your created "Automation Orchestrator" folder. So, your path could be similar to "C:\Automation Orchestrator\AutomationOrchestrator-0.0.16" or "C:\Program Files\Automation Orchestrator\AutomationOrchestrator-0.0.16". However, you may unzip the folder anywhere on your system.
4. After unzipping the folder, run the "INSTALL.bat" [file](https://github.com/Basico-PS/AutomationOrchestrator/blob/master/INSTALL.bat) for an automated installation process. You may also manually run the installation steps via, for example, the CMD. Remember to run the batch file (or commands manually) as an administrator.
5. The last command of the installation process will prompt you to create an account, a super user who has all permissions. After creating the super user, the installation process is complete.

Here is a [video walkthrough](https://www.screencast.com/t/PgK9OkKpx2) of the installation and setup process.

## Usage

After a succesful installation, you can now start your server either locally by running the "RUN_SERVER_LOCALLY.bat" [file](https://github.com/Basico-PS/AutomationOrchestrator/blob/master/RUN_SERVER_LOCALLY.bat) or in your protected internal network by running the "RUN_SERVER_NETWORK.bat" [file](https://github.com/Basico-PS/AutomationOrchestrator/blob/master/RUN_SERVER_NETWORK.bat). Remember to run the batch file (or commands manually) as an administrator. The server will automatically restart every 30 minutes (unless something is running, in the case, it will wait) and run for no more than 3 hours in total. This is to make sure that the server is restarted regurlarly.

<b>IMPORTANT: For the server to succesfully work as an automation orchestrator, it needs to be always running. A recommended way of ensuring this it to add a task in the Windows Task Scheduler that runs every minute of every day to run the batch file but only start if it is not already running.</b>

<p align="center">
  <img src="/images/run%20server.png">
</p>

<b>IMPORTANT: When you wish to stop the server, <u>you MUST click the shortcut ctrl+c</u> in the server window to see the confirmation that the server is stopped before closing the window. Make sure to NOT close the server while anything is running. Sometimes you need to click the shortcut a couple of times before it is registered by the server.</b>

<p align="center">
  <img src="/images/close%20server.png">
</p>

You are now ready to access the Automation Orchestrator via a browser and get started. To see an example of how to set it up, view the [video walkthrough](https://www.screencast.com/t/PgK9OkKpx2) of the installation and setup process.

<p align="center">
  <img src="/images/home%20page.png">
</p>

<i>More documentation is underway...</i>
