import os
import pytz
from .models import Bot, BotflowExecution, SmtpAccount
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save
from smtplib import SMTP, SMTP_SSL
from email.message import EmailMessage
from os.path import basename
from datetime import datetime


@receiver(pre_save, sender=BotflowExecution)
def botflow_execution_update_progress(sender, instance, **kwargs):
    if instance.time_end != None:
        instance.custom_progress = 100


@receiver(post_save, sender=BotflowExecution)
def botflow_execution_bot_status(sender, instance, **kwargs):
    if instance.status == "Running":
        try:
            bot = Bot.objects.filter(computer_name__iexact=instance.computer_name, user_name__iexact=instance.user_name)[0]
        except Exception:
            return

        if bot.status != "Running":
            bot.status = "Running"
            bot.save_without_historical_record()

    elif instance.status != "Pending":
        try:
            bot = Bot.objects.filter(computer_name__iexact=instance.computer_name, user_name__iexact=instance.user_name)[0]
        except Exception:
            return

        if instance.status == "Completed":
            if bot.status != "Active":
                bot.status = "Active"
                bot.save_without_historical_record()

        else:
            latest_execution = BotflowExecution.objects.filter(status="Running", computer_name__iexact=os.environ['COMPUTERNAME'], user_name__iexact=os.environ['USERNAME']).order_by('-time_start')

            if len(latest_execution) > 0:
                latest_execution = latest_execution[0]

                difference = datetime.now(pytz.timezone('UTC')) - latest_execution.time_start
                difference = difference.seconds / 60

                if difference < latest_execution.timeout_minutes:
                    return

            if bot.status != "Unknown":
                bot.status = "Unknown"
                bot.save_without_historical_record()


@receiver(post_save, sender=BotflowExecution)
def botflow_execution_notification(sender, instance, **kwargs):
    try:
        smtp_account = SmtpAccount.objects.filter(activated=True)[0]
    except Exception:
        return

    if instance.status == "Pending":
        if "@" in instance.queued_notification:
            email_subject = f"[{instance.pk}] Botflow queued: '{basename(instance.botflow)}'"
            email_to = [
                email for email in instance.queued_notification.split(",")
            ]
        else:
            return

    elif instance.status == "Running":
        if "@" in instance.started_notification:
            email_subject = f"[{instance.pk}] Botflow started: '{basename(instance.botflow)}'"
            email_to = [
                email for email in instance.started_notification.split(",")
            ]
        else:
            return

    elif instance.status == "Completed":
        if "@" in instance.completed_notification:
            email_subject = f"[{instance.pk}] Botflow completed: '{basename(instance.botflow)}'"
            email_to = [
                email for email in instance.completed_notification.split(",")
            ]
        else:
            return

    elif "ERROR" in instance.status.upper():
        if "@" in instance.error_notification:
            email_subject = f"[{instance.pk}] Botflow failed: '{basename(instance.botflow)}'"
            email_to = [
                email for email in instance.error_notification.split(",")
            ]
        else:
            return

    else:
        if "@" in instance.error_notification:
            email_subject = f"[{instance.pk}] UNKNOWN STATUS"
            email_to = [
                email for email in instance.error_notification.split(",")
            ]
        else:
            return

    try:
        email_to = [str(email).lower().strip()
                    for email in email_to if "@" in email]
        email_from = str(smtp_account.email).lower().strip()

        msg = EmailMessage()
        msg['Subject'] = email_subject
        msg['From'] = email_from
        msg['To'] = ", ".join(email_to)

        msg.set_content(f"Application: {instance.app}\nBotflow: {instance.botflow}\nTrigger: {instance.trigger}\n\nComputer Name: {instance.computer_name}\nUsername: {instance.user_name}\n\nStatus: {instance.status}\n\nTime Start: {instance.time_start}\nTime End: {instance.time_end}")

        with SMTP(smtp_account.server, smtp_account.port) as server:
            if smtp_account.tls:
                server.starttls()
            if smtp_account.password != "":
                server.login(email_from, smtp_account.password)
            server.send_message(msg)

        if smtp_account.status != "Active":
            smtp_account.status = "Active"
            smtp_account.save_without_historical_record()

    except Exception:
        if smtp_account.tls:
            try:
                msg = EmailMessage()
                msg['Subject'] = email_subject
                msg['From'] = email_from
                msg['To'] = ", ".join(email_to)

                msg.set_content(
                    f"Application: {instance.app}\nBotflow: {instance.botflow}\nTrigger: {instance.trigger}\n\nComputer Name: {instance.computer_name}\nUsername: {instance.user_name}\n\nStatus: {instance.status}\n\nTime Start: {instance.time_start}\nTime End: {instance.time_end}"
                )

                with SMTP_SSL(smtp_account.server, smtp_account.port) as server:
                    if smtp_account.password != "":
                        server.login(email_from, smtp_account.password)
                    server.send_message(msg)

                if smtp_account.status != "Active":
                    smtp_account.status = "Active"
                    smtp_account.save_without_historical_record()

            except Exception:
                if smtp_account.status != "ERROR":
                    smtp_account.status = "ERROR"
                    smtp_account.save_without_historical_record()

        else:
            if smtp_account.status != "ERROR":
                smtp_account.status = "ERROR"
                smtp_account.save_without_historical_record()
