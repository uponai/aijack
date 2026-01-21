from django.contrib import admin
from .models import BlogPost, BlogChapter

class BlogChapterInline(admin.StackedInline):
    model = BlogChapter
    extra = 1

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'is_published')
    list_filter = ('is_published', 'created_at')
    search_fields = ('title', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [BlogChapterInline]
    filter_horizontal = ('tools', 'stacks', 'professions', 'robots')

@admin.register(BlogChapter)
class BlogChapterAdmin(admin.ModelAdmin):
    list_display = ('blog_post', 'order', 'image')
    list_filter = ('blog_post',)
