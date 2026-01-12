# Bulk Tool Upload System

A professional AI-powered bulk import system for adding AI tools to the AIJACK platform via CSV files.

## Overview

This feature allows administrators to upload a CSV file containing AI tool information and automatically:
1. **Validate** the data for completeness
2. **Detect duplicates** by tool name and website domain
3. **Generate rich metadata** using AI (Gemini Flash)
4. **Create tools** with full translations, categories, professions, and tags

## File Structure

```
tools/
├── ai_service.py      # AIService.generate_tool_metadata() method
├── views.py           # bulk_upload_tools() view
├── urls.py            # URL route registration
templates/
├── admin_bulk_upload.html   # Three-step wizard UI
├── partials/
│   └── admin_nav.html       # Navigation with Bulk Upload tab
```

## CSV Format

The system expects a **semicolon-separated CSV** file with the following columns:

| Column | Required | Description |
|--------|----------|-------------|
| Tool Name | ✅ Yes | Name of the AI tool |
| Website URL | ✅ Yes | Official website URL |
| Short Description | ✅ Yes | Brief description (max 300 chars) |
| Detailed Description | ❌ No | Full description for tool page |
| Pricing Strategy | ❌ No | Pricing info (e.g., "Freemium / Subscription") |

### Example CSV
```csv
Tool Name;Website URL;Short Description;Detailed Description;Pricing Strategy
TestFit;https://www.testfit.io;Rapid site planning using AI.;TestFit uses generative algorithms...;Subscription / Enterprise
```

## How It Works

### Step 1: Upload & Validate
- User uploads a CSV file
- System parses with semicolon delimiter
- Validates required fields (Tool Name, Website URL, Short Description)
- Checks for duplicates by:
  - Tool slug (generated from name)
  - Website domain (extracted from URL)
- Shows preview with status for each row

### Step 2: AI-Powered Import
For each valid row, the AI generates:
- **pricing_type**: Converts CSV text → `free`, `freemium`, or `paid`
- **category_names**: 1-3 relevant categories
- **profession_names**: 1-4 target professions
- **tag_names**: 3-6 feature tags
- **meta_title**: SEO-optimized title (50-60 chars)
- **meta_description**: SEO description (150-160 chars)
- **use_cases**: 3-5 practical use cases
- **pros**: 3-5 advantages
- **cons**: 2-3 limitations

### Step 3: Results
- Shows created/skipped/error counts
- Links to view each created tool
- Option to upload more files

## API Reference

### `AIService.generate_tool_metadata()`

```python
from tools.ai_service import AIService

metadata = AIService.generate_tool_metadata(
    tool_name="TestFit",
    website_url="https://www.testfit.io",
    short_description="Rapid site planning using AI.",
    long_description="TestFit uses generative algorithms...",
    pricing_text="Subscription / Enterprise",
    existing_categories=["Design", "Construction"],
    existing_professions=["Architect", "Developer"],
    existing_tags=["AI-powered", "automation"]
)

# Returns:
{
    "pricing_type": "paid",
    "category_names": ["Design", "Architecture"],
    "profession_names": ["Architect", "Urban Planner"],
    "tag_names": ["AI-powered", "generative", "cloud-based"],
    "meta_title": "TestFit - AI Site Planning & Feasibility Tool",
    "meta_description": "Automate site layouts and feasibility studies...",
    "use_cases": "Site planning, Massing analysis, Unit mix optimization",
    "pros": "Fast iteration, Real-time feedback, Compliance checking",
    "cons": "Learning curve, Requires accurate input data"
}
```

### URL Route
```
/admin-dashboard/bulk-upload/
```

## Access Control

- Requires **staff member** authentication (`@staff_member_required`)
- Requires **superuser** privileges (checked in view)

---

## Improvement Suggestions

### High Priority

1. **Async Processing with Celery**
   - Current implementation processes tools synchronously
   - For 50+ tools, this causes HTTP timeouts
   - Solution: Use Celery tasks with progress WebSocket updates

2. **Rate Limiting for AI Calls**
   - Gemini API has rate limits
   - Add small delays between calls (e.g., 100ms)
   - Implement exponential backoff on 429 errors

3. **Transaction Rollback**
   - Wrap tool creation in database transaction
   - If AI fails mid-import, partially created tools remain
   - Use `@transaction.atomic` with savepoints

### Medium Priority

4. **Progress Streaming**
   - Use Server-Sent Events (SSE) or WebSocket
   - Show real-time progress during import
   - Display current tool being processed

5. **Dry Run Mode**
   - Preview what AI would generate without creating
   - Let admin review AI suggestions before commit
   - Add "Edit before import" capability

6. **Logo Fetching**
   - Auto-fetch favicon/logo from tool website
   - Use services like Clearbit Logo API
   - Store in `tool.logo` field

7. **URL Validation**
   - Verify website URLs are reachable
   - Check for 404s or redirects
   - Flag suspicious domains

### Low Priority

8. **CSV Column Mapping**
   - Allow custom column name mapping
   - Support different delimiters (comma, tab)
   - Handle different date formats

9. **Undo/Rollback Feature**
   - Track which tools were created in batch
   - Allow "undo last import" action
   - Keep import history log

10. **Duplicate Merge**
    - Instead of skipping duplicates, offer merge
    - Update existing tool with new data
    - Show diff of changes

11. **Export Feature**
    - Export existing tools to CSV
    - Useful for backup or transfer
    - Round-trip edit capability

---

## Troubleshooting

### Template Not Found Error
If you see `TemplateDoesNotExist: admin_bulk_upload.html`:
1. Verify file exists at `templates/admin_bulk_upload.html`
2. Restart Django development server
3. Check `TEMPLATES['DIRS']` in settings.py

### AI Generation Fails
If AI metadata is empty or default:
1. Check `GEMINI_API_KEY` is set in `.env`
2. Verify API quota hasn't been exceeded
3. Check console for "AI Metadata Gen Error" messages

### Session Data Lost
If validation results disappear:
1. Check `SESSION_ENGINE` in settings
2. Ensure session middleware is enabled
3. Verify cookies are not blocked

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-12 | Initial release with AI-powered metadata generation |
