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
        html_content = get_template('emails/welcome_email.html').render({
            'email': user_email,
            'site_host': settings.SITE_HOST
        })
        
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user_email],
            bcc=[settings.SUPPORT_EMAIL] # BCC support
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        
    except Exception as e:
        print(f"Error sending welcome email: {e}")

# --- Search Indexing Signals ---
from django.db.models.signals import post_save, post_delete
from .models import Tool, ToolStack, Profession, ToolTranslation, Tag
from .search import SearchService

@receiver(post_save, sender=Tool)
def update_tool_index(sender, instance, created, **kwargs):
    """Update or add tool to vector index on save."""
    if instance.status == 'published':
        SearchService.add_tools([instance])
    else:
        # If status changed to draft, remove it
        SearchService.remove_tools([instance])

@receiver(post_delete, sender=Tool)
def delete_tool_index(sender, instance, **kwargs):
    """Remove tool from vector index on delete."""
    SearchService.remove_tools([instance])

@receiver(post_save, sender=ToolTranslation)
def update_tool_index_from_translation(sender, instance, **kwargs):
    """Update tool index when translation changes."""
    if instance.tool.status == 'published':
        SearchService.add_tools([instance.tool])

@receiver(post_save, sender=ToolStack)
def update_stack_index(sender, instance, **kwargs):
    """Update stack index on save."""
    # Only index if it has visibility (though logic in add_stacks handles this metadata)
    # Re-indexing handles both add and update
    SearchService.add_stacks([instance])

@receiver(post_delete, sender=ToolStack)
def delete_stack_index(sender, instance, **kwargs):
    """Remove stack from index on delete."""
    SearchService.remove_stacks([instance])

@receiver(post_save, sender=Profession)
def update_profession_index(sender, instance, **kwargs):
    """Update profession index on save."""
    SearchService.add_professions([instance])

@receiver(post_delete, sender=Profession)
def delete_profession_index(sender, instance, **kwargs):
    """Remove profession from index on delete."""
    SearchService.remove_professions([instance])
