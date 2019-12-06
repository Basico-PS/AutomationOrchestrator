from .models import Botflow, Execution, SmtpAccount
from django.dispatch import receiver
from django.db.models.signals import post_save
import smtplib
from email.message import EmailMessage
from email.mime.text import MIMEText


@receiver(post_save, sender=Execution)
def execution_notification(sender, instance, **kwargs):
    try:
        smtp_account = SmtpAccount.objects.filter(activated=True)[0]
    except:
        return
    
    if instance.status == "Pending":
        if "@" in instance.queued_notification:
            subject = f"[{instance.pk}] Botflow queued: '{instance.botflow}'"
            to = [email.strip() for email in instance.queued_notification.split(",") if "@" in email]
        else:
            return
        
    elif instance.status == "Running":
        if "@" in instance.started_notification:
            subject = f"[{instance.pk}] Botflow started: '{instance.botflow}'"
            to = [email.strip() for email in instance.started_notification.split(",") if "@" in email]
        else:
            return
        
    elif instance.status == "Completed":
        if "@" in instance.completed_notification:
            subject = f"[{instance.pk}] Botflow completed: '{instance.botflow}'"
            to = [email.strip() for email in instance.completed_notification.split(",") if "@" in email]
        else:
            return
        
    elif "ERROR" in instance.status.upper():
        if "@" in instance.error_notification:
            subject = f"[{instance.pk}] Botflow failed: '{instance.botflow}'"
            to = [email.strip() for email in instance.error_notification.split(",") if "@" in email]
        else:
            return
        
    else:
        if "@" in instance.error_notification:
            subject = f"[{instance.pk}] UNKNOWN STATUS"
            to = [email.strip() for email in instance.error_notification.split(",") if "@" in email]
        else:
            return
    
    try:
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = smtp_account.email
        
        if not smtp_account.email in to:
            to.append(smtp_account.email)
        
        msg['To'] = ", ".join(to)
        
        msg.set_content(f"Application: {instance.app}\nBotflow: {instance.botflow}\nTrigger: {instance.trigger}\n\nComputer Name: {instance.computer_name}\nUsername: {instance.user_name}\n\nStatus: {instance.status}\n\nTime Start: {instance.time_start}\nTime End: {instance.time_end}")

        with smtplib.SMTP(smtp_account.server, smtp_account.port) as server:
            if smtp_account.tls == True:
                server.starttls()
            server.login(smtp_account.email, smtp_account.password)
            server.send_message(msg)
            
    except:
        pass
