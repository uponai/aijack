from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Case, When
from .models import Tool, Profession, Category, ToolStack, Tag
from .search import SearchService


def home(request):
    """Homepage with search and featured content."""
    professions = Profession.objects.all()[:8]
    featured_stacks = ToolStack.objects.filter(is_featured=True)[:3]
    featured_tools = Tool.objects.filter(status='published', is_featured=True)[:6]
    
    return render(request, 'home.html', {
        'professions': professions,
        'featured_stacks': featured_stacks,
        'featured_tools': featured_tools,
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
            tool_ids = SearchService.search(query)
            if tool_ids:
                # Preserve the order of IDs returned by vector search
                preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(tool_ids)])
                tools = Tool.objects.filter(
                    status='published',
                    id__in=tool_ids
                ).prefetch_related('translations').order_by(preserved)
            else:
                tools = []
        except Exception as e:
            # Fallback to simple keyword search if semantic search fails (e.g., db not ready)
            print(f"Semantic search failed: {e}. Falling back to keyword search.")
            tools = Tool.objects.filter(
                status='published'
            ).filter(
                Q(name__icontains=query) |
                Q(translations__short_description__icontains=query) |
                Q(translations__use_cases__icontains=query)
            ).distinct().prefetch_related('translations', 'tags')[:20]
    
    return render(request, 'search.html', {
        'query': query,
        'tools': tools,
    })
