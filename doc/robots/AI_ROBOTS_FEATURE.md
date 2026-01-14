# AI Robots Feature Specification

## Overview

The AI Robots section is a major new feature that introduces a dedicated category for showcasing physical AI-powered robots. This section will exist alongside the existing Tools, Professions, and Stacks sections, following the same design patterns while introducing unique visual elements that match the robotic/futuristic theme.

---

## 1. Data Model

### 1.1 Robot Model

Create a new `Robot` model in `tools/models.py` that extends `SEOModel` (like `Tool` and `ToolStack`).

```python
class Robot(SEOModel):
    """AI-powered physical robot entity."""
    
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
    company = models.CharField(max_length=150, help_text="Manufacturer/Company name")
    company_website = models.URLField(blank=True)
    product_url = models.URLField(help_text="Official product page URL")
    
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
    price_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, 
                                       help_text="Exact price if known (in USD)")
    
    # Descriptions
    short_description = models.CharField(max_length=300)
    long_description = models.TextField(blank=True)
    
    # Pros/Cons/Use Cases
    pros = models.TextField(blank=True, help_text="Comma-separated pros")
    cons = models.TextField(blank=True, help_text="Comma-separated cons")
    use_cases = models.TextField(blank=True, help_text="Comma-separated use cases")
    
    # Technical Specs (JSON field for flexibility)
    specifications = models.JSONField(default=dict, blank=True, 
                                       help_text="Technical specifications (height, weight, battery, etc.)")
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', '-created_at']
        verbose_name = "AI Robot"
        verbose_name_plural = "AI Robots"

    def __str__(self):
        return f"{self.name} by {self.company}"
    
    def get_pros_list(self):
        return [p.strip() for p in self.pros.split(',') if p.strip()]
    
    def get_cons_list(self):
        return [c.strip() for c in self.cons.split(',') if c.strip()]
    
    def get_use_cases_list(self):
        return [uc.strip() for uc in self.use_cases.split(',') if uc.strip()]
    
    def get_seo_description(self):
        return self.meta_description or self.short_description[:160]
    
    def get_schema_json(self):
        """Generate Product schema for robot."""
        data = {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": self.name,
            "description": self.get_seo_description(),
            "brand": {
                "@type": "Brand",
                "name": self.company
            },
            "category": "Robot",
            "url": f"/robots/{self.slug}/"
        }
        if self.image:
            data["image"] = self.image.url
        if self.price_value:
            data["offers"] = {
                "@type": "Offer",
                "price": str(self.price_value),
                "priceCurrency": "USD"
            }
        return json.dumps(data)
    
    def get_missing_fields(self):
        """Return a list of missing important fields."""
        missing = []
        if not self.short_description:
            missing.append('Short Description')
        if not self.image:
            missing.append('Image')
        if not self.pros:
            missing.append('Pros')
        if not self.cons:
            missing.append('Cons')
        if not self.use_cases:
            missing.append('Use Cases')
        if not self.meta_title:
            missing.append('Meta Title')
        if not self.meta_description:
            missing.append('Meta Description')
        return missing
```

### 1.2 Analytics Models

Create corresponding analytics models:

```python
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
```

### 1.3 SavedRobot Model

```python
class SavedRobot(models.Model):
    """User's saved/favorited robots."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_robots')
    robot = models.ForeignKey(Robot, on_delete=models.CASCADE, related_name='saved_by')
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ['user', 'robot']
        ordering = ['-created_at']
```

---

## 2. Search Integration (ChromaDB)

### 2.1 Add Robots Collection

Extend `tools/search.py` `SearchService` class:

```python
@classmethod
def add_robots(cls, robots):
    """Add or update robots in the vector database."""
    collection = cls.get_collection("robots")
    embedding_fn = cls.get_embedding_function()
    
    ids, documents, metadatas, embeddings = [], [], [], []
    
    for robot in robots:
        text = f"Name: {robot.name}. Company: {robot.company}. " \
               f"Description: {robot.short_description} {robot.long_description}. " \
               f"Type: {robot.get_robot_type_display()}. " \
               f"Target: {robot.get_target_market_display()}. " \
               f"Use Cases: {robot.use_cases}"
        
        ids.append(str(robot.id))
        documents.append(text)
        metadatas.append({
            "name": robot.name,
            "company": robot.company,
            "robot_type": robot.robot_type,
            "target_market": robot.target_market,
            "slug": robot.slug,
            "entity_type": "robot"  # Important for filtering
        })
        embeddings.append(embedding_fn([text])[0])
    
    if ids:
        collection.upsert(ids=ids, documents=documents, 
                          metadatas=metadatas, embeddings=embeddings)
        return len(ids)
    return 0

@classmethod
def remove_robots(cls, robots):
    """Remove robots from the vector database."""
    collection = cls.get_collection("robots")
    ids = [str(r.id) if hasattr(r, 'id') else str(r) for r in robots]
    if ids:
        collection.delete(ids=ids)
        return len(ids)
    return 0
```

### 2.2 Update clear_index Method

```python
@classmethod
def clear_index(cls, models=None):
    client = cls.get_client()
    all_models = ['tools', 'stacks', 'professions', 'robots']  # Add robots
    target_models = models if models else all_models
    # ... rest of the method
```

---

## 3. URL Routes

Add to `tools/urls.py`:

```python
# Robot Section (Public)
path('robots/', views.robots_list, name='robots'),
path('robot/<slug:slug>/', views.robot_detail, name='robot_detail'),

# Robot Admin Management
path('admin-dashboard/robots/', views.admin_robots, name='admin_robots'),
path('admin-dashboard/robots/add/', views.admin_robot_create, name='admin_robot_create'),
path('admin-dashboard/robots/<slug:slug>/edit/', views.admin_robot_edit, name='admin_robot_edit'),
path('admin-dashboard/robots/<slug:slug>/delete/', views.admin_robot_delete, name='admin_robot_delete'),
path('admin-dashboard/robots/<slug:slug>/ai-complete/', views.ai_complete_robot, name='ai_complete_robot'),

# API
path('api/save-robot/<int:robot_id>/', views.toggle_save_robot, name='toggle_save_robot'),
```

---

## 4. Views

### 4.1 Public Views

```python
def robots_list(request):
    """List all published AI robots with filters."""
    robots = Robot.objects.filter(status='published')
    
    # Filtering
    robot_type = request.GET.get('type')
    target_market = request.GET.get('target')
    availability = request.GET.get('availability')
    company = request.GET.get('company')
    
    if robot_type:
        robots = robots.filter(robot_type=robot_type)
    if target_market:
        robots = robots.filter(target_market=target_market)
    if availability:
        robots = robots.filter(availability=availability)
    if company:
        robots = robots.filter(company__icontains=company)
    
    # Get unique companies for filter dropdown
    companies = Robot.objects.filter(status='published').values_list('company', flat=True).distinct()
    
    return render(request, 'robots.html', {
        'robots': robots,
        'companies': companies,
        'robot_types': Robot.TYPE_CHOICES,
        'target_markets': Robot.TARGET_CHOICES,
        'availability_choices': Robot.AVAILABILITY_CHOICES,
        'selected_type': robot_type,
        'selected_target': target_market,
        'selected_availability': availability,
        'selected_company': company,
    })

def robot_detail(request, slug):
    """Single robot detail page."""
    robot = get_object_or_404(Robot, slug=slug, status='published')
    
    # Track view
    RobotView.objects.create(
        robot=robot,
        user=request.user if request.user.is_authenticated else None,
        session_key=request.session.session_key or '',
        ip_hash=hashlib.sha256(get_client_ip(request).encode()).hexdigest()[:32]
    )
    
    # Related robots (same type or company)
    related = Robot.objects.filter(
        status='published'
    ).filter(
        Q(company=robot.company) | Q(robot_type=robot.robot_type)
    ).exclude(id=robot.id)[:6]
    
    return render(request, 'robot_detail.html', {
        'robot': robot,
        'related_robots': related,
    })
```

### 4.2 Admin Views

Follow the pattern from `admin_tools`, `admin_stacks`, `admin_professions`:

```python
@user_passes_test(lambda u: u.is_superuser)
def admin_robots(request):
    """Admin: List and manage robots."""
    robots = Robot.objects.all()
    query = request.GET.get('q', '')
    filter_type = request.GET.get('filter', 'all')
    
    if query:
        robots = robots.filter(Q(name__icontains=query) | Q(company__icontains=query))
    
    if filter_type == 'incomplete':
        # Filter for robots with missing fields
        robots = [r for r in robots if r.get_missing_fields()]
    
    # Add missing_fields attribute for template
    for robot in robots:
        robot.missing_fields = robot.get_missing_fields()
    
    paginator = Paginator(list(robots) if filter_type == 'incomplete' else robots, 20)
    page = request.GET.get('page', 1)
    robots = paginator.get_page(page)
    
    return render(request, 'admin_robots_list.html', {
        'robots': robots,
        'query': query,
        'filter_type': filter_type,
    })
```

---

## 5. Search Page Modification

### 5.1 Add "Robots Only" Checkbox

Modify `templates/search.html` to add the checkbox:

```html
<div class="mt-3 flex flex-wrap justify-center gap-4">
    <label class="inline-flex items-center cursor-pointer">
        <input type="checkbox" name="community" class="form-checkbox w-5 h-5 text-brand-600 rounded bg-slate-100 border-slate-300 focus:ring-brand-500" {% if request.GET.community %}checked{% endif %}>
        <span class="ml-2 text-slate-600">Search in other users' public stacks too</span>
    </label>
    
    <!-- NEW: Robots Only Checkbox -->
    <label class="inline-flex items-center cursor-pointer">
        <input type="checkbox" name="robots_only" class="form-checkbox w-5 h-5 text-cyan-600 rounded bg-slate-100 border-slate-300 focus:ring-cyan-500" {% if request.GET.robots_only %}checked{% endif %}>
        <span class="ml-2 text-slate-600">
            <i class="fa-solid fa-robot text-cyan-500 mr-1"></i>
            Search for AI robotic solutions only
        </span>
    </label>
</div>
```

### 5.2 Modify Search View

In `views.py`, update the `search` function:

```python
def search(request):
    query = request.GET.get('q', '').strip()
    include_community = request.GET.get('community') == 'on'
    robots_only = request.GET.get('robots_only') == 'on'
    
    tools = []
    stacks = []
    professions = []
    robots = []
    
    if query:
        if robots_only:
            # Search only in robots collection
            robot_ids = SearchService.search(query, n_results=30, collection_name='robots')
            if robot_ids:
                robots = list(Robot.objects.filter(id__in=robot_ids, status='published'))
        else:
            # Existing search logic for tools, stacks, professions
            # ... plus add robots search
            robot_ids = SearchService.search(query, n_results=10, collection_name='robots')
            if robot_ids:
                robots = list(Robot.objects.filter(id__in=robot_ids, status='published'))
    
    return render(request, 'search.html', {
        'query': query,
        'tools': tools,
        'stacks': stacks,
        'professions': professions,
        'robots': robots,  # Add robots to context
    })
```

---

## 6. Templates

### 6.1 Main Listing Page: `templates/robots.html`

Design Theme: **Futuristic, Industrial, Neon Cyan/Teal Accents**

```html
{% extends 'base.html' %}

{% block title %}AI Robots - Physical AI-Powered Robotic Solutions | AIJACK{% endblock %}
{% block meta_description %}Explore cutting-edge AI robots from leading companies. Humanoid and specialized robots for home, industry, and beyond.{% endblock %}

{% block schema %}
<script type="application/ld+json">
{
    "@context": "https://schema.org",
    "@type": "CollectionPage",
    "name": "AI Robots",
    "description": "Directory of AI-powered physical robots and robotic solutions.",
    "url": "/robots/"
}
</script>
{% endblock %}

{% block content %}
<section class="py-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        <!-- Hero Section with Futuristic Design -->
        <div class="text-center mb-8 relative">
            <!-- Animated Grid Background -->
            <div class="absolute inset-0 bg-gradient-to-b from-cyan-50/50 to-transparent rounded-3xl -z-10"></div>
            
            <div class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-cyan-100 border border-cyan-200 mb-4">
                <i class="fa-solid fa-robot text-cyan-600 animate-pulse"></i>
                <span class="font-heading font-bold text-cyan-700 text-sm tracking-wider uppercase">Physical AI</span>
            </div>
            
            <h1 class="text-3xl md:text-4xl font-heading font-black text-slate-900 mb-3">
                AI <span class="text-cyan-600 glow-text-cyan">ROBOTS</span>
            </h1>
            <p class="text-base text-slate-600 max-w-2xl mx-auto mb-4">
                The future of physical AI - from humanoid companions to industrial powerhouses.
            </p>
            
            <div class="inline-flex items-center gap-3 px-4 py-2 rounded-xl bg-slate-900 text-white">
                <i class="fa-solid fa-microchip text-cyan-400"></i>
                <span class="font-heading font-bold text-cyan-400">{{ robots|length }}</span>
                <span class="text-slate-400 text-sm">Robots Indexed</span>
            </div>
        </div>

        <!-- Filters -->
        <div class="bg-white/80 backdrop-blur-sm rounded-2xl border border-slate-200 p-4 mb-6">
            <form method="GET" class="flex flex-wrap gap-4 items-center">
                <select name="type" class="rounded-lg border-slate-300 text-sm">
                    <option value="">All Types</option>
                    {% for value, label in robot_types %}
                    <option value="{{ value }}" {% if selected_type == value %}selected{% endif %}>{{ label }}</option>
                    {% endfor %}
                </select>
                
                <select name="target" class="rounded-lg border-slate-300 text-sm">
                    <option value="">All Markets</option>
                    {% for value, label in target_markets %}
                    <option value="{{ value }}" {% if selected_target == value %}selected{% endif %}>{{ label }}</option>
                    {% endfor %}
                </select>
                
                <select name="company" class="rounded-lg border-slate-300 text-sm">
                    <option value="">All Companies</option>
                    {% for comp in companies %}
                    <option value="{{ comp }}" {% if selected_company == comp %}selected{% endif %}>{{ comp }}</option>
                    {% endfor %}
                </select>
                
                <button type="submit" class="px-4 py-2 bg-cyan-600 text-white rounded-lg font-semibold text-sm hover:bg-cyan-700 transition">
                    <i class="fa-solid fa-filter mr-2"></i>Filter
                </button>
            </form>
        </div>

        <!-- Robot Cards Grid -->
        <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {% for robot in robots %}
            {% include 'includes/_robot_card.html' with robot=robot %}
            {% empty %}
            <div class="col-span-full text-center py-16">
                <div class="w-24 h-24 mx-auto mb-6 rounded-2xl bg-cyan-100 flex items-center justify-center">
                    <i class="fa-solid fa-robot text-4xl text-cyan-600"></i>
                </div>
                <h3 class="font-heading font-bold text-xl text-slate-900 mb-2">No Robots Found</h3>
                <p class="text-slate-600">Check back soon for the latest AI robots!</p>
            </div>
            {% endfor %}
        </div>
    </div>
</section>
{% endblock %}
```

### 6.2 Robot Card: `templates/includes/_robot_card.html`

```html
{# Robot Card Partial #}
<div class="group relative h-full">
    <a href="{% url 'robot_detail' robot.slug %}" class="robot-card block h-full bg-white rounded-2xl border border-slate-200 p-5 hover:border-cyan-400 hover:shadow-lg hover:shadow-cyan-100/50 transition-all duration-300">
        
        <!-- Robot Image -->
        <div class="relative mb-4 rounded-xl overflow-hidden bg-gradient-to-br from-slate-100 to-slate-50 aspect-square">
            {% if robot.image %}
            <img src="{{ robot.image.url }}" alt="{{ robot.name }}" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500">
            {% else %}
            <!-- Placeholder with Robot Icon -->
            <div class="w-full h-full flex items-center justify-center bg-gradient-to-br from-slate-800 to-slate-900">
                <i class="fa-solid fa-robot text-6xl text-cyan-500 opacity-50"></i>
            </div>
            {% endif %}
            
            <!-- Type Badge -->
            <div class="absolute top-3 left-3">
                <span class="px-2 py-1 rounded-full text-xs font-bold uppercase tracking-wider 
                    {% if robot.robot_type == 'humanoid' %}bg-violet-100 text-violet-700{% else %}bg-amber-100 text-amber-700{% endif %}">
                    {{ robot.get_robot_type_display }}
                </span>
            </div>
            
            <!-- Availability Badge -->
            <div class="absolute top-3 right-3">
                <span class="px-2 py-1 rounded-full text-xs font-bold uppercase tracking-wider
                    {% if robot.availability == 'available' %}bg-green-100 text-green-700
                    {% elif robot.availability == 'preorder' %}bg-blue-100 text-blue-700
                    {% else %}bg-slate-100 text-slate-600{% endif %}">
                    {{ robot.get_availability_display }}
                </span>
            </div>
        </div>
        
        <!-- Company Tag -->
        <div class="flex items-center gap-2 mb-2">
            <i class="fa-solid fa-building text-slate-400 text-xs"></i>
            <span class="text-xs font-semibold text-slate-500 uppercase tracking-wider">{{ robot.company }}</span>
        </div>
        
        <!-- Robot Name -->
        <h3 class="font-heading font-bold text-xl text-slate-900 mb-2 group-hover:text-cyan-600 transition-colors">
            {{ robot.name }}
        </h3>
        
        <!-- Short Description -->
        <p class="text-slate-600 text-sm mb-4 line-clamp-2">{{ robot.short_description }}</p>
        
        <!-- Meta Info -->
        <div class="flex items-center justify-between pt-4 border-t border-slate-100">
            <div class="flex items-center gap-2">
                <i class="fa-solid fa-target text-cyan-500"></i>
                <span class="text-xs text-slate-500">{{ robot.get_target_market_display }}</span>
            </div>
            {% if robot.release_date %}
            <span class="text-xs text-slate-400">
                <i class="fa-solid fa-calendar mr-1"></i>
                {{ robot.release_date|date:"M Y" }}
            </span>
            {% endif %}
        </div>
        
        <!-- Featured Badge -->
        {% if robot.is_featured %}
        <div class="absolute -top-2 -right-2 z-10">
            {% include 'includes/_featured_badge.html' %}
        </div>
        {% endif %}
    </a>
</div>
```

### 6.3 Robot Detail Page: `templates/robot_detail.html`

Create a detailed view with sections for:
- Hero image with robot info
- Company information
- Detailed description
- Pros/Cons in side-by-side cards
- Use cases as chips
- Technical specifications table
- Related robots section

### 6.4 Admin List: `templates/admin_robots_list.html`

Follow the pattern from `admin_tools_list.html` with:
- Search bar
- Filter tabs (All/Incomplete)
- Table with columns: Robot (image + name), Company, Type, Target, Availability, Completeness, Actions
- Pagination

---

## 7. Forms

Create `RobotForm` in `tools/forms.py`:

```python
class RobotForm(forms.ModelForm):
    class Meta:
        model = Robot
        fields = [
            'name', 'slug', 'company', 'company_website', 'product_url',
            'image', 'robot_type', 'target_market', 'release_date',
            'availability', 'pricing_tier', 'price_value',
            'short_description', 'long_description', 'pros', 'cons', 'use_cases',
            'specifications', 'status', 'is_featured',
            'meta_title', 'meta_description', 'og_image', 'canonical_url'
        ]
        widgets = {
            'short_description': forms.Textarea(attrs={'rows': 2}),
            'long_description': forms.Textarea(attrs={'rows': 6}),
            'pros': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Advanced AI, Long battery life, Easy to use'}),
            'cons': forms.Textarea(attrs={'rows': 3, 'placeholder': 'High price, Limited availability'}),
            'use_cases': forms.Textarea(attrs={'rows': 3}),
            'specifications': forms.Textarea(attrs={'rows': 4, 'placeholder': '{"height": "1.8m", "weight": "70kg"}'}),
        }
```

---

## 8. Signals

Add signals in `tools/signals.py` to auto-index robots in ChromaDB:

```python
@receiver(post_save, sender=Robot)
def index_robot(sender, instance, **kwargs):
    if instance.status == 'published':
        SearchService.add_robots([instance])
    else:
        SearchService.remove_robots([instance])

@receiver(post_delete, sender=Robot)
def remove_robot_from_index(sender, instance, **kwargs):
    SearchService.remove_robots([instance])
```

---

## 9. Admin Dashboard Updates

### 9.1 Add Robots Column

In `templates/admin_dashboard.html`, add a fourth column for Robots analytics:
- Most Viewed Robots
- Best Converting Robots (if affiliate tracking is added)

### 9.2 Admin Navigation

Update `templates/partials/admin_nav.html` to include Robots link:

```html
<a href="{% url 'admin_robots' %}" class="...">
    <i class="fa-solid fa-robot mr-2"></i> Robots
</a>
```

---

## 10. Dummy Image

Create a default placeholder image for robots without uploaded images:
- Location: `static/images/robot_placeholder.svg` or generate dynamically
- Design: Dark background with cyan robot icon
- Size: Square aspect ratio (400x400px recommended)

---

## 11. CSS Additions

Add to the stylesheet for robot-specific theming:

```css
/* Robot card hover glow */
.robot-card:hover {
    box-shadow: 0 0 30px rgba(6, 182, 212, 0.15);
}

/* Cyan glow text */
.glow-text-cyan {
    text-shadow: 0 0 20px rgba(6, 182, 212, 0.4);
}

/* Robot grid animation on load */
.robot-card {
    animation: fadeInUp 0.5s ease-out;
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}
```

---

## 12. Navigation Update

Add to base.html navigation:

```html
<a href="{% url 'robots' %}" class="nav-link flex items-center gap-2">
    <i class="fa-solid fa-robot"></i>
    <span>AI Robots</span>
    <span class="text-xs px-1.5 py-0.5 bg-cyan-100 text-cyan-700 rounded font-bold">NEW</span>
</a>
```

---

## 13. Sitemap Integration

Add robots to `tools/sitemaps.py`:

```python
class RobotSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Robot.objects.filter(status='published')

    def lastmod(self, obj):
        return obj.updated_at
```

---

## 14. Initial Robot Data (Examples)

Suggested initial robots to add:

| Name | Company | Type | Target | Availability |
|------|---------|------|--------|--------------|
| Optimus | Tesla | Humanoid | Home/Industry | Announced |
| Atlas | Boston Dynamics | Humanoid | Industry/Research | Available |
| Spot | Boston Dynamics | Specialized | Industry | Available |
| Pepper | SoftBank Robotics | Humanoid | Service | Available |
| Digit | Agility Robotics | Humanoid | Industry | Pre-order |
| Figure 01 | Figure AI | Humanoid | Industry | Development |
| Neo | 1X Technologies | Humanoid | Home | Development |
| Astribot S1 | Astribot | Humanoid | Industry | Announced |

---

## 15. Implementation Priority

1. **Phase 1 - Core**: Model, migrations, basic views, templates
2. **Phase 2 - Search**: ChromaDB integration, search filter
3. **Phase 3 - Admin**: Admin interface, forms, CRUD operations
4. **Phase 4 - Polish**: Analytics, SEO, featured robots, sitemap
5. **Phase 5 - Content**: Add initial robot data

---

## 16. Design Uniqueness

The robots section differentiates from other sections through:

1. **Color Scheme**: Cyan/Teal accent colors (vs. Brand purple for tools)
2. **Visual Elements**: Circuit-like patterns, futuristic grid backgrounds
3. **Typography**: More technical, monospace elements for specs
4. **Card Design**: Prominent image area, availability badges, company branding
5. **Animations**: Subtle pulse effects, scan-line animations
6. **Icons**: Robot-specific iconography (fa-robot, fa-microchip, fa-gear)

---

## 17. 🆕 Robot Comparison Tool

### Feature Overview
Allow users to compare up to 4 robots side-by-side with an intuitive comparison interface.

### URL Route
```python
path('robots/compare/', views.robot_comparison, name='robot_comparison'),
```

### Model Addition
```python
# In Robot model, add comparison-friendly specs
COMPARISON_SPECS = [
    ('height', 'Height', 'cm'),
    ('weight', 'Weight', 'kg'),
    ('battery_life', 'Battery Life', 'hours'),
    ('payload', 'Max Payload', 'kg'),
    ('speed', 'Max Speed', 'km/h'),
    ('degrees_of_freedom', 'Degrees of Freedom', ''),
    ('ai_model', 'AI Model', ''),
]
```

### Template: `templates/robot_comparison.html`
```html
<section class="py-8">
    <div class="max-w-7xl mx-auto px-4">
        <h1 class="text-3xl font-heading font-black text-center mb-8">
            Compare <span class="text-cyan-600">AI Robots</span>
        </h1>
        
        <!-- Robot Selection -->
        <div class="grid grid-cols-4 gap-4 mb-8">
            {% for slot in comparison_slots %}
            <div class="comparison-slot bg-white rounded-xl border-2 border-dashed border-slate-300 p-4 min-h-48
                        hover:border-cyan-400 transition cursor-pointer" data-slot="{{ forloop.counter }}">
                {% if slot.robot %}
                    <img src="{{ slot.robot.image.url }}" class="w-full aspect-square object-cover rounded-lg mb-2">
                    <h3 class="font-bold text-center">{{ slot.robot.name }}</h3>
                    <button class="remove-btn text-red-500 text-xs">Remove</button>
                {% else %}
                    <div class="flex flex-col items-center justify-center h-full text-slate-400">
                        <i class="fa-solid fa-plus text-3xl mb-2"></i>
                        <span>Add Robot</span>
                    </div>
                {% endif %}
            </div>
            {% endfor %}
        </div>
        
        <!-- Comparison Table -->
        <div class="comparison-table bg-white rounded-2xl shadow-xl overflow-hidden">
            <table class="w-full">
                <thead class="bg-slate-900 text-white">
                    <tr>
                        <th class="p-4 text-left">Specification</th>
                        {% for robot in selected_robots %}
                        <th class="p-4 text-center">{{ robot.name }}</th>
                        {% endfor %}
                    </tr>
                </thead>
                <tbody>
                    {% for spec in comparison_specs %}
                    <tr class="border-b border-slate-100 hover:bg-cyan-50/50">
                        <td class="p-4 font-semibold">{{ spec.label }}</td>
                        {% for robot in selected_robots %}
                        <td class="p-4 text-center">
                            {{ robot.specifications|get_spec:spec.key }} {{ spec.unit }}
                        </td>
                        {% endfor %}
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</section>
```

### JavaScript for Dynamic Selection
```javascript
// Robot comparison selector with AJAX
function addToComparison(robotSlug, slot) {
    fetch(`/api/robots/add-to-compare/?slug=${robotSlug}&slot=${slot}`)
        .then(r => r.json())
        .then(data => updateComparisonUI(data));
}
```

---

## 18. 🆕 Company Profiles

### Feature Overview
Dedicated pages for robot manufacturers with all their robots, company info, and news.

### Model: `RobotCompany`
```python
class RobotCompany(SEOModel):
    """Robot manufacturer/company profile."""
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(unique=True)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    
    # Company Info
    description = models.TextField()
    founded_year = models.PositiveIntegerField(null=True, blank=True)
    headquarters = models.CharField(max_length=200, blank=True)
    website = models.URLField()
    
    # Social Links
    twitter_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    
    # Stats (auto-calculated)
    @property
    def robot_count(self):
        return self.robots.filter(status='published').count()
    
    # Notable achievements
    achievements = models.TextField(blank=True, help_text="Comma-separated achievements")
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
```

### URL Routes
```python
path('companies/', views.robot_companies, name='robot_companies'),
path('company/<slug:slug>/', views.robot_company_detail, name='robot_company_detail'),
```

### Template: `templates/robot_company_detail.html`
- Company hero with logo and description
- Robot grid (all robots from this company)
- Company stats (founded, HQ, total robots)
- Social links
- Achievement timeline

---

## 19. 🆕 Video Gallery & Media Hub

### Feature Overview
Embed demo videos and media galleries for each robot.

### Model: `RobotMedia`
```python
class RobotMedia(models.Model):
    """Videos, images, and media for robots."""
    MEDIA_TYPES = [
        ('video_youtube', 'YouTube Video'),
        ('video_vimeo', 'Vimeo Video'),
        ('video_file', 'Uploaded Video'),
        ('image', 'Image'),
        ('pdf', 'PDF Document'),
    ]
    
    robot = models.ForeignKey(Robot, on_delete=models.CASCADE, related_name='media')
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPES)
    title = models.CharField(max_length=200)
    
    # For embeds
    embed_url = models.URLField(blank=True, help_text="YouTube/Vimeo URL")
    
    # For uploads
    file = models.FileField(upload_to='robot_media/', blank=True, null=True)
    thumbnail = models.ImageField(upload_to='robot_media/thumbs/', blank=True, null=True)
    
    is_featured = models.BooleanField(default=False, help_text="Show on robot card")
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']
```

### Video Embed Component
```html
<!-- templates/includes/_robot_video_embed.html -->
{% if media.media_type == 'video_youtube' %}
<div class="aspect-video rounded-xl overflow-hidden shadow-lg">
    <iframe src="https://www.youtube.com/embed/{{ media.embed_url|youtube_id }}" 
            class="w-full h-full" 
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
            allowfullscreen>
    </iframe>
</div>
{% endif %}
```

---

## 20. 🆕 AI Capabilities Rating System

### Feature Overview
Rate robots on multiple AI capability dimensions with a visual radar chart.

### Model Addition to Robot
```python
# AI Capability ratings (1-10 scale)
ai_autonomy = models.PositiveSmallIntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(10)],
    help_text="Level of autonomous operation capability")
ai_learning = models.PositiveSmallIntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(10)],
    help_text="Machine learning and adaptation capability")
ai_interaction = models.PositiveSmallIntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(10)],
    help_text="Natural language and human interaction")
ai_vision = models.PositiveSmallIntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(10)],
    help_text="Computer vision and object recognition")
ai_manipulation = models.PositiveSmallIntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(10)],
    help_text="Fine motor control and manipulation")
ai_navigation = models.PositiveSmallIntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(10)],
    help_text="Autonomous navigation and mapping")

@property
def ai_score_overall(self):
    """Calculate overall AI capability score."""
    scores = [self.ai_autonomy, self.ai_learning, self.ai_interaction, 
              self.ai_vision, self.ai_manipulation, self.ai_navigation]
    return round(sum(scores) / len(scores), 1)

def get_ai_capabilities_json(self):
    """Return capabilities as JSON for radar chart."""
    return json.dumps({
        'labels': ['Autonomy', 'Learning', 'Interaction', 'Vision', 'Manipulation', 'Navigation'],
        'data': [self.ai_autonomy, self.ai_learning, self.ai_interaction,
                 self.ai_vision, self.ai_manipulation, self.ai_navigation]
    })
```

### Radar Chart Component (using Chart.js)
```html
<!-- templates/includes/_ai_radar_chart.html -->
<div class="ai-capabilities-chart p-6 bg-slate-900 rounded-2xl">
    <h3 class="text-white font-heading font-bold text-lg mb-4 flex items-center gap-2">
        <i class="fa-solid fa-brain text-cyan-400"></i>
        AI Capabilities
    </h3>
    <canvas id="ai-radar-{{ robot.id }}" width="300" height="300"></canvas>
    <div class="mt-4 text-center">
        <span class="text-4xl font-heading font-black text-cyan-400">{{ robot.ai_score_overall }}</span>
        <span class="text-slate-400 text-sm block">Overall AI Score</span>
    </div>
</div>

<script>
new Chart(document.getElementById('ai-radar-{{ robot.id }}'), {
    type: 'radar',
    data: {
        labels: ['Autonomy', 'Learning', 'Interaction', 'Vision', 'Manipulation', 'Navigation'],
        datasets: [{
            data: {{ robot.get_ai_capabilities_json|safe }}.data,
            backgroundColor: 'rgba(6, 182, 212, 0.2)',
            borderColor: 'rgba(6, 182, 212, 1)',
            borderWidth: 2,
            pointBackgroundColor: 'rgba(6, 182, 212, 1)'
        }]
    },
    options: {
        scales: { r: { min: 0, max: 10, ticks: { display: false } } },
        plugins: { legend: { display: false } }
    }
});
</script>
```

---

## 21. 🆕 Robot Release Timeline

### Feature Overview
Interactive visual timeline showing robot releases across all companies.

### URL Route
```python
path('robots/timeline/', views.robot_timeline, name='robot_timeline'),
```

### View
```python
def robot_timeline(request):
    """Visual timeline of robot releases."""
    robots = Robot.objects.filter(status='published', release_date__isnull=False).order_by('release_date')
    
    # Group by year
    timeline_data = {}
    for robot in robots:
        year = robot.release_date.year
        if year not in timeline_data:
            timeline_data[year] = []
        timeline_data[year].append(robot)
    
    return render(request, 'robot_timeline.html', {
        'timeline_data': sorted(timeline_data.items()),
        'upcoming': robots.filter(release_date__gt=timezone.now().date()),
    })
```

### Template Design
```html
<!-- templates/robot_timeline.html -->
<section class="py-8 bg-slate-900 min-h-screen">
    <div class="max-w-5xl mx-auto px-4">
        <h1 class="text-3xl font-heading font-black text-white text-center mb-12">
            AI Robots <span class="text-cyan-400">Timeline</span>
        </h1>
        
        <div class="relative">
            <!-- Vertical timeline line -->
            <div class="absolute left-1/2 transform -translate-x-1/2 w-1 bg-cyan-600/30 h-full"></div>
            
            {% for year, robots in timeline_data %}
            <!-- Year marker -->
            <div class="relative mb-12">
                <div class="absolute left-1/2 transform -translate-x-1/2 -translate-y-1/2 
                            w-16 h-16 rounded-full bg-cyan-600 flex items-center justify-center z-10">
                    <span class="text-white font-black">{{ year }}</span>
                </div>
                
                <div class="grid grid-cols-2 gap-8 pt-12">
                    {% for robot in robots %}
                    <div class="{% cycle 'pr-8 text-right' 'pl-8 text-left col-start-2' %}">
                        <div class="bg-white/10 backdrop-blur rounded-xl p-4 hover:bg-white/20 transition">
                            <span class="text-cyan-400 text-sm">{{ robot.release_date|date:"M d" }}</span>
                            <h3 class="text-white font-bold">{{ robot.name }}</h3>
                            <span class="text-slate-400 text-sm">{{ robot.company }}</span>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
</section>
```

---

## 22. 🆕 Wishlist & Availability Alerts

### Feature Overview
Let users save robots to their wishlist and get notified when availability changes.

### Model: `RobotWishlist`
```python
class RobotWishlist(models.Model):
    """User wishlist for robots with notification preferences."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='robot_wishlist')
    robot = models.ForeignKey(Robot, on_delete=models.CASCADE, related_name='wishlisted_by')
    
    # Notification preferences
    notify_availability = models.BooleanField(default=True, help_text="Notify when availability changes")
    notify_price_drop = models.BooleanField(default=True, help_text="Notify on price changes")
    
    # Target price for alerts
    target_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'robot']
```

### Price History Model
```python
class RobotPriceHistory(models.Model):
    """Track price changes for robots."""
    robot = models.ForeignKey(Robot, on_delete=models.CASCADE, related_name='price_history')
    price = models.DecimalField(max_digits=12, decimal_places=2)
    recorded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-recorded_at']
```

### Notification System (using Django signals)
```python
@receiver(pre_save, sender=Robot)
def check_availability_change(sender, instance, **kwargs):
    if instance.pk:
        old_robot = Robot.objects.get(pk=instance.pk)
        if old_robot.availability != instance.availability:
            # Trigger availability change notifications
            notify_wishlist_users.delay(instance.pk, 'availability_change')
        if old_robot.price_value != instance.price_value:
            # Record price history
            RobotPriceHistory.objects.create(robot=instance, price=instance.price_value or 0)
            notify_wishlist_users.delay(instance.pk, 'price_change')
```

---

## 23. 🆕 ROI Calculator

### Feature Overview
Interactive calculator to estimate return on investment for industrial robots.

### URL Route
```python
path('robots/roi-calculator/', views.robot_roi_calculator, name='robot_roi_calculator'),
path('robot/<slug:slug>/roi/', views.robot_specific_roi, name='robot_specific_roi'),
```

### Template: `templates/robot_roi_calculator.html`
```html
<section class="py-8">
    <div class="max-w-4xl mx-auto px-4">
        <div class="bg-white rounded-2xl shadow-xl p-8">
            <h1 class="text-2xl font-heading font-black text-slate-900 mb-6 flex items-center gap-2">
                <i class="fa-solid fa-calculator text-cyan-600"></i>
                Robot ROI Calculator
            </h1>
            
            <form id="roi-calculator" class="space-y-6">
                <!-- Robot Selection -->
                <div>
                    <label class="block font-semibold mb-2">Select Robot</label>
                    <select name="robot_id" class="w-full rounded-lg border-slate-300">
                        {% for robot in robots %}
                        <option value="{{ robot.id }}" data-price="{{ robot.price_value }}">
                            {{ robot.name }} - ${{ robot.price_value|floatformat:0 }}
                        </option>
                        {% endfor %}
                    </select>
                </div>
                
                <!-- Labor Costs -->
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="block font-semibold mb-2">Hourly Labor Cost ($)</label>
                        <input type="number" name="labor_cost" value="25" class="w-full rounded-lg border-slate-300">
                    </div>
                    <div>
                        <label class="block font-semibold mb-2">Hours Replaced/Week</label>
                        <input type="number" name="hours_replaced" value="40" class="w-full rounded-lg border-slate-300">
                    </div>
                </div>
                
                <!-- Operating Costs -->
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="block font-semibold mb-2">Annual Maintenance ($)</label>
                        <input type="number" name="maintenance" value="5000" class="w-full rounded-lg border-slate-300">
                    </div>
                    <div>
                        <label class="block font-semibold mb-2">Annual Energy Cost ($)</label>
                        <input type="number" name="energy" value="2000" class="w-full rounded-lg border-slate-300">
                    </div>
                </div>
                
                <button type="button" onclick="calculateROI()" class="w-full py-4 bg-cyan-600 text-white rounded-xl font-bold hover:bg-cyan-700 transition">
                    Calculate ROI
                </button>
            </form>
            
            <!-- Results -->
            <div id="roi-results" class="hidden mt-8 p-6 bg-slate-50 rounded-xl">
                <div class="grid grid-cols-3 gap-4 text-center">
                    <div>
                        <span class="text-3xl font-black text-green-600" id="annual-savings">$0</span>
                        <span class="block text-slate-500 text-sm">Annual Savings</span>
                    </div>
                    <div>
                        <span class="text-3xl font-black text-cyan-600" id="payback-months">0</span>
                        <span class="block text-slate-500 text-sm">Months to Payback</span>
                    </div>
                    <div>
                        <span class="text-3xl font-black text-purple-600" id="five-year-roi">0%</span>
                        <span class="block text-slate-500 text-sm">5-Year ROI</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</section>

<script>
function calculateROI() {
    const form = document.getElementById('roi-calculator');
    const robotPrice = parseFloat(form.querySelector('[name="robot_id"]').selectedOptions[0].dataset.price) || 0;
    const laborCost = parseFloat(form.querySelector('[name="labor_cost"]').value);
    const hoursReplaced = parseFloat(form.querySelector('[name="hours_replaced"]').value);
    const maintenance = parseFloat(form.querySelector('[name="maintenance"]').value);
    const energy = parseFloat(form.querySelector('[name="energy"]').value);
    
    const annualLaborSaved = (laborCost * hoursReplaced * 52);
    const annualOperatingCost = maintenance + energy;
    const annualSavings = annualLaborSaved - annualOperatingCost;
    const paybackMonths = Math.ceil((robotPrice / annualSavings) * 12);
    const fiveYearROI = Math.round((((annualSavings * 5) - robotPrice) / robotPrice) * 100);
    
    document.getElementById('annual-savings').textContent = '$' + annualSavings.toLocaleString();
    document.getElementById('payback-months').textContent = paybackMonths;
    document.getElementById('five-year-roi').textContent = fiveYearROI + '%';
    document.getElementById('roi-results').classList.remove('hidden');
}
</script>
```

---

## 24. 🆕 Related AI Tools Integration

### Feature Overview
Link AI software tools that work with or enhance specific robots.

### Model: ManyToMany Relationship
```python
# In Robot model
compatible_tools = models.ManyToManyField(
    'Tool', 
    related_name='compatible_robots', 
    blank=True,
    help_text="AI software tools that integrate with this robot"
)
```

### Display on Robot Detail
```html
{% if robot.compatible_tools.exists %}
<div class="mt-8">
    <h3 class="font-heading font-bold text-xl mb-4 flex items-center gap-2">
        <i class="fa-solid fa-plug text-purple-500"></i>
        Compatible AI Tools
    </h3>
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        {% for tool in robot.compatible_tools.all %}
        <a href="{% url 'tool_detail' tool.slug %}" class="flex items-center gap-3 p-3 bg-white rounded-lg border hover:border-purple-400 transition">
            {% if tool.logo %}
            <img src="{{ tool.logo.url }}" class="w-10 h-10 rounded object-cover">
            {% endif %}
            <span class="font-semibold text-sm">{{ tool.name }}</span>
        </a>
        {% endfor %}
    </div>
</div>
{% endif %}
```

---

## 25. 🆕 Safety & Certification Badges

### Feature Overview
Display safety certifications and compliance badges for each robot.

### Model Addition
```python
CERTIFICATION_CHOICES = [
    ('iso_10218', 'ISO 10218 (Industrial Robot Safety)'),
    ('iso_13482', 'ISO 13482 (Personal Care Robots)'),
    ('ce', 'CE Marking'),
    ('ul', 'UL Listed'),
    ('fcc', 'FCC Certified'),
    ('tuv', 'TÜV Certified'),
    ('rohs', 'RoHS Compliant'),
]

certifications = models.JSONField(
    default=list, 
    blank=True,
    help_text="List of certification codes, e.g., ['iso_10218', 'ce', 'ul']"
)

safety_rating = models.CharField(
    max_length=20,
    choices=[
        ('collaborative', 'Collaborative (Human-Safe)'),
        ('caged', 'Requires Safety Cage'),
        ('supervised', 'Requires Supervision'),
        ('consumer', 'Consumer Grade'),
    ],
    blank=True
)
```

### Badge Display Component
```html
<!-- templates/includes/_robot_certifications.html -->
<div class="flex flex-wrap gap-2">
    {% for cert in robot.certifications %}
    <span class="inline-flex items-center px-2 py-1 rounded bg-green-100 text-green-700 text-xs font-bold">
        <i class="fa-solid fa-check-circle mr-1"></i>
        {{ cert|certification_label }}
    </span>
    {% endfor %}
    
    {% if robot.safety_rating %}
    <span class="inline-flex items-center px-2 py-1 rounded 
        {% if robot.safety_rating == 'collaborative' %}bg-blue-100 text-blue-700
        {% elif robot.safety_rating == 'consumer' %}bg-green-100 text-green-700
        {% else %}bg-amber-100 text-amber-700{% endif %} text-xs font-bold">
        <i class="fa-solid fa-shield-halved mr-1"></i>
        {{ robot.get_safety_rating_display }}
    </span>
    {% endif %}
</div>
```

---

## 26. 🆕 Robot "Personality" Cards

### Feature Overview
Fun, engaging personality descriptions that humanize the robots for consumer marketing.

### Model Addition
```python
# Personality fields (optional, for fun/marketing)
personality_tagline = models.CharField(max_length=100, blank=True, 
    help_text="e.g., 'The Friendly Helper', 'Industrial Powerhouse'")
personality_emoji = models.CharField(max_length=10, blank=True, 
    help_text="Representative emoji")
personality_description = models.TextField(blank=True,
    help_text="Fun personality write-up in third person")
```

### Template Display
```html
{% if robot.personality_tagline %}
<div class="personality-card bg-gradient-to-br from-cyan-500 to-purple-600 rounded-2xl p-6 text-white">
    <div class="text-4xl mb-2">{{ robot.personality_emoji }}</div>
    <h3 class="font-heading font-bold text-xl">{{ robot.personality_tagline }}</h3>
    <p class="text-white/80 text-sm mt-2">{{ robot.personality_description }}</p>
</div>
{% endif %}
```

---

## 27. 🆕 Specification Comparison Matrix

### Feature Overview
Filterable matrix view showing all robots with key specs in columns.

### URL Route
```python
path('robots/matrix/', views.robot_matrix, name='robot_matrix'),
```

### Template Design
```html
<section class="py-8">
    <div class="max-w-full mx-auto px-4 overflow-x-auto">
        <table class="w-full bg-white rounded-xl shadow-xl">
            <thead class="bg-slate-900 text-white sticky top-0">
                <tr>
                    <th class="p-4 text-left sticky left-0 bg-slate-900 z-20">Robot</th>
                    <th class="p-4 text-center cursor-pointer hover:bg-slate-800" onclick="sortMatrix('company')">
                        Company <i class="fa-solid fa-sort ml-1"></i>
                    </th>
                    <th class="p-4 text-center cursor-pointer hover:bg-slate-800" onclick="sortMatrix('price')">
                        Price <i class="fa-solid fa-sort ml-1"></i>
                    </th>
                    <th class="p-4 text-center">Type</th>
                    <th class="p-4 text-center">Height</th>
                    <th class="p-4 text-center">Weight</th>
                    <th class="p-4 text-center">Battery</th>
                    <th class="p-4 text-center">AI Score</th>
                    <th class="p-4 text-center">Availability</th>
                </tr>
            </thead>
            <tbody>
                {% for robot in robots %}
                <tr class="border-b hover:bg-cyan-50/50 transition">
                    <td class="p-4 sticky left-0 bg-white">
                        <div class="flex items-center gap-3">
                            <img src="{{ robot.image.url|default:'/static/images/robot_placeholder.svg' }}" 
                                 class="w-12 h-12 rounded-lg object-cover">
                            <a href="{% url 'robot_detail' robot.slug %}" class="font-bold hover:text-cyan-600">
                                {{ robot.name }}
                            </a>
                        </div>
                    </td>
                    <td class="p-4 text-center">{{ robot.company }}</td>
                    <td class="p-4 text-center font-mono">${{ robot.price_value|floatformat:0|default:"TBD" }}</td>
                    <td class="p-4 text-center">{{ robot.get_robot_type_display }}</td>
                    <td class="p-4 text-center font-mono">{{ robot.specifications.height|default:"-" }}</td>
                    <td class="p-4 text-center font-mono">{{ robot.specifications.weight|default:"-" }}</td>
                    <td class="p-4 text-center font-mono">{{ robot.specifications.battery_life|default:"-" }}h</td>
                    <td class="p-4 text-center">
                        <span class="inline-flex items-center justify-center w-10 h-10 rounded-full 
                            {% if robot.ai_score_overall >= 8 %}bg-green-100 text-green-700
                            {% elif robot.ai_score_overall >= 5 %}bg-amber-100 text-amber-700
                            {% else %}bg-slate-100 text-slate-600{% endif %} font-bold">
                            {{ robot.ai_score_overall }}
                        </span>
                    </td>
                    <td class="p-4 text-center">
                        <span class="px-2 py-1 rounded text-xs font-bold
                            {% if robot.availability == 'available' %}bg-green-100 text-green-700{% else %}bg-slate-100 text-slate-600{% endif %}">
                            {{ robot.get_availability_display }}
                        </span>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</section>
```

---

## 28. 🆕 Robot News Integration

### Feature Overview
Display latest news articles about specific robots or the robotics industry.

### Model: `RobotNews`
```python
class RobotNews(models.Model):
    """News and updates about robots."""
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    excerpt = models.CharField(max_length=300)
    
    # Linked robots
    robots = models.ManyToManyField(Robot, related_name='news_articles', blank=True)
    
    # Source
    source_name = models.CharField(max_length=100, blank=True)
    source_url = models.URLField(blank=True)
    
    featured_image = models.ImageField(upload_to='robot_news/', blank=True, null=True)
    
    published_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    is_featured = models.BooleanField(default=False)

    class Meta:
        ordering = ['-published_at']
        verbose_name_plural = "Robot News"
```

### News Feed Component
```html
<!-- On robots.html homepage -->
<div class="mt-12">
    <h2 class="text-2xl font-heading font-black text-slate-900 mb-6 flex items-center gap-2">
        <i class="fa-solid fa-newspaper text-cyan-600"></i>
        Latest Robot News
    </h2>
    <div class="grid md:grid-cols-3 gap-6">
        {% for news in latest_robot_news %}
        <article class="bg-white rounded-xl shadow-sm overflow-hidden hover:shadow-lg transition">
            {% if news.featured_image %}
            <img src="{{ news.featured_image.url }}" class="w-full h-40 object-cover">
            {% endif %}
            <div class="p-4">
                <span class="text-xs text-slate-500">{{ news.published_at|date:"M d, Y" }}</span>
                <h3 class="font-bold text-slate-900 mt-1 line-clamp-2">{{ news.title }}</h3>
                <p class="text-sm text-slate-600 mt-2 line-clamp-2">{{ news.excerpt }}</p>
            </div>
        </article>
        {% endfor %}
    </div>
</div>
```

---

## 29. 🆕 User Reviews & Ratings

### Feature Overview
Allow authenticated users to leave reviews and ratings for robots they own or have used.

### Model: `RobotReview`
```python
class RobotReview(models.Model):
    """User reviews and ratings for robots."""
    robot = models.ForeignKey(Robot, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='robot_reviews')
    
    # Rating (1-5 stars)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    
    # Detailed ratings (optional)
    rating_build_quality = models.PositiveSmallIntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    rating_ai_performance = models.PositiveSmallIntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    rating_value = models.PositiveSmallIntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    rating_support = models.PositiveSmallIntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    
    # Review content
    title = models.CharField(max_length=200)
    content = models.TextField()
    
    # Ownership verification
    is_verified_owner = models.BooleanField(default=False)
    
    # Helpful votes
    helpful_votes = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['robot', 'user']
        ordering = ['-helpful_votes', '-created_at']
```

### Review Display
```html
<div class="reviews-section mt-8">
    <div class="flex items-center justify-between mb-6">
        <h3 class="font-heading font-bold text-xl">User Reviews</h3>
        <div class="flex items-center gap-2">
            <div class="flex text-amber-400">
                {% for i in "12345" %}
                <i class="fa-{% if forloop.counter <= robot.avg_rating %}solid{% else %}regular{% endif %} fa-star"></i>
                {% endfor %}
            </div>
            <span class="font-bold">{{ robot.avg_rating|floatformat:1 }}</span>
            <span class="text-slate-500">({{ robot.reviews.count }} reviews)</span>
        </div>
    </div>
    
    {% for review in robot.reviews.all|slice:":5" %}
    <div class="review-card bg-white rounded-xl p-4 mb-4 border">
        <div class="flex items-start gap-4">
            <div class="flex-shrink-0">
                <div class="w-10 h-10 rounded-full bg-slate-200 flex items-center justify-center">
                    <i class="fa-solid fa-user text-slate-400"></i>
                </div>
            </div>
            <div class="flex-1">
                <div class="flex items-center gap-2 mb-1">
                    <span class="font-bold">{{ review.user.username }}</span>
                    {% if review.is_verified_owner %}
                    <span class="px-2 py-0.5 bg-green-100 text-green-700 text-xs rounded font-bold">Verified Owner</span>
                    {% endif %}
                </div>
                <div class="flex text-amber-400 text-sm mb-2">
                    {% for i in "12345" %}
                    <i class="fa-{% if forloop.counter <= review.rating %}solid{% else %}regular{% endif %} fa-star"></i>
                    {% endfor %}
                </div>
                <h4 class="font-semibold mb-1">{{ review.title }}</h4>
                <p class="text-slate-600 text-sm">{{ review.content }}</p>
            </div>
        </div>
    </div>
    {% empty %}
    <p class="text-slate-500 text-center py-8">No reviews yet. Be the first to review!</p>
    {% endfor %}
</div>
```

---

## 30. Implementation Priority (Updated)

### Phase 1 - Core (Week 1)
- Robot model with all fields
- Basic CRUD views
- List and detail templates
- Admin interface

### Phase 2 - Search & Discovery (Week 2)
- ChromaDB integration
- Search filter checkbox
- Filters on listing page
- Company profiles

### Phase 3 - Enhanced Features (Week 3)
- AI Capabilities radar chart
- Video gallery
- Comparison tool
- Specification matrix

### Phase 4 - Engagement (Week 4)
- User reviews & ratings
- Wishlist & alerts
- News integration
- Related tools linking

### Phase 5 - Advanced (Week 5+)
- ROI Calculator
- Timeline visualization
- Safety certifications
- Personality cards
- Price history tracking
