# Zero State · PatchHive Brand Guidelines

**Version:** 1.0  
**Audience:** Product, eng, marketing, design  
**Asset root:** [`brand/`](../../brand/)  
**Related:** [VISUAL_IDENTITY.md](VISUAL_IDENTITY.md) · [design-tokens.cyber-hive.json](design-tokens.cyber-hive.json)

---

## 1. Hierarchy

```text
ZERO STATE          ← parent company (quiet, monochrome)
    └── PATCHHIVE   ← product (hero, amber/cyan accents)
```

| Context | Treatment |
|---------|-----------|
| Splash / About | PatchHive large · “A Zero State Product” or “from Zero State” small |
| README header | `PatchHive` · subline `A Zero State Product` |
| Website footer | `Built by Zero State` |
| App footer | `Designed and engineered by Zero State` |
| Marketing lockups | Use `brand/patchhive/lockups/*-from-zero-state.svg` |

PatchHive is the hero. Zero State is understated.

---

## 2. Voice & tone

| Do | Don’t |
|----|--------|
| Precise, calm, systems-aware | Hype, gamer, crypto, “hacker” |
| “Confirmed inventory”, “deterministic” | Invented accuracy claims |
| “Signal architecture” as metaphor | Claim live audio DSP product scope |
| Quiet confidence | Neon cyberpunk overload |

**Product law (engineering):** documentation and patch generation constrained to confirmed inventory — not audio simulation or hardware control.

---

## 3. Color

### Zero State (parent)

| Token | Hex | Use |
|-------|-----|-----|
| Carbon | `#08090B` | Void |
| Graphite | `#111318` | Surfaces |
| Titanium | `#8B919C` | Text secondary / marks |
| White | `#E8ECF0` | Primary text on dark |
| Border | `#2A2F3A` | Hairlines |

Monochrome by default. Accent only when required.

### PatchHive (product)

| Token | Hex | Use |
|-------|-----|-----|
| Amber | `#F5A623` | Brand energy, CTAs, focus |
| Honey | `#D4891A` | Hover amber |
| Copper | `#B87333` | PCB traces |
| Cyan | `#3DDCFF` | Active routes, links |
| Emerald | `#00C896` | Success / ready |
| Violet | `#7B61FF` | Rare diagnostics |
| Danger | `#E23D4A` | Errors |
| Warn | `#FF8A3D` | Warnings |

**Never rainbow.** Amber + cyan pairing is enough.

---

## 4. Typography

| Role | Stack |
|------|--------|
| UI | `Inter, Geist, system-ui, sans-serif` |
| Display | `Space Grotesk, Inter, system-ui` |
| Mono | `JetBrains Mono, ui-monospace` |

Weights: 500–700 for UI; avoid ultra-black display spam. Letter-spacing slightly negative on large titles.

---

## 5. Spacing & radius

| Token | Value |
|-------|--------|
| Space scale | 4 / 8 / 12 / 16 / 24 / 32 / 48 px |
| Control radius | 10px |
| Card radius | 16–18px |
| Focus ring | 3px amber mix |

---

## 6. Elevation

| Level | Shadow |
|-------|--------|
| Flat | none |
| Raised | `0 8px 24px rgb(0 0 0 / 20%)` |
| Overlay | `0 16px 48px rgb(0 0 0 / 32%)` |

Prefer border + subtle blur over heavy skeuomorphism.

---

## 7. Motion

| Token | Value | Use |
|-------|--------|-----|
| Fast | 140ms | Hover, press |
| Med | 220ms | Panel open |
| Pulse | 1.8s ease | Status LEDs |

Micro only: circuit pulse, honeycomb assemble, signal propagation.  
Respect `prefers-reduced-motion`.

---

## 8. Logo rules

### Zero State
- Assets: `brand/zero-state/monogram.svg`, `wordmark.svg`, `monogram-zs.jpg`
- Monochrome only in product chrome
- Minimum digital size: 20px monogram

### PatchHive
- Mark: `brand/patchhive/logo/cyber-bee-mark.jpg` (hero) / flat icon for small sizes
- Wordmark: `brand/patchhive/lockups/wordmark.svg`
- Hierarchy lockups: `horizontal-from-zero-state.svg`, `vertical-from-zero-state.svg`
- Clear space ≥ 0.25× mark height
- Do not recolor the amber core to neon green rainbow
- Do not place mark on busy photography without scrim

### Don’t
- Stretch or rotate logos arbitrarily  
- Add drop shadows to flat icons  
- Use cute bee illustrations  
- Drop “Zero State” from public marketing splash without a reason  

---

## 9. Icons

- **340** outline icons · `brand/icons/svg/` · `sprite.svg`
- 24×24 viewBox · stroke 1.5 · `currentColor`
- Scale via CSS to 16 / 20 / 24 / 32 / 48 / 64
- Optical alignment on honeycomb when composing icon grids

---

## 10. Components (CSS)

App primitives live in `frontend/src/index.css` with Zero State / PatchHive tokens:

- `.button-primary` / secondary / quiet  
- `.panel` cards  
- `.field` forms  
- `.tab` / `.status-*`  
- `.wordmark` / footer Zero State credit  

Showcase: `brand/design-system/index.html`

---

## 11. Accessibility

| Rule | Spec |
|------|------|
| Contrast | WCAG AA minimum for text |
| Focus | Visible ring on all controls |
| Touch | 44×44px min targets |
| Motion | Reduced-motion safe |
| Color | Status never color-only (icon + text) |

---

## 12. Photography & illustration

- Studio lighting, PBR metals, graphite voids  
- Cyber bee / Hive Drone consistent with existing assets  
- Empty states: sparse geometry, not crowded narratives  
- Avoid stock “AI brain” clichés  

---

## 13. Do / Don’t

| Do | Don’t |
|----|--------|
| Quiet graphite UI + amber CTA | Neon city cyberpunk |
| PatchHive hero, Zero State whisper | Equal-weight dual logos everywhere |
| Monochrome icons | Multicolor icon soup |
| Fail-closed product language | Fake accuracy / DSP claims |

---

## 14. Figma / export map

See [figma-structure/README.md](figma-structure/README.md) for page/frame naming to import SVG/PNG into Figma.
