"""
Signals for the robots app.
Auto-index robots in ChromaDB when saved/deleted.
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Robot


@receiver(post_save, sender=Robot)
def index_robot_on_save(sender, instance, **kwargs):
    """Add or remove robot from search index based on status."""
    try:
        from .search import RobotSearchService
        
        if instance.status == 'published':
            RobotSearchService.add_robots([instance])
        else:
            RobotSearchService.remove_robots([instance])
    except Exception:
        # Silently fail if search service is not available
        pass


@receiver(post_delete, sender=Robot)
def remove_robot_on_delete(sender, instance, **kwargs):
    """Remove robot from search index when deleted."""
    try:
        from .search import RobotSearchService
        RobotSearchService.remove_robots([instance])
    except Exception:
        # Silently fail if search service is not available
        pass
