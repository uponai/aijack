from django.contrib import admin
from .models import Category, Profession, Tag, Tool, ToolTranslation, ToolStack


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
    list_display = ['name', 'pricing_type', 'status', 'is_featured', 'created_at']
    list_filter = ['status', 'pricing_type', 'is_featured', 'professions']
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
    list_display = ['name', 'tagline', 'is_featured', 'created_at']
    list_filter = ['is_featured', 'professions']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ['tools', 'professions']
    fieldsets = (
        ('General', {
            'fields': ('name', 'slug', 'tagline', 'description', 'workflow_description', 'is_featured')
        }),
        ('Relations', {
            'fields': ('tools', 'professions')
        }),
        ('SEO Metadata', {
            'fields': ('meta_title', 'meta_description', 'og_image', 'canonical_url'),
            'classes': ('collapse',),
        }),
    )
