# PatchHive Brand Guidelines

**Version 1.0 | ABX-Core Compliant Visual Identity**

---

## Design Philosophy

PatchHive's visual identity embodies the **techno-occult** aesthetic of modular synthesis: precise, geometric, deterministic, yet evocative of hidden signal flows and emergent complexity.

### Core Principles

1. **Modularity**: All elements are composable, grid-aligned, and reusable
2. **Determinism**: Visual language is consistent and rule-based
3. **Eurorack Mental Model**: Every design element references voltage, signals, or synthesis
4. **Entropy Minimization**: No organic forms, no gradients (except glow), pure geometry
5. **SEED Compliance**: All assets are version-controlled and reproducible

---

## Color Palette

### Primary Colors

| Color Name      | Hex Code | Usage                                    | RGB          |
|-----------------|----------|------------------------------------------|--------------|
| **Hive Cyan**   | #7FF7FF  | Primary brand color, logos, lines, icons | 127,247,255  |
| **Deep Synth Black** | #020407 | Backgrounds, void, negative space       | 2,4,7        |

### Accent Colors

| Color Name           | Hex Code | Usage                                  | RGB       |
|----------------------|----------|----------------------------------------|-----------|
| **Pulse Amber**      | #EBAF38  | Highlights, selected items, warnings   | 235,175,56|
| **Mod Voltage Blue** | #2E7CEB  | Active states, hover, live connections | 46,124,235|
| **Signal Magenta**   | #FF1EA0  | Errors, critical alerts, danger zones  | 255,30,160|
| **Graphite Grey**    | #1A1D21  | UI panels, secondary backgrounds       | 26,29,33  |

### Color Usage Rules

- **Backgrounds**: Always Deep Synth Black (#020407)
- **Foreground**: Always Hive Cyan (#7FF7FF) or white
- **Never**: Full saturation colors, rainbow gradients, organic textures
- **Glow effects**: Permitted only on Hive Cyan elements
- **Contrast ratio**: Maintain WCAG AA minimum (4.5:1) for text

---

## Typography

### Recommended Fonts

**Primary (UI/Code)**: Monospace fonts
- **JetBrains Mono** (preferred)
- **Fira Code**
- **Input Mono**
- **Courier New** (fallback)

**Secondary (Display/Headings)**: Geometric sans-serif
- **Space Grotesk** (preferred)
- **Inter**
- **Roboto**
- **Arial** (fallback)

### Type Scale

| Element          | Size   | Weight | Letter Spacing |
|------------------|--------|--------|----------------|
| Hero Heading     | 3rem   | Bold   | -0.02em        |
| H1               | 2rem   | Bold   | -0.01em        |
| H2               | 1.5rem | Bold   | 0              |
| H3               | 1.25rem| Semibold| 0             |
| Body             | 1rem   | Regular| 0              |
| Small/Caption    | 0.875rem| Regular| 0.01em        |
| Code             | 0.9em  | Regular| 0              |

---

## Logo System

### Primary Logo: "The Hex Coil"

**File**: `docs/assets/logo-primary.svg`

**Description**: Hexagon with luminous cyan core and three spiral CV pathways. Embedded honeycomb microgrid.

**Usage**:
- App headers
- Loading screens
- Official documents
- Social media profile pictures

**Minimum size**: 40px × 40px
**Clear space**: 20% of logo width on all sides
**Do not**: Rotate, skew, add drop shadows, or change colors

### Secondary Mark: "The Patch Sigil"

**File**: `docs/assets/sigil.svg`

**Description**: Vertical techno-rune representing oscillator → filter → amplifier signal chain.

**Usage**:
- Splash screens
- App icons (tall format)
- Loading indicators
- Print materials (vertical orientation)

**Minimum size**: 30px width
**Orientation**: Always vertical

### Favicon

**File**: `frontend/public/favicon.svg`

**Specifications**:
- 64×64px square
- Rounded corners (8px radius)
- Minimal hex + oscillator core
- Optimized for small sizes

---

## Visual Elements

### The Honeycomb

**Pattern**: Hexagonal grid tessellation
**Stroke**: 0.5–2px, Hive Cyan
**Opacity**: 0.1–0.3 for backgrounds, 0.6–1.0 for foregrounds
**Usage**: Backgrounds, textures, dividers

### CV Pathways

**Shape**: Curved Bézier paths, no sharp angles
**Stroke**: 1.5–3px, Hive Cyan
**Style**: Smooth, flowing, deterministic arcs
**Connections**: Always output → input (left-to-right or top-to-bottom)

### Waveforms

**Types**: Sine, sawtooth, square, triangle
**Stroke**: 1–2px, Hive Cyan at 0.4–0.8 opacity
**Usage**: Module decorations, patch diagrams, headers

### Signal Dots

**Size**: 2–4px radius
**Fill**: Hive Cyan
**Opacity**: 0.6–1.0
**Usage**: Connection points, data flow indicators, UI markers

### Glow Effect

**Type**: Gaussian blur
**Blur radius**: 2–5px
**Opacity**: 0.3–0.8
**Apply to**: Primary logo, sigil, active connections, oscillator cores
**Do not apply to**: Text, UI elements, icons

---

## UI Components

### Buttons

**Primary Button**:
- Background: Hive Cyan (#7FF7FF)
- Text: Deep Synth Black (#020407)
- Hover: Mod Voltage Blue (#2E7CEB)
- Border radius: 4px

**Secondary Button**:
- Background: Transparent
- Text: Hive Cyan (#7FF7FF)
- Border: 1px solid Hive Cyan
- Hover: Background Graphite Grey (#1A1D21)

### Input Fields

- Background: Graphite Grey (#1A1D21)
- Border: 1px solid Hive Cyan (opacity 0.3)
- Focus: Border opacity 1.0, glow effect
- Text: White
- Placeholder: Hive Cyan (opacity 0.5)

### Cards/Panels

- Background: Graphite Grey (#1A1D21) or transparent
- Border: 1px solid Hive Cyan (opacity 0.2–0.4)
- Border radius: 4–8px
- Padding: 16–24px

### Modals/Overlays

- Background: Deep Synth Black (#020407) at 0.95 opacity
- Border: 2px solid Hive Cyan
- Shadow: 0 20px 60px rgba(127,247,255,0.2)

---

## Icon Style

### Characteristics

- **Line weight**: 1.5–2.5px
- **Style**: Geometric, angular, no curves except CV paths
- **Color**: Hive Cyan (#7FF7FF)
- **Size**: 16px, 24px, 32px, 48px (multiples of 8)

### Module Type Icons

| Module Type | Visual Symbol                        |
|-------------|--------------------------------------|
| VCO         | Circle with sine wave inside         |
| VCF         | Chevron cascade (frequency cutoff)   |
| VCA         | Triangle (amplification)             |
| ENV         | ADSR curve shape                     |
| LFO         | Slow sine wave with loop indicator   |
| SEQ         | Step grid with dots                  |
| MIX         | Multiple lines converging            |
| FX          | Spiral or echo trails                |

---

## Export Assets

### Directory Structure

```
docs/assets/
├── logo-primary.svg          # Main hexagon logo
├── sigil.svg                 # Vertical patch sigil
├── header-banner.svg         # README/website header
├── social-preview.svg        # Open Graph image
└── favicon.svg               # Browser icon

frontend/public/
└── favicon.svg               # App favicon
```

### File Formats

**SVG** (primary):
- All logos and icons
- Scalable to any size
- Editable in Illustrator, Figma, or text editor

**PNG** (if rasterization needed):
- Export at 2x or 4x resolution
- Use transparent backgrounds
- 72 DPI for web, 300 DPI for print

---

## Usage Examples

### ✅ Correct Usage

- Logo on dark backgrounds only
- Maintain clear space around logos
- Use approved color palette
- Apply glow effects sparingly and only to designated elements
- Maintain geometric precision

### ❌ Incorrect Usage

- Do not place logo on light backgrounds without adjustment
- Do not rotate or skew logos
- Do not use unapproved colors
- Do not add gradients or textures to logos
- Do not outline text or add drop shadows
- Do not use organic shapes or hand-drawn elements

---

## Social Media Specifications

### Profile Images

- **Format**: Square (1:1)
- **Recommended size**: 400×400px
- **Asset**: `logo-primary.svg` (export as PNG)

### Cover Images

- **Twitter/X**: 1500×500px
- **LinkedIn**: 1584×396px
- **Facebook**: 820×312px
- **YouTube**: 2560×1440px
- **Asset**: `header-banner.svg` (adapt dimensions)

### Post Images

- **Square**: 1080×1080px (Instagram, LinkedIn)
- **Landscape**: 1200×630px (Open Graph, Twitter)
- **Story**: 1080×1920px (Instagram, Facebook)

---

## Animation Guidelines

### Permitted Animations

- **Pulsing glow**: Oscillator cores, active connections
- **Signal flow**: Dots moving along CV pathways
- **Waveform scanning**: Left-to-right waveform reveal
- **Hex expansion**: Hexagons scaling from center
- **Fade in/out**: Opacity transitions (0.3–1.0)

### Animation Timing

- **Duration**: 0.2s (fast), 0.5s (medium), 1.0s (slow)
- **Easing**: `cubic-bezier(0.4, 0, 0.2, 1)` or `ease-in-out`
- **FPS**: 60fps for smooth motion
- **Loop**: Infinite for loading, once for transitions

### Forbidden Animations

- No bouncing or elastic easing
- No spinning logos (except loading spinner)
- No particle explosions or organic motion
- No color cycling (use opacity instead)

---

## Print Guidelines

### Business Cards

- **Size**: 3.5" × 2" (89mm × 51mm)
- **Background**: Deep Synth Black
- **Logo**: Hex Coil or Sigil in Hive Cyan
- **Text**: White or Hive Cyan, monospace font
- **Finish**: Matte black with spot UV on logo

### Posters/Flyers

- **Color mode**: RGB (for digital), CMYK (for print)
- **Resolution**: Minimum 300 DPI
- **Bleed**: 0.125" (3mm)
- **Safe zone**: 0.25" (6mm) from trim

---

## Accessibility

### Contrast

- Hive Cyan (#7FF7FF) on Deep Synth Black (#020407): **14.7:1** (AAA)
- White (#FFFFFF) on Deep Synth Black (#020407): **19.6:1** (AAA)
- Pulse Amber (#EBAF38) on Deep Synth Black (#020407): **10.2:1** (AAA)

### Text Sizes

- Minimum body text: 16px (1rem)
- Minimum UI labels: 14px (0.875rem)
- Line height: 1.5–1.8 for readability

### Focus States

- All interactive elements must have visible focus indicators
- Focus ring: 2px solid Mod Voltage Blue (#2E7CEB)
- Focus glow: Optional, 0 0 8px rgba(46,124,235,0.6)

---

## Version History

| Version | Date       | Changes                           |
|---------|------------|-----------------------------------|
| 1.0     | 2025-01-XX | Initial brand guidelines release  |

---

## Questions?

For brand usage inquiries or permission requests, see the main [README.md](../README.md) or open an issue on GitHub.

**Built with ABX-Core v1.2 | Deterministic | Modular | SEED-Enforced**
