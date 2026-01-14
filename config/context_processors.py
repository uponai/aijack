from django.conf import settings

def global_settings(request):
    """
    Expose global settings to all templates.
    """
    return {
        'site_host': settings.SITE_HOST,
        'support_email': settings.SUPPORT_EMAIL,
    }
