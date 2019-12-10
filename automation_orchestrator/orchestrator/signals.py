from .models import Execution, SmtpAccount
from django.dispatch import receiver
from django.db.models.signals import post_save
from smtplib import SMTP, SMTP_SSL
from email.message import EmailMessage


@receiver(post_save, sender=Execution)
def execution_notification(sender, instance, **kwargs):
    try:
        smtp_account = SmtpAccount.objects.filter(activated=True)[0]
    except:
        return
    
    if instance.status == "Pending":
        if "@" in instance.queued_notification:
            email_subject = f"[{instance.pk}] Botflow queued: '{instance.botflow}'"
            email_to = [email for email in instance.queued_notification.split(",")]
        else:
            return
        
    elif instance.status == "Running":
        if "@" in instance.started_notification:
            email_subject = f"[{instance.pk}] Botflow started: '{instance.botflow}'"
            email_to = [email for email in instance.started_notification.split(",")]
        else:
            return
        
    elif instance.status == "Completed":
        if "@" in instance.completed_notification:
            email_subject = f"[{instance.pk}] Botflow completed: '{instance.botflow}'"
            email_to = [email for email in instance.completed_notification.split(",")]
        else:
            return
        
    elif "ERROR" in instance.status.upper():
        if "@" in instance.error_notification:
            email_subject = f"[{instance.pk}] Botflow failed: '{instance.botflow}'"
            email_to = [email for email in instance.error_notification.split(",")]
        else:
            return
        
    else:
        if "@" in instance.error_notification:
            email_subject = f"[{instance.pk}] UNKNOWN STATUS"
            email_to = [email for email in instance.error_notification.split(",")]
        else:
            return
    
    try:
        email_to = [str(email).lower().strip() for email in email_to if "@" in email]
        email_from = str(smtp_account.email).lower().strip()
        
        msg = EmailMessage()
        msg['Subject'] = email_subject
        msg['From'] = email_from
        
        if not email_from in email_to:
            email_to.append(email_from)
        
        msg['To'] = ", ".join(email_to)
        
        msg.set_content(f"Application: {instance.app}\nBotflow: {instance.botflow}\nTrigger: {instance.trigger}\n\nComputer Name: {instance.computer_name}\nUsername: {instance.user_name}\n\nStatus: {instance.status}\n\nTime Start: {instance.time_start}\nTime End: {instance.time_end}")

        with SMTP(smtp_account.server, smtp_account.port) as server:
            if smtp_account.tls:
                server.starttls()
            server.login(email_from, smtp_account.password)
            server.send_message(msg)
            
    except:
        if smtp_account.tls:
            try:
                msg = EmailMessage()
                msg['Subject'] = email_subject
                msg['From'] = email_from
                
                if not email_from in email_to:
                    email_to.append(email_from)
                
                msg['To'] = ", ".join(email_to)
                
                msg.set_content(f"Application: {instance.app}\nBotflow: {instance.botflow}\nTrigger: {instance.trigger}\n\nComputer Name: {instance.computer_name}\nUsername: {instance.user_name}\n\nStatus: {instance.status}\n\nTime Start: {instance.time_start}\nTime End: {instance.time_end}")
                
                with SMTP_SSL(smtp_account.server, smtp_account.port) as server:
                    server.login(email_from, smtp_account.password)
                    server.send_message(msg)
                    
            except:
                pass
