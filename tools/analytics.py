"""
Analytics Service for AIJACK
Handles tracking of searches, tool clicks, and stack views.
"""
import hashlib
from django.utils import timezone
from .models import SearchQuery, AffiliateClick, Tool, ToolStack


class AnalyticsService:
    """Service class for tracking user analytics."""
    
    @staticmethod
    def hash_ip(ip_address):
        """Hash IP address for privacy-safe storage."""
        if not ip_address:
            return ""
        return hashlib.sha256(ip_address.encode()).hexdigest()[:32]
    
    @staticmethod
    def get_client_ip(request):
        """Extract client IP from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '')
    
    @classmethod
    def log_search(cls, request, query, results_count, clicked_tool=None, source_page='search', filters=None):
        """
        Log a search query for analytics.
        
        Args:
            request: Django HTTP request
            query: Search query string
            results_count: Number of results returned
            clicked_tool: Tool instance if user clicked on a result
            source_page: Page where search was initiated
            filters: Dict of applied filters
        """
        user = request.user if request.user.is_authenticated else None
        session_key = request.session.session_key or ''
        
        return SearchQuery.objects.create(
            query=query[:500],  # Truncate to field max length
            user=user,
            session_key=session_key,
            results_count=results_count,
            clicked_tool=clicked_tool,
            source_page=source_page or 'U/N',
            filters_applied=filters or {}
        )
    
    @classmethod
    def log_tool_click(cls, request, tool, source_page='tool_detail'):
        """
        Log when a user clicks on a tool (for affiliate/analytics).
        
        Args:
            request: Django HTTP request
            tool: Tool instance
            source_page: Page where click originated
        """
        user = request.user if request.user.is_authenticated else None
        session_key = request.session.session_key or ''
        ip_hash = cls.hash_ip(cls.get_client_ip(request))
        
        return AffiliateClick.objects.create(
            tool=tool,
            user=user,
            session_key=session_key,
            source_page=source_page,
            referrer=request.META.get('HTTP_REFERER', '')[:200],
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
            ip_hash=ip_hash
        )
    
    @classmethod
    def log_stack_view(cls, request, stack, source_page='stack_detail'):
        """
        Log when a user views a stack.
        We'll reuse SearchQuery with special source_page for simplicity.
        """
        user = request.user if request.user.is_authenticated else None
        session_key = request.session.session_key or ''
        
        return SearchQuery.objects.create(
            query=f"[STACK_VIEW] {stack.name}",
            user=user,
            session_key=session_key,
            results_count=stack.tools.count(),
            source_page=source_page,
            filters_applied={'stack_id': stack.id, 'stack_slug': stack.slug}
        )
    
    @classmethod
    def get_top_clicked_tools(cls, limit=10, days=30):
        """Get most clicked tools in the last N days."""
        from django.db.models import Count
        since = timezone.now() - timezone.timedelta(days=days)
        
        return Tool.objects.filter(
            affiliate_clicks__clicked_at__gte=since
        ).annotate(
            click_count=Count('affiliate_clicks')
        ).order_by('-click_count')[:limit]
    
    @classmethod
    def get_top_viewed_stacks(cls, limit=10, days=30):
        """Get most viewed stacks in the last N days."""
        from django.db.models import Count
        since = timezone.now() - timezone.timedelta(days=days)
        
        # Get stack views from SearchQuery
        stack_views = SearchQuery.objects.filter(
            query__startswith='[STACK_VIEW]',
            created_at__gte=since
        ).values('filters_applied__stack_id').annotate(
            view_count=Count('id')
        ).order_by('-view_count')[:limit]
        
        # Get actual stack objects
        stack_ids = [sv['filters_applied__stack_id'] for sv in stack_views if sv['filters_applied__stack_id']]
        stacks = ToolStack.objects.filter(id__in=stack_ids)
        
        # Attach view counts
        view_counts = {sv['filters_applied__stack_id']: sv['view_count'] for sv in stack_views}
        for stack in stacks:
            stack.view_count = view_counts.get(stack.id, 0)
        
        return sorted(stacks, key=lambda x: x.view_count, reverse=True)
    
    @classmethod
    def get_recent_searches(cls, limit=100, days=7):
        """Get recent search queries."""
        since = timezone.now() - timezone.timedelta(days=days)
        return SearchQuery.objects.filter(
            created_at__gte=since
        ).exclude(
            query__startswith='[STACK_VIEW]'
        ).order_by('-created_at')[:limit]
    
    @classmethod
    def get_search_stats(cls, days=30):
        """Get aggregated search statistics."""
        from django.db.models import Count, Avg
        since = timezone.now() - timezone.timedelta(days=days)
        
        queries = SearchQuery.objects.filter(
            created_at__gte=since
        ).exclude(
            query__startswith='[STACK_VIEW]'
        )
        
        return {
            'total_searches': queries.count(),
            'unique_queries': queries.values('query').distinct().count(),
            'avg_results': queries.aggregate(avg=Avg('results_count'))['avg'] or 0,
            'with_clicks': queries.exclude(clicked_tool=None).count(),
        }
    
    @classmethod
    def get_click_stats(cls, days=30):
        """Get aggregated click statistics."""
        from django.db.models import Count, Sum
        since = timezone.now() - timezone.timedelta(days=days)
        
        clicks = AffiliateClick.objects.filter(clicked_at__gte=since)
        
        return {
            'total_clicks': clicks.count(),
            'unique_tools': clicks.values('tool').distinct().count(),
            'conversions': clicks.filter(converted=True).count(),
            'total_revenue': clicks.filter(converted=True).aggregate(
                total=Sum('conversion_value')
            )['total'] or 0,
        }
