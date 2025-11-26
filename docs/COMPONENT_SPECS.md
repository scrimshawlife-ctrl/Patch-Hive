# PatchHive Component Specifications

## Implementation Guide for Figma UI Kit

This document provides detailed specifications for building each component in Figma with exact measurements, states, and variants.

---

## **⬡ BUTTON COMPONENT**

### **Structure**

```
Button [Auto Layout: Horizontal]
├── Icon (Optional)
│   └── 20×20px, left aligned
├── Label [Text]
│   └── JetBrains Mono, weight varies by size
└── Icon (Optional)
    └── 20×20px, right aligned

Padding: Horizontal, Vertical (varies by size)
Gap: 8px (between icon and label)
Corner Radius: 4px
```

### **Variants**

**Size × Variant × State Grid:**

| Size | Height | Padding H | Padding V | Font Size | Font Weight |
|------|--------|-----------|-----------|-----------|-------------|
| Small | 32px | 16px | 8px | 12px | 600 |
| Medium | 40px | 24px | 12px | 14px | 600 |
| Large | 48px | 32px | 16px | 16px | 700 |

**Variant Styles:**

1. **Primary**
   - Background: #7FF7FF
   - Text: #020407
   - Border: none
   - Hover: + shadow (glow-cyan)
   - Active: + shadow (glow-intense), translateY(0)
   - Disabled: opacity 50%, cursor not-allowed

2. **Secondary**
   - Background: transparent
   - Text: #7FF7FF
   - Border: 2px solid #7FF7FF
   - Hover: + shadow (glow-cyan)
   - Active: background rgba(127, 247, 255, 0.1)
   - Disabled: opacity 50%

3. **Danger**
   - Background: #FF1EA0
   - Text: #020407
   - Border: none
   - Hover: + shadow (glow-magenta)
   - Active: + shadow (glow-intense), translateY(0)
   - Disabled: opacity 50%

4. **Ghost**
   - Background: transparent
   - Text: #7FF7FF
   - Border: none
   - Hover: background rgba(127, 247, 255, 0.1)
   - Active: background rgba(127, 247, 255, 0.2)
   - Disabled: opacity 50%

**States:** Default, Hover, Active, Disabled, Loading

**Properties:**
- Size: Small | Medium | Large
- Variant: Primary | Secondary | Danger | Ghost
- State: Default | Hover | Active | Disabled | Loading
- Icon Left: Boolean
- Icon Right: Boolean

---

## **⬡ INPUT COMPONENT**

### **Structure**

```
Input Container [Auto Layout: Vertical]
├── Label [Text] (Optional)
│   ├── Font: 12px
│   └── Color: #7FF7FF
├── Input Field [Frame]
│   ├── Border: 2px
│   ├── Height: 40px
│   ├── Padding: 12px 16px
│   ├── Placeholder Text [Text]
│   │   ├── Font: 14px
│   │   └── Color: #8B92A0
│   └── Icon (Optional)
│       └── 20×20px, left or right
└── Helper Text / Error [Text] (Optional)
    ├── Font: 11px
    └── Color: #8B92A0 (helper) / #FF1EA0 (error)

Gap: 8px (between elements)
```

### **Variants**

**States:**

1. **Default**
   - Background: transparent
   - Border: 2px solid rgba(127, 247, 255, 0.3)
   - Text: #E8ECF0

2. **Focus**
   - Background: transparent
   - Border: 2px solid #7FF7FF
   - Shadow: glow-cyan
   - Cursor: text

3. **Error**
   - Background: transparent
   - Border: 2px solid #FF1EA0
   - Helper text: #FF1EA0

4. **Disabled**
   - Background: rgba(127, 247, 255, 0.05)
   - Border: 2px solid rgba(127, 247, 255, 0.2)
   - Text: #8B92A0
   - Opacity: 50%
   - Cursor: not-allowed

5. **Success**
   - Background: transparent
   - Border: 2px solid #00FF88
   - Icon: checkmark in #00FF88

**Properties:**
- State: Default | Focus | Error | Disabled | Success
- Icon: Boolean
- Icon Position: Left | Right
- Label: Boolean
- Helper Text: Boolean

---

## **⬡ CARD COMPONENT**

### **Base Card**

```
Card [Frame]
├── Background: #1C2128
├── Border: 1px solid rgba(127, 247, 255, 0.2)
├── Corner Radius: 4px
├── Padding: 24px
└── Content [Auto Layout: Vertical]
    ├── Header
    ├── Body
    └── Footer

Hover: Border → #7FF7FF, Shadow → md
```

### **Module Card**

```
Module Card [Auto Layout: Vertical]
├── Hex Icon [40×40px]
│   └── Module type icon from icon set
├── Module Name [Text]
│   ├── Font: 16px bold
│   └── Color: #7FF7FF
├── HP Badge [Frame]
│   ├── Text: "84HP"
│   ├── Background: rgba(127, 247, 255, 0.2)
│   └── Padding: 4px 8px
├── I/O Ports [Auto Layout: Vertical]
│   └── Port items with labels
└── Power Draw [Text]
    ├── Font: 11px
    └── Color: #8B92A0

Gap: 12px
Width: 280px
```

### **Patch Card**

```
Patch Card [Auto Layout: Vertical]
├── Waveform Thumbnail [Image]
│   └── Size: 280×140px
├── Metadata [Auto Layout: Horizontal]
│   ├── Category Badge
│   └── SEED Display
├── Patch Name [Text]
│   ├── Font: 18px bold
│   └── Color: #7FF7FF
├── Actions [Auto Layout: Horizontal]
│   ├── Upvote Button
│   ├── Vote Count
│   ├── Downvote Button
│   └── Comment Count
└── Author [Auto Layout: Horizontal]
    ├── Avatar [20×20px circle]
    └── Username [Text, 12px]

Gap: 12px
Width: 280px
```

**Properties:**
- Type: Base | Module | Patch | Rack
- Hover State: Boolean

---

## **⬡ NAVIGATION COMPONENTS**

### **Top Navigation**

```
Top Nav [Frame]
├── Width: 100% (1440px)
├── Height: 64px
├── Background: #0A0E14
├── Border Bottom: 1px solid rgba(127, 247, 255, 0.2)
└── Content [Auto Layout: Horizontal]
    ├── Logo [120px]
    ├── Nav Links [Auto Layout: Horizontal]
    │   ├── Link 1
    │   ├── Link 2
    │   └── Link 3
    ├── Spacer [Fill]
    └── User Menu [Auto Layout: Horizontal]
        ├── Search Icon
        ├── Notifications Icon
        └── Avatar

Padding: 0 24px
Gap: 32px (between nav sections)
```

**Nav Link:**
```
Nav Link [Auto Layout: Horizontal]
├── Icon (Optional) [20×20px]
├── Label [Text, 14px]
└── Badge (Optional) [notification count]

Default: color #8B92A0
Hover: color #7FF7FF, underline
Active: color #7FF7FF, border-bottom 2px
```

### **Sidebar Navigation**

```
Sidebar [Frame]
├── Width: 240px
├── Height: 100vh
├── Background: #0A0E14
├── Border Right: 1px solid rgba(127, 247, 255, 0.2)
└── Content [Auto Layout: Vertical]
    ├── Nav Group 1
    │   ├── Group Label
    │   └── Nav Items
    ├── Nav Group 2
    └── Nav Group 3

Padding: 24px 0
Gap: 8px
```

**Sidebar Nav Item:**
```
Nav Item [Auto Layout: Horizontal]
├── Icon [20×20px]
├── Label [Text, 14px]
└── Badge (Optional)

Height: 40px
Padding: 0 24px
Gap: 12px

Default: transparent
Hover: background rgba(127, 247, 255, 0.1)
Active: background rgba(127, 247, 255, 0.2), border-left 3px #7FF7FF
```

### **Breadcrumbs**

```
Breadcrumbs [Auto Layout: Horizontal]
├── Home Link
├── Separator [⬡ or /]
├── Parent Link
├── Separator
└── Current Page [no link]

Gap: 8px
Font: 12px
Color: #8B92A0 (links), #7FF7FF (current)
```

---

## **⬡ MODAL COMPONENT**

### **Structure**

```
Modal Overlay [Frame]
├── Width: 100vw
├── Height: 100vh
├── Background: rgba(2, 4, 7, 0.8)
├── Blur: 4px
└── Modal Container [Frame]
    ├── Width: 600px (max)
    ├── Background: #1C2128
    ├── Border: 2px solid #7FF7FF
    ├── Corner Radius: 8px
    ├── Padding: 32px
    └── Content [Auto Layout: Vertical]
        ├── Header [Auto Layout: Horizontal]
        │   ├── Title [Text, 24px bold]
        │   ├── Spacer [Fill]
        │   └── Close Button [Icon]
        ├── Body [Auto Layout: Vertical]
        │   └── Content
        └── Footer [Auto Layout: Horizontal]
            ├── Spacer [Fill]
            ├── Cancel Button (Secondary)
            └── Confirm Button (Primary)

Gap: 24px
```

**Properties:**
- Size: Small (400px) | Medium (600px) | Large (800px)
- Show Close: Boolean
- Show Footer: Boolean

---

## **⬡ BADGE & TAG**

### **Badge**

```
Badge [Auto Layout: Horizontal]
├── Label [Text]
│   ├── Font: 10px
│   ├── Weight: 700
│   ├── Letter Spacing: 0.1em
│   └── Text Transform: Uppercase
└── Background: rgba(127, 247, 255, 0.2)

Height: 20px
Padding: 0 8px
Corner Radius: 2px
Color: #7FF7FF
```

**Variants:**
- Color: Cyan | Magenta | Green | Gray
- Size: Small (16px) | Medium (20px) | Large (24px)

### **Tag (Interactive)**

```
Tag [Auto Layout: Horizontal]
├── Label [Text]
└── Close Icon [12×12px]

Height: 24px
Padding: 0 8px 0 12px
Gap: 6px
Corner Radius: 2px
Background: rgba(127, 247, 255, 0.2)

Hover: background rgba(127, 247, 255, 0.3)
Active: background rgba(127, 247, 255, 0.4)
```

---

## **⬡ LOADING STATES**

### **Spinner**

```
Spinner [Component Instance]
├── Rotating Hexagon [Vector]
│   └── Size: 60×60px (adjustable)
├── Signal Dots [3 circles]
│   └── Size: 4px each
└── Message (Optional) [Text]
    ├── Font: 12px
    └── Margin Top: 16px

Animation: Rotation 2s linear infinite
Colors: #7FF7FF (hex), #FF1EA0 (dots)
```

**Variants:**
- Size: Small (40px) | Medium (60px) | Large (80px)
- With Message: Boolean

### **Skeleton**

```
Skeleton [Frame]
├── Background: linear-gradient(
│     90deg,
│     #1C2128 0%,
│     #3D4450 50%,
│     #1C2128 100%
│   )
├── Corner Radius: matches content type
└── Animation: Shimmer 2s infinite

Types:
├── Text: 14px height, variable width, 2px radius
├── Avatar: Circle, 32-64px
├── Card: 200×300px, 4px radius
└── Custom: adjustable dimensions
```

### **Progress Bar**

```
Progress Bar [Frame]
├── Background Track [Frame]
│   ├── Height: 4px
│   ├── Background: #3D4450
│   └── Corner Radius: 2px
└── Fill [Frame]
    ├── Height: 4px
    ├── Width: percentage
    ├── Background: linear-gradient(90deg, #7FF7FF, #FF1EA0)
    └── Corner Radius: 2px

Animation: Indeterminate slide
```

---

## **⬡ ICON BUTTON**

### **Structure**

```
Icon Button [Frame]
├── Size: 32×32px (small) | 40×40px (medium) | 48×48px (large)
├── Background: transparent
├── Corner Radius: 4px
└── Icon [20×20px, centered]

Hover: background rgba(127, 247, 255, 0.1)
Active: background rgba(127, 247, 255, 0.2)
Focus: outline 2px solid #7FF7FF, offset 2px
```

**Variants:**
- Size: Small | Medium | Large
- Color: Cyan | Magenta | Gray
- State: Default | Hover | Active | Disabled

---

## **⬡ DROPDOWN MENU**

### **Structure**

```
Dropdown [Frame]
├── Width: 200px (adjustable)
├── Background: #1C2128
├── Border: 1px solid rgba(127, 247, 255, 0.3)
├── Corner Radius: 4px
├── Shadow: md
└── Menu Items [Auto Layout: Vertical]
    ├── Menu Item 1
    ├── Divider (Optional)
    ├── Menu Item 2
    └── ...

Padding: 8px 0
Gap: 0
```

**Menu Item:**
```
Menu Item [Auto Layout: Horizontal]
├── Icon (Optional) [20×20px]
├── Label [Text, 14px]
├── Spacer [Fill]
└── Shortcut (Optional) [Text, 11px, #8B92A0]

Height: 36px
Padding: 0 16px
Gap: 12px

Hover: background rgba(127, 247, 255, 0.1)
Active: background rgba(127, 247, 255, 0.2), color #7FF7FF
Disabled: opacity 50%, cursor not-allowed
```

**Divider:**
```
Height: 1px
Background: rgba(127, 247, 255, 0.2)
Margin: 4px 0
```

---

## **⬡ TOOLTIP**

### **Structure**

```
Tooltip [Frame]
├── Background: #0A0E14
├── Border: 1px solid #7FF7FF
├── Corner Radius: 4px
├── Padding: 8px 12px
├── Shadow: md
└── Content [Auto Layout: Vertical]
    ├── Text [12px, #7FF7FF]
    └── Arrow [Triangle, 8×8px]

Max Width: 200px
Position: Top | Bottom | Left | Right
```

**Arrow Positions:**
- Top: Arrow bottom center
- Bottom: Arrow top center
- Left: Arrow right center
- Right: Arrow left center

---

## **⬡ TABLE**

### **Structure**

```
Table [Frame]
├── Width: 100%
└── Content [Auto Layout: Vertical]
    ├── Header Row
    │   └── Background: #1C2128, Border Bottom: 2px solid #7FF7FF
    ├── Data Row 1
    ├── Data Row 2
    └── ...

Gap: 0
```

**Header Cell:**
```
Header Cell [Auto Layout: Horizontal]
├── Label [Text, 12px bold, uppercase]
└── Sort Icon (Optional) [16×16px]

Height: 48px
Padding: 12px 16px
Gap: 8px
Color: #7FF7FF
```

**Data Row:**
```
Data Row [Auto Layout: Horizontal]
├── Cell 1
├── Cell 2
└── ...

Height: 56px
Border Bottom: 1px solid rgba(127, 247, 255, 0.1)
Hover: background rgba(127, 247, 255, 0.05)
```

**Data Cell:**
```
Padding: 12px 16px
Font: 14px
Color: #E8ECF0
```

---

## **⬡ CHECKBOX & RADIO**

### **Checkbox**

```
Checkbox [Frame]
├── Size: 20×20px
├── Border: 2px solid #7FF7FF
├── Corner Radius: 2px
├── Background: transparent (unchecked) | #7FF7FF (checked)
└── Checkmark [Icon, 16×16px, #020407]

Hover: shadow glow-cyan
Focus: outline 2px solid #7FF7FF, offset 2px
Disabled: opacity 50%
```

### **Radio Button**

```
Radio [Frame]
├── Size: 20×20px
├── Border: 2px solid #7FF7FF
├── Corner Radius: full (circle)
├── Background: transparent (unchecked)
└── Dot [Circle, 10×10px, #7FF7FF] (checked)

Hover: shadow glow-cyan
Focus: outline 2px solid #7FF7FF, offset 2px
Disabled: opacity 50%
```

### **Toggle Switch**

```
Toggle [Frame]
├── Width: 44px
├── Height: 24px
├── Corner Radius: full
├── Background: #3D4450 (off) | #7FF7FF (on)
└── Thumb [Circle]
    ├── Size: 20×20px
    ├── Background: #E8ECF0
    └── Position: left 2px (off) | right 2px (on)

Animation: Smooth slide 150ms
Hover: shadow glow-cyan
Focus: outline 2px solid #7FF7FF, offset 2px
```

---

## **⬡ AVATAR**

### **Structure**

```
Avatar [Frame or Image]
├── Size: 32px | 40px | 48px | 64px
├── Shape: Circle (border-radius: full)
├── Border: 2px solid #7FF7FF (optional)
└── Fallback: Initials [Text, centered]

Online Indicator (Optional):
└── Dot [8×8px circle]
    ├── Position: bottom right
    ├── Background: #00FF88
    └── Border: 2px solid #1C2128
```

**Variants:**
- Size: XS (32px) | SM (40px) | MD (48px) | LG (64px) | XL (96px)
- Border: Boolean
- Status: None | Online | Away | Busy | Offline

---

## **⬡ FIGMA SETUP INSTRUCTIONS**

### **1. Create Color Styles**

Create color styles for all tokens in `design-tokens.json`:
- Primary/Cyan: #7FF7FF
- Primary/Black: #020407
- Primary/Magenta: #FF1EA0
- Etc...

### **2. Create Text Styles**

Create text styles for typography scale:
- Display: 48px/700/1.1/-0.05em
- H1: 32px/700/1.2/-0.05em
- Body: 14px/400/1.6/normal
- Etc...

### **3. Create Effect Styles**

Create effect styles for shadows and glows:
- Shadow/SM
- Shadow/MD
- Glow/Cyan
- Glow/Magenta
- Etc...

### **4. Build Components**

For each component:
1. Create base frame with Auto Layout
2. Add all necessary layers
3. Apply color, text, and effect styles
4. Create component variants for states
5. Add properties for configuration
6. Document usage in description

### **5. Organize Library**

```
PatchHive UI Kit
├── 🎨 Foundations
│   ├── Colors
│   ├── Typography
│   ├── Spacing
│   └── Effects
├── 🧩 Components
│   ├── Buttons
│   ├── Inputs
│   ├── Cards
│   ├── Navigation
│   ├── Modals
│   └── Icons
└── 📐 Templates
    ├── Page Layouts
    └── Patterns
```

---

**Version: 1.0 | Built for Figma | PatchHive Design System**
