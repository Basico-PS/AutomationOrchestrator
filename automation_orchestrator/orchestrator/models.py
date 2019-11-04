from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import os


def get_computer_name():
    return os.environ['COMPUTERNAME']


def get_user_name():
    return os.environ['USERNAME']


class App(models.Model):
    name = models.CharField(max_length=255)
    path = models.CharField(max_length=255)

    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(auto_now=True, editable=False)
    
    def __str__(self):
        return self.name


class Botflow(models.Model):    
    name = models.CharField(max_length=255)
    path = models.CharField(max_length=255)
    queue_if_already_running = models.BooleanField(default=True)
    
    close_bot_automatically = models.BooleanField(default=False)
    
    timeout_minutes = models.PositiveIntegerField(default=60, validators=[MinValueValidator(1)])
    timeout_kill_processes = models.CharField(max_length=255, blank=True)

    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(auto_now=True, editable=False)
    
    def __str__(self):
        return self.name


class FileTrigger(models.Model):
    app = models.ForeignKey(App, on_delete=models.CASCADE)
    botflow = models.ForeignKey(Botflow, on_delete=models.CASCADE)
    
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
