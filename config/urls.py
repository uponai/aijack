"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView
from tools.sitemaps import StaticViewSitemap, ToolSitemap, ProfessionSitemap, StackSitemap, TagSitemap
from robots.sitemaps import RobotSitemap, RobotCompanySitemap, RobotNewsSitemap, RobotStaticSitemap
from blogs.sitemaps import BlogSitemap

sitemaps = {
    'static': StaticViewSitemap,
    'tools': ToolSitemap,
    'professions': ProfessionSitemap,
    'stacks': StackSitemap,
    'tags': TagSitemap,
    # Robots sitemaps
    'robots': RobotSitemap,
    'robot_companies': RobotCompanySitemap,
    'robot_news': RobotNewsSitemap,
    'robot_static': RobotStaticSitemap,
    'blogs': BlogSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('tools.urls')),
    path('', include('robots.urls')),  # AI Robots app
    path('blogs/', include('blogs.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps, 'template_name': 'sitemap.xml'}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom Error Handlers
handler404 = 'tools.views.custom_404'

