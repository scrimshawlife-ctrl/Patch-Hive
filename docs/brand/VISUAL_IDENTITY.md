# PatchHive visual identity

**Version:** 1.0 · Zero State × Cyber Hive  
**Date:** 2026-07-21  
**Assets root:** [`brand/`](../../brand/)  
**Full guidelines:** [BRAND_GUIDELINES.md](BRAND_GUIDELINES.md)  
**Product law:** visual metaphor may use signal / synth / swarm language; product remains **rig inventory → deterministic patches → export** (not audio DSP / hardware control).

## Parent company

**Zero State** owns the monochrome system language. **PatchHive** is a Zero State product — always the hero, with understated parent credit.

---

## Brand narrative

PatchHive is an **operating system for modular patch engineering** — precision software where human confirmation and machine assistance meet. The hive is **distributed intelligence**, not nature nostalgia. Geometry, PCB traces, and amber status LEDs communicate **signal architecture** and **collaborative rigor**.

**Keywords:** Cyber Hive · Modular Systems · Signal Architecture · Engineering Elegance · Human + AI Collaboration · Living Software (UI motion) · Swarm Computing (metaphor)

---

## Color system

| Role | Name | Hex | Usage |
|------|------|-----|--------|
| Base | Carbon Black | `#08090B` | Deep void, app chrome |
| Base | Deep Graphite | `#111318` | Primary surfaces |
| Base | Panel | `#1A1D24` | Cards, drawers |
| Base | Border | `#2A2F3A` | Hairlines |
| Metal | Titanium | `#8B919C` | Secondary text, icons |
| Metal | Gunmetal | `#4A5160` | Disabled, tracks |
| Signal | Electric Amber | `#F5A623` | Primary brand energy, focus |
| Signal | Honey Gold | `#D4891A` | Hover / pressed amber |
| Signal | Warm Copper | `#B87333` | PCB traces, secondary glow |
| Accent | Cyan Signal | `#3DDCFF` | Links, active routing |
| Accent | Azure LED | `#5B8CFF` | Info, secondary nodes |
| Status | Emerald | `#00C896` | Success / ready |
| Status | White UI | `#E8ECF0` | Primary text |
| Status | Diagnostics Purple | `#7B61FF` | Rare diagnostics |
| Danger | Deep Red | `#E23D4A` | Errors |
| Warn | Diagnostics Orange | `#FF8A3D` | Warnings |

**Rules:** never rainbow; amber + cyan pair at most; emerald only for success; purple sparingly.

### Relationship to current app tokens

Existing app tokens (`docs/design-tokens.json`) use cyan `#7FF7FF` and green `#00FF88`.  
**Cyber Hive v0.1** introduces amber as brand energy. Migration path:

1. Ship brand assets + this doc (this PR)  
2. Optionally dual-token in CSS (`--ph-amber` alongside `--accent`)  
3. Gradual UI chrome adoption without breaking green “ready” semantics overnight  

---

## Typography

| Role | Recommendation | Fallback |
|------|-----------------|----------|
| UI / body | Inter or Geist | system-ui, SF Pro |
| Display / marketing | Space Grotesk | Inter |
| Mono / console | JetBrains Mono / Geist Mono | ui-monospace |

Engineering-first, high x-height, geometric sans. Avoid decorative display fonts.

---

## Logo

| Asset | Path | Use |
|-------|------|-----|
| Cyber bee mark (PBR) | `brand/logo/cyber-bee-mark.jpg` | Hero, splash, marketing |
| Flat monochrome icon | `brand/logo/cyber-bee-icon-flat.jpg` | Favicon exploration, dark tiles |

**Concept:** hard-surface cyber bee — PCB wings, hexagonal thorax aperture, amber AI core, waveform etched into wings. **Not** a cute insect mascot.

**Clear space:** ≥ 0.25× mark height on all sides.  
**Min size:** 24px digital mark; prefer flat variant under 32px.

---

## Mascot — Hive Drone

| Asset | Path |
|-------|------|
| Hero still | `brand/mascot/hive-drone.jpg` |

Floating repair / scout drone: hexagonal shell, amber optics, modular arms, PCB wings, stabilization rings. Personality via subtle optic pulse — no face expressions.

---

## Icon system

**Location:** `brand/icons/svg/` · **48 monochrome outline icons** + `sprite.svg`

| Style | Spec |
|-------|------|
| Grid | 24×24 viewBox |
| Stroke | 1.5 · round caps/joins |
| Color | `currentColor` |
| Sizes | Use at 16 / 20 / 24 / 32 / 64 via CSS |

Names include: dashboard, projects, hive, workers, queen, nodes, audio, synth, mixer, patch, cable, signal, ai, search, import, export, analyze, repair, version, history, cloud, git, build, settings, plugin, documentation, package, performance, latency, cpu, gpu, warnings, errors, success, notifications, bookmarks, favorites, profile, marketplace, community, terminal, automation, database, routing, live-session, snapshots, deploy, monitoring.

---

## Motion language

| Motion | Use |
|--------|-----|
| Amber micro-pulse | Status ready / hive core |
| Cyan trace propagation | Routing, patch edges |
| Honeycomb assemble | Loading, sync |
| Soft particle drift | Background, never full-screen noise |

Never flashy neon strobes. Loopable, purposeful.

---

## UI chrome

| Element | Spec |
|---------|------|
| Cards | Smoked glass · radius 16–18px · 1px border `#2A2F3A` · optional amber edge on focus |
| Primary button | Graphite fill · amber edge glow · hover circuit pulse |
| Secondary | Transparent / smoked · thin border |
| Success | Emerald text/icon |
| Danger | Deep red |
| Separators | Hex ticks or 1px gunmetal |

---

## Asset inventory (generated)

| Category | Files |
|----------|--------|
| Logo | `cyber-bee-mark.jpg`, `cyber-bee-icon-flat.jpg` |
| Mascot | `hive-drone.jpg` |
| Splash / load | `splash/splash-hero.jpg`, `splash/loading-frame.jpg` |
| Patterns | `patterns/pcb-honeycomb.jpg` |
| Marketing | `github-banner.jpg`, `empty-state.jpg`, `dashboard-concept.jpg` |
| Icons | 48 SVG + sprite |

**Not fully generated in this pass (follow-on):** full marketing pack (T-shirts, booth, stickers), every UI illustration state, animated Lottie/video loops, lockup wordmark SVG (prefer code for exact “PatchHive” type).

---

## Product alignment note

Marketing copy in the art brief may say “audio patch intelligence.”  
**Engineering product** documents patches and signal *metadata*; it does **not** simulate audio DSP. Prefer:

- “Modular patch intelligence”  
- “Signal architecture for Eurorack documentation”  
- “Confirmed inventory → deterministic generation”  

over claims of live audio processing.

---

## Next steps

1. Approve mark + palette  
2. Export SVG wordmark in Figma/Illustrator from mark  
3. Wire CSS variables from table above into `frontend/src/index.css`  
4. Replace `frontend/public/favicon.svg` with simplified path from flat mark  
5. Domain launch assets once DNS is ready (reuse `github-banner.jpg` + splash)  
