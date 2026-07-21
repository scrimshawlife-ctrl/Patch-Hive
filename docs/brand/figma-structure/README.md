# Figma-compatible structure

Import assets from `brand/` into Figma using this page map.

```text
📁 Zero State — Brand
  📄 00 Cover
  📄 01 Foundations (color, type, space, radius, elevation, motion)
  📄 02 Zero State Logo (monogram, wordmark, clearspace, don'ts)
  📄 03 PatchHive Logo (mark, lockups, app icon, favicon)
  📄 04 Hierarchy (Zero State → PatchHive)
  📄 05 Icons (24 grid, categories)
  📄 06 Components (buttons, cards, forms, nav, badges, menus)
  📄 07 Patterns (PCB honeycomb, application)
  📄 08 Illustrations (empty, loading, dashboard concept)
  📄 09 Marketing (GitHub banner, splash, social)
  📄 10 Mascot (Hive Drone)
  📄 11 Do / Don't
  📄 12 Export Specs (iOS, web, GitHub)
```

## Import sources

| Figma page | Source path |
|------------|-------------|
| Zero State logo | `brand/zero-state/*` |
| PatchHive logo | `brand/patchhive/**` |
| Icons | `brand/icons/svg/*.svg` |
| Marketing | `brand/marketing/*`, `brand/splash/*` |
| Tokens | `docs/brand/design-tokens.cyber-hive.json` |

## Export checklist

- [ ] App icon 1024 PNG from `app-icon-ios.jpg`  
- [ ] Favicon from `frontend/public/favicon.svg`  
- [ ] GitHub social 1280×640 from `github-banner.jpg`  
- [ ] SVG icons as components (24 base)  
