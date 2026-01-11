from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Case, When
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
import json
from .models import Tool, Profession, Category, ToolStack, Tag
from .search import SearchService
from .ai_service import AIService
from .analytics import AnalyticsService


def home(request):
    """Homepage with search and featured content."""
    from datetime import date, timedelta
    
    today = date.today()
    thirty_days_ago = today - timedelta(days=30)
    
    professions = Profession.objects.all()[:8]
    featured_stacks = ToolStack.objects.filter(is_featured=True, visibility='public')[:3]
    featured_tools = Tool.objects.filter(status='published', is_featured=True)[:6]
    
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
                # If community checked: Public stacks (System OR (User & Public))
                # ChromaDB 'where' with $or is supported in newer versions, but if not:
                # We can query visibility="public". System stacks shd be public too?
                # System stacks usually public.
                where_clause = {"visibility": "public"}
            
            # If user wants ONLY their own? No, request was "search in other users' public stacks".
            
            stack_ids = SearchService.search(query, collection_name='stacks', where=where_clause)
            
            if stack_ids:
                # Preserved order for stacks
                preserved_stacks = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(stack_ids)])
                stacks_results = ToolStack.objects.filter(id__in=stack_ids).order_by(preserved_stacks)
            else:
                stacks_results = []
                
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
    })


@login_required
def my_stacks(request):
    """List authenticated user's stacks."""
    stacks = ToolStack.objects.filter(owner=request.user).order_by('-created_at')
    return render(request, 'my_stacks.html', {
        'stacks': stacks,
    })

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
    base_slug = slugify(f"{request.user.username}-{name}")[:100]
    unique_slug = f"{base_slug}-{uuid.uuid4().hex[:8]}"
        
    stack = ToolStack.objects.create(
        owner=request.user,
        name=name,
        slug=unique_slug,
        description=description,
        visibility=visibility,
        tagline=description[:100] if description else name[:100],
        workflow_description=description  # Add workflow description
    )
    
    if tool_ids:
        tools = Tool.objects.filter(id__in=tool_ids)
        stack.tools.set(tools)
        
    # Index it
    SearchService.add_stacks([stack])
    
    messages.success(request, "Stack created successfully!")
    return redirect('my_stacks')


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
    recent_searches = AnalyticsService.get_recent_searches(limit=50, days=days)
    search_stats = AnalyticsService.get_search_stats(days=days)
    click_stats = AnalyticsService.get_click_stats(days=days)
    
    return render(request, 'admin_dashboard.html', {
        'top_tools': top_tools,
        'top_stacks': top_stacks,
        'recent_searches': recent_searches,
        'search_stats': search_stats,
        'click_stats': click_stats,
        'days': days,
    })
