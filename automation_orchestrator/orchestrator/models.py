import os
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from fernet_fields import EncryptedCharField, EncryptedTextField
from simple_history.models import HistoricalRecords


def get_computer_name():
    computer_name = os.environ['COMPUTERNAME']
    user_name = os.environ['USERNAME']

    if not Bot.objects.filter(computer_name=computer_name).filter(user_name=user_name).exists():
        return computer_name
    else:
        return ""


def get_user_name():
    computer_name = os.environ['COMPUTERNAME']
    user_name = os.environ['USERNAME']

    if not Bot.objects.filter(computer_name=computer_name).filter(user_name=user_name).exists():
        return user_name
    else:
        return ""


def python_function_default_code():
    return """## This is some descriptive code to help you use the Python function.
## Simple calculation example :
# x = int(input)
# y = 5
# output = x * 5
## The returned response for this function will be:
# '{"output": X}'
## -----------------------------------------------------------------------------------------------------------
## Simple SMTP example:
# from smtplib import SMTP, SMTP_SSL
# from email.message import EmailMessage
# msg = EmailMessage()
# msg['Subject'] = "Testing SMTP"
# msg['From'] = input
# msg['To'] = input
# with SMTP("smtp.office365.com", 587) as server:
#   server.starttls()
#   server.login(input, encrypted_value_1)
#   server.send_message(msg)
# output = "Email sent successfully!"
## The returned response for this function will be:
# '{"output": "Email sent successfully!"}'"""


class Bot(models.Model):
    name = models.CharField(max_length=255, unique=True, help_text="Specify the name of the bot.")
    computer_name = models.CharField(max_length=255, default=get_computer_name, help_text="Specify the computer name of the bot.")
    user_name = models.CharField(max_length=255, default=get_user_name, help_text="Specify the username of the bot.")

    nintex_rpa_license_path = models.CharField(max_length=255, default="", verbose_name="License path", blank=True, help_text="Specify the Nintex RPA license path of the bot. If the field is blank there will be no check to ensure the availability of licenses. IMPORTANT: Only applies to the Concurrent Edition license model.")
    nintex_rpa_available_foxtrot_licenses = models.PositiveIntegerField(default=0, verbose_name="Available Foxtrot licenses", help_text="Specify the total number of available Foxtrot licenses in the path. IMPORTANT: Only applies to the Concurrent Edition license model.")
    nintex_rpa_available_foxbot_licenses = models.PositiveIntegerField(default=0, verbose_name="Available FoxBot licenses", help_text="Specify the total number of available FoxBot licenses in the path. IMPORTANT: Only applies to the Concurrent Edition license model.")

    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(auto_now=True, editable=False)

    history = HistoricalRecords()

    def __str__(self):
        return self.name

    def clean(self):
        if Bot.objects.filter(computer_name=self.computer_name).filter(user_name=self.user_name).exclude(id=self.id).exists():
            raise ValidationError('A bot with the same computer name and username already exists!')


class App(models.Model):
    name = models.CharField(max_length=255, unique=True, help_text="Specify the name of the application.")
    path = models.CharField(max_length=255, help_text="Specify the path to the application.")

    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(auto_now=True, editable=False)

    history = HistoricalRecords()

    def __str__(self):
        return self.name


class Botflow(models.Model):
    name = models.CharField(max_length=255, unique=True, help_text="Specify the name of the botflow/script/file.")
    path = models.CharField(max_length=255, help_text="Specify the path to the botflow/script/file.")
    queue_if_already_running = models.BooleanField(default=True, help_text="Specify whether the botflow should be added to the queue if this botflow is already in the queue as either 'Pending' or 'Running'.")

    priority = models.PositiveIntegerField(default=3, validators=[MinValueValidator(1), MaxValueValidator(5)], help_text="Specify the priority of the triggered botflow (1 is highest, 5 is lowest). The triggered botflow with the highest priority will always run first.")

    timeout_minutes = models.PositiveIntegerField(default=300, validators=[MinValueValidator(1)], help_text="Specify after how many minutes the botflow process should be forcibly killed.")
    timeout_kill_processes = models.CharField(max_length=255, blank=True, help_text="Specify any additional processes that should be killed in the event of a timeout. To specify multiple processes, use comma to separate them like this: 'iexplore.exe, explorer.exe'.")

    queued_notification = models.CharField(max_length=255, blank=True, help_text="Specify who (if any) should receive an email notification when the botflow is queued. To specify multiple emails, use comma to separate them like this: 'abc@basico.dk, xyz@basico.dk'.")
    started_notification = models.CharField(max_length=255, blank=True, help_text="Specify who (if any) should receive an email notification when the botflow is started. To specify multiple emails, use comma to separate them like this: 'abc@basico.dk, xyz@basico.dk'.")
    completed_notification = models.CharField(max_length=255, blank=True, help_text="Specify who (if any) should receive an email notification when the botflow is completed. To specify multiple emails, use comma to separate them like this: 'abc@basico.dk, xyz@basico.dk'.")
    error_notification = models.CharField(max_length=255, blank=True, help_text="Specify who (if any) should receive an email notification when the botflow fails. To specify multiple emails, use comma to separate them like this: 'abc@basico.dk, xyz@basico.dk'. IMPORTANT: This will not include errors during the execution of the botflow.")

    close_bot_automatically = models.BooleanField(default=False, help_text="Specify whether to automatically close the bot using the /Close /Exit commands. IMPORTANT: This is a Nintex RPA specific setting.")

    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(auto_now=True, editable=False)

    history = HistoricalRecords()

    def __str__(self):
        return self.name


class FileTrigger(models.Model):
    bot = models.ForeignKey(Bot, on_delete=models.PROTECT, help_text="Select the bot for this trigger.")
    app = models.ForeignKey(App, on_delete=models.PROTECT, help_text="Select the application for this trigger.")
    botflow = models.ForeignKey(Botflow, on_delete=models.PROTECT, help_text="Select the botflow for this trigger.")

    folder_in = models.CharField(max_length=255, help_text="Specify the folder for incoming files. When a file is detected in this folder, the trigger will be activated.")
    folder_out = models.CharField(max_length=255, help_text="Specify the folder that the files should be moved to. When the trigger is activated, the file will be moved to this folder.")
    filter = models.CharField(max_length=255, default="*", help_text="Specify any filter to only trigger on certain files. The default value '*' means all files. To specify multiple filters, use comma to separate them like this: '*.txt, *.pdf'.")

    activated = models.BooleanField(default=False, help_text="Specify whether the trigger should be active.")

    run_after = models.TimeField(null=True, blank=True, help_text="Specify a time to limit the trigger to only be active after this time.")
    run_until = models.TimeField(null=True, blank=True, help_text="Specify a time to limit the trigger to only be active before this time.")
    run_on_week_days = models.BooleanField(default=True, help_text="Specify whether the trigger should be active on week days.")
    run_on_weekend_days = models.BooleanField(default=True, help_text="Specify whether the trigger should be active on weekend days.")

    status = models.CharField(max_length=255, default="Working", editable=False, help_text="Indicates the status of the trigger.")

    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(auto_now=True, editable=False)

    history = HistoricalRecords()

    def clean(self):
        if self.folder_in == self.folder_out:
            raise ValidationError('The incoming and outgoing folders cannot be the same!')


class ScheduleTrigger(models.Model):
    bot = models.ForeignKey(Bot, on_delete=models.PROTECT, help_text="Select the bot for this trigger.")
    app = models.ForeignKey(App, on_delete=models.PROTECT, help_text="Select the application for this trigger.")
    botflow = models.ForeignKey(Botflow, on_delete=models.PROTECT, help_text="Select the botflow for this trigger.")

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

    status = models.CharField(max_length=255, default="Working", editable=False, help_text="Indicates the status of the trigger.")

    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(auto_now=True, editable=False)

    history = HistoricalRecords()


class EmailImapTrigger(models.Model):
    bot = models.ForeignKey(Bot, on_delete=models.PROTECT, help_text="Select the bot for this trigger.")
    app = models.ForeignKey(App, on_delete=models.PROTECT, help_text="Select the application for this trigger.")
    botflow = models.ForeignKey(Botflow, on_delete=models.PROTECT, help_text="Select the botflow for this trigger.")

    email = models.EmailField(help_text="Specify the email of the IMAP account.")
    password = EncryptedCharField(max_length=255, help_text="Specify the password of the IMAP account.")
    server = models.CharField(max_length=255, help_text="Specify the server of the IMAP account. For example: outlook.office365.com")
    port = models.PositiveIntegerField(help_text="Specify the port of the IMAP account. For example: 993")
    tls = models.BooleanField("SSL/TLS", default=True, help_text="Specify whether the IMAP account requires 'SSL/TLS'.")

    folder_in = models.CharField(max_length=255, help_text="Specify the folder for incoming emails. When an email is detected in this folder, the trigger will be activated. The folder must be in the 'INBOX'. To specify subfolders, use slash to separate the folder names like this: Invoices/Incoming")
    folder_out = models.CharField(max_length=255, help_text="Specify the folder that the emails should be moved to. When the trigger is activated, the email will be moved to this folder. The folder must be in the 'INBOX'. To specify subfolders, use slash to separate the folder names like this: Invoices/Incoming/Handled")

    activated = models.BooleanField(default=False, help_text="Specify whether the trigger should be active.")

    run_after = models.TimeField(null=True, blank=True, help_text="Specify a time to limit the trigger to only be active after this time.")
    run_until = models.TimeField(null=True, blank=True, help_text="Specify a time to limit the trigger to only be active before this time.")
    run_on_week_days = models.BooleanField(default=True, help_text="Specify whether the trigger should be active on week days.")
    run_on_weekend_days = models.BooleanField(default=True, help_text="Specify whether the trigger should be active on weekend days.")

    status = models.CharField(max_length=255, default="Working", editable=False, help_text="Indicates the status of the trigger.")

    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(auto_now=True, editable=False)

    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Email IMAP trigger'
        verbose_name_plural = 'Email IMAP triggers'

    def clean(self):
        if self.folder_in == self.folder_out:
            raise ValidationError('The incoming and outgoing folders cannot be the same!')


class EmailOutlookTrigger(models.Model):
    bot = models.ForeignKey(Bot, on_delete=models.PROTECT, help_text="Select the bot for this trigger.")
    app = models.ForeignKey(App, on_delete=models.PROTECT, help_text="Select the application for this trigger.")
    botflow = models.ForeignKey(Botflow, on_delete=models.PROTECT, help_text="Select the botflow for this trigger.")

    email = models.CharField(max_length=255, default="Default", help_text="Specify the email of the account to monitor. IMPORTANT: If you wish to monitor the primary Outlook account, the email should be set to 'Default'.")

    folder_in = models.CharField(max_length=255, help_text="Specify the folder for incoming emails. When an email is detected in this folder, the trigger will be activated. The folder must be in the 'INBOX'. To specify subfolders, use slash to separate the folder names like this: Invoices/Incoming")
    folder_out = models.CharField(max_length=255, help_text="Specify the folder that the emails should be moved to. When the trigger is activated, the email will be moved to this folder. The folder must be in the 'INBOX'. To specify subfolders, use slash to separate the folder names like this: Invoices/Incoming/Handled")

    activated = models.BooleanField(default=False, help_text="Specify whether the trigger should be active.")

    run_after = models.TimeField(null=True, blank=True, help_text="Specify a time to limit the trigger to only be active after this time.")
    run_until = models.TimeField(null=True, blank=True, help_text="Specify a time to limit the trigger to only be active before this time.")
    run_on_week_days = models.BooleanField(default=True, help_text="Specify whether the trigger should be active on week days.")
    run_on_weekend_days = models.BooleanField(default=True, help_text="Specify whether the trigger should be active on weekend days.")

    status = models.CharField(max_length=255, default="Working", editable=False, help_text="Indicates the status of the trigger.")

    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(auto_now=True, editable=False)

    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Email Outlook trigger'
        verbose_name_plural = 'Email Outlook triggers'

    def clean(self):
        if self.folder_in == self.folder_out:
            raise ValidationError('The incoming and outgoing folders cannot be the same!')


class ApiTrigger(models.Model):
    bot = models.ForeignKey(Bot, on_delete=models.PROTECT, help_text="Select the bot for this trigger.")
    app = models.ForeignKey(App, on_delete=models.PROTECT, help_text="Select the application for this trigger.")
    botflow = models.ForeignKey(Botflow, on_delete=models.PROTECT, help_text="Select the botflow for this trigger.")

    activated = models.BooleanField(default=False, help_text="Specify whether the trigger should be active.")

    status = models.CharField(max_length=255, default="Working", editable=False, help_text="Indicates the status of the trigger.")

    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(auto_now=True, editable=False)

    history = HistoricalRecords()

    class Meta:
        verbose_name = 'API trigger'
        verbose_name_plural = 'API triggers'


class BotflowExecution(models.Model):
    time_queued = models.DateTimeField(auto_now_add=True)

    app = models.CharField(max_length=255)
    botflow = models.CharField(max_length=255)
    trigger = models.CharField(max_length=255)

    computer_name = models.CharField(max_length=255)
    user_name = models.CharField(max_length=255)
    priority = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    status = models.CharField(max_length=255)

    timeout_minutes = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    timeout_kill_processes = models.CharField(max_length=255, blank=True)

    queued_notification = models.CharField(max_length=255, blank=True)
    started_notification = models.CharField(max_length=255, blank=True)
    completed_notification = models.CharField(max_length=255, blank=True)
    error_notification = models.CharField(max_length=255, blank=True)

    close_bot_automatically = models.BooleanField(default=False)

    nintex_rpa_license_path = models.CharField(max_length=255)
    nintex_rpa_available_foxtrot_licenses = models.PositiveIntegerField()
    nintex_rpa_available_foxbot_licenses = models.PositiveIntegerField()

    time_start = models.DateTimeField(null=True, blank=True)
    time_end = models.DateTimeField(null=True, blank=True)

    # Intentionally not adding 'history = HistoricalRecords()' to this model.


class SmtpAccount(models.Model):
    email = models.EmailField(unique=True, help_text="Specify the email of the SMTP account.")
    password = EncryptedCharField(max_length=255, help_text="Specify the password of the SMTP account.")
    server = models.CharField(max_length=255, help_text="Specify the server of the SMTP account. For example: smtp.office365.com")
    port = models.PositiveIntegerField(help_text="Specify the port of the SMTP account. For example: 587")
    tls = models.BooleanField("SSL/TLS", default=True, help_text="Specify whether the SMTP account requires 'SSL/TLS'.")
    activated = models.BooleanField(default=False, help_text="Specify whether the SMTP account should be active.")

    status = models.CharField(max_length=255, default="Working", editable=False, help_text="Indicates the status of the SMTP account.")

    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(auto_now=True, editable=False)

    history = HistoricalRecords()

    class Meta:
        verbose_name = 'SMTP account'
        verbose_name_plural = 'SMTP accounts'

    def __str__(self):
        return self.email

    def clean(self):
        if self.activated and SmtpAccount.objects.filter(activated=True).exclude(id=self.id).exists():
            raise ValidationError('An activated SMTP account already exists! Make sure to not activate this account or deactivate the activated account.')


class PythonFunction(models.Model):
    name = models.CharField(max_length=255, unique=True, help_text="Specify the name of the Python function.")
    description = EncryptedTextField(help_text="Specify a description of the Python function.")

    encrypted_value_1 = EncryptedCharField(max_length=255, blank=True, help_text="Specify an optional encrypted value to use in the Python function. To retrieve the value in the code, reference the 'encrypted_value_1' variable.")
    encrypted_value_2 = EncryptedCharField(max_length=255, blank=True, help_text="Specify an optional encrypted value to use in the Python function. To retrieve the value in the code, reference the 'encrypted_value_2' variable.")
    encrypted_value_3 = EncryptedCharField(max_length=255, blank=True, help_text="Specify an optional encrypted value to use in the Python function. To retrieve the value in the code, reference the 'encrypted_value_3' variable.")
    encrypted_value_4 = EncryptedCharField(max_length=255, blank=True, help_text="Specify an optional encrypted value to use in the Python function. To retrieve the value in the code, reference the 'encrypted_value_4' variable.")
    encrypted_value_5 = EncryptedCharField(max_length=255, blank=True, help_text="Specify an optional encrypted value to use in the Python function. To retrieve the value in the code, reference the 'encrypted_value_5' variable.")

    code = EncryptedTextField(default=python_function_default_code(), help_text="Specify the code of the Python function. To retrieve the input served by the API call, reference the 'input' variable. The value of the variable 'output' will be returned in the API response.")

    activated = models.BooleanField(default=False, help_text="Specify whether the trigger should be active.")

    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(auto_now=True, editable=False)

    history = HistoricalRecords()

    def __str__(self):
        return self.name


class PythonFunctionExecution(models.Model):
    python_function = models.ForeignKey(PythonFunction, null=True, on_delete=models.SET_NULL)
    request_user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    request_ip = EncryptedCharField(max_length=255)

    input = EncryptedTextField()
    output = EncryptedTextField()
    code = EncryptedTextField()

    time_start = models.DateTimeField(null=True, blank=True)
    time_end = models.DateTimeField(null=True, blank=True)

    # Intentionally not adding 'history = HistoricalRecords()' to this model.
