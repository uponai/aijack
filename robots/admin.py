"""
Django Admin registration for robots app.
"""

from django.contrib import admin
from .models import RobotCompany, Robot, RobotNews, RobotView, SavedRobot


@admin.register(RobotCompany)
class RobotCompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'headquarters', 'founded_year', 'robot_count', 'created_at']
    search_fields = ['name', 'description', 'headquarters']
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ['founded_year']


@admin.register(Robot)
class RobotAdmin(admin.ModelAdmin):
    list_display = ['name', 'company', 'robot_type', 'target_market', 'availability', 'status', 'is_featured', 'created_at']
    list_filter = ['status', 'robot_type', 'target_market', 'availability', 'is_featured', 'company']
    search_fields = ['name', 'short_description', 'company__name']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ['compatible_tools']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'slug', 'company', 'product_url', 'image')
        }),
        ('Classification', {
            'fields': ('robot_type', 'target_market')
        }),
        ('Release & Pricing', {
            'fields': ('release_date', 'availability', 'pricing_tier', 'price_value')
        }),
        ('Content', {
            'fields': ('short_description', 'long_description', 'pros', 'cons', 'use_cases')
        }),
        ('Technical', {
            'fields': ('specifications',)
        }),
        ('Integrations', {
            'fields': ('compatible_tools',)
        }),
        ('Status', {
            'fields': ('status', 'is_featured')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'og_image', 'canonical_url'),
            'classes': ('collapse',)
        }),
    )


@admin.register(RobotNews)
class RobotNewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'published_at', 'is_published', 'is_featured', 'created_at']
    list_filter = ['is_published', 'is_featured', 'published_at']
    search_fields = ['title', 'content', 'excerpt']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['robots']
    
    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'excerpt', 'content')
        }),
        ('Media', {
            'fields': ('featured_image',)
        }),
        ('Relationships', {
            'fields': ('robots',)
        }),
        ('Source', {
            'fields': ('source_name', 'source_url')
        }),
        ('Publishing', {
            'fields': ('published_at', 'is_published', 'is_featured')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'og_image', 'canonical_url'),
            'classes': ('collapse',)
        }),
    )


@admin.register(RobotView)
class RobotViewAdmin(admin.ModelAdmin):
    list_display = ['robot', 'user', 'source_page', 'created_at']
    list_filter = ['source_page', 'created_at']
    search_fields = ['robot__name', 'user__username']
    readonly_fields = ['robot', 'user', 'session_key', 'source_page', 'ip_hash', 'created_at']


@admin.register(SavedRobot)
class SavedRobotAdmin(admin.ModelAdmin):
    list_display = ['user', 'robot', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'robot__name']
    readonly_fields = ['user', 'robot', 'created_at']
