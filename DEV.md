
---

## 1. Termék vízió (Product Vision)

**Cél:**
Egy többnyelvű (EN / HU / DE), AI-eszközöket aggregáló és ajánló platform, amely:

* szakmák és feladatok szerint segíti a felhasználókat,
* nemcsak listáz, hanem **megoldáscsomagokat** (tool stacks) ajánl,
* fejlett **szemantikus kereséssel** működik,
* monetizálható affiliate, kupon és prémium funkciók révén.

**Pozícionálás:**
„AI Tools Intelligence Platform” – nem csak katalógus, hanem döntéstámogató rendszer.

---

## 2. Technológiai architektúra (High-level Architecture)

### Backend

* **Python 3.12**
* **Django 5.x**
* **Django REST Framework**
* **SQLite** (relációs adatok)
* **Vector Database**:

  * első körben: **Chromadb-ben**

### Frontend

* Django Templates (SSR)
* Tailwind CSS
* Alpine.js (interakciók)
* HTMX opcionálisan (modalok, lazy content)

NINCS:

* SPA
* React / Vue
* nehéz build pipeline

### AI / Search

* Embedding API (open-source multilingual model pl. `sentence-transformers`)
* Multilingual embeddings (EN/HU/DE egy vektortérben)


## 3. Adatmodell – kulcs entitások

### AI Tool

```
Tool
- id
- slug
- status (draft / published)
- pricing_type (free / freemium / paid)
- website_url
- affiliate_url
- created_at
```

### ToolTranslation

```
ToolTranslation
- tool (FK)
- language (en/hu/de)
- name
- short_description
- long_description (rich text / markdown)
- use_cases
```

### Media

```
ToolMedia
- tool
- type (image / video)
- file
- alt_text
```

### Categories

```
Category
- slug
- icon
- parent (hierarchikus)
```

(pl. Építőipar → Tervezés → BIM)

### Professions

```
Profession
- slug
- name
- description
```

(pl. építész, kivitelező, designer, marketer)

### Tags

```
Tag
- slug
- name
```

(pl. chatbot, image-generation, automation)

---

## 4. Szemantikus keresés (KRITIKUS RÉSZ)

### Elv

* **Minden nyelv egy embedding térben**
* A keresés nem csak kulcsszavas, hanem jelentés-alapú

### Folyamat

1. Tool mentésekor:

   * összevonjuk: név + leírás + use case
   * embedding generálás
   * tárolás Chromadb-ben

2. Kereséskor:

   * user query → embedding
   * cosine similarity
   * optional filters:

     * profession
     * pricing
     * category
     * language preference

## 7. Extra funkciók – ami igazán erőssé teszi

### 7.1 Tool Stackek (nagyon ajánlott)

„Építkezési AI csomag”

* 3–7 eszköz
* workflow magyarázat
* affiliate linkek

### 7.2 AI Assistant (későbbi fázis)

„Mondd el mit csinálsz, ajánlok eszközöket”

* RAG a tool adatbázison
* profession-aware

### 7.3 Newsletter rendszer

* témák szerint
* szakmák szerint
* heti „Top AI tools for Designers”

### 7.4 Affiliate & Kupon modul

```
Affiliate
- vendor
- tracking_code
- commission_type
```

```
Coupon
- code
- discount
- expiry
- region
```

### 7.5 Admin dashboard

* tool performance
* click-through
* affiliate revenue
* search queries

---

## 8. Jogosultságok

* Public user
* Registered user
* Editor (tool feltöltés)
* Admin

---

## 9. SEO & növekedés

* Programmatic SEO:

  * „Best AI tools for {profession}”
  * „AI tools for {task}”
* Multilingual SEO (hreflang)
* Schema.org (SoftwareApplication)

---

## 10. Roadmap javaslat

**MVP**

* Tool listing
* Semantic search
* Categories + professions
* Newsletter
* Affiliate link

**V2**

* Tool stacks
* Comparison
* Analytics

**V3**

* AI Assistant
* Personalization
* Premium access


---

---

# 1. UX alapelvek (Design Principles)

1. **Intent-first UX**

   * Nem „eszközöket” keres a user, hanem megoldást
   * UX mindig azt kérdezi: *Mit akarsz csinálni?*

2. **Progresszív felfedezés**

   * Kezdők: guided flow
   * Haladók: gyors keresés, szűrők

3. **Decision support, nem lista**

   * Miért ez az eszköz?
   * Kinek való?
   * Mivel kombináld?

4. **Trust & credibility**

   * strukturált leírás
   * use case-ek
   * vizuális anyag minden toolnál

---

# 2. Fő navigációs struktúra (Information Architecture)

### Globális felső navigáció

```
[ Search ]
[ Professions ]
[ Use cases ]
[ Tool stacks ]
```

Mobilon:

* Bottom tab bar

  * Home
  * Search
  * Explore
  * Saved
  * Profile

---

# 3. Home page UX (kulcsoldal)

### 3.1 Hero szekció (nem marketing bullshit)

**Primary input: Semantic Search**

```
"What do you want to build or solve?"
[ semantic input field ]
```

Alatta:

* placeholder példák:

  * “AI tools for architects”
  * “Automate client emails”
  * “AI for construction cost estimation”

Nyelv automatikusan felismerve.

---

### 3.2 Quick entry pointok

**Cards / chips:**

* By profession
* By task
* By industry

Pl.

* Architect
* Designer
* Marketer
* Developer
* Builder

---

### 3.3 Featured tool stacks

```
AI Toolkits for Professionals
[ Construction AI Toolkit ]
[ Designer AI Toolkit ]
[ Marketing Automation Stack ]
```

Ez **erősen monetizálható UX elem**.

---

# 4. Profession landing page UX

Példa: **Architect**

### 4.1 Hero

* Rövid szakma-specifikus statement
* „How AI helps architects”

### 4.2 Recommended stacks

```
Essential AI tools for architects
[ Stack card ]
```

### 4.3 Tool list (nem sima lista)

Minden card tartalmazza:

* tool name
* 1 mondatos value proposition
* pricing badge
* primary use case
* affiliate indicator (diszkréten)

### 4.4 Filters (UX szempontból fontos)

* Task type
* Pricing
* Learning curve
* Language support

---

# 5. Tool detail page UX (kritikus)

Ez az oldal **nem lehet üres vagy gyenge**, itt dől el a hitelesség.

### 5.1 Above the fold

```
[ Tool logo ]
Tool name
Short value proposition

[ Visit website ]
[ Save tool ]
```

Badge-ek:

* Free / Paid
* Best for: Architect
* Affiliate disclosure (UX-barát)

---

### 5.2 Visual proof

* Screenshot carousel
* Video embed (ha van)

---

### 5.3 Structured content (nem ömlesztve)

**Tabs vagy szekciók:**

* Overview
* Use cases
* Who is this for?
* Pros / Cons
* Pricing
* Alternatives

---

### 5.4 Semantic context

```
People also use this tool for:
- Cost estimation
- Floor plan generation
```

Ez **vector search eredményből** jön.

---

### 5.5 Monetizáció UX

* „Exclusive coupon available”
* „Affiliate link” – etikusan, transzparensen

---

# 6. Semantic search UX

### 6.1 Search input viselkedés

* Nem autocomplete
* Inkább: *suggested intents*

Pl. gépelés közben:

* „You might be looking for…”
* profession
* tool stack
* specific tools

---

### 6.2 Result page layout

Bal oldalon:

* intent summary:
  „Showing tools for: Architects → Design automation”

Jobb oldalon:

* Ranked results
* Explanation hint:
  „Why this tool matches your query”

Ez **bizalomnövelő UX**.

---

# 7. Tool Stack page UX (kiemelten fontos)

Ez az oldal különböztet meg a versenytársaktól.

### 7.1 Stack overview

```
Construction AI Toolkit
What this stack helps you achieve
```

### 7.2 Workflow diagram (vizuális)

* Step 1: Ideation
* Step 2: Design
* Step 3: Cost
* Step 4: Execution

### 7.3 Tools in stack

* miért ez
* mivel működik együtt

---

# 8. Newsletter UX

### 8.1 Low-friction signup

* oldalsáv
* exit intent
* tool page alján

### 8.2 Preference-based UX

User kiválasztja:

* profession
* language
* frequency

Ez **kulcs a relevanciához**.

---

# 9. User account UX (optional MVP+)

* Saved tools
* Saved stacks
* History (keresések)
* Personalized recommendations

---

# 10. Admin / Editor UX (nem csak backend)

Fontos, hogy **nem technikai editor** használja.

* Rich text editor
* Visual preview
* Embedding status indicator
* SEO preview

---

# 11. Design direction (guidance a designernek)

**Stílus:**

* editorial / knowledge platform
* nem app-szerű
* nagy whitespace
* typográfia dominál

**Inspirációk (nem másolni):**

* Notion
* Linear
* Stripe docs
* Arc browser site


---

# 12. Felhasználói Út (User Journey Map)

---


## Persona: „Ádám” – építész / tervező (Architect Persona)

**Profil**

* 35–45 éves
* KKV vagy freelancer
* Használ digitális eszközöket, de nincs ideje „AI-t kutatni”
* Fájdalompont: időhiány, költségkontroll, komplex workflow

**Cél**

> „Szeretnék olyan AI-eszközöket találni, amelyek tényleg segítenek gyorsabban és pontosabban tervezni.”

---

## 1. Fázis – Awareness (Rájövök, hogy van megoldás)

### Trigger

* Hall AI-ról egy kollégától
* Google keresés:

  > „AI tools for architects”
  > „AI építészet tervezés”

### Touchpoint

* SEO landing page
* Home page

### UX élmény

* Nem marketing szöveg
* Azonnali relevancia:

  * „AI tools for architects”
  * „Design faster. Reduce rework.”

### Érzelmi állapot

* Kíváncsi
* Szkeptikus

### UX opportunity

* Hero search mező intent-alapon
* Profession quick entry („Architect”)

---

## 2. Fázis – Exploration (Felfedezés)

### Felhasználói gondolat

> „Oké, nézzük meg, mit tud ez az oldal.”

### Touchpoint

* Profession landing page (Architect)

### UX elemek

* Rövid szakma-specifikus bevezető
* „Recommended AI Toolkit for Architects”
* Tool cardok nem technikai nyelvezettel

### Fájdalompont csökkentés

* Nem kell 100 eszközt végiglapozni
* „Best for…” jelölések

### Érzelmi állapot

* Megkönnyebbülés
* Kontroll érzése

---

## 3. Fázis – Intent clarification (Mit is akarok pontosan?)

### Felhasználói gondolat

> „Engem most főleg a költségbecslés és az előtervezés érdekel.”

### Touchpoint

* Semantic search
* Use case filter

### UX működés

* Beírja:

  > „cost estimation for buildings”
* Rendszer visszajelzése:

  > „We found tools used by architects for cost estimation”

### Extra UX elem

* „Why these tools match your intent”

### Érzelmi állapot

* Megerősödő bizalom

---

## 4. Fázis – Evaluation (Összehasonlítás)

### Felhasználói gondolat

> „Ez tényleg jó? Nem hype?”

### Touchpoint

* Tool detail page
* Comparison (opcionális)

### UX elemek

* Screenshotok
* Use case-ek
* Pros / Cons (nem marketing)
* Pricing átlátható

### Bizalomépítés

* „Used together with…”
* „Alternatives”

### Érzelmi állapot

* Kritikus
* Elemző

---

## 5. Fázis – Decision (Döntés)

### Felhasználói gondolat

> „Ezt kipróbálom.”

### Touchpoint

* Tool detail page CTA

### UX döntést segítő elemek

* „Start free trial”
* „Exclusive coupon available”
* Affiliate disclosure korrekt módon

### Frikció csökkentése

* Külső link egyértelmű
* „What happens next?” mini tooltip

---

## 6. Fázis – Activation (Használatba veszem)

### Off-platform esemény

* Felhasználó regisztrál a toolnál

### Platform szerepe

* Follow-up email:

  > „Want to see more AI tools for architects?”

### UX opportunity

* Saved tools
* Bookmark stack

---

## 7. Fázis – Retention (Visszatérés)

### Trigger

* Newsletter
* Új tool stack

### Touchpoint

* Email
* Direct visit

### UX elemek

* Personalized recommendations
* „New tools added for architects”

### Érzelmi állapot

* Elégedettség
* Rendszeres használat

---

## 8. Fázis – Advocacy (Ajánlás)

### Felhasználói gondolat

> „Ezt megmutatom a kollégáimnak.”

### Touchpoint

* Share tool
* Share stack

### UX elemek

* One-click share
* „Send to colleague”

### Üzleti érték

* Organikus növekedés
* Referral

---

# Journey Map – összefoglaló táblázat

| Fázis       | Cél         | UX fókusz       | Üzleti érték   |
| ----------- | ----------- | --------------- | -------------- |
| Awareness   | Relevancia  | SEO + intent    | Traffic        |
| Exploration | Áttekintés  | Szakma fókusz   | Engagement     |
| Intent      | Pontosítás  | Semantic search | Minőségi click |
| Evaluation  | Bizalom     | Rich content    | Conversion     |
| Decision    | Akció       | CTA + coupon    | Affiliate      |
| Retention   | Visszatérés | Personalization | LTV            |
| Advocacy    | Megosztás   | Share UX        | Growth         |

---

## Mitől ez **jobb**, mint egy sima „AI tools list”?

* Nem eszközökről, hanem **döntésekről** szól
* Szakmák szerint gondolkodik
* Szemantikus, nem technikai
* Monetizáció UX-be ágyazva, nem tolakodó