from django.views.generic import ListView, DetailView
from django.shortcuts import render
from .models import BlogPost

class BlogListView(ListView):
    model = BlogPost
    template_name = 'blogs/blog_list.html'
    context_object_name = 'blogs'
    paginate_by = 12
    queryset = BlogPost.objects.filter(is_published=True)

    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return ['blogs/partials/blog_list_rows.html']
        return ['blogs/blog_list.html']

class BlogDetailView(DetailView):
    model = BlogPost
    template_name = 'blogs/blog_detail.html'
    context_object_name = 'blog'

    def get_queryset(self):
        return BlogPost.objects.prefetch_related('chapters', 'tags', 'tools', 'stacks', 'professions', 'robots')

from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.db.models import Q

@staff_member_required
def admin_blogs(request):
    """Admin: List and manage blog posts (stories)."""
    query = request.GET.get('q', '')
    filter_type = request.GET.get('filter', 'all')
    
    blogs = BlogPost.objects.all().order_by('-created_at')
    
    if query:
        blogs = blogs.filter(
            Q(title__icontains=query) | 
            Q(slug__icontains=query)
        ).distinct()
    
    if filter_type == 'published':
        blogs = blogs.filter(is_published=True)
    elif filter_type == 'draft':
        blogs = blogs.filter(is_published=False)
        
    paginator = Paginator(blogs, 20)
    page_number = request.GET.get('page')
    blogs_page = paginator.get_page(page_number)
    
    return render(request, 'blogs/admin/admin_blogs_list.html', {
        'blogs': blogs_page,
        'query': query,
        'filter_type': filter_type,
        'active_tab': 'blogs'
    })

from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from .forms import BlogPostForm, BlogChapterFormSet

@staff_member_required
def admin_blog_create(request):
    """Admin: Create a new blog post."""
    if request.method == 'POST':
        form = BlogPostForm(request.POST)
        formset = BlogChapterFormSet(request.POST, request.FILES)
        
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    blog = form.save()
                    chapters = formset.save(commit=False)
                    for chapter in chapters:
                        chapter.blog_post = blog
                        chapter.save()
                    # Handle deletions
                    for obj in formset.deleted_objects:
                        obj.delete()
                        
                    messages.success(request, f"Story '{blog.title}' created successfully.")
                    return redirect('admin_blogs')
            except Exception as e:
                messages.error(request, f"Error creating story: {e}")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = BlogPostForm()
        formset = BlogChapterFormSet()
    
    return render(request, 'blogs/admin/admin_blog_form.html', {
        'form': form,
        'formset': formset,
        'title': 'Create New Story',
        'back_url': 'admin_blogs'
    })

@staff_member_required
def admin_blog_edit(request, pk):
    """Admin: Edit an existing blog post."""
    blog = get_object_or_404(BlogPost, pk=pk)
    
    if request.method == 'POST':
        form = BlogPostForm(request.POST, instance=blog)
        formset = BlogChapterFormSet(request.POST, request.FILES, instance=blog)
        
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    form.save()
                    chapters = formset.save(commit=False)
                    for chapter in chapters:
                        chapter.blog_post = blog
                        chapter.save()
                    for obj in formset.deleted_objects:
                        obj.delete()
                        
                    messages.success(request, f"Story '{blog.title}' updated successfully.")
                    return redirect('admin_blogs')
            except Exception as e:
                messages.error(request, f"Error updating story: {e}")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = BlogPostForm(instance=blog)
        formset = BlogChapterFormSet(instance=blog)
    
    return render(request, 'blogs/admin/admin_blog_form.html', {
        'form': form,
        'formset': formset,
        'title': f'Edit: {blog.title}',
        'back_url': 'admin_blogs',
        'blog': blog
    })
