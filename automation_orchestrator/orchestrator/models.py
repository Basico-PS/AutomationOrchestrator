from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import os


def get_computer_name():
    return os.environ['COMPUTERNAME']


def get_user_name():
    return os.environ['USERNAME']


class App(models.Model):
    name = models.CharField(max_length=255, help_text="Specify the name of the application.")
    path = models.CharField(max_length=255, help_text="Specify the path to the application. IMPORTANT: Make sure to NOT include quotes.")

    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(auto_now=True, editable=False)
    
    def __str__(self):
        return self.name


class Botflow(models.Model):    
    name = models.CharField(max_length=255, help_text="Specify the name of the botflow/script/file.")
    path = models.CharField(max_length=255, help_text="Specify the path to the botflow/script/file. IMPORTANT: Make sure to NOT include quotes.")
    queue_if_already_running = models.BooleanField(default=True, help_text="Specify whether a new record should be added to the queue when a record with this botflow is already in the queue either 'Pending' or 'Running'.")
    
    close_bot_automatically = models.BooleanField(default=False, help_text="(Nintex RPA specific setting) Specify whether to automatically close the bot using the /Close /Exit commands.")
    
    timeout_minutes = models.PositiveIntegerField(default=60, validators=[MinValueValidator(1)], help_text="Specify after how many minutes the botflow should be forcibly killed.")
    timeout_kill_processes = models.CharField(max_length=255, blank=True, help_text="Specify any additional applications that should be killed in the event of a timeout. To specify multiple, use comma to separate them like this: 'iexplore.exe, explorer.exe'.")

    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(auto_now=True, editable=False)
    
    def __str__(self):
        return self.name


class FileTrigger(models.Model):
    app = models.ForeignKey(App, on_delete=models.CASCADE, help_text="Select the application for this trigger.")
    botflow = models.ForeignKey(Botflow, on_delete=models.CASCADE, help_text="Select the botflow for this trigger.")
    
    folder_in = models.CharField(max_length=255, help_text="Specify the folder for incoming files. When a file is detected in this folder, the trigger will be activated.")
    folder_out = models.CharField(max_length=255, help_text="Specify the folder for the files to be moved to. When the trigger is activated, the file will be moved to this folder.")
    
    run_after = models.TimeField(null=True, blank=True, help_text="Specify a time to limit the trigger to only be active after this time.")
    run_until = models.TimeField(null=True, blank=True, help_text="Specify a time to limit the trigger to only be active before this time.")
    run_on_week_days = models.BooleanField(default=True, help_text="Specify whether the trigger should be active on week days.")
    run_on_weekend_days = models.BooleanField(default=True, help_text="Specify whether the trigger should be active on weekend days.")
    
    computer_name = models.CharField(max_length=255, default=get_computer_name, help_text="Specify on which computer the triggered botflow should run.")
    user_name = models.CharField(max_length=255, default=get_user_name, help_text="Specify on which user the triggered botflow should run.")
    priority = models.PositiveIntegerField(default=3, validators=[MinValueValidator(1), MaxValueValidator(5)], help_text="Specify the priority of the trigger. The queued record with the highest priority will always run first.")
    activated = models.BooleanField(default=False, help_text="Specify the priority of the trigger. The queued record with the highest priority will always run first.")

    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(auto_now=True, editable=False)


class ScheduleTrigger(models.Model):
    app = models.ForeignKey(App, on_delete=models.CASCADE)
    botflow = models.ForeignKey(Botflow, on_delete=models.CASCADE)

    frequency = models.CharField(max_length=2, choices=[('MI', 'Minute'),('HO', 'Hour'),('DA', 'Day'),('WE', 'Week')])
    run_every = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    run_start = models.DateTimeField()
    
    run_after = models.TimeField(null=True, blank=True)
    run_until = models.TimeField(null=True, blank=True)
    run_on_week_days = models.BooleanField(default=True)
    run_on_weekend_days = models.BooleanField(default=True)
    
    computer_name = models.CharField(max_length=255, default=get_computer_name)
    user_name = models.CharField(max_length=255, default=get_user_name)
    priority = models.PositiveIntegerField(default=3, validators=[MinValueValidator(1), MaxValueValidator(5)])
    activated = models.BooleanField(default=False)
    
    next_execution = models.CharField(max_length=255, blank=True)
    past_settings = models.CharField(max_length=255, blank=True)

    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(auto_now=True, editable=False)


class OutlookTrigger(models.Model):
    app = models.ForeignKey(App, on_delete=models.CASCADE)
    botflow = models.ForeignKey(Botflow, on_delete=models.CASCADE)
    
    email = models.CharField(max_length=255, default="Default")
    
    folder_in = models.CharField(max_length=255)
    folder_out = models.CharField(max_length=255)
    
    run_after = models.TimeField(null=True, blank=True)
    run_until = models.TimeField(null=True, blank=True)
    run_on_week_days = models.BooleanField(default=True)
    run_on_weekend_days = models.BooleanField(default=True)
    
    computer_name = models.CharField(max_length=255, default=get_computer_name)
    user_name = models.CharField(max_length=255, default=get_user_name)
    priority = models.PositiveIntegerField(default=3, validators=[MinValueValidator(1), MaxValueValidator(5)])
    activated = models.BooleanField(default=False)

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
