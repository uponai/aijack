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

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_seo_description(self):
        return self.meta_description or self.description[:160]

    def get_schema_json(self):
        data = {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "name": f"AI Tools for {self.name}",
            "description": self.get_seo_description(),
            "url": f"/profession/{self.slug}/"
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
                "price": "0" if self.pricing_type == 'free' else "0", # Simplified
                "priceCurrency": "USD"
            },
            "description": description,
            "url": f"/tool/{self.slug}/",
            "image": self.logo.url if self.logo else ""
        }
        
        if self.pricing_type == 'paid':
             data["offers"]["price"] = "10.00" # Placeholder, implies paid
        
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


class ToolStack(SEOModel):
    """Curated bundle of tools solving a specific workflow."""
    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    tagline = models.CharField(max_length=200)
    description = models.TextField()
    workflow_description = models.TextField(help_text="Step-by-step how these tools work together")
    
    tools = models.ManyToManyField(Tool, related_name='stacks')
    professions = models.ManyToManyField(Profession, related_name='stacks', blank=True)
    
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_featured', '-created_at']

    def __str__(self):
        return self.name

    def get_seo_description(self):
         return self.meta_description or self.description[:160]

    def get_schema_json(self):
        data = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": self.name,
            "description": self.get_seo_description(),
            "url": f"/stacks/{self.slug}/",
            "datePublished": self.created_at.isoformat()
        }
        return json.dumps(data)
