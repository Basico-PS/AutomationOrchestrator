from .models import Botflow, Execution, SmtpAccount
from django.dispatch import receiver
from django.db.models.signals import post_save
import smtplib
from email.message import EmailMessage
from email.mime.text import MIMEText


@receiver(post_save, sender=Execution)
def save_execution(sender, instance, **kwargs):
    smtp_account = SmtpAccount.objects.filter(activated=True)[0]
    
    if instance.status == "Pending":
        if instance.queued_notification == True:
            subject = f"[{instance.pk}] Botflow queued: '{instance.botflow}'"
        else:
            return
        
    elif instance.status == "Running":
        if instance.started_notification == True:
            subject = f"[{instance.pk}] Botflow started: '{instance.botflow}'"
        else:
            return
        
    elif instance.status == "Completed":
        if instance.completed_notification == True:
            subject = f"[{instance.pk}] Botflow completed: '{instance.botflow}'"
        else:
            return
        
    elif "ERROR" in instance.status.upper():
        if instance.error_notification == True:
            subject = f"[{instance.pk}] Botflow failed: '{instance.botflow}'"
        else:
            return
        
    else:
        if instance.error_notification == True:
            subject = f"[{instance.pk}] UNKNOWN STATUS"
        else:
            return
    
    try:
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = smtp_account.email
        msg['To'] = smtp_account.email
        
        msg.set_content(f"Application: {instance.app}\nBotflow: {instance.botflow}\nTrigger: {instance.trigger}\n\nComputer Name: {instance.computer_name}\nUsername: {instance.user_name}\n\nStatus: {instance.status}\n\nTime Start: {instance.time_start}\nTime End: {instance.time_end}")

        with smtplib.SMTP(smtp_account.server, smtp_account.port) as server:
            if smtp_account.tls == True:
                server.starttls()
            server.login(smtp_account.email, smtp_account.password)
            server.send_message(msg)
            
    except:
        pass
