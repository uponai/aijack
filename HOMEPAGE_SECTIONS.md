# Homepage Sections Documentation

This document explains how the homepage sections work, what appears in each section, and why.

---

## Section Order (Top to Bottom)

1. **Hero Section** - Always visible
2. **Explore by Profession** - Always visible
3. **Highlighted Apps** ⭐ - Only if items exist
4. **Highlighted Stacks** 🔥 - Only if items exist
5. **App Newbies** 🆕 - Only if items exist
6. **Stack Newbies** 📦 - Only if items exist
7. **Featured Stacks** - Only if items exist
8. **Featured Tools** - Only if items exist
9. **Newsletter CTA** - Always visible

---

## 1. Hero Section

**Always appears.**

Shows the main site headline, tagline, and semantic search bar. Users can type what they want to achieve (e.g., "AI for architects") and the system finds relevant tools.

---

## 2. Explore by Profession

**Always appears.**

Shows up to **8 professions** from the database. Each profession is a clickable chip that leads to a profession-specific page with filtered tools.

**Data source:**
```python
professions = Profession.objects.all()[:8]
```

---

## 3. Highlighted Apps ⭐ SPOTLIGHT

**Appears if:** There are tools with `highlight_start` and `highlight_end` dates that include today.

Shows up to **6 tools** that admins have manually highlighted for a specific date range in the Django admin.

**How to make items appear:**
1. Go to Django Admin → Tools → Tool
2. Edit a tool
3. Set `highlight_start` and `highlight_end` dates
4. The tool will appear in this section while today's date falls within that range

**Data source:**
```python
highlighted_tools = Tool.objects.filter(
    status='published',
    highlight_start__lte=today,
    highlight_end__gte=today
).order_by('-highlight_start')[:6]
```

---

## 4. Highlighted Stacks 🔥 HOT

**Appears if:** There are stacks with `highlight_start` and `highlight_end` dates that include today.

Shows up to **4 stacks** that admins have manually highlighted for a specific date range.

**How to make items appear:**
1. Go to Django Admin → Tools → Tool Stack
2. Edit a stack
3. Set `highlight_start` and `highlight_end` dates
4. The stack will appear in this section while today's date falls within that range

**Data source:**
```python
highlighted_stacks = ToolStack.objects.filter(
    visibility='public',
    highlight_start__lte=today,
    highlight_end__gte=today
).order_by('-highlight_start')[:4]
```

---

## 5. App Newbies 🆕 FRESH

**Appears if:** There are tools created in the last 30 days.

Shows up to **6 tools** that were added to the system recently. This section is **automatic** - no admin action required. Items rotate out after 30 days.

**Data source:**
```python
app_newbies = Tool.objects.filter(
    status='published',
    created_at__gte=thirty_days_ago  # 30 days ago
).order_by('-created_at')[:6]
```

---

## 6. Stack Newbies 📦 JUST ADDED

**Appears if:** There are stacks created in the last 30 days.

Shows up to **4 stacks** that were added recently. This section is **automatic** - items rotate out after 30 days.

**Data source:**
```python
stack_newbies = ToolStack.objects.filter(
    visibility='public',
    created_at__gte=thirty_days_ago  # 30 days ago
).order_by('-created_at')[:4]
```

---

## 7. Featured Stacks (AI TOOLKITS)

**Appears if:** There are stacks with `is_featured=True`.

Shows up to **3 stacks** that admins have marked as featured. This is **permanent** until an admin changes it.

**How to make items appear:**
1. Go to Django Admin → Tools → Tool Stack
2. Edit a stack
3. Check `is_featured`
4. The stack will appear until you uncheck it

**Data source:**
```python
featured_stacks = ToolStack.objects.filter(
    is_featured=True,
    visibility='public'
)[:3]
```

---

## 8. Featured Tools

**Appears if:** There are tools with `is_featured=True`.

Shows up to **6 tools** that admins have marked as featured. This is **permanent** until an admin changes it.

**How to make items appear:**
1. Go to Django Admin → Tools → Tool
2. Edit a tool
3. Check `is_featured`
4. The tool will appear until you uncheck it

**Data source:**
```python
featured_tools = Tool.objects.filter(
    status='published',
    is_featured=True
)[:6]
```

---

## 9. Newsletter CTA

**Always appears.**

A call-to-action section for email subscription.

---

## Quick Reference: How to Control What Appears

| Section | Control Method | Automatic? |
|---------|---------------|------------|
| Highlighted Apps | Set `highlight_start` and `highlight_end` dates | No |
| Highlighted Stacks | Set `highlight_start` and `highlight_end` dates | No |
| App Newbies | Created in last 30 days | Yes |
| Stack Newbies | Created in last 30 days | Yes |
| Featured Stacks | Check `is_featured` | No |
| Featured Tools | Check `is_featured` | No |

---

## Card Components

All sections use standardized reusable card templates:

- **Stack cards:** `templates/includes/_stack_card.html`
- **Tool cards:** `templates/includes/_tool_card.html`

This ensures visual consistency across the entire site.
