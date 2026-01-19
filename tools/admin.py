from django.contrib import admin
from .models import Category, Profession, Tag, Tool, ToolTranslation, ToolStack, ToolMedia, SavedTool, SavedStack, SearchQuery, AffiliateClick, NewsletterSubscriber, SubmittedTool, ToolReport


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
        ('Timestamps', {
            'fields': ('updated_at',),
            'classes': ('collapse',),
        }),
        ('SEO Metadata', {
            'fields': ('meta_title', 'meta_description', 'og_image', 'canonical_url'),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ['updated_at']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


class IncompleteToolFilter(admin.SimpleListFilter):
    title = 'Incomplete Tools'
    parameter_name = 'incomplete'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Incomplete (Missing Data / Invalid URL)'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            # This is a bit complex because we need to check multiple fields
            # We can use Q objects for OR condition
            from django.db.models import Q
            return queryset.filter(
                Q(is_website_valid=False) |
                Q(meta_description='') |
                Q(translations__short_description='') |
                Q(logo__exact='') |
                Q(categories=None) |
                Q(professions=None) |
                Q(tags=None)
            ).distinct()
        return queryset


@admin.register(Tool)
class ToolAdmin(admin.ModelAdmin):
    list_display = ['name', 'pricing_type', 'status', 'is_featured', 'is_website_valid', 'webcheck_last_run', 'highlight_start', 'highlight_end', 'created_at']
    list_filter = ['status', 'pricing_type', IncompleteToolFilter, 'is_featured', 'is_website_valid', 'highlight_start', 'highlight_end', 'professions']
    list_per_page = 100
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
        ('Webcheck Status', {
            'fields': ('is_website_valid', 'webcheck_last_run'),
            'classes': ('collapse',),
            'description': 'Website validation status - automatically updated by webcheck system',
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
        ('SEO Metadata', {
            'fields': ('meta_title', 'meta_description', 'og_image', 'canonical_url'),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ['created_at', 'updated_at']
    actions = ['reset_webcheck']

    def reset_webcheck(self, request, queryset):
        """
        Resets webcheck status and deletes auto-generated snapshots.
        """
        # 1. Delete generated media
        # We identify them by the caption "Auto-generated snapshot" used in webcheck.py
        count_media = 0
        for tool in queryset:
            media_qs = tool.media.filter(caption="Auto-generated snapshot")
            count_media += media_qs.count()
            media_qs.delete()
            
            # Reset SEO image if it was the one we generated (detected via filename pattern)
            if tool.og_image and tool.slug in tool.og_image.name and "_og.png" in tool.og_image.name:
                tool.og_image.delete(save=False)
                tool.og_image = None
                
            # Reset Logo if it was auto-generated (detected via filename pattern)
            # webcheck.py saves as f"{tool.slug}_icon.png"
            if tool.logo and tool.slug in tool.logo.name and "_icon.png" in tool.logo.name:
                tool.logo.delete(save=False)
                tool.logo = None
            
            tool.save()

        # 2. Reset flags
        updated_count = queryset.update(
            is_website_valid=None,
            webcheck_last_run=None
        )
        
        self.message_user(request, f"Reset webcheck for {updated_count} tools. Deleted {count_media} snapshots.")
    reset_webcheck.short_description = "Reset Webcheck status (clear flags & snapshots)"


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
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
        ('SEO Metadata', {
            'fields': ('meta_title', 'meta_description', 'og_image', 'canonical_url'),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ['created_at']


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


@admin.register(SavedStack)
class SavedStackAdmin(admin.ModelAdmin):
    list_display = ['user', 'stack', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'stack__name']
    raw_id_fields = ['user', 'stack']


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'created_at', 'is_active']
    list_filter = ['created_at', 'is_active']
    search_fields = ['email']
    readonly_fields = ['created_at']


@admin.register(SubmittedTool)
class SubmittedToolAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'website_url', 'created_at', 'is_approved']
    list_filter = ['created_at', 'is_approved']
    search_fields = ['name', 'user__username', 'website_url']
    actions = ['approve_tools']

    def approve_tools(self, request, queryset):
        # This action could technically move tools to the main Tool table, 
        # but for now we just mark them as approved.
        queryset.update(is_approved=True)
    approve_tools.short_description = "Mark selected tools as approved"


@admin.register(ToolReport)
class ToolReportAdmin(admin.ModelAdmin):
    list_display = ['tool', 'reason', 'user', 'is_resolved', 'created_at']
    list_filter = ['is_resolved', 'reason', 'created_at']
    search_fields = ['tool__name', 'message', 'user__username']
    actions = ['mark_as_resolved']

    def mark_as_resolved(self, request, queryset):
        queryset.update(is_resolved=True)
    mark_as_resolved.short_description = "Mark selected reports as resolved"

