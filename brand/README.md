# PatchHive brand kit (Cyber Hive v0.1)

Authoritative design write-up: [`docs/brand/VISUAL_IDENTITY.md`](../docs/brand/VISUAL_IDENTITY.md)

## Layout

```text
brand/
  logo/           cyber-bee mark + flat icon
  mascot/         Hive Drone
  splash/         splash + loading frame
  patterns/       seamless PCB honeycomb
  marketing/      GitHub banner, empty state, dashboard concept
  icons/svg/      48 monochrome outline icons + sprite.svg
```

## Quick use

**Icons (React-ish):**

```html
<svg width="24" height="24" stroke="currentColor" fill="none">
  <use href="/brand/icons/svg/sprite.svg#ph-icon-patch"/>
</svg>
```

Or inline any `brand/icons/svg/<name>.svg`.

**Local preview:** open JPGs under `brand/` or serve the repo root.

## Product note

Visual language may evoke signal, synth, and swarm intelligence. Product scope remains deterministic **rig + patch documentation** — not audio DSP.
