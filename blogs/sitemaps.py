from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import BlogPost

class BlogSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7
    protocol = "https"

    def items(self):
        return BlogPost.objects.filter(is_published=True).order_by('-created_at')

    def lastmod(self, obj):
        return obj.updated_at
