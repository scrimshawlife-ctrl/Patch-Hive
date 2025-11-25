# PatchHive Component Library

**React Components and Visual Assets**

This document describes the available UI components and how to use them.

---

## React Components

### AnimatedLogo

**Location**: `frontend/src/components/AnimatedLogo.tsx`

Animated version of the PatchHive logo with pulsing oscillator core and rotating CV pathways.

#### Usage

```tsx
import { AnimatedLogo } from '@/components/AnimatedLogo';

// Default (200px, animated)
<AnimatedLogo />

// Custom size
<AnimatedLogo size={150} />

// Static (no animation)
<AnimatedLogo animate={false} />
```

#### Props

| Prop     | Type    | Default | Description                    |
|----------|---------|---------|--------------------------------|
| size     | number  | 200     | Width and height in pixels     |
| animate  | boolean | true    | Enable/disable animations      |

#### Animations

- **Core pulse**: Breathing effect on oscillator core (2s cycle)
- **Pathway rotation**: CV pathways rotate slowly (15s cycle)
- **Hex rotation**: Inner hex frame rotates (20s cycle)
- **Signal flow**: Dots pulse along signal paths (4s cycle)

**Accessibility**: Respects `prefers-reduced-motion` - animations disabled automatically for users who prefer reduced motion.

---

### LoadingSpinner

**Location**: `frontend/src/components/LoadingSpinner.tsx`

Rotating hexagon spinner with orbiting signal dots.

#### Usage

```tsx
import { LoadingSpinner } from '@/components/LoadingSpinner';

// Default (80px)
<LoadingSpinner />

// With loading message
<LoadingSpinner message="Generating patches..." />

// Custom size
<LoadingSpinner size={120} message="Loading modules..." />
```

#### Props

| Prop    | Type   | Default | Description                    |
|---------|--------|---------|--------------------------------|
| size    | number | 80      | Width and height in pixels     |
| message | string | -       | Optional loading message       |

#### Animations

- **Hex rotation**: Outer hex rotates clockwise (2s cycle)
- **Inner hex rotation**: Inner hex rotates counter-clockwise (3s cycle)
- **Core pulse**: Central oscillator pulsing (1.5s cycle)
- **Dot orbit**: 6 dots orbit around center with fade (3s cycle)

**Use cases**:
- Initial app loading
- API request pending
- Patch generation in progress
- Module import processing

---

## SVG Assets

### Logo System

#### Primary Logo: The Hex Coil

**File**: `docs/assets/logo-primary.svg`

```html
<!-- HTML -->
<img src="docs/assets/logo-primary.svg" alt="PatchHive" width="200">
```

```tsx
// React
import logo from '@/assets/logo-primary.svg';
<img src={logo} alt="PatchHive" />
```

**Specifications**:
- Size: 400×400px
- Format: SVG (scalable)
- Background: Deep Synth Black (#020407)
- Primary color: Hive Cyan (#7FF7FF)

**Features**:
- Hexagon frame with glow effect
- Honeycomb pattern interior
- Three CV pathway spirals
- Central luminous oscillator core
- Voltage markers at vertices

---

#### Secondary Mark: The Patch Sigil

**File**: `docs/assets/sigil.svg`

```html
<img src="docs/assets/sigil.svg" alt="PatchHive Sigil" height="300">
```

**Specifications**:
- Size: 200×600px (vertical)
- Represents: Oscillator → Filter → Amplifier signal chain

**Use cases**:
- Splash screens
- Loading screens
- Vertical banners
- App icons (tall format)

---

### Icon Set

#### Module Type Icons

**File**: `docs/assets/icons/module-types.svg`

Contains 10 module type icons:

1. **VCO** (Voltage Controlled Oscillator) - Circle with sine wave
2. **VCF** (Voltage Controlled Filter) - Chevron cascade
3. **VCA** (Voltage Controlled Amplifier) - Expanding triangle
4. **ENV** (Envelope) - ADSR curve
5. **LFO** (Low Frequency Oscillator) - Slow sine with loop
6. **SEQ** (Sequencer) - Step grid
7. **MIX** (Mixer) - Converging lines
8. **FX** (Effects) - Spiral trails
9. **UTIL** (Utility) - Junction node
10. **NOISE** (Noise Generator) - Random static pattern

#### Extracting Individual Icons

To extract a single icon for use:

```tsx
// React component for VCO icon
export const VCOIcon = ({ size = 48 }) => (
  <svg width={size} height={size} viewBox="0 0 96 96" xmlns="http://www.w3.org/2000/svg">
    <circle cx="48" cy="48" r="40" fill="none" stroke="#7FF7FF" strokeWidth="2.5" />
    <path d="M 18,48 Q 33,28 48,48 T 78,48" fill="none" stroke="#7FF7FF" strokeWidth="2" />
    <circle cx="48" cy="48" r="6" fill="#7FF7FF" opacity="0.8" />
  </svg>
);
```

---

### Marketing Assets

#### Header Banner

**File**: `docs/assets/header-banner.svg`

```html
<img src="docs/assets/header-banner.svg" alt="PatchHive" width="100%">
```

**Specifications**:
- Size: 1200×300px
- Use: README headers, website hero sections

---

#### Social Preview

**File**: `docs/assets/social-preview.svg`

**Specifications**:
- Size: 1200×630px
- Use: Open Graph, Twitter cards, Discord embeds

**GitHub Setup**:
```yaml
# .github/social-preview.yml
image: docs/assets/social-preview.svg
```

---

#### Favicon

**File**: `frontend/public/favicon.svg`

```html
<!-- HTML -->
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
```

**Vite Configuration** (already set up):
```ts
// vite.config.ts
export default defineConfig({
  // Favicon is automatically served from public/
})
```

---

## CSS Utilities

### Color Variables

Add to your global CSS:

```css
:root {
  --hive-cyan: #7FF7FF;
  --deep-synth-black: #020407;
  --pulse-amber: #EBAF38;
  --mod-voltage-blue: #2E7CEB;
  --signal-magenta: #FF1EA0;
  --graphite-grey: #1A1D21;
}
```

### Component Classes

```css
/* Hex border style */
.hex-border {
  border: 2px solid var(--hive-cyan);
  clip-path: polygon(30% 0%, 70% 0%, 100% 50%, 70% 100%, 30% 100%, 0% 50%);
}

/* Glow effect */
.glow-cyan {
  box-shadow: 0 0 10px rgba(127, 247, 255, 0.5);
  filter: drop-shadow(0 0 8px rgba(127, 247, 255, 0.3));
}

/* Signal pulse animation */
@keyframes signal-pulse {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

.signal-active {
  animation: signal-pulse 2s ease-in-out infinite;
}
```

---

## Usage Examples

### Loading State

```tsx
import { LoadingSpinner } from '@/components/LoadingSpinner';

function ModulePage() {
  const [loading, setLoading] = useState(true);

  if (loading) {
    return (
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <LoadingSpinner message="Loading modules..." />
      </div>
    );
  }

  return <ModuleList />;
}
```

### Splash Screen

```tsx
import { AnimatedLogo } from '@/components/AnimatedLogo';

function SplashScreen() {
  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      width: '100vw',
      height: '100vh',
      backgroundColor: '#020407',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 9999
    }}>
      <AnimatedLogo size={300} />
    </div>
  );
}
```

### Module Type Badge

```tsx
function ModuleTypeBadge({ type }: { type: string }) {
  const iconMap: Record<string, string> = {
    VCO: '○', // Use actual icon component
    VCF: '⌄',
    VCA: '△',
    // ... etc
  };

  return (
    <span style={{
      display: 'inline-flex',
      alignItems: 'center',
      gap: '0.5rem',
      padding: '0.25rem 0.75rem',
      border: '1px solid #7FF7FF',
      borderRadius: '4px',
      color: '#7FF7FF',
      fontFamily: 'monospace',
      fontSize: '0.875rem'
    }}>
      <span>{iconMap[type] || '◆'}</span>
      <span>{type}</span>
    </span>
  );
}
```

---

## Animation Guidelines

### Performance

- All animations use CSS transforms and opacity (GPU-accelerated)
- No layout-triggering properties (width, height, top, left)
- Animations respect `prefers-reduced-motion`

### Timing

- **Fast**: 0.2s (hover states, clicks)
- **Medium**: 0.5s (transitions, fades)
- **Slow**: 1-3s (pulsing, breathing)
- **Infinite**: Loops for loading states

### Easing

```css
/* Standard transitions */
transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

/* Smooth pulse */
animation: pulse 2s ease-in-out infinite;

/* Linear rotation */
animation: rotate 3s linear infinite;
```

---

## Accessibility

### Keyboard Navigation

All interactive components support:
- Tab navigation
- Enter/Space activation
- Escape to close modals

### Screen Readers

```tsx
// Add ARIA labels
<AnimatedLogo aria-label="PatchHive logo" role="img" />
<LoadingSpinner aria-live="polite" aria-busy="true" />
```

### Reduced Motion

```tsx
// Check user preference
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

<AnimatedLogo animate={!prefersReducedMotion} />
```

---

## Testing Components

### Visual Testing

```tsx
// Storybook story example
export default {
  title: 'Components/AnimatedLogo',
  component: AnimatedLogo,
};

export const Default = () => <AnimatedLogo />;
export const Large = () => <AnimatedLogo size={300} />;
export const Static = () => <AnimatedLogo animate={false} />;
```

### Unit Testing

```tsx
import { render, screen } from '@testing-library/react';
import { LoadingSpinner } from './LoadingSpinner';

test('renders loading message', () => {
  render(<LoadingSpinner message="Loading..." />);
  expect(screen.getByText('Loading...')).toBeInTheDocument();
});
```

---

## Future Components

Planned for Phase 2:

- [ ] **ModuleCard** - Display module with specs and ports
- [ ] **RackVisualizer** - Interactive rack layout
- [ ] **PatchDiagram** - SVG patch connection viewer
- [ ] **WaveformDisplay** - Animated waveform component
- [ ] **ConnectionCable** - Animated patch cable
- [ ] **SignalMeter** - VU meter style indicator
- [ ] **HPCounter** - Remaining HP display
- [ ] **PowerMeter** - Power draw visualization

---

For more information, see:
- [Brand Guidelines](BRAND_GUIDELINES.md)
- [Architecture Documentation](ARCHITECTURE.md)
- [Main README](../README.md)
