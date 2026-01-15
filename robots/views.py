"""
Views for the robots app.
Includes public views, admin views, and API endpoints.
"""

import hashlib
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from django.contrib import messages
from django.views.decorators.http import require_POST

from .models import Robot, RobotCompany, RobotNews, RobotView, SavedRobot
from .forms import RobotForm, RobotCompanyForm, RobotNewsForm


def get_client_ip(request):
    """Get client IP from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip or ''


# =============================================================================
# PUBLIC VIEWS
# =============================================================================

def robots_list(request):
    """Main listing page for all published robots with filters."""
    robots = Robot.objects.filter(status='published').select_related('company')
    
    # Filtering
    robot_type = request.GET.get('type')
    target_market = request.GET.get('target')
    availability = request.GET.get('availability')
    company_slug = request.GET.get('company')
    
    if robot_type:
        robots = robots.filter(robot_type=robot_type)
    if target_market:
        robots = robots.filter(target_market=target_market)
    if availability:
        robots = robots.filter(availability=availability)
    if company_slug:
        robots = robots.filter(company__slug=company_slug)
    
    # Get unique companies for filter dropdown
    companies = RobotCompany.objects.annotate(
        published_count=Count('robots', filter=Q(robots__status='published'))
    ).filter(published_count__gt=0).order_by('name')
    
    # Featured robots first
    robots = robots.order_by('-is_featured', '-created_at')
    
    # Latest news for sidebar
    latest_news = RobotNews.objects.filter(is_published=True)[:3]
    
    return render(request, 'robots/robots.html', {
        'robots': robots,
        'companies': companies,
        'robot_types': Robot.TYPE_CHOICES,
        'target_markets': Robot.TARGET_CHOICES,
        'availability_choices': Robot.AVAILABILITY_CHOICES,
        'selected_type': robot_type,
        'selected_target': target_market,
        'selected_availability': availability,
        'selected_company': company_slug,
        'latest_news': latest_news,
        'total_count': robots.count(),
    })


def robot_detail(request, slug):
    """Single robot detail page with full information."""
    robot = get_object_or_404(Robot.objects.select_related('company'), slug=slug, status='published')
    
    # Track view
    RobotView.objects.create(
        robot=robot,
        user=request.user if request.user.is_authenticated else None,
        session_key=request.session.session_key or '',
        ip_hash=hashlib.sha256(get_client_ip(request).encode()).hexdigest()[:32]
    )
    
    # Related robots (same company or type)
    related_robots = Robot.objects.filter(
        status='published'
    ).filter(
        Q(company=robot.company) | Q(robot_type=robot.robot_type)
    ).exclude(id=robot.id).order_by('-is_featured')[:6]
    
    # Robot's news
    robot_news = robot.news_articles.filter(is_published=True)[:3]
    
    # Check if saved by user
    is_saved = False
    if request.user.is_authenticated:
        is_saved = SavedRobot.objects.filter(user=request.user, robot=robot).exists()
    
    return render(request, 'robots/robot_detail.html', {
        'robot': robot,
        'related_robots': related_robots,
        'robot_news': robot_news,
        'is_saved': is_saved,
    })


def robot_companies(request):
    """Directory of robot manufacturers."""
    companies = RobotCompany.objects.annotate(
        published_count=Count('robots', filter=Q(robots__status='published'))
    ).filter(published_count__gt=0).order_by('name')
    
    return render(request, 'robots/robot_companies.html', {
        'companies': companies,
    })


def robot_company_detail(request, slug):
    """Single company profile page."""
    company = get_object_or_404(RobotCompany, slug=slug)
    
    robots = Robot.objects.filter(
        company=company,
        status='published'
    ).order_by('-is_featured', '-created_at')
    
    return render(request, 'robots/robot_company_detail.html', {
        'company': company,
        'robots': robots,
    })


def robot_comparison(request):
    """Compare up to 4 robots side-by-side."""
    # Get comparison IDs from session
    comparison_ids = request.session.get('robot_comparison', [])
    robots = Robot.objects.filter(id__in=comparison_ids, status='published').select_related('company')
    
    # Get all robots for selection
    all_robots = Robot.objects.filter(status='published').select_related('company').order_by('name')
    
    # Comparison specs
    comparison_specs = [
        ('height', 'Height', 'cm'),
        ('weight', 'Weight', 'kg'),
        ('battery_life', 'Battery Life', 'hours'),
        ('payload', 'Max Payload', 'kg'),
        ('speed', 'Max Speed', 'km/h'),
        ('degrees_of_freedom', 'Degrees of Freedom', ''),
    ]
    
    return render(request, 'robots/robot_comparison.html', {
        'robots': robots,
        'all_robots': all_robots,
        'comparison_specs': comparison_specs,
        'max_comparison': 4,
    })


def robot_timeline(request):
    """Visual timeline of robot releases by year."""
    robots = Robot.objects.filter(
        status='published',
        release_date__isnull=False
    ).select_related('company').order_by('release_date')
    
    # Group by year
    timeline_data = {}
    for robot in robots:
        year = robot.release_date.year
        if year not in timeline_data:
            timeline_data[year] = []
        timeline_data[year].append(robot)
    
    # Separate upcoming robots
    today = timezone.now().date()
    upcoming = robots.filter(release_date__gt=today)
    
    return render(request, 'robots/robot_timeline.html', {
        'timeline_data': sorted(timeline_data.items()),
        'upcoming': upcoming,
    })


def robot_matrix(request):
    """Specification comparison matrix - sortable table of all robots."""
    robots = Robot.objects.filter(status='published').select_related('company').order_by('name')
    
    return render(request, 'robots/robot_matrix.html', {
        'robots': robots,
    })


def robot_news_list(request):
    """Listing of all robot news articles."""
    news = RobotNews.objects.filter(is_published=True).prefetch_related('robots')
    
    # Pagination
    paginator = Paginator(news, 12)
    page = request.GET.get('page', 1)
    news = paginator.get_page(page)
    
    return render(request, 'robots/robot_news.html', {
        'news_list': news,
    })


def robot_news_detail(request, slug):
    """Single news article page."""
    article = get_object_or_404(RobotNews.objects.prefetch_related('robots'), slug=slug, is_published=True)
    
    # Related news (by linked robots)
    related_news = RobotNews.objects.filter(
        is_published=True,
        robots__in=article.robots.all()
    ).exclude(id=article.id).distinct()[:3]
    
    return render(request, 'robots/robot_news_detail.html', {
        'article': article,
        'related_news': related_news,
    })


# =============================================================================
# API ENDPOINTS
# =============================================================================

@login_required
@require_POST
def toggle_save_robot(request, robot_id):
    """Toggle save/unsave a robot for the current user."""
    robot = get_object_or_404(Robot, id=robot_id)
    
    saved, created = SavedRobot.objects.get_or_create(
        user=request.user,
        robot=robot
    )
    
    if not created:
        saved.delete()
        is_saved = False
    else:
        is_saved = True
    
    return JsonResponse({
        'success': True,
        'is_saved': is_saved,
        'robot_id': robot_id,
    })


def add_to_comparison(request):
    """Add a robot to comparison (session-based)."""
    robot_id = request.GET.get('robot_id')
    
    if not robot_id:
        return JsonResponse({'success': False, 'error': 'No robot_id provided'})
    
    try:
        robot_id = int(robot_id)
        robot = Robot.objects.get(id=robot_id, status='published')
    except (ValueError, Robot.DoesNotExist):
        return JsonResponse({'success': False, 'error': 'Robot not found'})
    
    comparison = request.session.get('robot_comparison', [])
    
    if len(comparison) >= 4:
        return JsonResponse({'success': False, 'error': 'Maximum 4 robots can be compared'})
    
    if robot_id not in comparison:
        comparison.append(robot_id)
        request.session['robot_comparison'] = comparison
    
    return JsonResponse({
        'success': True,
        'comparison': comparison,
        'count': len(comparison),
        'robot_name': robot.name,
    })


def remove_from_comparison(request):
    """Remove a robot from session comparison."""
    robot_id = request.GET.get('robot_id')
    
    if robot_id and 'robot_comparison' in request.session:
        try:
            robot_id = int(robot_id)
            comparison = request.session['robot_comparison']
            if robot_id in comparison:
                comparison.remove(robot_id)
                request.session['robot_comparison'] = comparison
                request.session.modified = True
        except (ValueError, TypeError):
            pass
    
    return JsonResponse({'success': True})


def robot_comparison_status(request):
    """Get current comparison status for floating bar."""
    robot_ids = request.session.get('robot_comparison', [])
    robots_data = []
    
    if robot_ids:
        robots = Robot.objects.filter(id__in=robot_ids, status='published')
        robots_data = [{'id': r.id, 'name': r.name} for r in robots]
    
    return JsonResponse({
        'robots': robots_data,
        'count': len(robots_data)
    })


def clear_comparison(request):
    """Clear all robots from comparison."""
    request.session['robot_comparison'] = []
    return JsonResponse({'success': True, 'comparison': [], 'count': 0})


# =============================================================================
# ADMIN VIEWS - ROBOTS
# =============================================================================

@user_passes_test(lambda u: u.is_superuser)
def admin_robots(request):
    """Admin: List and manage robots."""
    robots = Robot.objects.all().select_related('company')
    query = request.GET.get('q', '')
    filter_type = request.GET.get('filter', 'all')
    
    if query:
        robots = robots.filter(
            Q(name__icontains=query) | 
            Q(company__name__icontains=query) |
            Q(short_description__icontains=query)
        )
    
    # Convert to list for in-memory filtering if needed
    robots_list = list(robots)
    
    if filter_type == 'incomplete':
        robots_list = [r for r in robots_list if r.get_missing_fields()]
    
    # Add missing_fields attribute for template
    for robot in robots_list:
        robot.missing_fields = robot.get_missing_fields()
    
    # Pagination
    paginator = Paginator(robots_list, 20)
    page = request.GET.get('page', 1)
    robots_page = paginator.get_page(page)
    
    return render(request, 'robots/admin/admin_robots_list.html', {
        'robots': robots_page,
        'query': query,
        'filter_type': filter_type,
        'total_count': len(robots_list),
    })


@user_passes_test(lambda u: u.is_superuser)
def admin_robot_create(request):
    """Admin: Create a new robot."""
    if request.method == 'POST':
        form = RobotForm(request.POST, request.FILES)
        if form.is_valid():
            robot = form.save()
            messages.success(request, f'Robot "{robot.name}" created successfully!')
            return redirect('admin_robots')
    else:
        form = RobotForm()
    
    return render(request, 'robots/admin/admin_robot_form.html', {
        'form': form,
        'title': 'Add New Robot',
        'is_edit': False,
    })


@user_passes_test(lambda u: u.is_superuser)
def admin_robot_edit(request, slug):
    """Admin: Edit an existing robot."""
    robot = get_object_or_404(Robot, slug=slug)
    
    if request.method == 'POST':
        form = RobotForm(request.POST, request.FILES, instance=robot)
        if form.is_valid():
            robot = form.save()
            messages.success(request, f'Robot "{robot.name}" updated successfully!')
            return redirect('admin_robots')
    else:
        form = RobotForm(instance=robot)
    
    return render(request, 'robots/admin/admin_robot_form.html', {
        'form': form,
        'robot': robot,
        'title': f'Edit: {robot.name}',
        'is_edit': True,
    })


@user_passes_test(lambda u: u.is_superuser)
def admin_robot_delete(request, slug):
    """Admin: Delete a robot."""
    robot = get_object_or_404(Robot, slug=slug)
    
    if request.method == 'POST':
        name = robot.name
        robot.delete()
        messages.success(request, f'Robot "{name}" deleted successfully!')
        return redirect('admin_robots')
    
    return render(request, 'robots/admin/admin_confirm_delete.html', {
        'object': robot,
        'object_type': 'Robot',
        'cancel_url': 'admin_robots',
    })


# =============================================================================
# ADMIN VIEWS - COMPANIES
# =============================================================================

@user_passes_test(lambda u: u.is_superuser)
def admin_robot_companies(request):
    """Admin: List and manage robot companies."""
    companies = RobotCompany.objects.annotate(
        robot_count_val=Count('robots')
    ).order_by('name')
    
    query = request.GET.get('q', '')
    if query:
        companies = companies.filter(
            Q(name__icontains=query) | Q(headquarters__icontains=query)
        )
    
    paginator = Paginator(companies, 20)
    page = request.GET.get('page', 1)
    companies = paginator.get_page(page)
    
    return render(request, 'robots/admin/admin_robot_companies_list.html', {
        'companies': companies,
        'query': query,
    })


@user_passes_test(lambda u: u.is_superuser)
def admin_robot_company_create(request):
    """Admin: Create a new robot company."""
    if request.method == 'POST':
        form = RobotCompanyForm(request.POST, request.FILES)
        if form.is_valid():
            company = form.save()
            messages.success(request, f'Company "{company.name}" created successfully!')
            return redirect('admin_robot_companies')
    else:
        form = RobotCompanyForm()
    
    return render(request, 'robots/admin/admin_robot_company_form.html', {
        'form': form,
        'title': 'Add New Company',
        'is_edit': False,
    })


@user_passes_test(lambda u: u.is_superuser)
def admin_robot_company_edit(request, slug):
    """Admin: Edit an existing robot company."""
    company = get_object_or_404(RobotCompany, slug=slug)
    
    if request.method == 'POST':
        form = RobotCompanyForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            company = form.save()
            messages.success(request, f'Company "{company.name}" updated successfully!')
            return redirect('admin_robot_companies')
    else:
        form = RobotCompanyForm(instance=company)
    
    return render(request, 'robots/admin/admin_robot_company_form.html', {
        'form': form,
        'company': company,
        'title': f'Edit: {company.name}',
        'is_edit': True,
    })


@user_passes_test(lambda u: u.is_superuser)
def admin_robot_company_delete(request, slug):
    """Admin: Delete a robot company."""
    company = get_object_or_404(RobotCompany, slug=slug)
    
    if request.method == 'POST':
        name = company.name
        company.delete()
        messages.success(request, f'Company "{name}" deleted successfully!')
        return redirect('admin_robot_companies')
    
    return render(request, 'robots/admin/admin_confirm_delete.html', {
        'object': company,
        'object_type': 'Company',
        'cancel_url': 'admin_robot_companies',
    })


# =============================================================================
# ADMIN VIEWS - NEWS
# =============================================================================

@user_passes_test(lambda u: u.is_superuser)
def admin_robot_news(request):
    """Admin: List and manage robot news."""
    news = RobotNews.objects.all().order_by('-published_at')
    
    query = request.GET.get('q', '')
    if query:
        news = news.filter(
            Q(title__icontains=query) | Q(excerpt__icontains=query)
        )
    
    paginator = Paginator(news, 20)
    page = request.GET.get('page', 1)
    news = paginator.get_page(page)
    
    return render(request, 'robots/admin/admin_robot_news_list.html', {
        'news_list': news,
        'query': query,
    })


@user_passes_test(lambda u: u.is_superuser)
def admin_robot_news_create(request):
    """Admin: Create a new robot news article."""
    if request.method == 'POST':
        form = RobotNewsForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save()
            messages.success(request, f'Article "{article.title}" created successfully!')
            return redirect('admin_robot_news')
    else:
        form = RobotNewsForm()
    
    return render(request, 'robots/admin/admin_robot_news_form.html', {
        'form': form,
        'title': 'Add News Article',
        'is_edit': False,
    })


@user_passes_test(lambda u: u.is_superuser)
def admin_robot_news_edit(request, slug):
    """Admin: Edit an existing robot news article."""
    article = get_object_or_404(RobotNews, slug=slug)
    
    if request.method == 'POST':
        form = RobotNewsForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            article = form.save()
            messages.success(request, f'Article "{article.title}" updated successfully!')
            return redirect('admin_robot_news')
    else:
        form = RobotNewsForm(instance=article)
    
    return render(request, 'robots/admin/admin_robot_news_form.html', {
        'form': form,
        'article': article,
        'title': f'Edit: {article.title}',
        'is_edit': True,
    })


@user_passes_test(lambda u: u.is_superuser)
def admin_robot_news_delete(request, slug):
    """Admin: Delete a robot news article."""
    article = get_object_or_404(RobotNews, slug=slug)
    
    if request.method == 'POST':
        title = article.title
        article.delete()
        messages.success(request, f'Article "{title}" deleted successfully!')
        return redirect('admin_robot_news')
    
    return render(request, 'robots/admin/admin_confirm_delete.html', {
        'object': article,
        'object_type': 'News Article',
        'cancel_url': 'admin_robot_news',
    })


# =============================================================================
# BULK UPLOAD ROBOTS
# =============================================================================

import csv
import io
from urllib.parse import urlparse
from django.utils.text import slugify
from .ai_service import RobotAIService
from .search import RobotSearchService


@user_passes_test(lambda u: u.is_superuser)
def bulk_upload_robots(request):
    """Handle CSV bulk upload of robots with AI-powered metadata generation."""
    
    context = {
        'active_tab': 'robots',
        'step': 'upload'  # upload, validate, complete
    }
    
    if request.method == 'POST':
        action = request.POST.get('action', 'upload')
        
        if action == 'upload':
            # Step 1: Parse and validate CSV
            csv_file = request.FILES.get('csv_file')
            if not csv_file:
                messages.error(request, "Please select a CSV file.")
                return render(request, 'robots/admin/admin_bulk_upload_robots.html', context)
            
            if not csv_file.name.endswith('.csv'):
                messages.error(request, "File must be a CSV file.")
                return render(request, 'robots/admin/admin_bulk_upload_robots.html', context)
            
            try:
                # Read and decode file
                decoded = csv_file.read().decode('utf-8-sig')
                
                # Auto-detect delimiter (semicolon or comma)
                try:
                    dialect = csv.Sniffer().sniff(decoded[:2048], delimiters=';,')
                    delimiter = dialect.delimiter
                except csv.Error:
                    delimiter = ','
                
                reader = csv.DictReader(io.StringIO(decoded), delimiter=delimiter)
                
                rows = []
                row_num = 1
                
                for row in reader:
                    row_num += 1
                    row_data = {
                        'row_num': row_num,
                        'robot_name': row.get('Robot Name', '').strip(),
                        'company_name': row.get('Company', '').strip(),
                        'product_url': row.get('Website URL', '').strip(),
                        'short_description': row.get('Short Description', '').strip(),
                        'long_description': row.get('Detailed Description', '').strip(),
                        'pricing_text': row.get('Pricing Strategy', '').strip(),
                        'status': 'pending',
                        'error': None
                    }
                    
                    # Validation
                    missing = []
                    if not row_data['robot_name']:
                        missing.append('Robot Name')
                    if not row_data['product_url']:
                        missing.append('Website URL')
                    if not row_data['short_description']:
                        missing.append('Short Description')
                    
                    if missing:
                        row_data['status'] = 'error'
                        row_data['error'] = f"Missing: {', '.join(missing)}"
                    else:
                        # Check for duplicates
                        domain = urlparse(row_data['product_url']).netloc.replace('www.', '')
                        name_slug = slugify(row_data['robot_name'])
                        
                        exists_by_name = Robot.objects.filter(slug=name_slug).exists()
                        exists_by_domain = Robot.objects.filter(product_url__icontains=domain).exists() if domain else False
                        
                        if exists_by_name or exists_by_domain:
                            row_data['status'] = 'skipped'
                            row_data['error'] = 'Robot already exists (by name or domain)'
                        
                    rows.append(row_data)
                
                # Store in session for next step
                request.session['bulk_upload_robot_rows'] = rows
                
                context['step'] = 'validate'
                context['rows'] = rows
                context['total'] = len(rows)
                context['valid'] = sum(1 for r in rows if r['status'] == 'pending')
                context['skipped'] = sum(1 for r in rows if r['status'] == 'skipped')
                context['errors'] = sum(1 for r in rows if r['status'] == 'error')
                
            except Exception as e:
                messages.error(request, f"Error parsing CSV: {str(e)}")
                return render(request, 'robots/admin/admin_bulk_upload_robots.html', context)
        
        elif action == 'import':
            # Step 2: Process the import
            rows = request.session.get('bulk_upload_robot_rows', [])
            if not rows:
                messages.error(request, "No data to import. Please upload a CSV first.")
                return render(request, 'robots/admin/admin_bulk_upload_robots.html', context)
            
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
                    # Get or create company
                    company_name = row['company_name'] or 'Unknown'
                    company_slug = slugify(company_name)
                    
                    # Extract base URL for company website (e.g., https://example.com)
                    company_website = ''
                    if row['product_url']:
                        parsed = urlparse(row['product_url'])
                        if parsed.scheme and parsed.netloc:
                            company_website = f"{parsed.scheme}://{parsed.netloc}"
                    
                    company, _ = RobotCompany.objects.get_or_create(
                        slug=company_slug,
                        defaults={
                            'name': company_name,
                            'website': company_website
                        }
                    )
                    
                    # Generate metadata via AI
                    metadata = RobotAIService.generate_robot_metadata(
                        robot_name=row['robot_name'],
                        product_url=row['product_url'],
                        short_description=row['short_description'],
                        long_description=row['long_description'],
                        pricing_text=row['pricing_text'],
                        company_name=company_name
                    )
                    
                    # Create slug
                    base_slug = slugify(row['robot_name'])
                    slug = base_slug
                    counter = 1
                    while Robot.objects.filter(slug=slug).exists():
                        slug = f"{base_slug}-{counter}"
                        counter += 1
                    
                    # Create Robot
                    robot = Robot.objects.create(
                        name=row['robot_name'],
                        slug=slug,
                        company=company,
                        product_url=row['product_url'],
                        short_description=row['short_description'],
                        long_description=row['long_description'],
                        robot_type=metadata.get('robot_type', 'humanoid'),
                        target_market=metadata.get('target_market', 'industry'),
                        availability=metadata.get('availability', 'announced'),
                        pricing_tier=metadata.get('pricing_tier', 'unknown'),
                        use_cases=metadata.get('use_cases', ''),
                        pros=metadata.get('pros', ''),
                        cons=metadata.get('cons', ''),
                        meta_title=metadata.get('meta_title', ''),
                        meta_description=metadata.get('meta_description', ''),
                        status='published',
                        is_featured=True
                    )
                    
                    # Find similar robots using vector search
                    similar_robot_names = []
                    try:
                        search_query = f"{row['robot_name']} {row['short_description']}"
                        similar_ids = RobotSearchService.search(search_query, n_results=4)
                        
                        for similar_id in similar_ids:
                            if similar_id != robot.id:
                                try:
                                    similar_robot = Robot.objects.get(id=similar_id)
                                    similar_robot_names.append(similar_robot.name)
                                    if len(similar_robot_names) >= 3:
                                        break
                                except Robot.DoesNotExist:
                                    continue
                    except Exception as e:
                        print(f"Similarity search error for {row['robot_name']}: {e}")
                    
                    # Add robot to vector database
                    try:
                        RobotSearchService.add_robots([robot])
                    except Exception as e:
                        print(f"Vector DB add error for {row['robot_name']}: {e}")
                    
                    row['status'] = 'success'
                    row['robot_id'] = robot.id
                    row['robot_slug'] = robot.slug
                    row['similar_robots'] = similar_robot_names
                    created_count += 1
                    
                except Exception as e:
                    row['status'] = 'error'
                    row['error'] = str(e)
                    error_count += 1
                
                results.append(row)
            
            # Clear session
            if 'bulk_upload_robot_rows' in request.session:
                del request.session['bulk_upload_robot_rows']
            
            context['step'] = 'complete'
            context['results'] = results
            context['created'] = created_count
            context['skipped'] = skipped_count
            context['errors'] = error_count
    
    return render(request, 'robots/admin/admin_bulk_upload_robots.html', context)

