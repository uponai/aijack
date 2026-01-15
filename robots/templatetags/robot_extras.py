"""
Template tags and filters for the robots app.
"""

from django import template
from ..models import SavedRobot

register = template.Library()


@register.filter
def is_robot_saved_by(robot, user):
    """Check if a robot is saved by the given user."""
    if not user or not user.is_authenticated:
        return False
    return SavedRobot.objects.filter(user=user, robot=robot).exists()


@register.filter
def get_spec(specifications, key):
    """Get a specification value from the JSON field."""
    if not specifications or not isinstance(specifications, dict):
        return '-'
    return specifications.get(key, '-')


@register.filter
def certification_label(cert_code):
    """Convert certification code to human-readable label."""
    labels = {
        'iso_10218': 'ISO 10218',
        'iso_13482': 'ISO 13482',
        'ce': 'CE Marking',
        'ul': 'UL Listed',
        'fcc': 'FCC Certified',
        'tuv': 'TÜV Certified',
        'rohs': 'RoHS Compliant',
    }
    return labels.get(cert_code, cert_code)


@register.simple_tag
def robot_comparison_count(request):
    """Get the count of robots in comparison from session."""
    comparison = request.session.get('robot_comparison', [])
    return len(comparison)


@register.simple_tag
def is_in_comparison(request, robot_id):
    """Check if a robot is in the comparison list."""
    comparison = request.session.get('robot_comparison', [])
    return robot_id in comparison
