from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Tool, Profession, Category, ToolStack, Tag


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


def profession_detail(request, slug):
    """Profession landing page with filtered tools."""
    profession = get_object_or_404(Profession, slug=slug)
    tools = Tool.objects.filter(
        status='published',
        professions=profession
    ).prefetch_related('translations', 'tags')
    
    # Filters
    pricing = request.GET.get('pricing')
    if pricing:
        tools = tools.filter(pricing_type=pricing)
    
    stacks = ToolStack.objects.filter(professions=profession)[:3]
    
    return render(request, 'profession_detail.html', {
        'profession': profession,
        'tools': tools,
        'stacks': stacks,
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
        # Simple keyword search (semantic search would use vector DB)
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
