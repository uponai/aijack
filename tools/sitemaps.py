from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Tool, Profession, ToolStack, Category, Tag

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return [
            'home', 'browse_tools', 'submit_tool', 'professions', 'stacks', 'search',
            'account_login', 'account_signup',
            'terms', 'privacy', 'cookies',
            'ai_stack_builder'
        ]

    def location(self, item):
        return reverse(item)

class ToolSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.9

    def items(self):
        return Tool.objects.filter(status='published')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return f"/tool/{obj.slug}/"

class ProfessionSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Profession.objects.all()

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return f"/profession/{obj.slug}/"

class StackSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        # Only include public stacks in sitemap
        return ToolStack.objects.filter(visibility='public')

    def lastmod(self, obj):
        return obj.created_at

    def location(self, obj):
        return f"/stack/{obj.slug}/"

class TagSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.6

    def items(self):
        return Tag.objects.all()

    def location(self, obj):
        return f"/tag/{obj.slug}/"
