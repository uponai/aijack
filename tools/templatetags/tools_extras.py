from django import template
from tools.models import SavedTool, SavedStack

register = template.Library()

@register.filter
def is_saved_by(obj, user):
    """
    Check if a tool or stack is saved by the user.
    Usage: {% if tool|is_saved_by:request.user %}
    """
    if not user.is_authenticated:
        return False
        
    # Check if obj is Tool (has pricing_type, etc) or ToolStack
    # Duck typing or isinstance
    if hasattr(obj, 'pricing_type'): # Tool
        return SavedTool.objects.filter(user=user, tool=obj).exists()
    elif hasattr(obj, 'tools'): # ToolStack (has m2m tools)
        return SavedStack.objects.filter(user=user, stack=obj).exists()
        
    return False
