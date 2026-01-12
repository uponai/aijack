from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Case, When
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
import json
from .models import Tool, Profession, Category, ToolStack, Tag, SavedTool, SavedStack
from .forms import ToolForm, ToolStackForm, ProfessionForm
from .search import SearchService
from .ai_service import AIService
from .analytics import AnalyticsService


def home(request):
    """Homepage with search and featured content."""
    from datetime import date, timedelta
    
    today = date.today()
    thirty_days_ago = today - timedelta(days=30)
    
    professions = Profession.objects.all()[:16]
    featured_stacks = ToolStack.objects.filter(is_featured=True, visibility='public')[:4]
    featured_tools = Tool.objects.filter(status='published', is_featured=True)[:6]
    
    # Global counts
    tool_count = Tool.objects.filter(status='published').count()
    stack_count = ToolStack.objects.filter(visibility='public').count()
    profession_count = Profession.objects.count()
    
    # Highlighted items (within highlight date range)
    highlighted_stacks = ToolStack.objects.filter(
        visibility='public',
        highlight_start__lte=today,
        highlight_end__gte=today
    ).order_by('-highlight_start')[:4]
    
    highlighted_tools = Tool.objects.filter(
        status='published',
        highlight_start__lte=today,
        highlight_end__gte=today
    ).prefetch_related('translations', 'tags').order_by('-highlight_start')[:6]
    
    # Newbies (created in last 30 days)
    stack_newbies = ToolStack.objects.filter(
        visibility='public',
        created_at__gte=thirty_days_ago
    ).order_by('-created_at')[:4]
    
    app_newbies = Tool.objects.filter(
        status='published',
        created_at__gte=thirty_days_ago
    ).prefetch_related('translations', 'tags').order_by('-created_at')[:6]
    
    return render(request, 'home.html', {
        'professions': professions,
        'featured_stacks': featured_stacks,
        'featured_tools': featured_tools,
        'highlighted_stacks': highlighted_stacks,
        'highlighted_tools': highlighted_tools,
        'stack_newbies': stack_newbies,
        'app_newbies': app_newbies,
        'tool_count': tool_count,
        'stack_count': stack_count,
        'profession_count': profession_count,
    })



def professions(request):
    """List all professions."""
    professions = Profession.objects.all()
    return render(request, 'professions.html', {
        'professions': professions,
    })


def profession_detail(request, slug, pricing=None):
    """Profession landing page with filtered tools."""
    profession = get_object_or_404(Profession, slug=slug)
    tools = Tool.objects.filter(
        status='published',
        professions=profession
    ).prefetch_related('translations', 'tags')
    
    # Base query for counts (unfiltered by pricing)
    base_tools = Tool.objects.filter(
        status='published',
        professions=profession
    )
    
    # Calculate counts
    counts = {
        'all': base_tools.count(),
        'free': base_tools.filter(pricing_type='free').count(),
        'freemium': base_tools.filter(pricing_type='freemium').count(),
        'paid': base_tools.filter(pricing_type='paid').count(),
    }

    # Apply pricing filter if selected
    # Check both path param (pricing) and query param (request.GET) for backward compatibility if needed
    pricing_filter = pricing or request.GET.get('pricing')
    
    if pricing_filter:
        tools = tools.filter(pricing_type=pricing_filter)
    stacks = ToolStack.objects.filter(professions=profession)[:3]
    
    return render(request, 'profession_detail.html', {
        'profession': profession,
        'tools': tools,
        'stacks': stacks,
        'counts': counts,
    })


def tool_detail(request, slug):
    """Single tool detail page."""
    tool = get_object_or_404(
        Tool.objects.prefetch_related('translations', 'tags', 'categories', 'professions'),
        slug=slug, 
        status='published'
    )
    
    # Get translation (default to English)
    lang = request.GET.get('lang', 'en')
    translation = tool.get_translation(lang)
    
    # Related tools (same profession or category)
    related_tools = Tool.objects.filter(
        status='published',
        professions__in=tool.professions.all()
    ).exclude(id=tool.id).distinct()[:4]
    
    # Log tool view for analytics
    AnalyticsService.log_tool_click(request, tool, source_page='tool_detail')
    
    return render(request, 'tool_detail.html', {
        'tool': tool,
        'translation': translation,
        'related_tools': related_tools,
    })


def stacks(request):
    """List all tool stacks."""
    stacks = ToolStack.objects.prefetch_related('tools', 'professions').all()
    return render(request, 'stacks.html', {
        'stacks': stacks,
    })


def stack_detail(request, slug):
    """Tool stack detail page."""
    stack = get_object_or_404(
        ToolStack.objects.prefetch_related('tools__translations', 'professions'),
        slug=slug
    )
    
    # Log stack view for analytics
    AnalyticsService.log_stack_view(request, stack, source_page='stack_detail')
    
    return render(request, 'stack_detail.html', {
        'stack': stack,
    })


def search(request):
    """Search tools page."""
    query = request.GET.get('q', '')
    tools = []
    professions_results = []
    
    if query:
        # Semantic Search using ChromaDB
        try:
            # 1. Search Tools
            tool_ids = SearchService.search(query, collection_name='tools')
            if tool_ids:
                preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(tool_ids)])
                tools = Tool.objects.filter(
                    status='published',
                    id__in=tool_ids
                ).prefetch_related('translations').order_by(preserved)
            else:
                tools = []
            
            # 2. Search Stacks
            include_community = request.GET.get('community') == 'on'
            
            # Default: System stacks (owner is None)
            where_clause = {"owner_id": ""}
            
            if include_community:
                where_clause = {"visibility": "public"}
            
            stack_ids = SearchService.search(query, collection_name='stacks', where=where_clause)
            
            if stack_ids:
                preserved_stacks = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(stack_ids)])
                stacks_results = ToolStack.objects.filter(id__in=stack_ids).order_by(preserved_stacks)[:4]
            else:
                stacks_results = []
            
            # 3. Search Professions (keyword match on name/description)
            professions_results = Profession.objects.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )[:6]
                
        except Exception as e:
            # Fallback to simple keyword search
            print(f"Semantic search failed: {e}. Falling back to keyword search.")
            tools = Tool.objects.filter(
                status='published'
            ).filter(
                Q(name__icontains=query) |
                Q(translations__short_description__icontains=query) |
                Q(translations__use_cases__icontains=query)
            ).distinct().prefetch_related('translations', 'tags')[:20]
            stacks_results = []
            
            # Fallback profession search
            professions_results = Profession.objects.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )[:6]
    else:
        # No query
        stacks_results = []
    
    # Log search query for analytics
    if query:
        results_count = len(tools) if isinstance(tools, list) else tools.count() if hasattr(tools, 'count') else 0
        AnalyticsService.log_search(
            request, 
            query, 
            results_count,
            source_page='search',
            filters={'community': request.GET.get('community') == 'on'}
        )

    return render(request, 'search.html', {
        'query': query,
        'tools': tools,
        'stacks': stacks_results,
        'professions': professions_results,
    })



def tag_detail(request, slug):
    """List tools by tag."""
    tag = get_object_or_404(Tag, slug=slug)
    tools = Tool.objects.filter(
        status='published',
        tags=tag
    ).prefetch_related('translations', 'tags')
    
    return render(request, 'tag_detail.html', {
        'tag': tag,
        'tools': tools,
    })


@login_required
def my_stacks(request):
    """List authenticated user's created and saved stacks/tools."""
    # User's created stacks
    my_stacks = ToolStack.objects.filter(owner=request.user).order_by('-created_at')
    
    # User's saved stacks
    saved_stacks = SavedStack.objects.filter(user=request.user).select_related('stack').order_by('-created_at')
    
    # User's saved tools
    saved_tools = SavedTool.objects.filter(user=request.user).select_related('tool').order_by('-created_at')
    
    return render(request, 'my_stacks.html', {
        'stacks': my_stacks,
        'saved_stacks': [s.stack for s in saved_stacks],
        'saved_tools': [t.tool for t in saved_tools],
    })

@login_required
@require_POST
def toggle_save_tool(request, tool_id):
    """Toggle save status for a tool."""
    tool = get_object_or_404(Tool, id=tool_id)
    saved, created = SavedTool.objects.get_or_create(user=request.user, tool=tool)
    
    if not created:
        saved.delete()
        is_saved = False
        message = "Tool removed from favorites."
    else:
        is_saved = True
        message = "Tool added to favorites."
        
    # Return JSON for both HTMX and Fetch/AJAX
    if request.headers.get('HX-Request') or request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'application/json' in request.headers.get('Accept', ''):
         return JsonResponse({'is_saved': is_saved, 'message': message})
         
    messages.success(request, message)
    return redirect(request.META.get('HTTP_REFERER', 'tool_detail'))


@login_required
@require_POST
def toggle_save_stack(request, stack_slug):
    """Toggle save status for a stack."""
    stack = get_object_or_404(ToolStack, slug=stack_slug)
    saved, created = SavedStack.objects.get_or_create(user=request.user, stack=stack)
    
    if not created:
        saved.delete()
        is_saved = False
        message = "Stack removed from favorites."
    else:
        is_saved = True
        message = "Stack added to favorites."

    # Return JSON for both HTMX and Fetch/AJAX
    if request.headers.get('HX-Request') or request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'application/json' in request.headers.get('Accept', ''):
         return JsonResponse({'is_saved': is_saved, 'message': message})

    messages.success(request, message)
    return redirect(request.META.get('HTTP_REFERER', 'stack_detail'))

@login_required
def ai_stack_builder(request):
    """AI Stack Builder Interface."""
    return render(request, 'ai_stack_builder.html')

@login_required
@require_POST
def ai_generate_tools(request):
    """AJAX endpoint for AI suggestions."""
    data = json.loads(request.body)
    prompt = data.get('prompt', '')
    
    if not prompt:
        return JsonResponse({'error': 'No prompt provided'}, status=400)
        
    try:
        # Get suggestions with metadata
        result = AIService.generate_tool_suggestions(prompt)
        
        suggested_tools = result['tools']
        title = result['title']
        description = result['description']
        
        tools_data = [{
            'id': tool.id,
            'name': tool.name,
            'description': tool.get_translation('en').short_description if tool.get_translation('en') else '',
            'pricing': tool.get_pricing_type_display(),
            'logo': tool.logo.url if tool.logo else None
        } for tool in suggested_tools]
        
        return JsonResponse({
            'tools': tools_data,
            'title': title,
            'description': description
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_POST
def create_custom_stack(request):
    """Save the stack from AI Builder."""
    from django.utils.text import slugify
    import uuid
    
    name = request.POST.get('name')
    description = request.POST.get('description', '')
    visibility = request.POST.get('visibility', 'private')
    tool_ids = request.POST.getlist('tool_ids')
    
    if not name:
        messages.error(request, "Stack name is required.")
        return redirect('ai_stack_builder')
    
    # Generate a valid slug using Django's slugify + unique suffix
    base_slug = slugify(name)[:100]
    unique_slug = f"{base_slug}-{uuid.uuid4().hex[:8]}"
    
    # Fetch tools first to generate workflow description
    tools = []
    if tool_ids:
        tools = Tool.objects.filter(id__in=tool_ids)
        
    # Generate AI Workflow Description
    workflow_description = AIService.generate_workflow_description(name, tools)
    
    stack = ToolStack.objects.create(
        owner=request.user,
        name=name,
        slug=unique_slug,
        description=description,
        visibility=visibility,
        tagline=description[:100] if description else name[:100],
        workflow_description=workflow_description # Use AI generated description
    )
    
    if tools:
        stack.tools.set(tools)
        
    # Index it
    SearchService.add_stacks([stack])
    
    messages.success(request, "Stack created successfully with AI Workflow!")
    return redirect('my_stacks')


@login_required
def edit_custom_stack(request, slug):
    """Edit an existing custom stack."""
    stack = get_object_or_404(ToolStack, slug=slug)
    
    # Permission check: Only owner can edit
    if stack.owner != request.user:
        messages.error(request, "You do not have permission to edit this stack.")
        return redirect('my_stacks')
        
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        workflow_description = request.POST.get('workflow_description', '')
        visibility = request.POST.get('visibility', 'private')
        tool_ids = request.POST.getlist('tool_ids')
        
        if not name:
            messages.error(request, "Stack name is required.")
            return render(request, 'edit_stack.html', {'stack': stack, 'all_tools': Tool.objects.filter(status='published')})

        stack.name = name
        stack.description = description
        stack.workflow_description = workflow_description
        stack.visibility = visibility
        stack.save()
        
        if tool_ids:
             tools = Tool.objects.filter(id__in=tool_ids)
             stack.tools.set(tools)
        else:
            stack.tools.clear()
            
        # Re-index
        SearchService.add_stacks([stack])
            
        messages.success(request, "Stack updated successfully.")
        return redirect('my_stacks')
    
    # GET request - show form
    all_tools = Tool.objects.filter(status='published')
    return render(request, 'edit_stack.html', {
        'stack': stack, 
        'all_tools': all_tools
    })


@login_required
def delete_custom_stack(request, slug):
    """Delete a custom stack."""
    stack = get_object_or_404(ToolStack, slug=slug)
    
    # Permission check
    if stack.owner != request.user:
        messages.error(request, "You do not have permission to delete this stack.")
        return redirect('my_stacks')
        
    if request.method == 'POST':
        stack.delete()
        messages.success(request, "Stack deleted successfully.")
        return redirect('my_stacks')
        
    # Confirmation page (optional, but good practice. For now we will rely on a JS confirm or a modal in my_stacks, 
    # but if visited via GET, we should probably show a confirm page or redirect. 
    # Let's assume the UI handles the POST directly or we show a confirm page.)
    return render(request, 'confirm_delete_stack.html', {'stack': stack})


@staff_member_required
def admin_dashboard(request):
    """Analytics dashboard for superusers only."""
    if not request.user.is_superuser:
        messages.error(request, "Access denied. Superuser required.")
        return redirect('home')
    
    # Get time period from query params (default 30 days)
    days = int(request.GET.get('days', 30))
    
    # Get analytics data
    top_tools = AnalyticsService.get_top_clicked_tools(limit=10, days=days)
    top_stacks = AnalyticsService.get_top_viewed_stacks(limit=10, days=days)
    
    # Pagination for recent searches
    # Fetch more results to allow for deep scrolling (e.g. 500 instead of 50)
    # The AnalyticsService.get_recent_searches creates a slice, which returns a list/queryset. 
    # We should probably modify get_recent_searches or just slice it larger here if it returned a queryset.
    # Looking at likely implementation of get_recent_searches, it returns a sliced queryset.
    # Let's see... it returns SearchQuery.objects.filter(...).order_by(...)[:limit]
    # Pagination requires an unsliced queryset usually, OR we can just paginate the list, but for infinite scroll 
    # and large datasets, better to paginate the queryset.
    # For now, let's just ask for a larger limit from the service and paginate that, 
    # or better, bypassing the limit in the service if we want true infinite scroll.
    # But for this task, I will just call it with a large limit (e.g. 1000) and paginate locally, 
    # or I should modify the service to return a queryset. 
    # Let's check the service code again... 
    # it does: return SearchQuery.objects.filter(...)...[:limit]
    # So it returns a queryset but sliced. Sliced querysets cannot be filtered or re-ordered, but can be iterated.
    # Paginator works on lists/tuples too.
    
    recent_searches_list = AnalyticsService.get_recent_searches(limit=1000, days=days)
    paginator = Paginator(recent_searches_list, 20) # Show 20 per page
    page_number = request.GET.get('page')
    recent_searches = paginator.get_page(page_number)


    search_stats = AnalyticsService.get_search_stats(days=days)
    click_stats = AnalyticsService.get_click_stats(days=days)
    
    # Newsletter Subscribers
    q_sub = request.GET.get('q_sub', '')
    sub_page = int(request.GET.get('sub_page', 1))
    
    sub_qs = NewsletterSubscriber.objects.all().order_by('-created_at')
    if q_sub:
        sub_qs = sub_qs.filter(email__icontains=q_sub)
        
    total_subs = sub_qs.count()
    
    if sub_page == 1:
        start = 0
        end = 10
    else:
        start = 10 + (sub_page - 2) * 20
        end = start + 20
        
    newsletter_subscribers = sub_qs[start:end]
    has_more = end < total_subs
    next_page = sub_page + 1 if has_more else None
    
    # Handle AJAX Requests
    if request.headers.get('HX-Request'):
        # Check if this is a newsletter request (search or pagination)
        if 'q_sub' in request.GET or 'sub_page' in request.GET:
             return render(request, 'partials/newsletter_rows.html', {
                 'subscribers': newsletter_subscribers,
                 'has_more': has_more,
                 'next_page': next_page,
                 'days': days,
                 'q_sub': q_sub
             })
        
        # Otherwise assume it's the recent searches infinite scroll
        # (This block was previously simpler, but now we need to be strict)
        # However, the previous code just rendered 'partials/search_rows.html' directly.
        # We'll preserve that behavior for non-newsletter AJAX requests.
        return render(request, 'partials/search_rows.html', {
            'recent_searches': recent_searches,
             'days': days
        })

    return render(request, 'admin_dashboard.html', {
        'top_tools': top_tools,
        'top_stacks': top_stacks,
        'recent_searches': recent_searches,
        'search_stats': search_stats,
        'click_stats': click_stats,
        'days': days,
        'newsletter_subscribers': newsletter_subscribers,
        'newsletter_has_more': has_more,
        'newsletter_next_page': next_page,
        'newsletter_total': total_subs,
        'q_sub': q_sub,
        'active_tab': 'analytics'
    })


# --- Admin Tool Management ---

@staff_member_required
def admin_tools(request):
    """Admin: List and manage tools."""
    query = request.GET.get('q', '')
    if query:
        tools_list = Tool.objects.filter(
            Q(name__icontains=query) | Q(slug__icontains=query)
        ).order_by('-created_at')
    else:
        tools_list = Tool.objects.all().order_by('-created_at')
        
    paginator = Paginator(tools_list, 20)
    page_number = request.GET.get('page')
    tools = paginator.get_page(page_number)
    
    return render(request, 'admin_tools_list.html', {
        'tools': tools,
        'query': query,
        'active_tab': 'tools'
    })

@staff_member_required
def admin_tool_create(request):
    """Admin: Create a new tool."""
    if request.method == 'POST':
        form = ToolForm(request.POST, request.FILES)
        if form.is_valid():
            tool = form.save()
            messages.success(request, f"Tool '{tool.name}' created successfully.")
            return redirect('admin_tools')
    else:
        form = ToolForm()
    
    return render(request, 'admin_form.html', {
        'form': form,
        'title': 'Add New Tool',
        'back_url': 'admin_tools',
        'active_tab': 'tools'
    })

@staff_member_required
def admin_tool_edit(request, slug):
    """Admin: Edit an existing tool."""
    tool = get_object_or_404(Tool, slug=slug)
    if request.method == 'POST':
        form = ToolForm(request.POST, request.FILES, instance=tool)
        if form.is_valid():
            form.save()
            messages.success(request, f"Tool '{tool.name}' updated successfully.")
            return redirect('admin_tools')
    else:
        form = ToolForm(instance=tool)
    
    return render(request, 'admin_form.html', {
        'form': form,
        'title': f'Edit Tool: {tool.name}',
        'back_url': 'admin_tools',
        'active_tab': 'tools'
    })

@staff_member_required
def admin_tool_delete(request, slug):
    """Admin: Delete a tool."""
    tool = get_object_or_404(Tool, slug=slug)
    if request.method == 'POST':
        name = tool.name
        tool.delete()
        messages.success(request, f"Tool '{name}' deleted successfully.")
        return redirect('admin_tools')
    
    return render(request, 'admin_confirm_delete.html', {
        'object': tool,
        'title': f'Delete Tool: {tool.name}',
        'back_url': 'admin_tools',
        'active_tab': 'tools'
    })


# --- Admin Stack Management ---

@staff_member_required
def admin_stacks(request):
    """Admin: List and manage stacks."""
    query = request.GET.get('q', '')
    if query:
        stacks_list = ToolStack.objects.filter(
            Q(name__icontains=query) | Q(slug__icontains=query)
        ).order_by('-created_at')
    else:
        stacks_list = ToolStack.objects.all().order_by('-created_at')
        
    paginator = Paginator(stacks_list, 20)
    page_number = request.GET.get('page')
    stacks = paginator.get_page(page_number)
    
    return render(request, 'admin_stacks_list.html', {
        'stacks': stacks,
        'query': query,
        'active_tab': 'stacks'
    })

@staff_member_required
def admin_stack_create(request):
    """Admin: Create a new stack."""
    if request.method == 'POST':
        form = ToolStackForm(request.POST)
        if form.is_valid():
            stack = form.save(commit=False)
            
            # Auto-generate workflow description if empty
            tools = form.cleaned_data.get('tools', [])
            if not stack.workflow_description and tools:
                stack.workflow_description = AIService.generate_workflow_description(stack.name, tools)
                
            stack.save()
            form.save_m2m() # Important for saving the tools relation
            
            messages.success(request, f"Stack '{stack.name}' created successfully.")
            return redirect('admin_stacks')
    else:
        form = ToolStackForm()
    
    return render(request, 'admin_form.html', {
        'form': form,
        'title': 'Add New Stack',
        'back_url': 'admin_stacks',
        'active_tab': 'stacks'
    })

@staff_member_required
def admin_stack_edit(request, slug):
    """Admin: Edit an existing stack."""
    stack = get_object_or_404(ToolStack, slug=slug)
    if request.method == 'POST':
        form = ToolStackForm(request.POST, instance=stack)
        if form.is_valid():
            stack_instance = form.save(commit=False)
             
            # Auto-generate workflow description if empty
            tools = form.cleaned_data.get('tools', [])
            if not stack_instance.workflow_description and tools:
                stack_instance.workflow_description = AIService.generate_workflow_description(stack_instance.name, tools)
                
            stack_instance.save()
            form.save_m2m() # Important for m2m
            
            messages.success(request, f"Stack '{stack.name}' updated successfully.")
            return redirect('admin_stacks')
    else:
        form = ToolStackForm(instance=stack)
    
    return render(request, 'admin_form.html', {
        'form': form,
        'title': f'Edit Stack: {stack.name}',
        'back_url': 'admin_stacks',
        'active_tab': 'stacks'
    })

@staff_member_required
def admin_stack_delete(request, slug):
    """Admin: Delete a stack."""
    stack = get_object_or_404(ToolStack, slug=slug)
    if request.method == 'POST':
        name = stack.name
        stack.delete()
        messages.success(request, f"Stack '{name}' deleted successfully.")
        return redirect('admin_stacks')
    
    return render(request, 'admin_confirm_delete.html', {
        'object': stack,
        'title': f'Delete Stack: {stack.name}',
        'back_url': 'admin_stacks',
        'active_tab': 'stacks'
    })


# --- Admin Profession Management ---

@staff_member_required
def admin_professions(request):
    """Admin: List and manage professions."""
    query = request.GET.get('q', '')
    if query:
        professions_list = Profession.objects.filter(
            Q(name__icontains=query) | Q(slug__icontains=query)
        ).order_by('name')
    else:
        professions_list = Profession.objects.all().order_by('name')
        
    paginator = Paginator(professions_list, 20)
    page_number = request.GET.get('page')
    professions = paginator.get_page(page_number)
    
    return render(request, 'admin_professions_list.html', {
        'professions': professions,
        'query': query,
        'active_tab': 'professions'
    })

@staff_member_required
def admin_profession_create(request):
    """Admin: Create a new profession."""
    if request.method == 'POST':
        form = ProfessionForm(request.POST)
        if form.is_valid():
            profession = form.save()
            messages.success(request, f"Profession '{profession.name}' created successfully.")
            return redirect('admin_professions')
    else:
        form = ProfessionForm()
    
    return render(request, 'admin_form.html', {
        'form': form,
        'title': 'Add New Profession',
        'back_url': 'admin_professions',
        'active_tab': 'professions'
    })

@staff_member_required
def admin_profession_edit(request, slug):
    """Admin: Edit an existing profession."""
    profession = get_object_or_404(Profession, slug=slug)
    if request.method == 'POST':
        form = ProfessionForm(request.POST, instance=profession)
        if form.is_valid():
            form.save()
            messages.success(request, f"Profession '{profession.name}' updated successfully.")
            return redirect('admin_professions')
    else:
        form = ProfessionForm(instance=profession)
    
    return render(request, 'admin_form.html', {
        'form': form,
        'title': f'Edit Profession: {profession.name}',
        'back_url': 'admin_professions',
        'active_tab': 'professions'
    })

@staff_member_required
def admin_profession_delete(request, slug):
    """Admin: Delete a profession."""
    profession = get_object_or_404(Profession, slug=slug)
    if request.method == 'POST':
        name = profession.name
        profession.delete()
        messages.success(request, f"Profession '{name}' deleted successfully.")
        return redirect('admin_professions')
    
    return render(request, 'admin_confirm_delete.html', {
        'object': profession,
        'title': f'Delete Profession: {profession.name}',
        'back_url': 'admin_professions',
        'active_tab': 'professions'
    })


class TermsView(TemplateView):
    template_name = "terms.html"

class PrivacyView(TemplateView):
    template_name = "privacy.html"

class CookieView(TemplateView):
    template_name = "cookies.html"



from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import NewsletterSubscriber
import json

@require_POST
def subscribe_newsletter(request):
    try:
        data = json.loads(request.body)
        email = data.get('email')
        
        if not email:
            return JsonResponse({'message': 'Email is required.'}, status=400)
            
        if NewsletterSubscriber.objects.filter(email=email).exists():
            return JsonResponse({'message': 'You are already subscribed!'})
            
        subscriber = NewsletterSubscriber.objects.create(email=email)
        
        # Send Welcome Email
        try:
            from django.core.mail import EmailMultiAlternatives
            from django.template.loader import get_template
            from django.conf import settings
            
            subject = "Welcome to AIJACK! 🚀"
            text_content = "Welcome to AIJACK! Thanks for joining our intelligence network. You'll receive weekly curated AI tools and workflows."
            html_content = get_template('emails/welcome_email.html').render({'email': email})
            
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email],
                bcc=["support@growiumagent.com"]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        except Exception as e:
            # Log error but don't fail the subscription response
            print(f"Email error: {e}")
            
        return JsonResponse({'message': 'Thanks for subscribing!'})
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=400)


# --- Bulk Tool Upload ---
import csv
import io
from urllib.parse import urlparse
from django.utils.text import slugify
from .models import ToolTranslation

@staff_member_required
def bulk_upload_tools(request):
    """Handle CSV bulk upload of tools with AI-powered metadata generation."""
    if not request.user.is_superuser:
        messages.error(request, "Access denied. Superuser required.")
        return redirect('home')
    
    context = {
        'active_tab': 'bulk_upload',
        'step': 'upload'  # upload, validate, importing, complete
    }
    
    if request.method == 'POST':
        action = request.POST.get('action', 'upload')
        
        if action == 'upload':
            # Step 1: Parse and validate CSV
            csv_file = request.FILES.get('csv_file')
            if not csv_file:
                messages.error(request, "Please select a CSV file.")
                return render(request, 'admin_bulk_upload.html', context)
            
            if not csv_file.name.endswith('.csv'):
                messages.error(request, "File must be a CSV file.")
                return render(request, 'admin_bulk_upload.html', context)
            
            try:
                # Read and decode file
                decoded = csv_file.read().decode('utf-8-sig')
                
                # Auto-detect delimiter (semicolon or comma)
                try:
                    dialect = csv.Sniffer().sniff(decoded[:2048], delimiters=';,')
                    delimiter = dialect.delimiter
                except csv.Error:
                    # Default to semicolon if detection fails
                    delimiter = ';'
                
                reader = csv.DictReader(io.StringIO(decoded), delimiter=delimiter)
                
                rows = []
                errors = []
                row_num = 1
                
                for row in reader:
                    row_num += 1
                    row_data = {
                        'row_num': row_num,
                        'tool_name': row.get('Tool Name', '').strip(),
                        'website_url': row.get('Website URL', '').strip(),
                        'short_description': row.get('Short Description', '').strip(),
                        'long_description': row.get('Detailed Description', '').strip(),
                        'pricing_text': row.get('Pricing Strategy', '').strip(),
                        'status': 'pending',
                        'error': None
                    }
                    
                    # Validation
                    missing = []
                    if not row_data['tool_name']:
                        missing.append('Tool Name')
                    if not row_data['website_url']:
                        missing.append('Website URL')
                    if not row_data['short_description']:
                        missing.append('Short Description')
                    
                    if missing:
                        row_data['status'] = 'error'
                        row_data['error'] = f"Missing: {', '.join(missing)}"
                        errors.append(row_data)
                    else:
                        # Check for duplicates
                        domain = urlparse(row_data['website_url']).netloc.replace('www.', '')
                        name_slug = slugify(row_data['tool_name'])
                        
                        exists_by_name = Tool.objects.filter(slug=name_slug).exists()
                        exists_by_domain = Tool.objects.filter(website_url__icontains=domain).exists()
                        
                        if exists_by_name or exists_by_domain:
                            row_data['status'] = 'skipped'
                            row_data['error'] = 'Tool already exists (by name or domain)'
                        
                    rows.append(row_data)
                
                # Store in session for next step
                request.session['bulk_upload_rows'] = rows
                
                context['step'] = 'validate'
                context['rows'] = rows
                context['total'] = len(rows)
                context['valid'] = sum(1 for r in rows if r['status'] == 'pending')
                context['skipped'] = sum(1 for r in rows if r['status'] == 'skipped')
                context['errors'] = sum(1 for r in rows if r['status'] == 'error')
                
            except Exception as e:
                messages.error(request, f"Error parsing CSV: {str(e)}")
                return render(request, 'admin_bulk_upload.html', context)
        
        elif action == 'import':
            # Step 2: Process the import
            rows = request.session.get('bulk_upload_rows', [])
            if not rows:
                messages.error(request, "No data to import. Please upload a CSV first.")
                return render(request, 'admin_bulk_upload.html', context)
            
            # Get existing entities for AI context
            existing_categories = list(Category.objects.values_list('name', flat=True))
            existing_professions = list(Profession.objects.values_list('name', flat=True))
            existing_tags = list(Tag.objects.values_list('name', flat=True))
            
            results = []
            created_count = 0
            skipped_count = 0
            error_count = 0
            
            for row in rows:
                if row['status'] != 'pending':
                    if row['status'] == 'skipped':
                        skipped_count += 1
                    elif row['status'] == 'error':
                        error_count += 1
                    results.append(row)
                    continue
                
                try:
                    # Generate metadata via AI
                    metadata = AIService.generate_tool_metadata(
                        tool_name=row['tool_name'],
                        website_url=row['website_url'],
                        short_description=row['short_description'],
                        long_description=row['long_description'],
                        pricing_text=row['pricing_text'],
                        existing_categories=existing_categories,
                        existing_professions=existing_professions,
                        existing_tags=existing_tags
                    )
                    
                    # Create slug
                    base_slug = slugify(row['tool_name'])
                    slug = base_slug
                    counter = 1
                    while Tool.objects.filter(slug=slug).exists():
                        slug = f"{base_slug}-{counter}"
                        counter += 1
                    
                    # Create Tool
                    tool = Tool.objects.create(
                        name=row['tool_name'],
                        slug=slug,
                        website_url=row['website_url'],
                        pricing_type=metadata.get('pricing_type', 'freemium'),
                        status='published',
                        is_featured=True,
                        meta_title=metadata.get('meta_title', ''),
                        meta_description=metadata.get('meta_description', '')
                    )
                    
                    # Create ToolTranslation
                    ToolTranslation.objects.create(
                        tool=tool,
                        language='en',
                        short_description=row['short_description'],
                        long_description=row['long_description'],
                        use_cases=metadata.get('use_cases', ''),
                        pros=metadata.get('pros', ''),
                        cons=metadata.get('cons', '')
                    )
                    
                    # Handle Categories
                    for cat_name in metadata.get('category_names', []):
                        cat_slug = slugify(cat_name)
                        category, created = Category.objects.get_or_create(
                            slug=cat_slug,
                            defaults={'name': cat_name}
                        )
                        tool.categories.add(category)
                        if created and cat_name not in existing_categories:
                            existing_categories.append(cat_name)
                    
                    # Handle Professions  
                    for prof_name in metadata.get('profession_names', []):
                        prof_slug = slugify(prof_name)
                        profession, created = Profession.objects.get_or_create(
                            slug=prof_slug,
                            defaults={'name': prof_name}
                        )
                        tool.professions.add(profession)
                        if created and prof_name not in existing_professions:
                            existing_professions.append(prof_name)
                    
                    # Handle Tags
                    for tag_name in metadata.get('tag_names', []):
                        tag_slug = slugify(tag_name)
                        tag, created = Tag.objects.get_or_create(
                            slug=tag_slug,
                            defaults={'name': tag_name}
                        )
                        tool.tags.add(tag)
                        if created and tag_name not in existing_tags:
                            existing_tags.append(tag_name)
                    
                    row['status'] = 'success'
                    row['tool_id'] = tool.id
                    row['tool_slug'] = tool.slug
                    created_count += 1
                    
                except Exception as e:
                    row['status'] = 'error'
                    row['error'] = str(e)
                    error_count += 1
                
                results.append(row)
            
            # Clear session
            if 'bulk_upload_rows' in request.session:
                del request.session['bulk_upload_rows']
            
            context['step'] = 'complete'
            context['results'] = results
            context['created'] = created_count
            context['skipped'] = skipped_count
            context['errors'] = error_count
    
    return render(request, 'admin_bulk_upload.html', context)
