# AI Robots Feature - Implementation Plan

## Overview

This plan implements the AI Robots feature as a **separate Django app** (`robots`) to keep it isolated from the existing `tools` app. The implementation covers Phases 1-4 plus selected advanced features, with **professional-grade SEO** matching the rest of the AIJACK website.

> [!IMPORTANT]
> This creates a new Django app called `robots` that will be completely separate from the `tools` app. It follows the same patterns but has its own models, views, templates, and admin interface.

---

## Scope

### Core Features (Phases 1-4)
- **Phase 1**: Robot model, RobotCompany model, migrations, basic views, templates
- **Phase 2**: ChromaDB search integration, search filter checkbox
- **Phase 3**: Admin interface with forms, full CRUD operations
- **Phase 4**: Analytics (RobotView), **complete SEO suite**, featured robots, sitemap integration

### Advanced Features
- **17**: Robot Comparison Tool (compare up to 4 robots)
- **18**: Company Profiles (dedicated pages for manufacturers)
- **21**: Robot Release Timeline (visual timeline by year)
- **24**: Related AI Tools Integration (link tools to robots)
- **27**: Specification Comparison Matrix (sortable table view)
- **28**: Robot News Integration (news articles linked to robots)

---

## Proposed Changes

### New Django App: `robots/`

```
robots/
├── __init__.py
├── admin.py              # Django admin registration
├── apps.py               # App configuration
├── forms.py              # RobotForm, RobotCompanyForm, RobotNewsForm
├── models.py             # Robot, RobotCompany, RobotNews, RobotView, SavedRobot
├── search.py             # RobotSearchService (ChromaDB integration)
├── signals.py            # Auto-index robots on save
├── sitemaps.py           # RobotSitemap, RobotCompanySitemap, RobotNewsSitemap
├── templatetags/
│   ├── __init__.py
│   └── robot_extras.py   # Template filters (is_saved_by, certification_label)
├── urls.py               # URL patterns for robots section
└── views.py              # All view functions
```

---

## SEO Implementation (Professional Grade)

> [!IMPORTANT]
> All SEO follows the existing patterns from `tools/models.py` and `templates/tool_detail.html`, adhering to the **SEO Guidelines 2025-2026** documented in `doc/SEO_GUIDELINES_2025_2026.md`.

### SEO Model Inheritance

All primary models extend the `SEOModel` abstract base class pattern:

```python
class SEOModelMixin(models.Model):
    """SEO fields for all robot-related models."""
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
    canonical_url = models.URLField(
        blank=True,
        help_text="Override canonical URL if needed"
    )

    class Meta:
        abstract = True
```

### JSON-LD Schema Implementation

Each model implements `get_schema_json()` and `get_breadcrumb_json()` methods:

| Model | Schema Type | Purpose |
|-------|-------------|---------|
| `Robot` | `Product` | Product structured data for robots |
| `RobotCompany` | `Organization` | Company/brand information |
| `RobotNews` | `NewsArticle` | News article structured data |
| Robot listings | `CollectionPage` | Collection of robots |

#### Robot Schema Example
```python
def get_schema_json(self):
    """Generate Product schema for robot."""
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
        "image": self.image.url if self.image else None,
        "manufacturer": {
            "@type": "Organization",
            "name": self.company.name,
            "url": self.company.website
        },
        "releaseDate": self.release_date.isoformat() if self.release_date else None,
    }
    if self.price_value:
        data["offers"] = {
            "@type": "Offer",
            "price": str(self.price_value),
            "priceCurrency": "USD",
            "availability": self._get_availability_schema(),
            "url": self.product_url
        }
    return json.dumps(data)

def get_breadcrumb_json(self, company=None):
    """Generate BreadcrumbList schema."""
    items = [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": "/"},
        {"@type": "ListItem", "position": 2, "name": "AI Robots", "item": "/robots/"},
    ]
    if company or self.company:
        c = company or self.company
        items.append({"@type": "ListItem", "position": 3, "name": c.name, "item": f"/robots/company/{c.slug}/"})
        items.append({"@type": "ListItem", "position": 4, "name": self.name, "item": f"/robot/{self.slug}/"})
    else:
        items.append({"@type": "ListItem", "position": 3, "name": self.name, "item": f"/robot/{self.slug}/"})
    return json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items})
```

### Template SEO Blocks

Each template implements these blocks (matching `tool_detail.html` pattern):

```html
{% extends 'base.html' %}

{% block title %}{{ robot.get_seo_title }}{% endblock %}
{% block meta_description %}{{ robot.get_seo_description }}{% endblock %}
{% block meta_keywords %}{{ robot.name }}, {{ robot.company.name }}, AI robot, {{ robot.get_robot_type_display }}, {% for tag in robot.use_cases_list %}{{ tag }}, {% endfor %}robotics, automation{% endblock %}

{% block schema %}
<script type="application/ld+json">
{{ robot.get_schema_json|safe }}
</script>
<script type="application/ld+json">
{{ robot.get_breadcrumb_json|safe }}
</script>
{% endblock %}
```

### URL Structure (SEO-Optimized)

Clean, descriptive URLs following best practices:

| URL Pattern | Example | SEO Purpose |
|-------------|---------|-------------|
| `/robots/` | - | Category landing page |
| `/robot/<slug>/` | `/robot/tesla-optimus/` | Robot detail page |
| `/robots/company/<slug>/` | `/robots/company/boston-dynamics/` | Company profile |
| `/robots/companies/` | - | Company directory |
| `/robots/timeline/` | - | Timeline landing |
| `/robots/matrix/` | - | Comparison matrix |
| `/robots/compare/` | - | Comparison tool |
| `/robots/news/` | - | News listing |
| `/robots/news/<slug>/` | `/robots/news/tesla-optimus-update/` | News article |

### Sitemap Integration

Create `robots/sitemaps.py` with priority and changefreq settings:

```python
class RobotSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.9  # High priority (same as tools)

    def items(self):
        return Robot.objects.filter(status='published')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return f"/robot/{obj.slug}/"

class RobotCompanySitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return RobotCompany.objects.all()

    def location(self, obj):
        return f"/robots/company/{obj.slug}/"

class RobotNewsSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.7

    def items(self):
        return RobotNews.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.published_at

    def location(self, obj):
        return f"/robots/news/{obj.slug}/"
```

### Image SEO

- **Descriptive filenames**: `tesla-optimus-humanoid-robot.jpg` (not `img123.jpg`)
- **Alt text**: Always descriptive, e.g., `alt="{{ robot.name }} - {{ robot.get_robot_type_display }} robot by {{ robot.company.name }}"`
- **Lazy loading**: `loading="lazy"` on all images below the fold
- **WebP format**: Prefer WebP for optimized loading

### Internal Linking Strategy

- Robot cards link to detail pages
- Detail pages link to company profiles
- Company profiles link back to all their robots
- Related robots section on detail pages
- Compatible AI tools cross-linking
- News articles link to related robots

---

## Models Specification

### [NEW] `robots/models.py`

| Model | Description |
|-------|-------------|
| `RobotCompany` | Robot manufacturers (Boston Dynamics, Tesla, etc.) |
| `Robot` | Core robot entity with specs, pricing, availability |
| `RobotNews` | News articles linked to robots |
| `RobotView` | Analytics tracking for robot page views |
| `SavedRobot` | User wishlisted/saved robots |

#### Robot Model Fields

| Category | Fields |
|----------|--------|
| **Basic** | `name`, `slug`, `company` (FK), `product_url`, `image` |
| **Classification** | `robot_type` (humanoid/specialized), `target_market` |
| **Release** | `release_date`, `availability` |
| **Pricing** | `pricing_tier`, `price_value` |
| **Content** | `short_description`, `long_description`, `pros`, `cons`, `use_cases` |
| **Technical** | `specifications` (JSONField) |
| **Relationships** | `compatible_tools` (M2M to tools.Tool) |
| **Status** | `status` (draft/published), `is_featured` |
| **SEO** | `meta_title`, `meta_description`, `og_image`, `canonical_url` |
| **Timestamps** | `created_at`, `updated_at` |

#### Key Methods

| Method | Purpose |
|--------|---------|
| `get_seo_title()` | Returns meta_title or generates default |
| `get_seo_description()` | Returns meta_description or short_description |
| `get_schema_json()` | Product schema for structured data |
| `get_breadcrumb_json()` | BreadcrumbList schema |
| `get_pros_list()` | Parse comma-separated pros |
| `get_cons_list()` | Parse comma-separated cons |
| `get_use_cases_list()` | Parse comma-separated use cases |
| `get_missing_fields()` | For admin completeness indicator |

---

## Views Specification

### [NEW] `robots/views.py`

| View | URL | Description |
|------|-----|-------------|
| `robots_list` | `/robots/` | Main listing with filters |
| `robot_detail` | `/robot/<slug>/` | Single robot page |
| `robot_companies` | `/robots/companies/` | List all manufacturers |
| `robot_company_detail` | `/robots/company/<slug>/` | Company profile page |
| `robot_comparison` | `/robots/compare/` | Comparison tool |
| `robot_timeline` | `/robots/timeline/` | Visual release timeline |
| `robot_matrix` | `/robots/matrix/` | Specification matrix |
| `robot_news_list` | `/robots/news/` | News listing |
| `robot_news_detail` | `/robots/news/<slug>/` | Single news article |
| `admin_robots` | `/admin-dashboard/robots/` | Admin CRUD list |
| `admin_robot_create` | `/admin-dashboard/robots/add/` | Create robot |
| `admin_robot_edit` | `/admin-dashboard/robots/<slug>/edit/` | Edit robot |
| `admin_robot_delete` | `/admin-dashboard/robots/<slug>/delete/` | Delete robot |
| `admin_robot_companies` | `/admin-dashboard/robot-companies/` | Manage companies |
| `admin_robot_news` | `/admin-dashboard/robot-news/` | Manage news |
| `toggle_save_robot` | `/api/save-robot/<id>/` | Save/unsave robot |
| `add_to_comparison` | `/api/robots/comparison/add/` | Add robot to comparison |

---

## Templates Specification

### [NEW] Templates

| Template | Description | SEO Features |
|----------|-------------|--------------|
| `robots/robots.html` | Main listing | CollectionPage schema, meta tags |
| `robots/robot_detail.html` | Detailed page | Product schema, BreadcrumbList, full meta |
| `robots/robot_comparison.html` | Comparison | CollectionPage schema |
| `robots/robot_timeline.html` | Timeline | CollectionPage schema |
| `robots/robot_matrix.html` | Spec table | CollectionPage schema |
| `robots/robot_companies.html` | Company directory | CollectionPage schema |
| `robots/robot_company_detail.html` | Company profile | Organization schema, BreadcrumbList |
| `robots/robot_news.html` | News listing | CollectionPage schema |
| `robots/robot_news_detail.html` | News article | NewsArticle schema, BreadcrumbList |
| `robots/includes/_robot_card.html` | Robot card | Alt tags, lazy loading |
| `robots/includes/_company_card.html` | Company card | Alt tags, lazy loading |
| `robots/admin/admin_robots_list.html` | Admin list | - |
| `robots/admin/admin_robot_form.html` | Admin form | SEO fields section |

---

## File Modifications

### [MODIFY] `config/settings.py`

Add `'robots'` to `INSTALLED_APPS`:
```python
INSTALLED_APPS = [
    # ...existing apps...
    'tools',
    'robots',  # NEW
]
```

### [MODIFY] `config/urls.py`

Add robots app URLs and sitemaps:
```python
from robots.sitemaps import RobotSitemap, RobotCompanySitemap, RobotNewsSitemap

sitemaps = {
    # ...existing sitemaps...
    'robots': RobotSitemap,
    'robot_companies': RobotCompanySitemap,
    'robot_news': RobotNewsSitemap,
}

urlpatterns = [
    # ...existing patterns...
    path('', include('robots.urls')),  # NEW
]
```

### [MODIFY] `templates/base.html`

Add AI Robots navigation link with NEW badge.

### [MODIFY] `templates/search.html`

Add "Search for AI robotic solutions only" checkbox.

### [MODIFY] `tools/views.py` → `search` function

Handle `robots_only` filter parameter.

### [MODIFY] `templates/admin_dashboard.html`

Add Robots analytics column.

---

## Static Assets

| File | Description |
|------|-------------|
| `static/images/robot_placeholder.svg` | Default placeholder |
| `static/css/robots.css` | Cyan theme styles |

---

## Design Theme

The robots section uses a **futuristic, techy cyan/teal theme**:
- Primary: Cyan (`#06B6D4`)
- Background: Dark slate gradients (`slate-900`)
- Cards: Glassmorphism with cyan glow on hover
- Typography: Monospace for specs, bold headings
- Icons: `fa-robot`, `fa-microchip`, `fa-gear`, `fa-building`
- Animations: Pulse effects, fade-in, glow transitions

---

## Verification Plan

### SEO Verification

1. **Schema Validation**: Test pages with [Google Rich Results Test](https://search.google.com/test/rich-results)
2. **Meta Tags**: View page source, verify title/description/keywords
3. **Sitemap**: Check `/sitemap.xml` includes all robot URLs
4. **Canonical URLs**: Verify canonical tags on all pages
5. **Breadcrumbs**: Verify BreadcrumbList schema renders correctly
6. **Core Web Vitals**: Run PageSpeed Insights on robot pages

### Functional Verification

1. **Phase 1**: Migrations, robot CRUD, templates render
2. **Phase 2**: Search filter works, ChromaDB indexes robots
3. **Phase 3**: Admin interface complete, forms work
4. **Phase 4**: Analytics tracking, featured badges display
5. **Advanced**: Comparison, timeline, matrix, news all functional

---

## Implementation Order

1. Create Django app structure
2. Implement models with full SEO fields
3. Run migrations
4. Add to INSTALLED_APPS
5. Create URL routes with clean SEO-friendly patterns
6. Implement sitemaps
7. Create basic views with SEO context
8. Create templates with schema blocks
9. Add ChromaDB search integration
10. Create admin views and forms
11. Add analytics (RobotView)
12. Implement advanced features
13. Add navigation links
14. Final SEO audit and testing

---

## Risk Considerations

> [!WARNING]
> The `compatible_tools` field creates a cross-app relationship from `robots.Robot` to `tools.Tool`. Use string reference `'tools.Tool'` to avoid circular imports.

> [!NOTE]
> The search integration uses a separate ChromaDB collection called `robots`.

> [!TIP]
> All SEO implementations follow existing patterns in `tool_detail.html` and `SEOModel` for consistency.
