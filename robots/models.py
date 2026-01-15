"""
AI Robots Models

This module defines the core models for the AI Robots feature:
- RobotCompany: Robot manufacturers (Boston Dynamics, Tesla, etc.)
- Robot: Core robot entity with specs, pricing, availability
- RobotNews: News articles linked to robots
- RobotView: Analytics tracking for robot page views
- SavedRobot: User wishlisted/saved robots
"""

import json
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class RobotCompany(models.Model):
    """Robot manufacturer/company profile with SEO support."""
    
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(unique=True)
    logo = models.ImageField(upload_to='robot_company_logos/', blank=True, null=True)
    
    # Company Info
    description = models.TextField(blank=True)
    founded_year = models.PositiveIntegerField(null=True, blank=True)
    headquarters = models.CharField(max_length=200, blank=True)
    website = models.URLField(blank=True)
    
    # Social Links
    twitter_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    
    # SEO Fields
    meta_title = models.CharField(
        max_length=200, blank=True,
        help_text="50-60 chars recommended. Format: 'CompanyName - AI Robotics | AIJACK'"
    )
    meta_description = models.TextField(
        blank=True,
        help_text="150-160 chars. Compelling summary with call-to-action."
    )
    og_image = models.ImageField(
        upload_to='seo_images/', blank=True, null=True,
        help_text="Open Graph image (1200x630px recommended)"
    )
    canonical_url = models.URLField(blank=True, help_text="Override canonical URL if needed")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Robot Company"
        verbose_name_plural = "Robot Companies"

    def __str__(self):
        return self.name
    
    @property
    def robot_count(self):
        """Returns count of published robots from this company."""
        return self.robots.filter(status='published').count()
    
    def get_seo_title(self):
        """Returns meta_title or generates default."""
        return self.meta_title or f"{self.name} - AI Robotics Company | AIJACK"
    
    def get_seo_description(self):
        """Returns meta_description or excerpt from description."""
        return self.meta_description or (self.description[:160] if self.description else "")
    
    def get_schema_json(self):
        """Generate Organization schema for structured data."""
        data = {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": self.name,
            "description": self.get_seo_description(),
            "url": f"/robots/company/{self.slug}/"
        }
        if self.logo:
            data["logo"] = self.logo.url
        if self.website:
            data["sameAs"] = [self.website]
            social_links = [self.twitter_url, self.linkedin_url, self.youtube_url]
            data["sameAs"].extend([url for url in social_links if url])
        if self.founded_year:
            data["foundingDate"] = str(self.founded_year)
        if self.headquarters:
            data["location"] = {"@type": "Place", "name": self.headquarters}
        return json.dumps(data)
    
    def get_breadcrumb_json(self):
        """Generate BreadcrumbList schema."""
        items = [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": "/"},
            {"@type": "ListItem", "position": 2, "name": "AI Robots", "item": "/robots/"},
            {"@type": "ListItem", "position": 3, "name": "Companies", "item": "/robots/companies/"},
            {"@type": "ListItem", "position": 4, "name": self.name, "item": f"/robots/company/{self.slug}/"},
        ]
        return json.dumps({
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": items
        })


class Robot(models.Model):
    """Core AI Robot entity with full SEO support."""
    
    # Type Choices
    TYPE_CHOICES = [
        ('humanoid', 'Humanoid'),
        ('specialized', 'Specialized'),
    ]
    
    TARGET_CHOICES = [
        ('home', 'Home/Consumer'),
        ('industry', 'Industrial'),
        ('medical', 'Medical'),
        ('service', 'Service/Hospitality'),
        ('military', 'Military/Defense'),
        ('research', 'Research'),
    ]
    
    AVAILABILITY_CHOICES = [
        ('available', 'Available Now'),
        ('preorder', 'Pre-order'),
        ('announced', 'Announced'),
        ('development', 'In Development'),
        ('prototype', 'Prototype'),
        ('discontinued', 'Discontinued'),
    ]
    
    PRICING_CHOICES = [
        ('unknown', 'Unknown'),
        ('consumer', 'Consumer ($1K - $10K)'),
        ('prosumer', 'Prosumer ($10K - $50K)'),
        ('professional', 'Professional ($50K - $200K)'),
        ('enterprise', 'Enterprise ($200K+)'),
        ('lease', 'Lease Only'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]

    # Basic Info
    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    company = models.ForeignKey(
        RobotCompany, on_delete=models.CASCADE, related_name='robots'
    )
    product_url = models.URLField(help_text="Official product page URL", blank=True)
    
    # Images
    image = models.ImageField(upload_to='robot_images/', blank=True, null=True)
    
    # Classification
    robot_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='humanoid')
    target_market = models.CharField(max_length=20, choices=TARGET_CHOICES, default='home')
    
    # Release Info
    release_date = models.DateField(null=True, blank=True, help_text="Actual or expected release date")
    availability = models.CharField(max_length=20, choices=AVAILABILITY_CHOICES, default='announced')
    
    # Pricing
    pricing_tier = models.CharField(max_length=20, choices=PRICING_CHOICES, default='unknown')
    price_value = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
        help_text="Exact price if known (in USD)"
    )
    
    # Content
    short_description = models.CharField(max_length=300)
    long_description = models.TextField(blank=True)
    pros = models.TextField(blank=True, help_text="Comma-separated pros")
    cons = models.TextField(blank=True, help_text="Comma-separated cons")
    use_cases = models.TextField(blank=True, help_text="Comma-separated use cases")
    
    # Technical Specs (JSON field for flexibility)
    specifications = models.JSONField(
        default=dict, blank=True,
        help_text="Technical specs: {height, weight, battery_life, payload, speed, etc.}"
    )
    
    # Cross-app relationship
    compatible_tools = models.ManyToManyField(
        'tools.Tool',
        related_name='compatible_robots',
        blank=True,
        help_text="AI software tools that integrate with this robot"
    )
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False)
    
    # SEO Fields
    meta_title = models.CharField(
        max_length=200, blank=True,
        help_text="50-60 chars recommended. Format: 'RobotName - Description | AIJACK'"
    )
    meta_description = models.TextField(
        blank=True,
        help_text="150-160 chars. Compelling summary with call-to-action."
    )
    og_image = models.ImageField(
        upload_to='seo_images/', blank=True, null=True,
        help_text="Open Graph image (1200x630px recommended)"
    )
    canonical_url = models.URLField(blank=True, help_text="Override canonical URL if needed")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', '-created_at']
        verbose_name = "AI Robot"
        verbose_name_plural = "AI Robots"

    def __str__(self):
        return f"{self.name} by {self.company.name}"
    
    # Content helpers
    def get_pros_list(self):
        """Parse comma-separated pros into list."""
        return [p.strip() for p in self.pros.split(',') if p.strip()]
    
    def get_cons_list(self):
        """Parse comma-separated cons into list."""
        return [c.strip() for c in self.cons.split(',') if c.strip()]
    
    def get_use_cases_list(self):
        """Parse comma-separated use cases into list."""
        return [uc.strip() for uc in self.use_cases.split(',') if uc.strip()]
    
    # SEO Methods
    def get_seo_title(self):
        """Returns meta_title or generates default."""
        if self.meta_title:
            return self.meta_title
        return f"{self.name} - {self.get_robot_type_display()} Robot by {self.company.name} | AIJACK"
    
    def get_seo_description(self):
        """Returns meta_description or short_description."""
        return self.meta_description or self.short_description[:160]
    
    def _get_availability_schema(self):
        """Map availability to schema.org values."""
        mapping = {
            'available': 'https://schema.org/InStock',
            'preorder': 'https://schema.org/PreOrder',
            'announced': 'https://schema.org/PreOrder',
            'development': 'https://schema.org/PreOrder',
            'prototype': 'https://schema.org/OutOfStock',
            'discontinued': 'https://schema.org/Discontinued',
        }
        return mapping.get(self.availability, 'https://schema.org/PreOrder')
    
    def get_schema_json(self):
        """Generate Product schema for structured data."""
        data = {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": self.name,
            "description": self.get_seo_description(),
            "brand": {
                "@type": "Brand",
                "name": self.company.name
            },
            "category": "AI Robot",
            "url": f"/robot/{self.slug}/",
            "manufacturer": {
                "@type": "Organization",
                "name": self.company.name,
                "url": f"/robots/company/{self.company.slug}/"
            }
        }
        
        if self.image:
            data["image"] = self.image.url
        
        if self.release_date:
            data["releaseDate"] = self.release_date.isoformat()
        
        if self.price_value:
            data["offers"] = {
                "@type": "Offer",
                "price": str(self.price_value),
                "priceCurrency": "USD",
                "availability": self._get_availability_schema(),
                "url": self.product_url or f"/robot/{self.slug}/"
            }
        
        # Add keywords from use cases
        if self.use_cases:
            data["keywords"] = self.use_cases
        
        return json.dumps(data)
    
    def get_breadcrumb_json(self):
        """Generate BreadcrumbList schema."""
        items = [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": "/"},
            {"@type": "ListItem", "position": 2, "name": "AI Robots", "item": "/robots/"},
            {"@type": "ListItem", "position": 3, "name": self.company.name, "item": f"/robots/company/{self.company.slug}/"},
            {"@type": "ListItem", "position": 4, "name": self.name, "item": f"/robot/{self.slug}/"},
        ]
        return json.dumps({
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": items
        })
    
    def get_missing_fields(self):
        """Return a list of missing important fields for admin completeness indicator."""
        missing = []
        
        if not self.short_description:
            missing.append('Short Description')
        if not self.long_description:
            missing.append('Long Description')
        if not self.image:
            missing.append('Image')
        if not self.pros:
            missing.append('Pros')
        if not self.cons:
            missing.append('Cons')
        if not self.use_cases:
            missing.append('Use Cases')
        if not self.product_url:
            missing.append('Product URL')
        if not self.meta_title:
            missing.append('Meta Title')
        if not self.meta_description:
            missing.append('Meta Description')
        
        return missing


class RobotNews(models.Model):
    """News articles linked to robots with SEO support."""
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    excerpt = models.CharField(max_length=300, help_text="Short summary for listings")
    
    # Linked robots
    robots = models.ManyToManyField(Robot, related_name='news_articles', blank=True)
    
    # Source
    source_name = models.CharField(max_length=100, blank=True, help_text="Original source name")
    source_url = models.URLField(blank=True, help_text="Link to original article")
    
    # Image
    featured_image = models.ImageField(upload_to='robot_news/', blank=True, null=True)
    
    # Publishing
    published_at = models.DateTimeField()
    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    
    # SEO Fields
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    og_image = models.ImageField(upload_to='seo_images/', blank=True, null=True)
    canonical_url = models.URLField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at']
        verbose_name = "Robot News"
        verbose_name_plural = "Robot News"

    def __str__(self):
        return self.title
    
    def get_seo_title(self):
        return self.meta_title or f"{self.title} | AI Robots News | AIJACK"
    
    def get_seo_description(self):
        return self.meta_description or self.excerpt[:160]
    
    def get_schema_json(self):
        """Generate NewsArticle schema."""
        data = {
            "@context": "https://schema.org",
            "@type": "NewsArticle",
            "headline": self.title,
            "description": self.get_seo_description(),
            "datePublished": self.published_at.isoformat(),
            "dateModified": self.updated_at.isoformat(),
            "url": f"/robots/news/{self.slug}/",
            "author": {
                "@type": "Organization",
                "name": "AIJACK"
            },
            "publisher": {
                "@type": "Organization",
                "name": "AIJACK",
                "url": "/"
            }
        }
        
        if self.featured_image:
            data["image"] = self.featured_image.url
        
        # Add mentions for linked robots
        robot_mentions = []
        for robot in self.robots.all()[:5]:
            robot_mentions.append({
                "@type": "Product",
                "name": robot.name,
                "url": f"/robot/{robot.slug}/"
            })
        if robot_mentions:
            data["mentions"] = robot_mentions
        
        return json.dumps(data)
    
    def get_breadcrumb_json(self):
        """Generate BreadcrumbList schema."""
        items = [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": "/"},
            {"@type": "ListItem", "position": 2, "name": "AI Robots", "item": "/robots/"},
            {"@type": "ListItem", "position": 3, "name": "News", "item": "/robots/news/"},
            {"@type": "ListItem", "position": 4, "name": self.title[:50], "item": f"/robots/news/{self.slug}/"},
        ]
        return json.dumps({
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": items
        })


class RobotView(models.Model):
    """Analytics: Tracking robot page views."""
    
    robot = models.ForeignKey(Robot, on_delete=models.CASCADE, related_name='views')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_key = models.CharField(max_length=40, blank=True)
    source_page = models.CharField(max_length=100, default='robot_detail')
    ip_hash = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Robot View"
        verbose_name_plural = "Robot Views"

    def __str__(self):
        return f"View: {self.robot.name} at {self.created_at}"


class SavedRobot(models.Model):
    """User's saved/favorited robots."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_robots')
    robot = models.ForeignKey(Robot, on_delete=models.CASCADE, related_name='saved_by')
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, help_text="Personal notes about this robot")

    class Meta:
        unique_together = ['user', 'robot']
        ordering = ['-created_at']
        verbose_name = "Saved Robot"
        verbose_name_plural = "Saved Robots"

    def __str__(self):
        return f"{self.user.username} saved {self.robot.name}"
