from django.db import models
import json
from django.utils.html import strip_tags


class SEOModel(models.Model):
    """Abstract base class for SEO metadata."""
    meta_title = models.CharField(
        max_length=200, 
        blank=True, 
        help_text="Overwrites the default title. 50-60 chars recommended."
    )
    meta_description = models.TextField(
        blank=True, 
        help_text="Overwrites the default description. 150-160 chars recommended."
    )
    og_image = models.ImageField(
        upload_to='seo_images/', 
        blank=True, 
        null=True,
        help_text="Social share image (1200x630px recommended)."
    )
    canonical_url = models.URLField(
        blank=True, 
        help_text="Override canonical URL if needed (e.g., for syndicated content)."
    )

    class Meta:
        abstract = True
    
    def get_seo_title(self):
        return self.meta_title or str(self)

    def get_seo_description(self):
        return self.meta_description or ""

    def get_schema_json(self):
        """Override this in subclasses to return specific Schema.org JSON."""
        return "{}"


class Category(SEOModel):
    """Hierarchical category for tools (e.g., Construction -> Design -> BIM)."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Icon class name (e.g., 'fa-cube')")
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='children'
    )

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_schema_json(self):
        data = {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "name": self.name,
            "description": self.get_seo_description(),
            "url": f"/category/{self.slug}/"  # Placeholder until get_absolute_url is implemented
        }
        return json.dumps(data)


class Profession(SEOModel):
    """Target user role (e.g., Architect, Designer, Marketer)."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    hero_tagline = models.CharField(max_length=200, blank=True, help_text="e.g., 'AI tools that design faster'")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_seo_description(self):
        return self.meta_description or self.description[:160]

    def get_schema_json(self, tools=None):
        """Generate CollectionPage + ItemList schema for profession."""
        data = {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "name": f"AI Tools for {self.name}",
            "description": self.get_seo_description(),
            "url": f"/profession/{self.slug}/"
        }
        
        # Add ItemList if tools provided
        if tools:
            item_list = {
                "@type": "ItemList",
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": i,
                        "name": t.name,
                        "url": f"/tool/{t.slug}/"
                    }
                    for i, t in enumerate(tools[:10], 1)  # Limit to 10 for schema
                ]
            }
            data["mainEntity"] = item_list
        
        return json.dumps(data)

    def get_breadcrumb_json(self):
        """Generate BreadcrumbList schema for this profession."""
        items = [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": "/"},
            {"@type": "ListItem", "position": 2, "name": "Professions", "item": "/professions/"},
            {"@type": "ListItem", "position": 3, "name": self.name, "item": f"/profession/{self.slug}/"}
        ]
        
        data = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": items
        }
        return json.dumps(data)


class Tag(models.Model):
    """Feature tags (e.g., 'generative', 'automation', 'free')."""
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Tool(SEOModel):
    """Core AI Tool entity."""
    PRICING_CHOICES = [
        ('free', 'Free'),
        ('freemium', 'Freemium'),
        ('paid', 'Paid'),
    ]
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]

    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    logo = models.ImageField(upload_to='tool_logos/', blank=True, null=True)
    website_url = models.URLField()
    affiliate_url = models.URLField(blank=True)
    pricing_type = models.CharField(max_length=20, choices=PRICING_CHOICES, default='freemium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    categories = models.ManyToManyField(Category, related_name='tools', blank=True)
    professions = models.ManyToManyField(Profession, related_name='tools', blank=True)
    tags = models.ManyToManyField(Tag, related_name='tools', blank=True)
    
    is_featured = models.BooleanField(default=False)
    
    # Highlight period
    highlight_start = models.DateField(null=True, blank=True, help_text="Start date of highlight period")
    highlight_end = models.DateField(null=True, blank=True, help_text="End date of highlight period")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', '-created_at']

    def __str__(self):
        return self.name

    def get_translation(self, lang='en'):
        """Get translation for a specific language, fallback to English."""
        try:
            return self.translations.get(language=lang)
        except ToolTranslation.DoesNotExist:
            try:
                return self.translations.get(language='en')
            except ToolTranslation.DoesNotExist:
                return None
    
    def get_seo_description(self):
        if self.meta_description:
            return self.meta_description
        trans = self.get_translation('en')
        return trans.short_description[:160] if trans else ""

    def get_schema_json(self):
        """Generate SoftwareApplication schema with enhanced fields."""
        trans = self.get_translation('en')
        description = self.get_seo_description()
        
        data = {
            "@context": "https://schema.org",
            "@type": "SoftwareApplication",
            "name": self.name,
            "applicationCategory": "BusinessApplication",
            "operatingSystem": "Web",
            "offers": {
                "@type": "Offer",
                "price": "0" if self.pricing_type == 'free' else "0",
                "priceCurrency": "USD",
                "availability": "https://schema.org/InStock"
            },
            "description": description,
            "url": f"/tool/{self.slug}/",
            "datePublished": self.created_at.isoformat(),
            "dateModified": self.updated_at.isoformat(),
        }
        
        if self.logo:
            data["image"] = self.logo.url
        
        if self.pricing_type == 'paid':
            data["offers"]["price"] = "10.00"
        elif self.pricing_type == 'freemium':
            data["offers"]["price"] = "0"
            data["offers"]["priceValidUntil"] = "2099-12-31"
        
        # Add categories as keywords
        if self.categories.exists():
            data["keywords"] = ", ".join([c.name for c in self.categories.all()])
        
        return json.dumps(data)

    def get_breadcrumb_json(self, profession=None):
        """Generate BreadcrumbList schema for this tool."""
        items = [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": "/"},
        ]
        
        if profession:
            items.append({"@type": "ListItem", "position": 2, "name": profession.name, "item": f"/profession/{profession.slug}/"})
            items.append({"@type": "ListItem", "position": 3, "name": self.name, "item": f"/tool/{self.slug}/"})
        else:
            items.append({"@type": "ListItem", "position": 2, "name": self.name, "item": f"/tool/{self.slug}/"})
        
        data = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": items
        }
        return json.dumps(data)


class ToolTranslation(models.Model):
    """Multilingual content for Tool."""
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('hu', 'Hungarian'),
        ('de', 'German'),
    ]

    tool = models.ForeignKey(Tool, on_delete=models.CASCADE, related_name='translations')
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES)
    short_description = models.CharField(max_length=300)
    long_description = models.TextField(blank=True)
    use_cases = models.TextField(blank=True, help_text="Comma-separated use cases")
    pros = models.TextField(blank=True, help_text="Comma-separated pros")
    cons = models.TextField(blank=True, help_text="Comma-separated cons")

    class Meta:
        unique_together = ['tool', 'language']

    def __str__(self):
        return f"{self.tool.name} ({self.language})"

    def get_use_cases_list(self):
        return [uc.strip() for uc in self.use_cases.split(',') if uc.strip()]

    def get_pros_list(self):
        return [p.strip() for p in self.pros.split(',') if p.strip()]

    def get_cons_list(self):
        return [c.strip() for c in self.cons.split(',') if c.strip()]


from django.contrib.auth.models import User

class ToolStack(SEOModel):
    """Curated bundle of tools solving a specific workflow."""
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
    ]

    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='public')
    
    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    tagline = models.CharField(max_length=200)
    description = models.TextField()
    workflow_description = models.TextField(help_text="Step-by-step how these tools work together", null=True, blank=True, default="")
    
    tools = models.ManyToManyField(Tool, related_name='stacks')
    professions = models.ManyToManyField(Profession, related_name='stacks', blank=True)
    
    is_featured = models.BooleanField(default=False)
    
    # Highlight period
    highlight_start = models.DateField(null=True, blank=True, help_text="Start date of highlight period")
    highlight_end = models.DateField(null=True, blank=True, help_text="End date of highlight period")
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_featured', '-created_at']

    def __str__(self):
        return self.name

    def get_seo_description(self):
         return self.meta_description or self.description[:160]

    def get_schema_json(self):
        """Generate HowTo schema for workflow stacks."""
        tools_list = list(self.tools.all())
        
        # Build HowToStep from tools
        steps = []
        for i, tool in enumerate(tools_list, 1):
            trans = tool.get_translation('en')
            step = {
                "@type": "HowToStep",
                "position": i,
                "name": f"Use {tool.name}",
                "text": trans.short_description if trans else f"Integrate {tool.name} into your workflow.",
                "url": f"/tool/{tool.slug}/"
            }
            if tool.logo:
                step["image"] = tool.logo.url
            steps.append(step)
        
        data = {
            "@context": "https://schema.org",
            "@type": "HowTo",
            "name": self.name,
            "description": self.get_seo_description(),
            "totalTime": "PT30M",
            "step": steps,
            "tool": [{"@type": "HowToTool", "name": t.name} for t in tools_list],
            "datePublished": self.created_at.isoformat()
        }
        return json.dumps(data)

    def get_breadcrumb_json(self):
        """Generate BreadcrumbList schema for this stack."""
        items = [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": "/"},
            {"@type": "ListItem", "position": 2, "name": "Stacks", "item": "/stacks/"},
            {"@type": "ListItem", "position": 3, "name": self.name, "item": f"/stack/{self.slug}/"}
        ]
        
        data = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": items
        }
        return json.dumps(data)


class ToolMedia(models.Model):
    """Screenshots, videos, and other media for tools."""
    MEDIA_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('gif', 'GIF'),
    ]

    tool = models.ForeignKey(Tool, on_delete=models.CASCADE, related_name='media')
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES, default='image')
    file = models.FileField(upload_to='tool_media/')
    alt_text = models.CharField(max_length=200, blank=True, help_text="Alternative text for accessibility")
    caption = models.CharField(max_length=300, blank=True)
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Tool Media"
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"{self.tool.name} - {self.media_type} #{self.order}"


class SavedTool(models.Model):
    """User's saved/favorited tools."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_tools')
    tool = models.ForeignKey(Tool, on_delete=models.CASCADE, related_name='saved_by')
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, help_text="User's personal notes about this tool")

    class Meta:
        unique_together = ['user', 'tool']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} saved {self.tool.name}"


class SavedStack(models.Model):
    """User's saved/favorited stacks."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_stacks')
    stack = models.ForeignKey(ToolStack, on_delete=models.CASCADE, related_name='saved_by')
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, help_text="User's personal notes about this stack")

    class Meta:
        unique_together = ['user', 'stack']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} saved {self.stack.name}"


class ToolView(models.Model):
    """Analytics: Tracking tool page views."""
    tool = models.ForeignKey(Tool, on_delete=models.CASCADE, related_name='views')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_key = models.CharField(max_length=40, blank=True)
    source_page = models.CharField(max_length=100, default='tool_detail')
    ip_hash = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"View: {self.tool.name} @ {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class StackView(models.Model):
    """Analytics: Tracking stack page views."""
    stack = models.ForeignKey(ToolStack, on_delete=models.CASCADE, related_name='views')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_key = models.CharField(max_length=40, blank=True)
    source_page = models.CharField(max_length=100, default='stack_detail')
    ip_hash = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"View: {self.stack.name} @ {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class ProfessionView(models.Model):
    """Analytics: Tracking profession page views."""
    profession = models.ForeignKey(Profession, on_delete=models.CASCADE, related_name='views')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_key = models.CharField(max_length=40, blank=True)
    source_page = models.CharField(max_length=100, default='profession_detail')
    ip_hash = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"View: {self.profession.name} @ {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class SearchQuery(models.Model):
    """Analytics for search queries."""
    query = models.CharField(max_length=500)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_key = models.CharField(max_length=40, blank=True, help_text="Anonymous session tracking")
    results_count = models.PositiveIntegerField(default=0)
    clicked_tool = models.ForeignKey(Tool, on_delete=models.SET_NULL, null=True, blank=True, related_name='search_clicks')
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Search context
    source_page = models.CharField(max_length=100, default='U/N', help_text="Page where search was initiated")
    filters_applied = models.JSONField(default=dict, blank=True, help_text="Filters used in search")

    class Meta:
        verbose_name_plural = "Search Queries"
        ordering = ['-created_at']

    def __str__(self):
        return f"'{self.query}' ({self.results_count} results)"


class AffiliateClick(models.Model):
    """Tracking affiliate link clicks for analytics and revenue."""
    tool = models.ForeignKey(Tool, on_delete=models.CASCADE, related_name='affiliate_clicks')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_key = models.CharField(max_length=40, blank=True)
    
    # Click context
    source_page = models.CharField(max_length=200, help_text="Page where click originated")
    referrer = models.URLField(blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    ip_hash = models.CharField(max_length=64, blank=True, help_text="Hashed IP for fraud detection")
    
    # Timestamps
    clicked_at = models.DateTimeField(auto_now_add=True)
    
    # Conversion tracking (updated via webhook or manual)
    converted = models.BooleanField(default=False)
    conversion_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    converted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-clicked_at']

    def __str__(self):
        status = "✓" if self.converted else "○"
        return f"{status} {self.tool.name} click @ {self.clicked_at.strftime('%Y-%m-%d %H:%M')}"


class NewsletterSubscriber(models.Model):
    """Newsletter subscriber email."""
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.email


class SubmittedTool(models.Model):
    """Tools submitted by users for approval."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submitted_tools')
    name = models.CharField(max_length=150)
    website_url = models.URLField()
    description = models.TextField(blank=True)
    recommended_profession = models.CharField(max_length=100, blank=True, help_text="The main profession this tool is for")
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} (by {self.user.username})"
