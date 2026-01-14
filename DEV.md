# IAS AI Tools Platform – Detailed MVP Specification

## 1. Product Vision
**Goal:** A multilingual (EN/HU/DE), AI-powered platform that aggregates and recommends AI tools and "tool stacks" based on user professions and intent. It goes beyond a simple directory by providing solution-oriented packages and semantic search capabilities.

**Positioning:** "AI Tools Intelligence Platform" – A decision support system for professionals, not just a catalog.

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

### 2.3 UI Components
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
- **Avoid**: SPA complexities (React/Vue), heavy build pipelines.

---

## 4. Data Models (Core Entities)

### 4.1 AI Tool (`Tool`)
- `id`, `slug`: Unique identifiers.
- `website_url`, `affiliate_url`.
- `status`: Draft / Published.
- `pricing_type`: Free / Freemium / Paid.
- `created_at`, `updated_at`.

### 4.2 Translation (`ToolTranslation`)
- `tool`: FK to Tool.
- `language`: EN / HU / DE.
- `name`: Localized name (if applicable).
- `short_description`: Concise summary for cards.
- `long_description`: Rich text/Markdown detailed view.
- `use_cases`: List of specific applications.
- `pros`: List of advantages.
- `cons`: List of limitations.

### 4.3 Media (`ToolMedia`)
- `tool`: FK to Tool.
- `type`: Image / Video.
- `file`: Path to file.
- `alt_text`: For accessibility.

### 4.4 Classification
- **Category**: Hierarchical (e.g., Construction -> Design -> BIM).
- **Profession**: Target roles (e.g., Architect, Marketer).
- **Tags**: Specific features (e.g., "generative", "automation").

### 4.5 Tool Stacks (`ToolStack`)
- "Packages" of tools solving a specific complex problem.
- `tools`: Many-to-Many relationship with Tool.
- `workflow_description`: How to use them together.

---

## 5. Semantic Search & AI Logic
**Critical USP:** Users search by *intent* ("How to design a house faster"), not just keywords. All languages coexist in the same embedding space.

### 5.1 Ingestion Process
1. Concatenate `Tool` data (Name + Description + Use Cases).
2. Generate Embedding using a multilingual model.
3. Store vector in **Chromadb**.

### 5.2 Search Process
1. User enters query (e.g., "automated email marketing").
2. Query is converted to vector.
3. Cosine Similarity search performed in Chromadb.
4. Filters applied (Language/Pricing/Profession).
5. Result: Ranked list of Tools and Stacks.

---

## 6. UX Principles
1. **Intent-first UX**: Users aren't looking for "tools", they are looking for solutions. The UX always asks: *What do you want to achieve?*
2. **Progressive Discovery**: Guided flow for beginners, fast search and filters for power users.
3. **Decision Support**: Not just a list. Explain *Why this tool?*, *Who is it for?*, and *What does it work with?*.
4. **Trust & Credibility**: Structured descriptions, use cases, and visual proof for every tool.

---

## 7. UX & Frontend Flow

### 7.1 Global Structure
- **Nav**: Search, Professions, Use Cases, Stacks.
- **Mobile**: Bottom tab bar (Home, Search, Explore, Saved, Profile).

### 7.2 Home Page (The "Concierge")
- **Hero**: "What do you want to build or solve?"
  - Large, semantic inputs.
  - Examples: "AI tools for architects", "Automate client emails".
  - Auto-language detection.
- **Quick Entry**: Chips/Cards for Professions (Architect, Developer, Marketer, Builder).
- **Featured Stacks**: "AI Toolkits for [Profession]" (High monetization potential).

### 7.3 Profession Landing Page (e.g., /architects)
- **Hero**: "AI for Architects" - Short, specific statement.
- **Recommended Stack**: The "Starter Pack" for this profession.
- **Tool List**: Cards with value prop, pricing badge, and affiliate link.
- **Filters**: Task type, Pricing, Learning curve, Language support.

### 7.4 Tool Detail Page
**The "Money Page" – where trust is built.**
- **Above the Fold**: Logo, Name, Short value prop, "Visit Website" (CTA), Badges (Free/Paid, Best for X).
- **Visual Proof**: Screenshot carousel or video embed.
- **Structured Content**: Tabs/Sections for Overview, Use cases, "Who is this for?", Pros/Cons, Pricing, Alternatives.
- **Semantic Context**: "People also use this tool for..." (derived from vector search).
- **Monetization**: "Exclusive coupon available", transparent Affiliate disclosure.

### 7.5 Tool Stack Page
- **Overview**: "Construction AI Toolkit" - What this stack helps you achieve.
- **Workflow Diagram**: Visual step-by-step (Ideation -> Design -> Cost -> Execution).
- **Synergy**: Explanation of why these tools work well together.

### 7.6 Newsletter
- Low-friction signup (sidebar, exit intent).
- Preference-based: Users select profession and language.

---

## 8. User Journey Map

### Persona: "Adam" – Architect / Designer
**Profile**: 35-45 years old, freelancer or SME owner. Uses digital tools but lacks time to "research AI".
**Pain Point**: Lack of time, need for cost control, complex workflows.
**Goal**: "I want to find AI tools that actually help me design faster and more accurately."

### Phase 1: Awareness
- **Trigger**: Hears about AI from a colleague or Googles "AI tools for architects".
- **Touchpoint**: SEO landing page or Home page.
- **UX Experience**: No marketing fluff. Immediate relevance: "Design faster. Reduce rework."

### Phase 2: Exploration
- **Thought**: "Okay, let's see what this site can do."
- **Touchpoint**: Profession Landing Page (Architect).
- **UX Elements**: "Recommended AI Toolkit for Architects". Cards with non-technical language.
- **Result**: Relief. Doesn't have to browse 100 tools.

### Phase 3: Intent Clarification
- **Thought**: "I'm specifically interested in cost estimation."
- **Touchpoint**: Semantic Search.
- **Action**: Types "cost estimation for buildings".
- **Result**: "We found tools used by architects for cost estimation." (Trust building).

### Phase 4: Evaluation
- **Thought**: "Is this actually good? Is it just hype?"
- **Touchpoint**: Tool Detail Page.
- **UX Elements**: Screenshots, Pros/Cons, Pricing transparency, "Used together with...".
- **Result**: Critical analysis turns into confidence.

### Phase 5: Decision
- **Thought**: "I'll try this."
- **Touchpoint**: Tool Detail CTA.
- **UX Elements**: "Start free trial", "Exclusive coupon", clear exit link.

### Phase 6: Activation & Retention
- **Event**: User registers at the tool's site.
- **Platform Follow-up**: Newsletter "Want to see more AI tools for architects?".
- **Return**: Comes back for new stacks or recommendations.

---

## 9. Monetization Strategy
- **Affiliate Links**: Primary revenue source on external clicks.
- **Coupons**: Exclusive deals to drive conversion.
- **Sponsored Stacks**: (Future) Vendors paying to be part of a recommended stack.
- **Newsletter**: Recurring engagement.

---

## 10. Roadmap (MVP)

### Phase 1: Foundation
- [ ] Setup Django project & Tailwind/Alpine environment.
- [ ] Implement `DESIGN_SYSTEM.md` styles.
- [ ] Define Models (Tool, Category, Profession).
- [ ] Setup Chromadb pipeline.

### Phase 2: Core Data & Search
- [ ] Create Admin interface for adding Tools/Translations.
- [ ] Implement Semantic Search logic.
- [ ] Build Home Page with Search Input.

### Phase 3: Public Views
- [ ] Build Profession & Category pages.
- [ ] Build Tool Detail page.
- [ ] Implement Tool Stacks logic and views.

### Phase 4: Polish & Growth
- [ ] SEO implementation.
- [ ] Mobile responsiveness check.
- [ ] Newsletter signup integration.