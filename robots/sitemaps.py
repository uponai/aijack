"""
Sitemaps for the robots app.
"""

from django.contrib.sitemaps import Sitemap
from .models import Robot, RobotCompany, RobotNews


class RobotSitemap(Sitemap):
    """Sitemap for individual robot pages."""
    changefreq = 'weekly'
    priority = 0.9

    def items(self):
        return Robot.objects.filter(status='published')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return f"/robot/{obj.slug}/"


class RobotCompanySitemap(Sitemap):
    """Sitemap for robot company profile pages."""
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return RobotCompany.objects.all()

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return f"/robots/company/{obj.slug}/"


class RobotNewsSitemap(Sitemap):
    """Sitemap for robot news articles."""
    changefreq = 'daily'
    priority = 0.7

    def items(self):
        return RobotNews.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return f"/robots/news/{obj.slug}/"


class RobotStaticSitemap(Sitemap):
    """Sitemap for static robot pages."""
    priority = 0.6
    changefreq = 'weekly'

    def items(self):
        return ['robots', 'robot_companies', 'robot_comparison', 'robot_timeline', 'robot_matrix', 'robot_news']

    def location(self, item):
        locations = {
            'robots': '/robots/',
            'robot_companies': '/robots/companies/',
            'robot_comparison': '/robots/compare/',
            'robot_timeline': '/robots/timeline/',
            'robot_matrix': '/robots/matrix/',
            'robot_news': '/robots/news/',
        }
        return locations.get(item, f'/{item}/')
