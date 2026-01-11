from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Tool, Profession, ToolStack, Category

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return ['home', 'professions', 'stacks', 'search']

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

    def location(self, obj):
        return f"/profession/{obj.slug}/"

class StackSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return ToolStack.objects.all()

    def lastmod(self, obj):
        return obj.created_at

    def location(self, obj):
        return f"/stacks/{obj.slug}/"
