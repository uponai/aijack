# IAS AI Tools Platform – Detailed MVP Specification

## 1. Product Vision (Termék Vízió)
**Goal:** A multilingual (EN/HU/DE), AI-powered platform that aggregates and recommends AI tools and "tool stacks" based on user professions and intent. It goes beyond a simple directory by providing solution-oriented packages and semantic search capabilities.

**Positioning:** "AI Tools Intelligence Platform" – A decision support system for professionals.

**Target Audience:** Architects, Designers, Developers, Marketers, and other professionals looking to optimize their workflow tools without endless research.

---

## 2. Design System: "Neonpunk"
The application uses the **"Neonpunk"** design system (defined in `DESIGN_SYSTEM.md`), combining a light-themed professional base with vibrant neon accents and glassmorphism.

### 2.1 Core Principles
- **Light & Airy**: White/Light Blue base (`#eff6ff` to `#ffffff`) for a clean, professional look.
- **Neon Accents**: Vibrant Cyan (`#0284c7` base), Magenta, and Lime for actions and highlights.
- **Glassmorphism**: Semi-transparent cards (`rgba(255, 255, 255, 0.85)`) with `backdrop-filter: blur(10px)`.
- **Futuristic Typography**: `Orbitron` (Headings) and `Rajdhani` (Body).

### 2.2 Color Palette
| Role | Color | Hex/Class | Usage |
|------|-------|-----------|-------|
| **Primary Brand** | Sky Blue | `#0284c7` / `text-sky-600` | Primary actions, glows, borders |
| **Background** | Gradient | `#eff6ff` -> `#ffffff` | Page background with faint grid overlay |
| **Text Main** | Slate 900 | `#0f172a` | Primary content |
| **Text Muted** | Slate 600 | `#475569` | Secondary info |
| **Accents** | Neon Cyan/Magenta | Custom CSS vars | Glow effects, buttons |

### 2.3 UI Components (Classes)
- **Buttons**:
  - Primary: `.neon-button-cyan` (Transparent w/ cyan border, fills on hover)
  - Secondary/Alert: `.neon-button-magenta`
- **Cards**: `.neon-card` (Rounded, glassmorphism, hover lift)
- **Inputs**: `.neon-input` (Semi-transparent, subtle border)
- **Badges**: `.neon-badge-green`, `.neon-badge-yellow`, `.neon-badge-red`

---

## 3. Technical Architecture

### 3.1 Backend
- **Language**: Python 3.12
- **Framework**: Django 5.x + Django REST Framework (DRF)
- **Database**: 
  - Relational: **SQLite** (for MVP simplicity and portability)
  - Vector: **Chromadb** (for storing embeddings of tools/stacks)
- **Search**: Semantic search using `sentence-transformers` (multilingual model).

### 3.2 Frontend
- **Rendering**: Django Templates (SSR) for SEO and performance.
- **Styling**: Tailwind CSS + Custom "Neonpunk" CSS.
- **Interactivity**: Alpine.js (lightweight JS for UI state).
- **HTMX** (Optional): For lazy loading and modal interactions without full SPA complexity.

---

## 4. Data Models (Core Entities)

### 4.1 AI Tool (`Tool`)
- `id`, `slug`: Unique identifiers.
- `name`, `website_url`, `affiliate_url`.
- `status`: Draft / Published.
- `pricing_type`: Free / Freemium / Paid.
- `created_at`, `updated_at`.

### 4.2 Translation (`ToolTranslation`)
- `tool`: FK to Tool.
- `language`: EN / HU / DE.
- `short_description`: Concise summary for cards.
- `long_description`: Rich text/Markdown detailed view.
- `use_cases`: List of specific applications.

### 4.3 Classification
- **Category**: Hierarchical (e.g., Construction -> Design -> BIM).
- **Profession**: Target roles (e.g., Architect, Marketer).
- **Tags**: Specific features (e.g., "generative", "automation").

### 4.4 Tool Stacks (`ToolStack`)
- "Packages" of tools solving a specific complex problem.
- `tools`: Many-to-Many relationship with Tool.
- `workflow_description`: How to use them together.

---

## 5. Semantic Search & AI Logic
**Critical USP:** Users search by *intent* ("How to design a house faster"), not just keywords.

### 5.1 Ingestion Process
1. Concatenate `Tool` data (Name + Description + Use Cases).
2. Generate Embedding using a multilingual model.
3. Store vector in **Chromadb**.

### 5.2 Search Process
1. User enters query ("automated email marketing").
2. Convert query to vector.
3. Perform Cosine Similarity search in Chromadb.
4. Filter results by Language/Pricing/Profession if selected.
5. Return ranked list of Tools and Stacks.

---

## 6. UX & Frontend Flow

### 6.1 Global Structure
- **Nav**: Search, Professions, Use Cases, Stacks.
- **Mobile**: Bottom tab bar (Home, Search, Explore, Profile).

### 6.2 Home Page (The "Concierge")
- **Hero**: "What do you want to build or solve?" with a large specific semantic search bar.
- **Quick Entry**: Chips for Professions (Architect, Developer, etc.).
- **Featured Stacks**: "AI Toolkits for [Profession]" (High monetization potential).

### 6.3 Profession Landing Page (e.g., /architects)
- **Hero**: "AI for Architects".
- **Recommended Stack**: The "Starter Pack" for this profession.
- **Tool List**: Cards with value prop, pricing badge, and affiliate link.
- **Filters**: Task type, Pricing, Curve.

### 6.4 Tool Detail Page
- **Header**: Logo, Name, Value Prop, "Visit Website" (CTA).
- **Visuals**: Screenshot/Video carousel (Glassmorphism container).
- **Content**: Tabs for Overview, Use Cases, "Who is this for?", Pricing.
- **Context**: "People also use this for..." (Vector search suggestions).
- **Monetization**: Coupon codes, Affiliate disclosure.

### 6.5 Tool Stack Page
- **Overview**: "Construction AI Toolkit" - What it achieves.
- **Workflow**: Step-by-step diagram (Step 1: Tool A, Step 2: Tool B).
- **Synergy**: Why these tools work well together.

---

## 7. Monetization Strategy
- **Affiliate Links**: Primary revenue source on external clicks.
- **Coupons**: Exclusive deals to drive conversion.
- **Sponsored Stacks**: (Future) Vendors paying to be part of a recommended stack.
- **Newsletter**: "Weekly AI Tools for [Profession]" capture.

---

## 8. Implementation Roadmap (MVP)

### Phase 1: Foundation
- [ ] Setup Django project & Tailwind/Alpine environment.
- [ ] Implement `DESIGN_SYSTEM.md` styles (base.html, CSS variables).
- [ ] Define Models (Tool, Category, Profession).
- [ ] Setup Chromadb pipeline.

### Phase 2: Core Data & Search
- [ ] Create Admin interface for adding Tools/Translations.
- [ ] Implement Semantic Search logic (Embedding generation).
- [ ] Build Home Page with Search Input.

### Phase 3: Public Views
- [ ] Build Profession & Category pages.
- [ ] Build Tool Detail page (the "Money Page").
- [ ] Implement Tool Stacks logic and views.

### Phase 4: Polish & Growth
- [ ] SEO implementation (Sitemap, Metadata).
- [ ] Mobile responsiveness check.
- [ ] Newsletter signup integration.
