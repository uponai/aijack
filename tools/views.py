from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Case, When
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import send_mail
from django.conf import settings
import json
from .models import Tool, Profession, Category, ToolStack, Tag, SavedTool, SavedStack, SubmittedTool, ToolReport
from .forms import ToolForm, ToolStackForm, ProfessionForm, ToolSubmissionForm
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
    
    # Hero Animation Data
    import random
    from django.template.loader import render_to_string
    from robots.models import Robot

    hero_data = {
        'tools': [],
        'professions': [],
        'stacks': [],
        'robots': []
    }

    # Helper to serialize
    def serialize_hero_item(item, type_name):
        data = {
            'type': type_name,
            'name': item.name,
            'html': '',
            'description': ''
        }
        
        if type_name == 'tool':
            # Get short description from translation or meta
            trans = item.get_translation('en')
            data['description'] = trans.short_description if trans else item.meta_description or "AI Tool"
            data['html'] = render_to_string('includes/_tool_card.html', {'tool': item, 'request': request})
            
        elif type_name == 'profession':
            data['description'] = item.hero_tagline or f"AI tools for {item.name}"
            data['html'] = render_to_string('includes/_profession_card.html', {'profession': item})
            
        elif type_name == 'stack':
            data['description'] = item.tagline
            data['html'] = render_to_string('includes/_stack_card.html', {'stack': item, 'request': request})

        elif type_name == 'robot':
            data['description'] = item.short_description
            data['html'] = render_to_string('robots/includes/_robot_card.html', {'robot': item, 'request': request})

        return data

    # 1. Random Tools (Verified/Published with Logo)
    tools_pool = list(Tool.objects.filter(status='published', logo__isnull=False).exclude(logo='').values_list('id', flat=True))
    if tools_pool:
        random_tool_ids = random.sample(tools_pool, min(len(tools_pool), 5))
        for t in Tool.objects.filter(id__in=random_tool_ids):
            hero_data['tools'].append(serialize_hero_item(t, 'tool'))

    # 2. Random Professions (with Icon)
    prof_pool = list(Profession.objects.exclude(icon='').values_list('id', flat=True))
    if prof_pool:
        random_prof_ids = random.sample(prof_pool, min(len(prof_pool), 5))
        for p in Profession.objects.filter(id__in=random_prof_ids):
            hero_data['professions'].append(serialize_hero_item(p, 'profession'))

    # 3. Random Stacks (Public)
    stack_pool = list(ToolStack.objects.filter(visibility='public').values_list('id', flat=True))
    if stack_pool:
        random_stack_ids = random.sample(stack_pool, min(len(stack_pool), 5))
        for s in ToolStack.objects.filter(id__in=random_stack_ids):
             hero_data['stacks'].append(serialize_hero_item(s, 'stack'))

    # 4. Random Robots (Published with Image)
    robot_pool = list(Robot.objects.filter(status='published', image__isnull=False).exclude(image='').values_list('id', flat=True))
    if robot_pool:
        random_robot_ids = random.sample(robot_pool, min(len(robot_pool), 5))
        for r in Robot.objects.filter(id__in=random_robot_ids):
             hero_data['robots'].append(serialize_hero_item(r, 'robot'))

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
        'hero_data': hero_data,
    })



def guide(request):
    """Documentation page explaining the platform data types."""
    # Get one example of each type for the guide
    # We try to get featured/high quality items first
    
    example_tool = Tool.objects.filter(status='published', is_featured=True).first()
    if not example_tool:
        example_tool = Tool.objects.filter(status='published').first()
        
    example_stack = ToolStack.objects.filter(visibility='public', is_featured=True).first()
    if not example_stack:
        example_stack = ToolStack.objects.filter(visibility='public').first()
        
    example_profession = Profession.objects.first()
    
    room_company_qs = None
    try:
        from robots.models import Robot
        example_robot = Robot.objects.filter(status='published').first()
    except ImportError:
        example_robot = None
    
    return render(request, 'guide.html', {
        'example_tool': example_tool,
        'example_stack': example_stack,
        'example_profession': example_profession,
        'example_robot': example_robot,
    })


def professions(request):
    """List all professions."""
    professions = Profession.objects.all()
    return render(request, 'professions.html', {
        'professions': professions,
    })


def browse_tools(request):
    """Public tools browse page with filters and infinite scroll."""
    tools = Tool.objects.filter(status='published').prefetch_related('translations', 'tags', 'categories', 'professions')
    
    # Get filter options for dropdowns
    categories = Category.objects.all().order_by('name')
    all_professions = Profession.objects.all().order_by('name')
    tags = Tag.objects.all().order_by('name')
    
    # Apply filters
    category_slug = request.GET.get('category', '')
    profession_slug = request.GET.get('profession', '')
    pricing = request.GET.get('pricing', '')
    tag_slug = request.GET.get('tag', '')
    
    if category_slug:
        tools = tools.filter(categories__slug=category_slug)
    if profession_slug:
        tools = tools.filter(professions__slug=profession_slug)
    if pricing:
        tools = tools.filter(pricing_type=pricing)
    if tag_slug:
        tools = tools.filter(tags__slug=tag_slug)
    
    # Apply sorting
    sort = request.GET.get('sort', 'newest')
    if sort == 'newest':
        tools = tools.order_by('-created_at')
    elif sort == 'oldest':
        tools = tools.order_by('created_at')
    elif sort == 'featured':
        tools = tools.order_by('-is_featured', '-created_at')
    elif sort == 'name_asc':
        tools = tools.order_by('name')
    elif sort == 'name_desc':
        tools = tools.order_by('-name')
    else:
        tools = tools.order_by('-created_at')
    
    # Remove duplicates that might occur from multiple M2M joins
    tools = tools.distinct()
    
    # Pagination
    page = int(request.GET.get('page', 1))
    per_page = 20
    paginator = Paginator(tools, per_page)
    tools_page = paginator.get_page(page)
    
    total_count = paginator.count
    has_more = tools_page.has_next()
    next_page = tools_page.next_page_number() if has_more else None
    
    # Build active filters for display
    active_filters = []
    if category_slug:
        cat = Category.objects.filter(slug=category_slug).first()
        if cat:
            active_filters.append({'type': 'category', 'slug': category_slug, 'name': cat.name})
    if profession_slug:
        prof = Profession.objects.filter(slug=profession_slug).first()
        if prof:
            active_filters.append({'type': 'profession', 'slug': profession_slug, 'name': prof.name})
    if pricing:
        pricing_display = dict(Tool.PRICING_CHOICES).get(pricing, pricing)
        active_filters.append({'type': 'pricing', 'slug': pricing, 'name': pricing_display})
    if tag_slug:
        tag_obj = Tag.objects.filter(slug=tag_slug).first()
        if tag_obj:
            active_filters.append({'type': 'tag', 'slug': tag_slug, 'name': tag_obj.name})
    
    context = {
        'tools': tools_page,
        'categories': categories,
        'professions': all_professions,
        'tags': tags,
        'total_count': total_count,
        'has_more': has_more,
        'next_page': next_page,
        'current_page': page,
        'active_filters': active_filters,
        'current_sort': sort,
        'filter_category': category_slug,
        'filter_profession': profession_slug,
        'filter_pricing': pricing,
        'filter_tag': tag_slug,
    }
    
    return render(request, 'browse_tools.html', context)


def browse_tools_api(request):
    """API endpoint for infinite scroll - returns JSON or HTML partial."""
    tools = Tool.objects.filter(status='published').prefetch_related('translations', 'tags', 'categories', 'professions')
    
    # Apply filters
    category_slug = request.GET.get('category', '')
    profession_slug = request.GET.get('profession', '')
    pricing = request.GET.get('pricing', '')
    tag_slug = request.GET.get('tag', '')
    
    if category_slug:
        tools = tools.filter(categories__slug=category_slug)
    if profession_slug:
        tools = tools.filter(professions__slug=profession_slug)
    if pricing:
        tools = tools.filter(pricing_type=pricing)
    if tag_slug:
        tools = tools.filter(tags__slug=tag_slug)
    
    # Apply sorting
    sort = request.GET.get('sort', 'newest')
    if sort == 'newest':
        tools = tools.order_by('-created_at')
    elif sort == 'oldest':
        tools = tools.order_by('created_at')
    elif sort == 'featured':
        tools = tools.order_by('-is_featured', '-created_at')
    elif sort == 'name_asc':
        tools = tools.order_by('name')
    elif sort == 'name_desc':
        tools = tools.order_by('-name')
    else:
        tools = tools.order_by('-created_at')
    
    tools = tools.distinct()
    
    # Pagination
    try:
        page = int(request.GET.get('page', 1))
    except (ValueError, TypeError):
        page = 1
        
    per_page = 20
    paginator = Paginator(tools, per_page)
    tools_page = paginator.get_page(page)
    
    has_more = tools_page.has_next()
    next_page = tools_page.next_page_number() if has_more else None
    
    # Return HTML partial for HTMX/infinite scroll
    return render(request, 'partials/_tools_grid_items.html', {
        'tools': tools_page,
        'has_more': has_more,
        'next_page': next_page,
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
    
    # Log view
    AnalyticsService.log_profession_view(request, profession, source_page='profession_detail')
    
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
    AnalyticsService.log_tool_view(request, tool, source_page='tool_detail')
    
    return render(request, 'tool_detail.html', {
        'tool': tool,
        'translation': translation,
        'related_tools': related_tools,
    })


def visit_tool(request, slug):
    """
    Handle logic when user clicks 'Visit Website'.
    Logs an AffiliateClick and redirects to external URL.
    """
    tool = get_object_or_404(Tool, slug=slug, status='published')
    
    # Log the click (AffiliateClick)
    AnalyticsService.log_affiliate_click(request, tool, source_page='tool_detail')
    
    # Redirect to affiliate URL if exists, else website URL
    target_url = tool.affiliate_url if tool.affiliate_url else tool.website_url
    
    # Add ref parameter
    from .utils import append_ref_param
    target_url = append_ref_param(target_url)
    
    return redirect(target_url)


def submit_tool(request):
    """Handle user tool submissions."""
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to submit a tool.")
            return redirect('account_login')
            
        form = ToolSubmissionForm(request.POST)
        if form.is_valid():
            tool = form.save(commit=False)
            tool.user = request.user
            tool.save()
            
            # Send email notification
            try:
                subject = 'Tool Submission Received'
                # Render HTML content
                from django.template.loader import render_to_string
                from django.core.mail import EmailMultiAlternatives
                from django.utils.html import strip_tags

                html_content = render_to_string('emails/tool_submission_received.html', {
                    'user': request.user,
                    'tool': tool,
                    'site_host': settings.SITE_HOST
                })
                text_content = strip_tags(html_content)
                
                msg = EmailMultiAlternatives(
                    subject,
                    text_content,
                    settings.DEFAULT_FROM_EMAIL,
                    [request.user.email],
                    bcc=[settings.SUPPORT_EMAIL]
                )
                msg.attach_alternative(html_content, "text/html")
                msg.send(fail_silently=True)

            except Exception as e:
                print(f"Failed to send email: {e}")
                pass
                
            messages.success(request, "Tool submitted successfully! We've sent you a confirmation email.")
            return redirect('submit_tool')
    else:
        form = ToolSubmissionForm()
    
    return render(request, 'submit_tool.html', {'form': form})


@require_POST
def report_tool(request, slug):
    """Handle tool report submission via HTMX."""
    tool = get_object_or_404(Tool, slug=slug)
    
    reason = request.POST.get('reason')
    message = request.POST.get('message', '')
    
    if reason:
        ToolReport.objects.create(
            tool=tool,
            reason=reason,
            message=message,
            user=request.user if request.user.is_authenticated else None
        )
        # Return success message fragment
        return render(request, 'partials/_report_success.html')
    
    return JsonResponse({'error': 'Reason is required'}, status=400)



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
    robots_results = []
    
    if query:
        # Check if robots-only search is enabled
        robots_only = request.GET.get('robots_only') == 'on'
        
        # Semantic Search using ChromaDB
        try:
            # 1. Search Robots (if enabled or not filtered)
            if not robots_only:
                # Search Tools
                tool_ids = SearchService.search(query, collection_name='tools')
                if tool_ids:
                    preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(tool_ids)])
                    tools = Tool.objects.filter(
                        status='published',
                        id__in=tool_ids
                    ).prefetch_related('translations').order_by(preserved)[:9]
                else:
                    tools = []
            
            # Search Robots using RobotSearchService
            try:
                from robots.search import RobotSearchService
                from robots.models import Robot
                
                robot_ids = RobotSearchService.search(query, n_results=20)
                if robot_ids:
                    preserved_robots = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(robot_ids)])
                    robots_results = Robot.objects.filter(
                        status='published',
                        id__in=robot_ids
                    ).select_related('company').order_by(preserved_robots)
                else:
                    robots_results = []
            except Exception as robot_error:
                print(f"Robot search failed: {robot_error}")
                robots_results = []
            
            if not robots_only:
                # 2. Search Stacks
                include_community = request.GET.get('community') == 'on'
                
                # Default: System stacks (owner is None)
                where_clause = {"owner_id": ""}
                
                if include_community:
                    where_clause = {"visibility": "public"}
                
                stack_ids = SearchService.search(query, collection_name='stacks', where=where_clause)
                
                if stack_ids:
                    preserved_stacks = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(stack_ids)])
                    stacks_results = ToolStack.objects.filter(id__in=stack_ids).order_by(preserved_stacks)[:6]
                else:
                    stacks_results = []
                
                # 3. Search Professions
                pro_ids = SearchService.search(query, collection_name='professions')
                if pro_ids:
                     preserved_pros = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(pro_ids)])
                     professions_results = Profession.objects.filter(id__in=pro_ids).order_by(preserved_pros)[:6]
                else:
                     professions_results = []
            else:
                # Robots-only mode: skip stacks and professions
                stacks_results = []
                professions_results = []
                
        except Exception as e:
            # Fallback to simple keyword search
            print(f"Semantic search failed: {e}. Falling back to keyword search.")
            
            if not robots_only:
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
                    Q(name__icontains=query) | Q(description__icontains=query) | Q(hero_tagline__icontains=query)
                )[:6]
            else:
                tools = []
                stacks_results = []
                professions_results = []
            
            # Fallback robot search
            try:
                from robots.models import Robot
                robots_results = Robot.objects.filter(
                    Q(name__icontains=query) |
                    Q(short_description__icontains=query) |
                    Q(use_cases__icontains=query) |
                    Q(company__name__icontains=query)
                ).filter(status='published').select_related('company')[:20]
            except Exception:
                robots_results = []
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
            filters={
                'community': request.GET.get('community') == 'on',
                'robots_only': request.GET.get('robots_only') == 'on'
            }
        )

    return render(request, 'search.html', {
        'query': query,
        'tools': tools,
        'stacks': stacks_results,
        'professions': professions_results,
        'robots': robots_results,
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
    # Get analytics data
    # "Clicked Tools" means outbound clicks now (AffiliateClick)
    top_clicked_tools = AnalyticsService.get_top_clicked_tools(limit=10, days=days)
    
    # "Viewed Tools" (New metric)
    top_viewed_tools = AnalyticsService.get_top_viewed_tools(limit=10, days=days)

    # "Viewed Stacks" (New metric using StackView)
    top_stacks = AnalyticsService.get_top_viewed_stacks_new(limit=10, days=days)
    
    # "Clicked Stacks" (Stacks with most tool citations/clicks)
    top_clicked_stacks = AnalyticsService.get_top_clicked_stacks(limit=10, days=days)

    # "Viewed Professions"
    top_professions = AnalyticsService.get_top_viewed_professions(limit=10, days=days)

    # "Clicked Professions"
    top_clicked_professions = AnalyticsService.get_top_clicked_professions(limit=10, days=days)
    
    # Pagination for recent searches
    # Fetch more results to allow for deep scrolling (e.g. 1000) and paginate locally
    # AnalyticsService.get_recent_searches returns a sliced queryset/list, so we use a large limit.
    
    recent_searches_list = AnalyticsService.get_recent_searches(limit=1000, days=days)
    paginator = Paginator(recent_searches_list, 20) # Show 20 per page
    page_number = request.GET.get('page')
    recent_searches = paginator.get_page(page_number)


    search_stats = AnalyticsService.get_search_stats(days=days)
    click_stats = AnalyticsService.get_click_stats(days=days)
    
    # Robot Analytics
    try:
        from robots.models import RobotView
        from django.db.models import Count
        from datetime import timedelta, datetime
        
        cutoff_date = datetime.now()  - timedelta(days=days)
        top_viewed_robots = RobotView.objects.filter(
            created_at__gte=cutoff_date
        ).values(
            'robot__name', 'robot__slug', 'robot__image'
        ).annotate(
            view_count=Count('id')
        ).order_by('-view_count')[:10]
    except Exception as e:
        print(f"Robot analytics failed: {e}")
        top_viewed_robots = []
    
    # Tool Reports
    unresolved_reports = ToolReport.objects.filter(is_resolved=False).select_related('tool', 'user')[:5]
    total_unresolved_reports = ToolReport.objects.filter(is_resolved=False).count()
    
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
        'top_clicked_tools': top_clicked_tools,
        'top_viewed_tools': top_viewed_tools,
        'top_stacks': top_stacks,
        'top_clicked_stacks': top_clicked_stacks,
        'top_professions': top_professions,
        'top_clicked_professions': top_clicked_professions,
        'top_viewed_robots': top_viewed_robots,
        'recent_searches': recent_searches,
        'search_stats': search_stats,
        'click_stats': click_stats,
        'days': days,
        'newsletter_subscribers': newsletter_subscribers,
        'unresolved_reports': unresolved_reports,
        'total_unresolved_reports': total_unresolved_reports,
        'newsletter_has_more': has_more,
        'newsletter_next_page': next_page,
        'newsletter_total': total_subs,
        'q_sub': q_sub,
        'active_tab': 'analytics'
    })


# --- Admin Tool Management ---

@staff_member_required
def admin_tools(request):
    """Admin tool management list."""
    query = request.GET.get('q', '')
    filter_type = request.GET.get('filter', 'all')
    
    tools = Tool.objects.all().order_by('-created_at')
    
    if query:
        tools = tools.filter(
            Q(name__icontains=query) | 
            Q(slug__icontains=query) |
            Q(categories__name__icontains=query)
        ).distinct()
    
    if filter_type == 'incomplete':
        # Filter for tools missing critical fields that can be checked at DB level
        # Description is checked via translations in get_missing_fields()
        tools = tools.filter(
            Q(logo="") |
            Q(categories__isnull=True) |
            Q(professions__isnull=True) |
            Q(tags__isnull=True) |
            Q(meta_title="") |
            Q(meta_description="")
        ).distinct()

    paginator = Paginator(tools, 100)
    page_number = request.GET.get('page')
    tools_page = paginator.get_page(page_number)
    
    # Calculate missing fields for each tool in the current page
    for tool in tools_page:
        tool.missing_fields = tool.get_missing_fields()
        
    return render(request, 'admin_tools_list.html', {
        'tools': tools_page,
        'query': query,
        'filter_type': filter_type,
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
        'title': tool.name,
        'model_type': 'Tool',
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
    filter_type = request.GET.get('filter', 'all')
    
    stacks = ToolStack.objects.all().order_by('-created_at')
    
    if query:
        stacks = stacks.filter(
            Q(name__icontains=query) | 
            Q(slug__icontains=query)
        ).distinct()
    
    if filter_type == 'incomplete':
        # Filter for stacks missing critical fields
        stacks = stacks.filter(
            Q(description="") |
            Q(tagline="") |
            Q(tools__isnull=True) |
            Q(professions__isnull=True) |
            Q(meta_title="") |
            Q(meta_description="")
        ).distinct()
        
    paginator = Paginator(stacks, 20)
    page_number = request.GET.get('page')
    stacks_page = paginator.get_page(page_number)
    
    # Calculate missing fields for each stack in the current page
    for stack in stacks_page:
        stack.missing_fields = stack.get_missing_fields()
    
    return render(request, 'admin_stacks_list.html', {
        'stacks': stacks_page,
        'query': query,
        'filter_type': filter_type,
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
        'title': stack.name,
        'model_type': 'Stack',
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
    filter_type = request.GET.get('filter', 'all')
    
    professions = Profession.objects.all().order_by('name')
    
    if query:
        professions = professions.filter(
            Q(name__icontains=query) | 
            Q(slug__icontains=query)
        ).distinct()
    
    if filter_type == 'incomplete':
        # Filter for professions missing critical fields
        professions = professions.filter(
            Q(description="") |
            Q(icon="") |
            Q(hero_tagline="") |
            Q(meta_title="") |
            Q(meta_description="")
        ).distinct()
        
    paginator = Paginator(professions, 20)
    page_number = request.GET.get('page')
    professions_page = paginator.get_page(page_number)
    
    # Calculate missing fields for each profession in the current page
    for profession in professions_page:
        profession.missing_fields = profession.get_missing_fields()
    
    return render(request, 'admin_professions_list.html', {
        'professions': professions_page,
        'query': query,
        'filter_type': filter_type,
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
        'title': profession.name,
        'model_type': 'Profession',
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
            html_content = get_template('emails/welcome_email.html').render({
                'email': email,
                'site_host': settings.SITE_HOST
            })
            
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email],
                bcc=[settings.SUPPORT_EMAIL]
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
                    
                    # Find similar existing tools using vector search
                    similar_tool_ids = []
                    similar_tool_names = []
                    try:
                        # Create search query from tool description
                        search_query = f"{row['tool_name']} {row['short_description']}"
                        similar_ids = SearchService.search(search_query, n_results=4, collection_name="tools")
                        
                        # Filter out the newly created tool itself and get top 3
                        for similar_id in similar_ids:
                            if str(tool.id) != similar_id:
                                try:
                                    similar_tool = Tool.objects.get(id=int(similar_id))
                                    similar_tool_ids.append(similar_tool.id)
                                    similar_tool_names.append(similar_tool.name)
                                    if len(similar_tool_ids) >= 3:
                                        break
                                except Tool.DoesNotExist:
                                    continue
                    except Exception as e:
                        print(f"Similarity search error for {row['tool_name']}: {e}")
                    
                    # Add tool to vector database for future similarity searches
                    try:
                        SearchService.add_tools([tool])
                    except Exception as e:
                        print(f"Vector DB add error for {row['tool_name']}: {e}")
                    
                    row['status'] = 'success'
                    row['tool_id'] = tool.id
                    row['tool_slug'] = tool.slug
                    row['similar_tools'] = similar_tool_names  # Store for display
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


def custom_404(request, exception):
    """Custom 404 error handler."""
    return render(request, '404.html', status=404)

# --- AI Tool Completion ---
@staff_member_required
@require_POST
def ai_complete_tool(request, slug):
    """AJAX endpoint to AI-complete missing tool fields."""
    tool = get_object_or_404(Tool, slug=slug)
    translation = tool.get_translation('en')
    
    # Gather existing data
    tool_data = {
        'name': tool.name,
        'slug': tool.slug,
        'website_url': tool.website_url or '',
        'pricing_type': tool.pricing_type if tool.pricing_type else '(MISSING)',
        'categories': ', '.join(tool.categories.values_list('name', flat=True)) or '(MISSING)',
        'professions': ', '.join(tool.professions.values_list('name', flat=True)) or '(MISSING)',
        'tags': ', '.join(tool.tags.values_list('name', flat=True)) or '(MISSING)',
        'meta_title': tool.meta_title or '(MISSING)',
        'meta_description': tool.meta_description or '( MISSING)',
    }
    
    if translation:
        tool_data.update({
            'short_description': translation.short_description or '(MISSING)',
            'long_description': translation.long_description or '(MISSING)',
            'use_cases': translation.use_cases or '(MISSING)',
            'pros': translation.pros or '(MISSING)',
            'cons': translation.cons or '(MISSING)',
        })
    else:
        tool_data.update({
            'short_description': '(MISSING)',
            'long_description': '(MISSING)',
            'use_cases': '(MISSING)',
            'pros': '(MISSING)',
            'cons': '(MISSING)',
        })
    
    # Get existing entities for context
    existing_categories = list(Category.objects.values_list('name', flat=True))
    existing_professions = list(Profession.objects.values_list('name', flat=True))
    existing_tags = list(Tag.objects.values_list('name', flat=True))
    
    # Call AI
    completed_data = AIService.complete_tool_fields(
        tool_data, existing_categories, existing_professions, existing_tags
    )
    
    if 'error' in completed_data:
        return JsonResponse({'success': False, 'error': completed_data['error']})
    
    # Apply completed fields to tool
    updated_fields = []
    
    if 'pricing_type' in completed_data:
        tool.pricing_type = completed_data['pricing_type']
        updated_fields.append('pricing_type')
    
    if 'meta_title' in completed_data:
        tool.meta_title = completed_data['meta_title']
        updated_fields.append('meta_title')
    
    if 'meta_description' in completed_data:
        tool.meta_description = completed_data['meta_description']
        updated_fields.append('meta_description')
    
    # Handle categories
    if 'category_names' in completed_data:
        for cat_name in completed_data['category_names']:
            cat_slug = slugify(cat_name)
            category, _ = Category.objects.get_or_create(slug=cat_slug, defaults={'name': cat_name})
            tool.categories.add(category)
        updated_fields.append('categories')
    
    # Handle professions
    if 'profession_names' in completed_data:
        for prof_name in completed_data['profession_names']:
            prof_slug = slugify(prof_name)
            profession, _ = Profession.objects.get_or_create(slug=prof_slug, defaults={'name': prof_name})
            tool.professions.add(profession)
        updated_fields.append('professions')
    
    # Handle tags
    if 'tag_names' in completed_data:
        for tag_name in completed_data['tag_names']:
            tag_slug = slugify(tag_name)
            tag, _ = Tag.objects.get_or_create(slug=tag_slug, defaults={'name': tag_name})
            tool.tags.add(tag)
        updated_fields.append('tags')
    
    tool.save()
    
    # Update translation
    if any(k in completed_data for k in ['short_description', 'long_description', 'use_cases', 'pros', 'cons']):
        ToolTranslation.objects.update_or_create(
            tool=tool,
            language='en',
            defaults={
                'short_description': completed_data.get('short_description', translation.short_description if translation else ''),
                'long_description': completed_data.get('long_description', translation.long_description if translation else ''),
                'use_cases': completed_data.get('use_cases', translation.use_cases if translation else ''),
                'pros': completed_data.get('pros', translation.pros if translation else ''),
                'cons': completed_data.get('cons', translation.cons if translation else ''),
            }
        )
        updated_fields.extend([k for k in ['short_description', 'long_description', 'use_cases', 'pros', 'cons'] if k in completed_data])
    
    # Refresh translation from DB
    translation = tool.get_translation('en')
    
    # Check if tool is now complete and set as featured
    is_complete = all([
        tool.pricing_type,
        tool.categories.exists(),
        tool.professions.exists(),
        tool.tags.exists(),
        tool.meta_title,
        tool.meta_description,
        translation and translation.short_description,
        translation and translation.long_description,
        translation and translation.use_cases,
        translation and translation.pros,
        translation and translation.cons
    ])
    
    if is_complete and not tool.is_featured:
        tool.is_featured = True
        tool.save()
        updated_fields.append('is_featured')
    
    return JsonResponse({
        'success': True,
        'updated_fields': updated_fields,
        'is_featured': tool.is_featured,
        'message': f'Completed {len(updated_fields)} fields with AI' + (' - marked as featured!' if is_complete else '')
    })

# --- AI Stack Completion ---
@staff_member_required
@require_POST
def ai_complete_stack(request, slug):
    """AJAX endpoint to AI-complete missing stack fields."""
    stack = get_object_or_404(ToolStack, slug=slug)
    
    # Gather existing data
    stack_data = {
        'name': stack.name,
        'slug': stack.slug,
        'tagline': stack.tagline or '(MISSING)',
        'description': stack.description or '(MISSING)',
        'workflow_description': stack.workflow_description or '(MISSING)',
        'tools': ', '.join(stack.tools.values_list('name', flat=True)) or '(MISSING)',
        'professions': ', '.join(stack.professions.values_list('name', flat=True)) or '(MISSING)',
        'meta_title': stack.meta_title or '(MISSING)',
        'meta_description': stack.meta_description or '(MISSING)',
    }
    
    # Get context
    existing_professions = list(Profession.objects.values_list('name', flat=True))
    available_tools = list(Tool.objects.filter(status='published').values_list('name', flat=True))
    
    # Call AI
    completed_data = AIService.complete_stack_fields(
        stack_data, existing_professions, available_tools
    )
    
    if 'error' in completed_data:
        return JsonResponse({'success': False, 'error': completed_data['error']})
    
    # Apply completed fields
    updated_fields = []
    
    if 'tagline' in completed_data:
        stack.tagline = completed_data['tagline']
        updated_fields.append('tagline')
    
    if 'description' in completed_data:
        stack.description = completed_data['description']
        updated_fields.append('description')
    
    if 'workflow_description' in completed_data:
        stack.workflow_description = completed_data['workflow_description']
        updated_fields.append('workflow_description')
    
    if 'meta_title' in completed_data:
        stack.meta_title = completed_data['meta_title']
        updated_fields.append('meta_title')
    
    if 'meta_description' in completed_data:
        stack.meta_description = completed_data['meta_description']
        updated_fields.append('meta_description')
    
    # Handle tool suggestions
    if 'tool_names' in completed_data:
        for tool_name in completed_data['tool_names']:
            try:
                tool = Tool.objects.filter(name__iexact=tool_name, status='published').first()
                if tool and tool not in stack.tools.all():
                    stack.tools.add(tool)
            except Tool.DoesNotExist:
                continue
        updated_fields.append('tools')
    
    # Handle professions
    if 'profession_names' in completed_data:
        for prof_name in completed_data['profession_names']:
            prof_slug = slugify(prof_name)
            profession, _ = Profession.objects.get_or_create(slug=prof_slug, defaults={'name': prof_name})
            if profession not in stack.professions.all():
                stack.professions.add(profession)
        updated_fields.append('professions')
    
    stack.save()
    
    # Check completeness and mark as featured
    is_complete = all([
        stack.tagline,
        stack.description,
        stack.workflow_description,
        stack.tools.exists(),
        stack.professions.exists(),
        stack.meta_title,
        stack.meta_description
    ])
    
    if is_complete and not stack.is_featured:
        stack.is_featured = True
        stack.save()
        updated_fields.append('is_featured')
    
    return JsonResponse({
        'success': True,
        'updated_fields': updated_fields,
        'is_featured': stack.is_featured,
        'message': f'Completed {len(updated_fields)} fields with AI' + (' - marked as featured!' if is_complete else '')
    })

# --- AI Profession Completion ---
@staff_member_required
@require_POST
def ai_complete_profession(request, slug):
    """AJAX endpoint to AI-complete missing profession fields."""
    profession = get_object_or_404(Profession, slug=slug)
    
    # Gather existing data
    profession_data = {
        'name': profession.name,
        'slug': profession.slug,
        'description': profession.description or '(MISSING)',
        'hero_tagline': profession.hero_tagline or '(MISSING)',
        'icon': profession.icon or '(MISSING)',
        'meta_title': profession.meta_title or '(MISSING)',
        'meta_description': profession.meta_description or '(MISSING)',
    }
    
    # Call AI
    completed_data = AIService.complete_profession_fields(profession_data)
    
    if 'error' in completed_data:
        return JsonResponse({'success': False, 'error': completed_data['error']})
    
    # Apply completed fields
    updated_fields = []
    
    if 'description' in completed_data:
        profession.description = completed_data['description']
        updated_fields.append('description')
    
    if 'hero_tagline' in completed_data:
        profession.hero_tagline = completed_data['hero_tagline']
        updated_fields.append('hero_tagline')
    
    if 'icon' in completed_data:
        profession.icon = completed_data['icon']
        updated_fields.append('icon')
    
    if 'meta_title' in completed_data:
        profession.meta_title = completed_data['meta_title']
        updated_fields.append('meta_title')
    
    if 'meta_description' in completed_data:
        profession.meta_description = completed_data['meta_description']
        updated_fields.append('meta_description')
    
    profession.save()
    
    # Check completeness (all important fields filled)
    is_complete = all([
        profession.description,
        profession.hero_tagline,
        profession.icon,
        profession.meta_title,
        profession.meta_description
    ])
    
    return JsonResponse({
        'success': True,
        'updated_fields': updated_fields,
        'is_complete': is_complete,
        'message': f'Completed {len(updated_fields)} fields with AI' + (' - profession is now complete!' if is_complete else '')
    })

@staff_member_required
def admin_webcheck(request):
    """
    Renders the Webcheck progress dashboard.
    """
    return render(request, 'admin_webcheck_progress.html')

@staff_member_required
def api_get_pending_webcheck_tools(request):
    """
    Returns list of tools pending webcheck.
    """
    from django.utils import timezone
    from datetime import timedelta
    
    cutoff = timezone.now() - timedelta(days=1)
    
    tools = Tool.objects.filter(
        Q(is_website_valid__isnull=True) | 
        Q(webcheck_last_run__isnull=True) |
        Q(webcheck_last_run__lt=cutoff)
    ).order_by('webcheck_last_run', 'created_at')[:500]
    
    data = [{
        'id': t.id,
        'name': t.name,
        'website_url': t.website_url,
        'slug': t.slug
    } for t in tools]
    
    return JsonResponse({'tools': data, 'count': len(data)})

@staff_member_required
@require_POST
def api_process_webcheck_tool(request, tool_id):
    """
    Process a single tool.
    """
    from .webcheck import process_tool_webcheck
    
    try:
        tool = Tool.objects.get(id=tool_id)
        results = process_tool_webcheck(tool)
        return JsonResponse({'success': True, 'results': results})
    except Tool.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Tool not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
