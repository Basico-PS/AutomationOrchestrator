from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import os


def get_computer_name():
    return os.environ['COMPUTERNAME']


def get_user_name():
    return os.environ['USERNAME']


class App(models.Model):
    name = models.CharField(max_length=255, help_text="Specify the name of the application.")
    path = models.CharField(max_length=255, help_text="Specify the path to the application.")

    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(auto_now=True, editable=False)
    
    def __str__(self):
        return self.name


class Botflow(models.Model):    
    name = models.CharField(max_length=255, help_text="Specify the name of the botflow/script/file.")
    path = models.CharField(max_length=255, help_text="Specify the path to the botflow/script/file.")
    queue_if_already_running = models.BooleanField(default=True, help_text="Specify whether the botflow should be added to the queue if this botflow is already in the queue as either 'Pending' or 'Running'.")
    
    computer_name = models.CharField(max_length=255, default=get_computer_name, help_text="Specify on which computer the triggered botflow should run.")
    user_name = models.CharField(max_length=255, default=get_user_name, help_text="Specify on which user the triggered botflow should run.")
    priority = models.PositiveIntegerField(default=3, validators=[MinValueValidator(1), MaxValueValidator(5)], help_text="Specify the priority of the triggered botflow (1 is highest, 5 is lowest). The triggered botflow with the highest priority will always run first.")
    
    timeout_minutes = models.PositiveIntegerField(default=300, validators=[MinValueValidator(1)], help_text="Specify after how many minutes the botflow process should be forcibly killed.")
    timeout_kill_processes = models.CharField(max_length=255, blank=True, help_text="Specify any additional processes that should be killed in the event of a timeout. To specify multiple processes, use comma to separate them like this: 'iexplore.exe, explorer.exe'.")
    
    close_bot_automatically = models.BooleanField(default=False, help_text="Specify whether to automatically close the bot using the /Close /Exit commands. IMPORTANT: This is a Nintex RPA specific setting.")

    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(auto_now=True, editable=False)
    
    def __str__(self):
        return self.name


class FileTrigger(models.Model):
    app = models.ForeignKey(App, on_delete=models.CASCADE, help_text="Select the application for this trigger.")
    botflow = models.ForeignKey(Botflow, on_delete=models.CASCADE, help_text="Select the botflow for this trigger.")
    
    folder_in = models.CharField(max_length=255, help_text="Specify the folder for incoming files. When a file is detected in this folder, the trigger will be activated.")
    folder_out = models.CharField(max_length=255, help_text="Specify the folder that the files should be moved to. When the trigger is activated, the file will be moved to this folder.")
    filter = models.CharField(max_length=255, default="*", help_text="Specify any filter to only trigger on certain files. The default value '*' means all files. To specify multiple filters, use comma to separate them like this: '*.txt, *.pdf'.")
    
    activated = models.BooleanField(default=False, help_text="Specify whether the trigger should be active.")
    
    run_after = models.TimeField(null=True, blank=True, help_text="Specify a time to limit the trigger to only be active after this time.")
    run_until = models.TimeField(null=True, blank=True, help_text="Specify a time to limit the trigger to only be active before this time.")
    run_on_week_days = models.BooleanField(default=True, help_text="Specify whether the trigger should be active on week days.")
    run_on_weekend_days = models.BooleanField(default=True, help_text="Specify whether the trigger should be active on weekend days.")

    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(auto_now=True, editable=False)


class ScheduleTrigger(models.Model):
    app = models.ForeignKey(App, on_delete=models.CASCADE, help_text="Select the application for this trigger.")
    botflow = models.ForeignKey(Botflow, on_delete=models.CASCADE, help_text="Select the botflow for this trigger.")

    frequency = models.CharField(max_length=3, choices=[('MIN', 'Minute'),('HOU', 'Hour'),('DAY', 'Day'),('WEE', 'Week'),('MON', 'Month'),
                                                        ('FWK', 'First Week Day'),('FWD', 'First Weekend Day'), ('LWK', 'Last Week Day'),('LWD', 'Last Weekend Day')], help_text="Specify the frequency of the trigger.")
    run_every = models.PositiveIntegerField(validators=[MinValueValidator(1)], help_text="Specify how often to run every minute/hour/day/week.")
    run_start = models.DateTimeField(help_text="Specify the start date and time for the trigger. This will be the starting point of the trigger.")
    
    activated = models.BooleanField(default=False, help_text="Specify whether the trigger should be active.")
    
    run_after = models.TimeField(null=True, blank=True, help_text="Specify a time to limit the trigger to only be active after this time.")
    run_until = models.TimeField(null=True, blank=True, help_text="Specify a time to limit the trigger to only be active before this time.")
    run_on_week_days = models.BooleanField(default=True, help_text="Specify whether the trigger should be active on week days.")
    run_on_weekend_days = models.BooleanField(default=True, help_text="Specify whether the trigger should be active on weekend days.")
    
    next_execution = models.CharField(max_length=255, blank=True, editable=False, help_text="This field specifies the scheduled time for the next execution. IMPORTANT: This date and time field is in UTC timezone, therefore, an offset is expected!")
    past_settings = models.CharField(max_length=255, blank=True)

    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(auto_now=True, editable=False)


class OutlookTrigger(models.Model):
    app = models.ForeignKey(App, on_delete=models.CASCADE, help_text="Select the application for this trigger.")
    botflow = models.ForeignKey(Botflow, on_delete=models.CASCADE, help_text="Select the botflow for this trigger.")
    
    email = models.CharField(max_length=255, default="Default", help_text="Specify the email of the account to monitor. IMPORTANT: If you wish to monitor the primary Outlook account, the email should be set to 'Default'.")
    
    folder_in = models.CharField(max_length=255, help_text="Specify the folder for incoming emails. When an email is detected in this folder, the trigger will be activated.")
    folder_out = models.CharField(max_length=255, help_text="Specify the folder that the emails should be moved to. When the trigger is activated, the email will be moved to this folder.")
    
    activated = models.BooleanField(default=False, help_text="Specify whether the trigger should be active.")
    
    run_after = models.TimeField(null=True, blank=True, help_text="Specify a time to limit the trigger to only be active after this time.")
    run_until = models.TimeField(null=True, blank=True, help_text="Specify a time to limit the trigger to only be active before this time.")
    run_on_week_days = models.BooleanField(default=True, help_text="Specify whether the trigger should be active on week days.")
    run_on_weekend_days = models.BooleanField(default=True, help_text="Specify whether the trigger should be active on weekend days.")

    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(auto_now=True, editable=False)


class Execution(models.Model):
    time_queued = models.DateTimeField(auto_now_add=True)
    
    app = models.CharField(max_length=255)
    botflow = models.CharField(max_length=255)
    trigger = models.CharField(max_length=255)
    
    computer_name = models.CharField(max_length=255)
    user_name = models.CharField(max_length=255)
    priority = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    status = models.CharField(max_length=255)

    close_bot_automatically = models.BooleanField(default=False)
    
    timeout_minutes = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    timeout_kill_processes = models.CharField(max_length=255, blank=True)
    
    time_start = models.DateTimeField(null=True, blank=True)
    time_end = models.DateTimeField(null=True, blank=True)
