# Neonpunk Design System Documentation

This document outlines the design system used in the **IAS Fund** application. The system, codenamed "Neonpunk," combines a modern, light-themed aesthetic with vibrant neon accents, glassmorphism, and futuristic typography.

## 1. Core Principles
- **Light & Airy**: Unlike traditional cyberpunk (dark), this theme uses a white/light blue base to feel professional and clean.
- **Neon Accents**: Critical actions and data points are highlighted with vibrant cyan, magenta, and lime neon glows.
- **Glassmorphism**: Cards and overlays use semi-transparent backgrounds with blur effects to create depth.
- **Futuristic Typography**: A combination of tech-inspired fonts creates a unique brand identity.
### Backgrounds
The application uses a subtle gradient background with a grid overlay.

- **Gradient**: `linear-gradient` from `#eff6ff` (Blue 50) to `#ffffff` (White).
- **Grid Pattern**: Faint blue grid lines (`rgba(2, 132, 199, 0.1)`) on top of the gradient.
- **Card Background**: `rgba(255, 255, 255, 0.85)` with `backdrop-filter: blur(10px)`.

## 2. Colors

### Brand Colors
The primary brand color is **Sky Blue** (`#0284c7`), which serves as the foundation for the "Neon Cyan" effects.

| Color Name | Hex Code | Usage |
| :--- | :--- | :--- |
| **Brand (Sky 600)** | `#0284c7` | Primary actions, headings, borders, glows |
| **Brand Dark (Sky 700)**| `#0369a1` | Hover states |

### Backgrounds
The application uses a subtle gradient background with a grid overlay.

- **Gradient**: `linear-gradient` from `#eff6ff` (Blue 50) to `#ffffff` (White).
- **Grid Pattern**: Faint blue grid lines (`rgba(2, 132, 199, 0.1)`) on top of the gradient.
- **Card Background**: `rgba(255, 255, 255, 0.85)` with `backdrop-filter: blur(10px)`.

### Typography Colors
Designed for high contrast on light backgrounds.

- **Main Text**: `#0f172a` (Slate 900)
- **Muted Text**: `#475569` (Slate 600)

## 3. Typography

### Headings
- **Font Family**: `Orbitron`, sans-serif
- **Weights**: 400, 700, 900
- **Style**: Uppercase, letter-spacing `0.05em`
- **Usage**: Page titles `<h1>`, Section headers `<h2> - <h6>`, `.heading-font`

### Body Text
- **Font Family**: `Rajdhani`, sans-serif
- **Weights**: 300, 400, 500, 600, 700
- **Usage**: Paragraphs, navigation links, buttons, inputs

## 4. UI Components

All components are defined in the global `<style>` block in `templates/base/base.html`.

### Buttons

#### Cyan Button (`.neon-button-cyan`)
Primary action button. Transparent background with cyan border and text. Fills on hover.
```html
<button class="neon-button-cyan">Action</button>
```

#### Magenta Button (`.neon-button-magenta`)
Secondary or "Danger" action button. Transparent background with magenta border and text. Fills on hover.
```html
<button class="neon-button-magenta">Danger / Alert</button>
```

### Cards (`.neon-card`)
The fundamental container for content. Features rounded corners, glassmorphism, and a slight lift on hover.
```html
<div class="neon-card p-6">
  <!-- Content -->
</div>
```

### Inputs (`.neon-input`)
Styled form inputs with a semi-transparent white background and a subtle blue border.
```html
<input type="text" class="neon-input w-full" placeholder="Enter text...">
```

### Badges
Used for status indicators.
- **Green**: `.neon-badge-green` (Success / Active)
- **Yellow**: `.neon-badge-yellow` (Warning / Pending)
- **Red**: `.neon-badge-red` (Error / Cancelled)

### Sliders (`.neon-slider`)
Custom styled range inputs with a gradient track and a glowing thumb.

### Progress Bars (`.neon-progress-bar`)
Gradient bar with `transition` effects, used for campaign goals.

### Tables (`.neon-table`)
Clean tables with cyan uppercase headers and subtle row hover effects.

## 5. Effects & Utilities

### Glows (CSS Variables)
- `--glow-cyan`: `0 0 15px rgba(2, 132, 199, 0.4)`
- `--glow-magenta`: `0 0 15px rgba(2, 132, 199, 0.4)`
*(Note: Shifts mainly to brand blue shadow on light mode to maintain consistency)*

### Animations
- **Glow Pulse**: `.glow-pulse` class adds a pulsating shadow effect.
```css
@keyframes glow-pulse {
    0%, 100% { box-shadow: 0 0 10px rgba(0, 240, 255, 0.3); }
    50% { box-shadow: 0 0 25px rgba(0, 240, 255, 0.6); }
}
```

## 6. CSS Framework
The project uses **Tailwind CSS** (via CDN) for layout and utility classes, extended with the custom "Neonpunk" styles defined in `base.html`.

### Tailwind Configuration
The Tailwind config is injected via script in `base.html` to extend the color palette:
- `cyan`, `purple`, `lime`, `magenta` are all mapped to the brand blue range (`#0284c7`) to enforce the monochrome/duotone aesthetic while keeping semantic class names.
