from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Case, When
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
import json
from .models import Tool, Profession, Category, ToolStack, Tag
from .search import SearchService
from .ai_service import AIService


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
            'description': tool.description,
            'pricing': tool.get_pricing_display(),
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
    name = request.POST.get('name')
    description = request.POST.get('description', '')
    visibility = request.POST.get('visibility', 'private')
    tool_ids = request.POST.getlist('tool_ids')
    
    if not name:
        messages.error(request, "Stack name is required.")
        return redirect('ai_stack_builder')
        
    stack = ToolStack.objects.create(
        owner=request.user,
        name=name,
        slug=f"{request.user.username}-{name.lower().replace(' ', '-')}"[:150], # Simple slug gen
        description=description,
        visibility=visibility,
        tagline=description[:100] # Reuse desc
    )
    
    if tool_ids:
        tools = Tool.objects.filter(id__in=tool_ids)
        stack.tools.set(tools)
        
    # Index it
    SearchService.add_stacks([stack])
    
    messages.success(request, "Stack created successfully!")
    return redirect('my_stacks')
