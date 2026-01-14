# AI Robots Implementation - Task Checklist

## Phase 1 - Core (Model, Migrations, Basic Views, Templates)

### 1.1 Django App Setup
- [ ] Create `robots` Django app with `python manage.py startapp robots`
- [ ] Configure `robots/apps.py` with proper app name and signal registration
- [ ] Add `'robots'` to `INSTALLED_APPS` in `config/settings.py`

### 1.2 Models - RobotCompany
- [ ] Create `RobotCompany` model in `robots/models.py`
  - [ ] Fields: `name`, `slug`, `logo`, `description`
  - [ ] Fields: `founded_year`, `headquarters`, `website`
  - [ ] Social links: `twitter_url`, `linkedin_url`, `youtube_url`
  - [ ] Property: `robot_count` (returns count of published robots)
  - [ ] SEO: `meta_title`, `meta_description`, `og_image`, `canonical_url`
  - [ ] Method: `get_schema_json()` → Organization schema
  - [ ] Method: `get_seo_title()`, `get_seo_description()`

### 1.3 Models - Robot (Core)
- [ ] Create `Robot` model extending SEO mixin
  - [ ] Basic: `name`, `slug`, `company` (FK to RobotCompany), `product_url`, `image`
  - [ ] Classification: `robot_type` (humanoid/specialized), `target_market`
  - [ ] Release: `release_date`, `availability` (choices)
  - [ ] Pricing: `pricing_tier` (choices), `price_value` (DecimalField)
  - [ ] Content: `short_description`, `long_description`
  - [ ] Content: `pros`, `cons`, `use_cases` (comma-separated text)
  - [ ] Technical: `specifications` (JSONField)
  - [ ] Cross-app: `compatible_tools` (M2M to `'tools.Tool'`)
  - [ ] Status: `status` (draft/published), `is_featured`
  - [ ] Timestamps: `created_at`, `updated_at`
  - [ ] SEO: `meta_title`, `meta_description`, `og_image`, `canonical_url`

### 1.4 Models - Robot Methods (SEO)
- [ ] Implement `get_seo_title()` - returns meta_title or default
- [ ] Implement `get_seo_description()` - returns meta_description or short_description[:160]
- [ ] Implement `get_schema_json()` - returns Product schema JSON-LD
- [ ] Implement `get_breadcrumb_json()` - returns BreadcrumbList schema
- [ ] Implement `get_pros_list()`, `get_cons_list()`, `get_use_cases_list()`
- [ ] Implement `get_missing_fields()` for admin completeness indicator
- [ ] Add helper `_get_availability_schema()` for offer availability

### 1.5 Models - RobotNews
- [ ] Create `RobotNews` model
  - [ ] Fields: `title`, `slug`, `content`, `excerpt`
  - [ ] Fields: `robots` (M2M to Robot)
  - [ ] Source: `source_name`, `source_url`
  - [ ] Image: `featured_image`
  - [ ] Dates: `published_at`, `created_at`
  - [ ] Flags: `is_featured`, `is_published`
  - [ ] SEO fields and methods
  - [ ] Method: `get_schema_json()` → NewsArticle schema

### 1.6 Migrations
- [ ] Run `python manage.py makemigrations robots`
- [ ] Run `python manage.py migrate`
- [ ] Verify tables created: `robots_robot`, `robots_robotcompany`, `robots_robotnews`

### 1.7 Basic Views
- [ ] Create `robots/views.py`
- [ ] Implement `robots_list` view with filtering (type, market, company)
- [ ] Implement `robot_detail` view with SEO context
- [ ] Implement `robot_companies` view (list)
- [ ] Implement `robot_company_detail` view with SEO context

### 1.8 URL Configuration
- [ ] Create `robots/urls.py` with clean, SEO-friendly URL patterns
- [ ] Include robots URLs in `config/urls.py`
- [ ] Patterns: `/robots/`, `/robot/<slug>/`, `/robots/company/<slug>/`

### 1.9 Templates - Main Listing (`robots.html`)
- [ ] Create `templates/robots/` directory
- [ ] Implement SEO blocks: `{% block title %}`, `{% block meta_description %}`, `{% block meta_keywords %}`
- [ ] Implement `{% block schema %}` with CollectionPage JSON-LD
- [ ] Hero section with cyan theme and robot count
- [ ] Filter dropdowns (type, market, company)
- [ ] Grid layout for robot cards
- [ ] Empty state design

### 1.10 Templates - Robot Card (`_robot_card.html`)
- [ ] Create `templates/robots/includes/_robot_card.html`
- [ ] Robot image with `alt="{{ robot.name }} - {{ robot.get_robot_type_display }} by {{ robot.company.name }}"`
- [ ] `loading="lazy"` on images
- [ ] Type badge (humanoid/specialized)
- [ ] Availability badge with color coding
- [ ] Company tag
- [ ] Name and description
- [ ] Target market and release date
- [ ] Featured badge (include `_featured_badge.html`)
- [ ] Hover effects with cyan glow

### 1.11 Templates - Detail Page (`robot_detail.html`)
- [ ] SEO blocks: title, meta_description, meta_keywords
- [ ] Schema block with Product + BreadcrumbList JSON-LD
- [ ] Visual breadcrumb navigation
- [ ] Hero image section with company link
- [ ] Full description with proper heading hierarchy (H1, H2, H3)
- [ ] Pros/Cons side-by-side cards
- [ ] Use cases as chips
- [ ] Specifications table
- [ ] Compatible AI Tools section (if any)
- [ ] Related robots section
- [ ] Save/favorite button
- [ ] Visit website CTA button

### 1.12 Static Assets
- [ ] Create `static/images/robot_placeholder.svg` (dark with cyan robot icon)
- [ ] Add robot-specific CSS to existing stylesheet or new `robots.css`
  - [ ] `.robot-card:hover` glow effect
  - [ ] `.glow-text-cyan` text shadow
  - [ ] Fade-in animations

### 1.13 Navigation
- [ ] Add "AI Robots" link to `templates/base.html` navigation
- [ ] Include robot icon (`fa-robot`)
- [ ] Add "NEW" cyan badge

---

## Phase 2 - Search (ChromaDB Integration, Search Filter)

### 2.1 ChromaDB Service
- [ ] Create `robots/search.py`
- [ ] Implement `RobotSearchService` class
  - [ ] `get_collection("robots")` method
  - [ ] `add_robots(robots)` method with text embedding
  - [ ] `remove_robots(robots)` method
  - [ ] `search(query, n_results)` method

### 2.2 Signals for Auto-Indexing
- [ ] Create `robots/signals.py`
- [ ] Implement `post_save` signal for Robot
  - [ ] If `status='published'`: add to index
  - [ ] Else: remove from index
- [ ] Implement `post_delete` signal to remove from index
- [ ] Connect signals in `robots/apps.py` `ready()` method

### 2.3 Search Page Modification
- [ ] Modify `templates/search.html`
  - [ ] Add "Search for AI robotic solutions only" checkbox
  - [ ] Style with cyan color scheme
  - [ ] Robot icon next to label
- [ ] Modify `tools/views.py` → `search` function
  - [ ] Handle `robots_only` query parameter
  - [ ] Import `RobotSearchService` from robots app
  - [ ] Add robots to search context

### 2.4 Search Results Display
- [ ] Add robots section to `search.html` results
  - [ ] Section header with robot icon and count
  - [ ] Grid of robot cards (include `_robot_card.html`)

---

## Phase 3 - Admin (Interface, Forms, CRUD Operations)

### 3.1 Forms
- [ ] Create `robots/forms.py`
- [ ] Implement `RobotForm` ModelForm
  - [ ] All robot fields in logical groups
  - [ ] Textarea widgets for descriptions
  - [ ] JSONField widget for specifications
  - [ ] M2M widget for compatible_tools
  - [ ] **SEO Fields Section**: meta_title, meta_description, og_image, canonical_url
- [ ] Implement `RobotCompanyForm` ModelForm with SEO fields
- [ ] Implement `RobotNewsForm` ModelForm with SEO fields

### 3.2 Admin Views - Robots
- [ ] Implement `admin_robots` view (list with pagination)
  - [ ] Search by name/company
  - [ ] Filter tabs: All / Incomplete
  - [ ] Show missing fields indicator (including SEO fields)
- [ ] Implement `admin_robot_create` view
- [ ] Implement `admin_robot_edit` view
- [ ] Implement `admin_robot_delete` view (with confirmation)

### 3.3 Admin Views - Companies
- [ ] Implement `admin_robot_companies` view
- [ ] Implement `admin_robot_company_create` view
- [ ] Implement `admin_robot_company_edit` view
- [ ] Implement `admin_robot_company_delete` view

### 3.4 Admin Views - News
- [ ] Implement `admin_robot_news` view
- [ ] Implement `admin_robot_news_create` view
- [ ] Implement `admin_robot_news_edit` view
- [ ] Implement `admin_robot_news_delete` view

### 3.5 Admin URL Routes
- [ ] Add admin routes to `robots/urls.py`
  - [ ] `/admin-dashboard/robots/`
  - [ ] `/admin-dashboard/robots/add/`
  - [ ] `/admin-dashboard/robots/<slug>/edit/`
  - [ ] `/admin-dashboard/robots/<slug>/delete/`
  - [ ] Similar routes for companies and news

### 3.6 Admin Templates
- [ ] Create `templates/robots/admin/admin_robots_list.html`
  - [ ] Search bar
  - [ ] Filter tabs (All/Incomplete)
  - [ ] Table: Robot, Company, Type, Availability, Completeness, Actions
  - [ ] Pagination
- [ ] Create `templates/robots/admin/admin_robot_form.html`
  - [ ] Form layout matching existing tool form
  - [ ] Image upload preview
  - [ ] JSON editor for specifications
  - [ ] **SEO Fields Section** with character counters
- [ ] Create `admin_confirm_delete.html`
- [ ] Create similar templates for companies and news

### 3.7 Admin Navigation
- [ ] Modify `templates/partials/admin_nav.html` or equivalent
  - [ ] Add "Robots" section with fa-robot icon
  - [ ] Sub-links: Robots, Companies, News

### 3.8 Django Admin Registration
- [ ] Create `robots/admin.py`
- [ ] Register `Robot` model with list_display and search_fields
- [ ] Register `RobotCompany` model
- [ ] Register `RobotNews` model

---

## Phase 4 - Polish (Analytics, SEO, Featured, Sitemap)

### 4.1 Analytics Models
- [ ] Add `RobotView` model to `robots/models.py`
  - [ ] FK to Robot
  - [ ] User (optional), session_key, ip_hash
  - [ ] source_page, created_at
- [ ] Add `SavedRobot` model
  - [ ] User FK, Robot FK
  - [ ] created_at, notes
- [ ] Run migrations

### 4.2 View Analytics Integration
- [ ] Track views in `robot_detail` view (create RobotView record)
- [ ] Implement `toggle_save_robot` API view
- [ ] Add save button to robot cards and detail page

### 4.3 Template Tags
- [ ] Create `robots/templatetags/` directory
- [ ] Create `__init__.py`
- [ ] Create `robot_extras.py`
  - [ ] `is_saved_by` filter
  - [ ] `certification_label` filter (for future)
  - [ ] `get_spec` filter for specifications JSONField

### 4.4 SEO Implementation - Complete
- [ ] Verify all templates have proper meta blocks
- [ ] Verify all models have `get_schema_json()` methods
- [ ] Verify all detail pages have `get_breadcrumb_json()` methods
- [ ] Test with [Google Rich Results Test](https://search.google.com/test/rich-results)
- [ ] Verify canonical URLs on all pages
- [ ] Verify Open Graph tags for social sharing

### 4.5 Sitemap Integration
- [ ] Create `robots/sitemaps.py`
- [ ] Implement `RobotSitemap` (priority: 0.9, changefreq: weekly)
- [ ] Implement `RobotCompanySitemap` (priority: 0.8, changefreq: weekly)
- [ ] Implement `RobotNewsSitemap` (priority: 0.7, changefreq: daily)
- [ ] Modify `config/urls.py` to include robot sitemaps
- [ ] Verify robots appear in `/sitemap.xml`

### 4.6 Featured Robots
- [ ] Verify `is_featured` ordering works (featured first)
- [ ] Add featured badge to cards (include `_featured_badge.html`)
- [ ] Highlight featured robots on listing page

### 4.7 Admin Dashboard Integration
- [ ] Modify `admin_dashboard` view to include robot stats
  - [ ] Total robots count
  - [ ] Top viewed robots
- [ ] Update `templates/admin_dashboard.html` with robots column

---

## Advanced Features

### 17. Robot Comparison Tool
- [ ] Create session-based comparison storage (max 4 robots)
- [ ] Implement `robot_comparison` view
- [ ] Create `robot_comparison.html` template
  - [ ] SEO: CollectionPage schema
  - [ ] 4 selection slots with add/remove
  - [ ] Comparison table with specs
- [ ] Implement `add_to_comparison` API endpoint
- [ ] Implement `remove_from_comparison` API endpoint
- [ ] Add "Add to Compare" button on robot cards
- [ ] Add floating comparison bar when robots selected

### 18. Company Profiles
- [ ] Verify `RobotCompany` model complete with SEO
- [ ] Create `robot_companies.html` (directory page)
  - [ ] SEO: CollectionPage schema
  - [ ] Grid of company cards with logos
  - [ ] Robot count per company
- [ ] Create `includes/_company_card.html`
- [ ] Create `robot_company_detail.html`
  - [ ] SEO: Organization schema + BreadcrumbList
  - [ ] Company hero with logo and stats
  - [ ] Description
  - [ ] Social links
  - [ ] All robots by this company (grid)
- [ ] Link companies from robot cards/detail pages

### 21. Robot Release Timeline
- [ ] Implement `robot_timeline` view
  - [ ] Group robots by release year
  - [ ] Separate upcoming section
- [ ] Create `robot_timeline.html` template
  - [ ] SEO: CollectionPage schema
  - [ ] Dark background theme
  - [ ] Vertical timeline with year markers
  - [ ] Alternating left/right robot cards
  - [ ] Upcoming robots section
- [ ] Add "Timeline" link to robots navigation

### 24. Related AI Tools Integration
- [ ] Verify `compatible_tools` M2M field on Robot model
- [ ] Display compatible tools on `robot_detail.html`
  - [ ] Grid of tool cards with logos
  - [ ] Links to tool detail pages
- [ ] Add tool selection to admin robot form (M2M widget)
- [ ] Consider adding reverse link on tool detail pages

### 27. Specification Comparison Matrix
- [ ] Implement `robot_matrix` view
- [ ] Create `robot_matrix.html` template
  - [ ] SEO: CollectionPage schema
  - [ ] Full-width scrollable table
  - [ ] Sticky first column (robot name/image)
  - [ ] Columns: Company, Price, Type, Height, Weight, Battery, Availability
  - [ ] Sortable column headers (JavaScript)
  - [ ] Color-coded values
- [ ] Add "Matrix View" link to robots navigation

### 28. Robot News Integration
- [ ] Verify `RobotNews` model complete with SEO
- [ ] Implement `robot_news_list` view
- [ ] Implement `robot_news_detail` view
- [ ] Create `robot_news.html` (listing)
  - [ ] SEO: CollectionPage schema
  - [ ] Grid of news cards (featured image, title, excerpt)
  - [ ] Linked robots badges
- [ ] Create `robot_news_detail.html`
  - [ ] SEO: NewsArticle schema + BreadcrumbList
  - [ ] Full article content
  - [ ] Linked robots section
  - [ ] Related news
- [ ] Add "News" section to `robots.html` homepage
- [ ] Display robot's news on `robot_detail.html`

---

## Final Integration & Testing

### Navigation & Links
- [ ] Verify all navigation links work
- [ ] Add breadcrumbs to all robot pages
- [ ] Ensure back links work correctly

### SEO Audit
- [ ] Run Lighthouse SEO audit on all major templates
- [ ] Test 3-5 pages with [Google Rich Results Test](https://search.google.com/test/rich-results)
- [ ] Verify sitemap includes all robot URLs
- [ ] Verify canonical URLs correct
- [ ] Verify meta titles 50-60 chars
- [ ] Verify meta descriptions 150-160 chars
- [ ] Check image alt tags

### Responsive Design
- [ ] Test robots page on mobile
- [ ] Test comparison tool on tablet
- [ ] Test matrix view horizontal scroll on small screens
- [ ] Ensure filters are mobile-friendly

### Browser Testing
- [ ] Navigate through all pages
- [ ] Test search filter
- [ ] Test comparison tool workflow
- [ ] Test admin CRUD operations
- [ ] Verify image uploads work

### Final Polish
- [ ] Review all templates for consistency
- [ ] Ensure cyan theme applied correctly
- [ ] Verify animations and hover effects
- [ ] Check loading states
- [ ] Test empty states

---

## Files Created

| File | Purpose |
|------|---------|
| `robots/__init__.py` | App init |
| `robots/apps.py` | App config with signals |
| `robots/admin.py` | Django admin registration |
| `robots/forms.py` | ModelForms with SEO sections |
| `robots/models.py` | Robot, RobotCompany, RobotNews, RobotView, SavedRobot |
| `robots/search.py` | RobotSearchService (ChromaDB) |
| `robots/signals.py` | Auto-index signals |
| `robots/sitemaps.py` | RobotSitemap, RobotCompanySitemap, RobotNewsSitemap |
| `robots/urls.py` | URL patterns |
| `robots/views.py` | All view functions |
| `robots/templatetags/__init__.py` | Template tags init |
| `robots/templatetags/robot_extras.py` | Custom filters |
| `templates/robots/*.html` | All templates |
| `static/images/robot_placeholder.svg` | Default image |

## Files Modified

| File | Change |
|------|--------|
| `config/settings.py` | Add `'robots'` to INSTALLED_APPS |
| `config/urls.py` | Include robots URLs and sitemaps |
| `templates/base.html` | Add AI Robots nav link |
| `templates/search.html` | Add robots_only checkbox |
| `tools/views.py` | Add robots to search |
| `templates/admin_dashboard.html` | Add robots stats |
| `templates/partials/admin_nav.html` | Add robots admin links |

---

## Estimated Effort

| Phase | Tasks | Tool Calls |
|-------|-------|------------|
| Phase 1 - Core | 13 major items | ~25 |
| Phase 2 - Search | 4 major items | ~8 |
| Phase 3 - Admin | 8 major items | ~15 |
| Phase 4 - Polish | 7 major items | ~12 |
| Advanced Features | 6 features | ~25 |
| Testing | Verification | ~5 |
| **Total** | | **~90** |
