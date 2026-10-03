# ASTRA Frontend — Phase P03 Notes
**Topic:** Design System & Shared Components  
**Phase:** P03 (Frontend MVP Phase Aa / Ab Shared Layer)  
**Date:** 2026-10-03  
**Author:** Worker 01 (Frontend)

---

## 1. External URL Audit & Classification

Re-running the external URL pattern scan on the build artifacts (`dist/`):
```powershell
Select-String -Path dist\assets\*.js,dist\*.html,dist\assets\*.css -Pattern "https?://" -AllMatches
```

### Classification Table

| Source Location | Matched String | Classification | Details / Evidence |
|---|---|---|---|
| `dist/index.html` (meta / SVG) | `http://www.w3.org/2000/svg` | (a) Inert XML Namespace | Standard SVG namespace declaration; zero network request initiated. |
| `dist/assets/index-*.js` | `https://reactrouter.com/...` | (a) Inert Diagnostic Warning | React Router v7 future-flag warning message embedded in router bundle. |
| `dist/assets/index-*.js` | `https://reactjs.org/docs/error-decoder.html?...` | (a) Inert Diagnostic Error URL | Production minified React error-decoder documentation link. |

**Verdict:** 0 runtime network requests. Air-gapped / sovereign compliance verified.

---

## 2. Design Tokens & Contrast Ratios

All tokens are defined in [src/index.css](file:///d:/SIH%202026%20Astra/astra-main/frontend/src/index.css) using values extracted directly from the dark theme prototype [frontend/legacy/index.static.html](file:///d:/SIH%202026%20Astra/astra-main/frontend/legacy/index.static.html).

### WCAG 2.1 AA / AAA Contrast Verification Results (`node frontend/scripts/check_contrast.mjs`)

| Foreground Token | Background Token | Ratio | Status (AA >= 4.5:1) | Description |
|---|---|---|---|---|
| `--text-main` (#f8fafc) | `--bg-base` (#090d16) | 18.57:1 | **PASS (AAA)** | Primary text on base |
| `--text-main` (#f8fafc) | `--bg-surface` (#0f172a) | 17.06:1 | **PASS (AAA)** | Primary text on surface |
| `--text-main` (#f8fafc) | `--bg-card` (#1e293b) | 13.98:1 | **PASS (AAA)** | Primary text on card |
| `--text-muted` (#94a3b8) | `--bg-base` (#090d16) | 7.58:1 | **PASS (AAA)** | Secondary text on base |
| `--text-muted` (#94a3b8) | `--bg-surface` (#0f172a) | 6.96:1 | **PASS (AA)** | Secondary text on surface |
| `--text-muted` (#94a3b8) | `--bg-card` (#1e293b) | 5.71:1 | **PASS (AA)** | Secondary text on card |
| `--text-dim` (#64748b) | `--bg-base` (#090d16) | 4.08:1 | *WARNING (< 4.5:1)* | Non-essential decorative text only (restricted) |
| `--text-dim` (#64748b) | `--bg-surface` (#0f172a) | 3.75:1 | *WARNING (< 4.5:1)* | Non-essential decorative text only (restricted) |
| `badge-safe-text` (#34d399) | `badge-safe-bg` (#064e3b) | 5.06:1 | **PASS (AA)** | Safe badge text on badge bg |
| `badge-vulnerable-text` (#fda4af) | `badge-vulnerable-bg` (#4c0519) | 8.27:1 | **PASS (AAA)** | Vulnerable badge text on badge bg |
| `badge-unknown-text` (#cbd5e1) | `badge-unknown-bg` (#1e293b) | 9.85:1 | **PASS (AAA)** | Unknown badge text on badge bg |
| `badge-critical-text` (#fecdd3) | `badge-critical-bg` (#4c0519) | 11.08:1 | **PASS (AAA)** | Critical badge text on badge bg |
| `badge-high-text` (#fde68a) | `badge-high-bg` (#451a03) | 12.03:1 | **PASS (AAA)** | High urgency badge text on badge bg |
| `badge-medium-text` (#c7d2fe) | `badge-medium-bg` (#1e1b4b) | 10.72:1 | **PASS (AAA)** | Medium urgency badge text on badge bg |
| `badge-low-text` (#6ee7b7) | `badge-low-bg` (#064e3b) | 6.38:1 | **PASS (AA)** | Low urgency badge text on badge bg |
| `badge-info-text` (#67e8f9) | `badge-info-bg` (#083344) | 9.24:1 | **PASS (AAA)** | Info badge text on badge bg |

---

## 3. Component Prop Tables

### 1. `Button`
| Prop | Type | Default | Description |
|---|---|---|---|
| `variant` | `'primary' \| 'secondary' \| 'ghost' \| 'danger'` | `'primary'` | Visual styling variant |
| `size` | `'sm' \| 'md' \| 'lg'` | `'md'` | Padding and font sizing |
| `loading` | `boolean` | `false` | Shows animated spinner, sets `aria-busy`, prevents clicks |
| `disabled` | `boolean` | `false` | Disables button and sets `aria-disabled` |
| `icon` | `React.ReactNode` | `null` | Optional leading icon element |
| `as` | `React.ElementType` | `'button'` | Polymorphic element tag (e.g., router Link) |
| `type` | `string` | `'button'` | HTML button type attribute |
| `id` | `string` | `useId()` | Unique DOM element ID |

### 2. `Card`
| Prop | Type | Default | Description |
|---|---|---|---|
| `variant` | `'default' \| 'elevated' \| 'glass' \| 'interactive'` | `'default'` | Elevation and surface appearance |
| `title` | `React.ReactNode` | `null` | Header title |
| `actions` | `React.ReactNode` | `null` | Header action buttons or badges |
| `onClick` | `Function` | `undefined` | Interactive click handler (adds tabIndex=0, role="button", Enter/Space keydown) |
| `as` | `React.ElementType` | `'section'` | Semantic HTML container element |

### 3. `Badge`
| Prop | Type | Default | Description |
|---|---|---|---|
| `variant` | `'safe' \| 'vulnerable' \| 'unknown' \| 'critical' \| 'high' \| 'medium' \| 'low' \| 'info' \| 'pass' \| 'fail'` | `'unknown'` | Semantic badge category |
| `pulse` | `boolean` | `false` | Enables glowing pulse animation (critical variant) |
| `live` | `boolean` | `false` | Adds `role="status"` and `aria-live="polite"` |
| `icon` | `React.ReactNode` | `auto` | Lucide icon override |

### 4. `LoadingSpinner`
| Prop | Type | Default | Description |
|---|---|---|---|
| `size` | `'sm' \| 'md' \| 'lg'` | `'md'` | Spinner dimensions |
| `label` | `string` | `undefined` | Visible accompanying text |
| `elapsedSeconds` | `number` | `undefined` | Elapsed timer count (renders "Analyzing... {elapsed}s") |
| `ariaLabel` | `string` | `'Loading'` | Accessible screen reader label |

### 5. `ErrorBanner`
| Prop | Type | Default | Description |
|---|---|---|---|
| `title` | `string` | `undefined` | Optional alert heading |
| `message` | `string` | (Required) | Alert explanation text (`role="alert"`) |
| `onRetry` | `Function` | `undefined` | Retry callback (renders retry button) |
| `onDismiss` | `Function` | `undefined` | Dismiss callback (renders close X button) |

### 6. `EmptyState`
| Prop | Type | Default | Description |
|---|---|---|---|
| `icon` | `React.ReactNode` | `<PackageOpen />` | Center illustration icon |
| `title` | `string` | (Required) | Heading text |
| `message` | `string` | (Required) | Descriptive body text |
| `ctaLabel` | `string` | `undefined` | Action button label |
| `ctaTo` | `string` | `undefined` | Target route path for React Router navigation |
| `onCta` | `Function` | `undefined` | Action click callback |

### 7. `TabBar` & `TabPanel`
| Prop | Type | Default | Description |
|---|---|---|---|
| `tabs` | `Array<{ id, label, icon?, badge?, disabled? }>` | `[]` | Tab configuration list |
| `value` | `string` | `undefined` | Controlled active tab ID |
| `defaultValue` | `string` | `tabs[0]?.id` | Uncontrolled active tab ID |
| `onChange` | `Function` | `undefined` | Tab change callback |
| `ariaLabel` | `string` | `'Navigation Tabs'` | `role="tablist"` label |

### 8. `Modal`
| Prop | Type | Default | Description |
|---|---|---|---|
| `open` | `boolean` | `false` | Controls open/closed visibility |
| `onClose` | `Function` | (Required) | Close handler |
| `title` | `React.ReactNode` | (Required) | Dialog title (`aria-labelledby`) |
| `description` | `string` | `undefined` | Dialog description (`aria-describedby`) |
| `closeOnBackdrop`| `boolean` | `true` | Allows closing by clicking outer backdrop |
| `size` | `'sm' \| 'md' \| 'lg' \| 'xl'` | `'md'` | Modal width |

### 9. `Tooltip`
| Prop | Type | Default | Description |
|---|---|---|---|
| `content` | `React.ReactNode` | (Required) | Tooltip body |
| `placement` | `'top' \| 'bottom' \| 'left' \| 'right'` | `'top'` | Preferred placement (auto-flips if overflowing viewport) |
| `children` | `React.ReactElement` | (Required) | Trigger element |

### 10. `ProgressRing`
| Prop | Type | Default | Description |
|---|---|---|---|
| `value` | `number` | `0` | Numeric percentage (0 - 100, clamped, always visible) |
| `size` | `number` | `100` | Diameter in pixels |
| `strokeWidth` | `number` | `8` | Arc stroke width |
| `label` | `string` | `undefined` | Secondary status text below percentage |
| `tone` | `'danger' \| 'warning' \| 'good' \| 'neutral' \| 'info'` | `auto` | Tone override |

---

## 4. Accessibility & Truthfulness Product Rules

1. **Badge Truthfulness:**
   - The `unknown` badge variant is styled strictly with neutral/muted slate tones (`#cbd5e1` on `#1e293b`) with a `HelpCircle` (`?`) icon. It never renders in green or implies safety.
2. **ProgressRing Honesty:**
   - The exact numerical percentage is always rendered as prominent text (`.progress-ring__value`) inside the ring. Status is never represented by color alone.
3. **Modal Focus Management:**
   - Focus is captured and transferred to the first focusable element when opened.
   - Focus is trapped within modal boundaries (Tab and Shift+Tab wrap around).
   - Focus is automatically returned to the triggering element when the modal is dismissed.
   - Body scrolling is locked with `overflow: hidden` during presentation.
4. **TabBar Roving TabIndex:**
   - WAI-ARIA tablist pattern: only the selected tab receives `tabIndex={0}`, while unselected tabs have `tabIndex={-1}`.
   - `ArrowRight`, `ArrowLeft`, `Home`, and `End` keys navigate and focus active tabs.
5. **Prefers-Reduced-Motion:**
   - Globally configured in [src/index.css](file:///d:/SIH%202026%20Astra/astra-main/frontend/src/index.css) to clamp transitions and animation durations to 0.01ms.
