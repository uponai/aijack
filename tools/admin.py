from django.contrib import admin
from .models import Category, Profession, Tag, Tool, ToolTranslation, ToolStack, ToolMedia, SavedTool, SearchQuery, AffiliateClick


class ToolTranslationInline(admin.TabularInline):
    model = ToolTranslation
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'parent']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    fieldsets = (
        ('General', {
            'fields': ('name', 'slug', 'icon', 'parent')
        }),
        ('SEO Metadata', {
            'fields': ('meta_title', 'meta_description', 'og_image', 'canonical_url'),
            'classes': ('collapse',),
        }),
    )


@admin.register(Profession)
class ProfessionAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'hero_tagline']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    fieldsets = (
        ('General', {
            'fields': ('name', 'slug', 'icon', 'hero_tagline', 'description')
        }),
        ('SEO Metadata', {
            'fields': ('meta_title', 'meta_description', 'og_image', 'canonical_url'),
            'classes': ('collapse',),
        }),
    )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Tool)
class ToolAdmin(admin.ModelAdmin):
    list_display = ['name', 'pricing_type', 'status', 'is_featured', 'highlight_start', 'highlight_end', 'created_at']
    list_filter = ['status', 'pricing_type', 'is_featured', 'highlight_start', 'highlight_end', 'professions']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    filter_horizontal = ['categories', 'professions', 'tags']
    inlines = [ToolTranslationInline]
    fieldsets = (
        ('General', {
            'fields': ('name', 'slug', 'status', 'is_featured', 'logo')
        }),
        ('Links', {
            'fields': ('website_url', 'affiliate_url')
        }),
        ('Highlight Period', {
            'fields': ('highlight_start', 'highlight_end'),
            'description': 'Set date range when this tool should be highlighted on the homepage',
        }),
        ('Classification', {
            'fields': ('pricing_type', 'categories', 'professions', 'tags')
        }),
        ('SEO Metadata', {
            'fields': ('meta_title', 'meta_description', 'og_image', 'canonical_url'),
            'classes': ('collapse',),
        }),
    )


@admin.register(ToolStack)
class ToolStackAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'visibility', 'tagline', 'is_featured', 'highlight_start', 'highlight_end', 'created_at']
    list_filter = ['is_featured', 'visibility', 'highlight_start', 'highlight_end', 'professions']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ['tools', 'professions']
    raw_id_fields = ['owner']
    fieldsets = (
        ('General', {
            'fields': ('name', 'slug', 'owner', 'visibility', 'tagline', 'description', 'workflow_description', 'is_featured')
        }),
        ('Highlight Period', {
            'fields': ('highlight_start', 'highlight_end'),
            'description': 'Set date range when this stack should be highlighted on the homepage',
        }),
        ('Relations', {
            'fields': ('tools', 'professions')
        }),
        ('SEO Metadata', {
            'fields': ('meta_title', 'meta_description', 'og_image', 'canonical_url'),
            'classes': ('collapse',),
        }),
    )


class ToolMediaInline(admin.TabularInline):
    model = ToolMedia
    extra = 1


@admin.register(ToolMedia)
class ToolMediaAdmin(admin.ModelAdmin):
    list_display = ['tool', 'media_type', 'alt_text', 'order', 'created_at']
    list_filter = ['media_type', 'created_at']
    search_fields = ['tool__name', 'alt_text', 'caption']
    ordering = ['tool', 'order']


@admin.register(SavedTool)
class SavedToolAdmin(admin.ModelAdmin):
    list_display = ['user', 'tool', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'tool__name']
    raw_id_fields = ['user', 'tool']


@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = ['query', 'user', 'results_count', 'clicked_tool', 'created_at']
    list_filter = ['created_at', 'source_page']
    search_fields = ['query', 'user__username']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'


@admin.register(AffiliateClick)
class AffiliateClickAdmin(admin.ModelAdmin):
    list_display = ['tool', 'user', 'source_page', 'converted', 'conversion_value', 'clicked_at']
    list_filter = ['converted', 'clicked_at', 'tool']
    search_fields = ['tool__name', 'user__username', 'source_page']
    readonly_fields = ['clicked_at']
    date_hierarchy = 'clicked_at'

