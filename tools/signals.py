from allauth.account.signals import email_confirmed
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.conf import settings

@receiver(email_confirmed)
def send_welcome_email(request, email_address, **kwargs):
    """
    Sent when an email address has been confirmed.
    """
    try:
        user_email = email_address.email
        
        subject = "Welcome to AIJACK! 🚀"
        text_content = "Welcome to AIJACK! Your email has been verified. You can now access all features."
        html_content = get_template('emails/welcome_email.html').render({'email': user_email})
        
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user_email],
            bcc=["support@growiumagent.com"] # BCC support
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        
    except Exception as e:
        print(f"Error sending welcome email: {e}")
