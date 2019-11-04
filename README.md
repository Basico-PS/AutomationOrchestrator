# Basico P/S - Automation Orchestrator

<i>Better documentation is underway...</i>

For support, please contact us: robotics@basico.dk

This solution allows you to run a local [Django Web Application](https://www.djangoproject.com/) to administrate and orchestrate automation scripts such as Nintex RPA botflows. Feature highlights out-of-the-box:
- Groups and User Setup
- File Triggers
- Schedule Triggers
- Outlook Triggers
- Queue Functionality
- Execution Log

As described on the official Django project site, it <i>"is a high-level Python Web framework that encourages rapid development and clean, pragmatic design. Built by experienced developers, it takes care of much of the hassle of Web development, so you can focus on writing your app without needing to reinvent the wheel. It’s free and open source."</i>

Some of the biggest web platforms and brands like [Instagram and Pinterest use the Django Framework](https://www.djangoproject.com/start/overview/) due to its leading security features and ability to scale.

The purpose of this solution is to offer a well-functioning, fully customizable automation orchestrator application to trigger and schedule scripts. At this moment, the solution is only intended to work as a local automation orchestrator running on the same machine and user as where the scripts are supposed to be executed. IMPORTANT: The solution runs with the ["DEBUG" flag set to "True"](https://docs.djangoproject.com/en/2.2/ref/settings/#debug) even though it is not recommended in a cloud production environment since the solution should only be used to run fully locally or shared in your protected internal network. It is in the plans to make it possible to use the automation orchestrator as a centralized tool in your protected internal network to orchestrate scripts across machines and users, however, if you wish to deploy the solution in the open cloud, there are [many additional steps](https://docs.djangoproject.com/en/2.2/howto/deployment/) to consider and implement.

## Installation

For the solution to work, you need to install [Python](https://www.python.org/). The solution is tested with Python 3.7 and 3.8.

1. Download the [latest version](https://github.com/Basico-PS/AutomationOrchestrator/archive/v0.0.8.zip).
2. Create a folder called "Automation Orchestrator" somewhere convenient, for example, directly on the C: drive or in the "Program Files" folder.
3. Unzip the folder in your created "Automation Orchestrator" folder. So, your path could be similar to "C:\Automation Orchestrator\AutomationOrchestrator-0.0.8" or "C:\Program Files\Automation Orchestrator\AutomationOrchestrator-0.0.8". However, you may unzip the folder anywhere on your system.
4. After unzipping the folder, run the "INSTALL.bat" [file](https://github.com/Basico-PS/AutomationOrchestrator/blob/master/INSTALL.bat) for an automated installation process. You may also manually run the installation steps via, for example, the CMD. Remember to run the batch file (or commands manually) as an administrator.
5. The last command of the installation process will prompt you to create an account, a super user who has all permissions. After creating the super user, the installation process is complete.

## Usage

After a succesful installation, you can now start your local server by running the "RUN_SERVER.bat" [file](https://github.com/Basico-PS/AutomationOrchestrator/blob/master/RUN_SERVER.bat). Remember to run the batch file (or commands manually) as an administrator. As long as the server is running, you are able to locally (only on your own machine) access the Automation Orchestrator via a browser on http://127.0.0.1:8000/.

More documentation on how to set up the system and how to make the Automation Orchestrator accessible from other machines in your protected internal network is underway...
