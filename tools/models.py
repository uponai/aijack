from django.db import models


class Category(models.Model):
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


class Profession(models.Model):
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


class Tag(models.Model):
    """Feature tags (e.g., 'generative', 'automation', 'free')."""
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Tool(models.Model):
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


class ToolStack(models.Model):
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
