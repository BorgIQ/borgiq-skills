# React App Themes — Token Contract & Theme Library (v1)

The theming system for React apps built in a **ReactAppTriggerActor**. One shared **token contract**, one **base stylesheet**, and **five theme skins** — all defining the same custom-property names, so every generated app is written against identical tokens and swapping one CSS block reskins the whole app with zero component changes.

Not to be confused with [themes.md](themes.md) (presentation/marketing color palettes) — this document is the app-UI token system.

This library mirrors the BorgIQ platform's theme definitions; when token values change there, update this file to match.

## How to apply a theme

1. Create `src/theme.css` = the [Base Contract stylesheet](#base-contract-stylesheet) + **exactly one** [theme block](#the-five-themes).
2. `import './theme.css'` **first** in `src/main.tsx`.
3. Write every component against the tokens and [component recipes](#component-recipes). **Never hard-code a color, font, radius, or shadow in a component.**
4. Do not edit token values. A theme is a contract, not a starting point.

## Choosing a theme

**Default to `hearth`** unless the customer names a theme or supplies brand colors. Otherwise pick by app genre:

| Theme | Personality | Reach for it when building |
|---|---|---|
| `hearth` | The BorgIQ house look — warm ivory, ink primaries, clay accent | **Default.** Internal tools, admin panels, anything "BorgIQ-branded" |
| `ledger` | Green-tinted paper, deep pine, serif headings, ruled tables | Finance, ops, inventory, reporting, anything ledger-shaped |
| `meridian` | Cool slate, cobalt accent, precise geometry | Enterprise data tools, analytics, developer-facing consoles |
| `signal` | Dark-first graphite with an amber instrumentation accent | Monitoring, dashboards-on-a-wall, control rooms, on-call tooling |
| `bloom` | Blush neutrals, raspberry-plum, rounded and friendly | Customer portals, surveys, signups, anything public-facing and human |

Every theme ships light **and** dark. Four are light-first; `signal` is dark-first (its `:root` is the dark palette).

## Token contract

### Color roles (defined per theme, per mode)

| Token | Role |
|---|---|
| `--bg` | Page background |
| `--surface` | Default surface (often equals `--bg`) |
| `--surface-sunken` | Recessed areas: sidebars, wells, table headers |
| `--surface-raised` | Cards, popovers, modals |
| `--surface-hover` | Hover state for rows/items on `--surface` |
| `--sunken-hover` | Hover state on sunken surfaces |
| `--surface-selected` | Selected row/item |
| `--border-subtle` | Hairlines inside components (table row rules) |
| `--border` | Default component borders |
| `--border-strong` | Input borders, emphasized dividers |
| `--border-hover` | Border on hover |
| `--text-1` | Primary text |
| `--text-2` | Secondary text (labels, descriptions) |
| `--text-3` | Tertiary text (placeholders, captions, disabled) |
| `--accent` | Interactive accent: links, active nav, focused input border |
| `--accent-hover` | Accent hover |
| `--accent-soft` | Translucent accent wash (active-nav bg, selection tint) |
| `--ink` | **Primary action fill** (the primary button background) |
| `--ink-hover` | Primary action fill, hover |
| `--ivory` | Text/icon color on `--ink` |
| `--focus-ring` | Keyboard focus outline color |
| `--shadow-pop` | Elevation shadow for raised surfaces |

`--ink` is where each theme keeps its personality: `hearth` and `ledger` fill primary buttons with near-black ink that flips to near-white in dark mode (the BorgIQ signature); `meridian` fills with cobalt, `bloom` with plum, `signal` with amber. Components never need to know — they use `--ink`/`--ivory`.

### Status channels (identical in every theme)

Status is a **system-wide constant**: success, info, warning, and error look the same in every app regardless of theme, so meaning transfers between apps. Each channel has `-bg`, `-border`, `-text` (e.g. `--success-bg`). Values live in the Base Contract stylesheet, one light set and one dark set.

Deliberate adjacency: `signal`'s amber accent sits near the warning channel — that instrumentation-panel feel is the point. Badges stay distinguishable by their tinted containers; don't use bare `--accent` text for status copy in any theme.

### Type and shape (defined per theme, mode-independent)

| Token | Role |
|---|---|
| `--sans` | UI text stack |
| `--display` | Headings (falls back to `--sans` in most themes) |
| `--mono` | Code, IDs, tabular data |
| `--radius-control` | Buttons, inputs, selects |
| `--radius-card` | Cards, modals, popovers |

Webfonts are **optional**. Every stack starts with a webfont name and degrades to a solid system stack. Default builds ship no font files; if the customer wants the exact webfont, overlay `woff2` files under `src/assets/fonts/` via `options.files` + `${{ assets.<key> }}` and add `@font-face` in `theme.css` — never load fonts from a CDN (`allowedStyleDomains` stays empty).

### Scale tokens (identical in every theme)

Defined once in the Base Contract: a 4px spacing grid (`--space-1` … `--space-8` = 4, 8, 12, 16, 20, 24, 32, 48px) and a compact app-UI type scale (`--text-xs` 12 … `--text-2xl` 28, in rem). Body line-height 1.5; headings 1.25.

## Base Contract stylesheet

Theme-independent; goes at the top of every `src/theme.css`, followed by exactly one theme block.

```css
/* ============ BorgIQ App Themes v1 — Base Contract ============ */
/* Scale */
:root {
  --space-1: 4px;  --space-2: 8px;  --space-3: 12px; --space-4: 16px;
  --space-5: 20px; --space-6: 24px; --space-7: 32px; --space-8: 48px;
  --text-xs: 0.75rem;   --text-sm: 0.8125rem; --text-base: 0.875rem;
  --text-md: 1rem;      --text-lg: 1.125rem;  --text-xl: 1.375rem;
  --text-2xl: 1.75rem;
}

/* Status channels — system-wide constants (light) */
:root {
  --success-bg: hsl(152 56% 95%); --success-border: hsl(152 50% 80%); --success-text: hsl(152 64% 28%);
  --info-bg:    hsl(205 80% 95%); --info-border:    hsl(205 70% 80%); --info-text:    hsl(205 75% 32%);
  --warning-bg: hsl(38 95% 94%);  --warning-border: hsl(38 85% 78%);  --warning-text: hsl(30 80% 32%);
  --error-bg:   hsl(350 90% 96%); --error-border:   hsl(350 80% 85%); --error-text:   hsl(348 75% 36%);
}
/* Status channels (dark) */
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --success-bg: hsl(152 45% 11%); --success-border: hsl(152 40% 22%); --success-text: hsl(152 55% 65%);
  --info-bg:    hsl(205 60% 12%); --info-border:    hsl(205 55% 24%); --info-text:    hsl(205 75% 68%);
  --warning-bg: hsl(35 60% 11%);  --warning-border: hsl(36 55% 22%);  --warning-text: hsl(38 85% 62%);
  --error-bg:   hsl(348 55% 12%); --error-border:   hsl(348 50% 24%); --error-text:   hsl(350 85% 70%);
} }
[data-theme="dark"] {
  --success-bg: hsl(152 45% 11%); --success-border: hsl(152 40% 22%); --success-text: hsl(152 55% 65%);
  --info-bg:    hsl(205 60% 12%); --info-border:    hsl(205 55% 24%); --info-text:    hsl(205 75% 68%);
  --warning-bg: hsl(35 60% 11%);  --warning-border: hsl(36 55% 22%);  --warning-text: hsl(38 85% 62%);
  --error-bg:   hsl(348 55% 12%); --error-border:   hsl(348 50% 24%); --error-text:   hsl(350 85% 70%);
}

/* Ground */
* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--text-1);
  font-family: var(--sans);
  font-size: var(--text-base);
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
}
h1, h2, h3, h4 { font-family: var(--display); line-height: 1.25; margin: 0 0 var(--space-3); }
h1 { font-size: var(--text-2xl); } h2 { font-size: var(--text-xl); }
h3 { font-size: var(--text-lg); }  h4 { font-size: var(--text-md); }
a { color: var(--accent); }
a:hover { color: var(--accent-hover); }
code, pre, .mono { font-family: var(--mono); font-size: 0.92em; }
:focus-visible { outline: 2px solid var(--focus-ring); outline-offset: 2px; }
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation: none !important; transition: none !important; }
}
```

**Dark mode wiring.** Each theme block defines its light values on `:root` (dark values for `signal`), then redefines them under `@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { … } }` and again under `[data-theme="dark"]` so an explicit in-app toggle (setting `data-theme` on `<html>`) beats the OS preference in both directions. Apps don't need a toggle; if the customer asks for one, it's three lines against `data-theme`.

## Component recipes

The anatomy of every app. Reuse these classes (or replicate their token usage in CSS modules) rather than inventing parallel patterns.

```css
/* Buttons */
.btn {
  display: inline-flex; align-items: center; justify-content: center; gap: var(--space-2);
  font: 500 var(--text-base) var(--sans);
  border-radius: var(--radius-control);
  padding: var(--space-2) var(--space-4);
  border: 1px solid transparent;
  cursor: pointer;
  transition: background-color 120ms ease, border-color 120ms ease, color 120ms ease;
}
.btn-primary { background: var(--ink); color: var(--ivory); }
.btn-primary:hover:not(:disabled) { background: var(--ink-hover); }
.btn-secondary { background: var(--surface-raised); color: var(--text-1); border-color: var(--border-strong); }
.btn-secondary:hover:not(:disabled) { background: var(--surface-hover); border-color: var(--border-hover); }
.btn-ghost { background: transparent; color: var(--text-2); }
.btn-ghost:hover:not(:disabled) { background: var(--surface-hover); color: var(--text-1); }
.btn-danger { background: var(--error-text); color: var(--bg); }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
/* Hover pitfalls:
   1. CSS :hover matches disabled controls — always guard hover rules with
      :not(:disabled), or a loading/disabled button restyles under the cursor.
   2. If you restructure into base + modifier (.btn + .btn--primary), the base
      hover (.btn:hover, specificity 0,2,0) OUTRANKS the modifier's resting
      rule (.btn--primary, 0,1,0): a disabled primary then flips to the base
      hover surface while keeping its ivory text — an invisible label. Keep
      variant hover rules at equal-or-higher specificity and after the base
      hover in source order. */

/* Inputs */
.field label { display: block; font-size: var(--text-sm); font-weight: 500; color: var(--text-2); margin-bottom: var(--space-1); }
.input, .select, .textarea {
  width: 100%;
  font: 400 var(--text-base) var(--sans);
  color: var(--text-1);
  background: var(--surface-raised);
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-control);
  padding: var(--space-2) var(--space-3);
}
.input::placeholder { color: var(--text-3); }
.input:hover { border-color: var(--border-hover); }
.input:focus { border-color: var(--accent); outline: 2px solid var(--focus-ring); outline-offset: 0; }

/* Cards */
.card {
  background: var(--surface-raised);
  border: 1px solid var(--border);
  border-radius: var(--radius-card);
  box-shadow: var(--shadow-pop);
  padding: var(--space-5);
}

/* Stat tiles */
.stat .stat-label { font-size: var(--text-xs); font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; color: var(--text-3); }
.stat .stat-value { font-size: var(--text-2xl); font-weight: 600; color: var(--text-1); font-variant-numeric: tabular-nums; }

/* Tables */
.table { width: 100%; border-collapse: collapse; font-size: var(--text-base); }
.table th {
  text-align: left; font-size: var(--text-xs); font-weight: 600;
  letter-spacing: 0.06em; text-transform: uppercase; color: var(--text-3);
  background: var(--surface-sunken);
  padding: var(--space-2) var(--space-3);
  border-bottom: 1px solid var(--border);
}
.table td { padding: var(--space-3); border-bottom: 1px solid var(--border-subtle); }
.table td.num { font-variant-numeric: tabular-nums; text-align: right; }
.table tbody tr:hover { background: var(--surface-hover); }
.table tbody tr[aria-selected="true"] { background: var(--surface-selected); }

/* Badges */
.badge {
  display: inline-block; font-size: var(--text-xs); font-weight: 600;
  padding: 2px var(--space-2); border-radius: 999px; border: 1px solid;
}
.badge-success { background: var(--success-bg); border-color: var(--success-border); color: var(--success-text); }
.badge-info    { background: var(--info-bg);    border-color: var(--info-border);    color: var(--info-text); }
.badge-warning { background: var(--warning-bg); border-color: var(--warning-border); color: var(--warning-text); }
.badge-error   { background: var(--error-bg);   border-color: var(--error-border);   color: var(--error-text); }

/* App chrome */
.topbar {
  display: flex; align-items: center; gap: var(--space-4);
  padding: var(--space-3) var(--space-5);
  background: var(--surface);
  border-bottom: 1px solid var(--border);
}
.topbar .app-name { font-family: var(--display); font-weight: 600; font-size: var(--text-md); }
.nav-item { color: var(--text-2); border-radius: var(--radius-control); padding: var(--space-1) var(--space-3); text-decoration: none; }
.nav-item:hover { background: var(--surface-hover); color: var(--text-1); }
.nav-item[aria-current="page"] { background: var(--accent-soft); color: var(--accent); font-weight: 500; }

/* Empty states */
.empty { text-align: center; color: var(--text-2); padding: var(--space-8) var(--space-5); }
.empty .empty-title { font-weight: 600; color: var(--text-1); margin-bottom: var(--space-1); }
```

Copy rules: sentence case everywhere; buttons name the action ("Save changes", not "Submit"); errors say what went wrong and what to do; empty states invite the first action. An action keeps the same name through its whole flow.

## Icons

**Tabler Icons is the icon set** — one family in every theme, via `@tabler/icons-react` (MIT, ~5,000 stroke icons, tree-shakes into the single-JS build; inline SVG, so no CDN and no CSP change):

```tsx
import { IconPlus } from '@tabler/icons-react'

<button className="btn btn-primary">
  <IconPlus size={16} stroke={1.75} /> Create order
</button>
```

Treat icons as **part of the UI design, planned with the layout** — decided alongside nav, buttons, and empty states, not sprinkled on at the end:

- **Where they earn their place:** nav items (one per item), buttons whose action has a recognizable symbol, empty states (one large icon above the title), and table cells or stat tiles only when the symbol reads faster than the label alone. An icon must add recognition; if it doesn't, leave it out.
- **Color is never set on the icon.** Tabler renders `currentColor`, so icons inherit the text token of their context — `--text-2` in nav, `--ivory` inside a primary button, a status `-text` token in a badge. Hard-coding an icon color breaks theme swapping and dark mode.
- **One size and stroke per context, consistent app-wide:** 16px / stroke 1.75 inline and in buttons, 18–20px / 1.75 in nav, 28–32px / 1.5 in empty states (colored `--text-3`). Don't mix stroke weights in one view.
- **Icons support labels, they don't replace them.** Keep the text label except for universally understood controls (close, chevrons); an icon-only button requires an `aria-label`.
- **Never mix icon families or use emoji as UI icons.**

## The five themes

Each block is complete and self-contained: paste it after the Base Contract and the app is themed.

### 1. `hearth` — the BorgIQ house theme (default)

Warm ivory and stone, ink-filled primaries, the clay accent, IBM Plex. Token values come from the live BorgIQ platform design system, so `hearth` apps sit next to the BorgIQ product without a seam.

```css
/* ============ Theme: hearth (light-first) ============ */
:root {
  --sans: "IBM Plex Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  --display: var(--sans);
  --mono: "IBM Plex Mono", ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  --radius-control: 4px; --radius-card: 8px;

  --bg: hsl(60 14% 98.6%);
  --surface: hsl(60 14% 98.6%);
  --surface-sunken: hsl(60 14% 97.3%);
  --surface-raised: hsl(0 0% 100%);
  --surface-hover: hsl(60 10% 96%);
  --sunken-hover: hsl(60 5% 92.5%);
  --surface-selected: hsl(60 4% 90%);
  --border-subtle: hsl(60 5% 92.5%);
  --border: hsl(60 2% 87%);
  --border-strong: hsl(60 2% 82%);
  --border-hover: hsl(60 2% 74%);
  --text-1: hsl(60 3% 8%);
  --text-2: hsl(48 3% 37%);
  --text-3: hsl(52 5% 55%);
  --accent: #914127;
  --accent-hover: #AE5132;
  --accent-soft: color-mix(in srgb, #914127 12%, transparent);
  --ink: #151514;
  --ink-hover: #3D3D3A;
  --ivory: #FCFCFB;
  --focus-ring: color-mix(in srgb, #914127 55%, transparent);
  --shadow-pop: 0 8px 24px rgba(21, 21, 20, 0.08);
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg: hsl(60 3% 7%);
  --surface: hsl(60 3% 10%);
  --surface-sunken: hsl(60 3% 9%);
  --surface-raised: hsl(60 3% 13%);
  --surface-hover: hsl(60 3% 15%);
  --sunken-hover: hsl(60 3% 15%);
  --surface-selected: hsl(60 3% 18%);
  --border-subtle: hsl(60 3% 15%);
  --border: hsl(60 3% 17%);
  --border-strong: hsl(54 3% 24%);
  --border-hover: hsl(48 3% 35%);
  --text-1: hsl(60 14% 98.6%);
  --text-2: hsl(49 8% 65%);
  --text-3: hsl(53 4% 45%);
  --accent: #D97757;
  --accent-hover: #DC9074;
  --accent-soft: color-mix(in srgb, #D97757 12%, transparent);
  --ink: #FCFCFB;
  --ink-hover: #E0DDD2;
  --ivory: #151514;
  --focus-ring: color-mix(in srgb, #D97757 60%, transparent);
  --shadow-pop: 0 8px 24px rgba(0, 0, 0, 0.4);
} }
[data-theme="dark"] {
  --bg: hsl(60 3% 7%);
  --surface: hsl(60 3% 10%);
  --surface-sunken: hsl(60 3% 9%);
  --surface-raised: hsl(60 3% 13%);
  --surface-hover: hsl(60 3% 15%);
  --sunken-hover: hsl(60 3% 15%);
  --surface-selected: hsl(60 3% 18%);
  --border-subtle: hsl(60 3% 15%);
  --border: hsl(60 3% 17%);
  --border-strong: hsl(54 3% 24%);
  --border-hover: hsl(48 3% 35%);
  --text-1: hsl(60 14% 98.6%);
  --text-2: hsl(49 8% 65%);
  --text-3: hsl(53 4% 45%);
  --accent: #D97757;
  --accent-hover: #DC9074;
  --accent-soft: color-mix(in srgb, #D97757 12%, transparent);
  --ink: #FCFCFB;
  --ink-hover: #E0DDD2;
  --ivory: #151514;
  --focus-ring: color-mix(in srgb, #D97757 60%, transparent);
  --shadow-pop: 0 8px 24px rgba(0, 0, 0, 0.4);
}
```

### 2. `ledger` — paper, pine, and ruled lines

For apps whose soul is a table of numbers. Barely-green paper, deep pine-teal accent, green-black ink primaries that flip light in dark mode, serif headings, tabular numerals, tight 2px/4px radii.

```css
/* ============ Theme: ledger (light-first) ============ */
:root {
  --sans: "Source Sans 3", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  --display: "Source Serif 4", "Iowan Old Style", Georgia, serif;
  --mono: "IBM Plex Mono", ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  --radius-control: 2px; --radius-card: 4px;

  --bg: hsl(140 12% 97.3%);
  --surface: hsl(140 12% 97.3%);
  --surface-sunken: hsl(140 10% 95.8%);
  --surface-raised: hsl(0 0% 100%);
  --surface-hover: hsl(140 8% 95%);
  --sunken-hover: hsl(140 6% 92%);
  --surface-selected: hsl(145 10% 90%);
  --border-subtle: hsl(140 8% 91%);
  --border: hsl(140 5% 85%);
  --border-strong: hsl(140 4% 79%);
  --border-hover: hsl(140 4% 68%);
  --text-1: hsl(160 25% 9%);
  --text-2: hsl(155 8% 34%);
  --text-3: hsl(150 6% 50%);
  --accent: #166A5D;
  --accent-hover: #1E8271;
  --accent-soft: color-mix(in srgb, #166A5D 11%, transparent);
  --ink: #0D2B21;
  --ink-hover: #1E4436;
  --ivory: #F7FAF8;
  --focus-ring: color-mix(in srgb, #166A5D 55%, transparent);
  --shadow-pop: 0 6px 20px rgba(13, 43, 33, 0.08);
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg: hsl(160 12% 6.5%);
  --surface: hsl(160 10% 9%);
  --surface-sunken: hsl(160 10% 8%);
  --surface-raised: hsl(160 9% 12%);
  --surface-hover: hsl(160 8% 14%);
  --sunken-hover: hsl(160 8% 14%);
  --surface-selected: hsl(160 8% 17%);
  --border-subtle: hsl(160 8% 14%);
  --border: hsl(160 7% 16%);
  --border-strong: hsl(158 6% 23%);
  --border-hover: hsl(155 5% 34%);
  --text-1: hsl(140 15% 96%);
  --text-2: hsl(145 8% 66%);
  --text-3: hsl(148 6% 46%);
  --accent: #3FA98C;
  --accent-hover: #5BBCA1;
  --accent-soft: color-mix(in srgb, #3FA98C 14%, transparent);
  --ink: hsl(140 15% 96%);
  --ink-hover: hsl(140 10% 84%);
  --ivory: hsl(160 12% 6.5%);
  --focus-ring: color-mix(in srgb, #3FA98C 60%, transparent);
  --shadow-pop: 0 8px 24px rgba(0, 0, 0, 0.45);
} }
[data-theme="dark"] {
  --bg: hsl(160 12% 6.5%);
  --surface: hsl(160 10% 9%);
  --surface-sunken: hsl(160 10% 8%);
  --surface-raised: hsl(160 9% 12%);
  --surface-hover: hsl(160 8% 14%);
  --sunken-hover: hsl(160 8% 14%);
  --surface-selected: hsl(160 8% 17%);
  --border-subtle: hsl(160 8% 14%);
  --border: hsl(160 7% 16%);
  --border-strong: hsl(158 6% 23%);
  --border-hover: hsl(155 5% 34%);
  --text-1: hsl(140 15% 96%);
  --text-2: hsl(145 8% 66%);
  --text-3: hsl(148 6% 46%);
  --accent: #3FA98C;
  --accent-hover: #5BBCA1;
  --accent-soft: color-mix(in srgb, #3FA98C 14%, transparent);
  --ink: hsl(140 15% 96%);
  --ink-hover: hsl(140 10% 84%);
  --ivory: hsl(160 12% 6.5%);
  --focus-ring: color-mix(in srgb, #3FA98C 60%, transparent);
  --shadow-pop: 0 8px 24px rgba(0, 0, 0, 0.45);
}
```

### 3. `meridian` — slate and cobalt precision

The calm enterprise console. Cool slate neutrals, one vivid cobalt doing all the interactive work (accent *and* primary fill), 6px/10px radii. No display face — restraint is the personality.

```css
/* ============ Theme: meridian (light-first) ============ */
:root {
  --sans: "Inter", "SF Pro Text", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  --display: var(--sans);
  --mono: "IBM Plex Mono", ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  --radius-control: 6px; --radius-card: 10px;

  --bg: hsl(220 25% 98%);
  --surface: hsl(220 25% 98%);
  --surface-sunken: hsl(220 20% 96.5%);
  --surface-raised: hsl(0 0% 100%);
  --surface-hover: hsl(220 16% 95.5%);
  --sunken-hover: hsl(220 14% 92.5%);
  --surface-selected: hsl(221 16% 90%);
  --border-subtle: hsl(220 14% 91.5%);
  --border: hsl(220 10% 86%);
  --border-strong: hsl(220 9% 80%);
  --border-hover: hsl(220 9% 69%);
  --text-1: hsl(224 35% 11%);
  --text-2: hsl(222 12% 36%);
  --text-3: hsl(220 9% 53%);
  --accent: #2050D8;
  --accent-hover: #3A66E4;
  --accent-soft: color-mix(in srgb, #2050D8 10%, transparent);
  --ink: #2050D8;
  --ink-hover: #1A44B8;
  --ivory: #FAFBFE;
  --focus-ring: color-mix(in srgb, #2050D8 45%, transparent);
  --shadow-pop: 0 6px 20px rgba(16, 26, 51, 0.08);
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg: hsl(224 28% 7%);
  --surface: hsl(224 24% 10%);
  --surface-sunken: hsl(224 24% 9%);
  --surface-raised: hsl(224 20% 13%);
  --surface-hover: hsl(224 18% 15%);
  --sunken-hover: hsl(224 18% 15%);
  --surface-selected: hsl(224 18% 19%);
  --border-subtle: hsl(224 18% 15%);
  --border: hsl(224 16% 17%);
  --border-strong: hsl(224 14% 24%);
  --border-hover: hsl(224 12% 35%);
  --text-1: hsl(220 25% 97%);
  --text-2: hsl(220 12% 70%);
  --text-3: hsl(220 8% 48%);
  --accent: #6C8FF2;
  --accent-hover: #88A5F5;
  --accent-soft: color-mix(in srgb, #6C8FF2 14%, transparent);
  --ink: #3E67E8;
  --ink-hover: #5A7DEC;
  --ivory: #F7F9FE;
  --focus-ring: color-mix(in srgb, #6C8FF2 55%, transparent);
  --shadow-pop: 0 8px 24px rgba(0, 0, 0, 0.45);
} }
[data-theme="dark"] {
  --bg: hsl(224 28% 7%);
  --surface: hsl(224 24% 10%);
  --surface-sunken: hsl(224 24% 9%);
  --surface-raised: hsl(224 20% 13%);
  --surface-hover: hsl(224 18% 15%);
  --sunken-hover: hsl(224 18% 15%);
  --surface-selected: hsl(224 18% 19%);
  --border-subtle: hsl(224 18% 15%);
  --border: hsl(224 16% 17%);
  --border-strong: hsl(224 14% 24%);
  --border-hover: hsl(224 12% 35%);
  --text-1: hsl(220 25% 97%);
  --text-2: hsl(220 12% 70%);
  --text-3: hsl(220 8% 48%);
  --accent: #6C8FF2;
  --accent-hover: #88A5F5;
  --accent-soft: color-mix(in srgb, #6C8FF2 14%, transparent);
  --ink: #3E67E8;
  --ink-hover: #5A7DEC;
  --ivory: #F7F9FE;
  --focus-ring: color-mix(in srgb, #6C8FF2 55%, transparent);
  --shadow-pop: 0 8px 24px rgba(0, 0, 0, 0.45);
}
```

### 4. `signal` — graphite and amber, dark-first

Built to be read across a room. Cool graphite ground, one amber instrumentation accent, amber-filled primaries with near-black labels in both modes, mono-forward for anything numeric. **`:root` is the dark palette; light mode is the override.**

```css
/* ============ Theme: signal (dark-first) ============ */
:root {
  --sans: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  --display: var(--sans);
  --mono: "JetBrains Mono", "IBM Plex Mono", ui-monospace, SFMono-Regular, Menlo, monospace;
  --radius-control: 4px; --radius-card: 6px;

  --bg: hsl(228 10% 6.5%);
  --surface: hsl(228 9% 9.5%);
  --surface-sunken: hsl(228 9% 8%);
  --surface-raised: hsl(228 8% 12.5%);
  --surface-hover: hsl(228 8% 14.5%);
  --sunken-hover: hsl(228 8% 14.5%);
  --surface-selected: hsl(228 8% 18%);
  --border-subtle: hsl(228 8% 15%);
  --border: hsl(228 7% 17%);
  --border-strong: hsl(228 7% 24%);
  --border-hover: hsl(228 6% 34%);
  --text-1: hsl(220 15% 96%);
  --text-2: hsl(222 8% 68%);
  --text-3: hsl(224 6% 47%);
  --accent: #E9A13B;
  --accent-hover: #F0B25C;
  --accent-soft: color-mix(in srgb, #E9A13B 13%, transparent);
  --ink: #E9A13B;
  --ink-hover: #F0B25C;
  --ivory: #1A1205;
  --focus-ring: color-mix(in srgb, #E9A13B 55%, transparent);
  --shadow-pop: 0 8px 24px rgba(0, 0, 0, 0.5);
}
@media (prefers-color-scheme: light) { :root:not([data-theme="dark"]) {
  --bg: hsl(228 20% 97.5%);
  --surface: hsl(228 20% 97.5%);
  --surface-sunken: hsl(228 16% 95.5%);
  --surface-raised: hsl(0 0% 100%);
  --surface-hover: hsl(228 14% 94.5%);
  --sunken-hover: hsl(228 12% 91.5%);
  --surface-selected: hsl(228 12% 89%);
  --border-subtle: hsl(228 12% 90.5%);
  --border: hsl(228 9% 85%);
  --border-strong: hsl(228 8% 79%);
  --border-hover: hsl(228 8% 68%);
  --text-1: hsl(228 12% 10%);
  --text-2: hsl(226 8% 36%);
  --text-3: hsl(224 6% 52%);
  --accent: #9A6210;
  --accent-hover: #B4791C;
  --accent-soft: color-mix(in srgb, #9A6210 12%, transparent);
  --ink: #D9922C;
  --ink-hover: #C4821F;
  --ivory: #231604;
  --focus-ring: color-mix(in srgb, #9A6210 50%, transparent);
  --shadow-pop: 0 6px 20px rgba(20, 24, 38, 0.10);
} }
[data-theme="light"] {
  --bg: hsl(228 20% 97.5%);
  --surface: hsl(228 20% 97.5%);
  --surface-sunken: hsl(228 16% 95.5%);
  --surface-raised: hsl(0 0% 100%);
  --surface-hover: hsl(228 14% 94.5%);
  --sunken-hover: hsl(228 12% 91.5%);
  --surface-selected: hsl(228 12% 89%);
  --border-subtle: hsl(228 12% 90.5%);
  --border: hsl(228 9% 85%);
  --border-strong: hsl(228 8% 79%);
  --border-hover: hsl(228 8% 68%);
  --text-1: hsl(228 12% 10%);
  --text-2: hsl(226 8% 36%);
  --text-3: hsl(224 6% 52%);
  --accent: #9A6210;
  --accent-hover: #B4791C;
  --accent-soft: color-mix(in srgb, #9A6210 12%, transparent);
  --ink: #D9922C;
  --ink-hover: #C4821F;
  --ivory: #231604;
  --focus-ring: color-mix(in srgb, #9A6210 50%, transparent);
  --shadow-pop: 0 6px 20px rgba(20, 24, 38, 0.10);
}
```

When embedding `signal`, also move the Base Contract's **dark** status values onto `:root` and its light values behind the light-mode guards, mirroring the theme block's inverted wiring.

### 5. `bloom` — blush, plum, and soft edges

The public face: portals, surveys, signups. Warm blush-tinted neutrals, raspberry-plum doing both accent and fill duty, generous 12px/16px radii, humanist sans. Friendly comes from shape and warmth, not decoration.

```css
/* ============ Theme: bloom (light-first) ============ */
:root {
  --sans: "Nunito Sans", "Avenir Next", "Segoe UI", Verdana, sans-serif;
  --display: var(--sans);
  --mono: "IBM Plex Mono", ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  --radius-control: 12px; --radius-card: 16px;

  --bg: hsl(340 30% 98.2%);
  --surface: hsl(340 30% 98.2%);
  --surface-sunken: hsl(340 22% 96.5%);
  --surface-raised: hsl(0 0% 100%);
  --surface-hover: hsl(340 18% 95.5%);
  --sunken-hover: hsl(340 16% 93%);
  --surface-selected: hsl(340 18% 91%);
  --border-subtle: hsl(340 15% 91.5%);
  --border: hsl(340 10% 86%);
  --border-strong: hsl(340 9% 80%);
  --border-hover: hsl(340 9% 69%);
  --text-1: hsl(335 30% 12%);
  --text-2: hsl(335 10% 38%);
  --text-3: hsl(335 7% 54%);
  --accent: #9C2F66;
  --accent-hover: #B24479;
  --accent-soft: color-mix(in srgb, #9C2F66 10%, transparent);
  --ink: #9C2F66;
  --ink-hover: #872757;
  --ivory: #FDF9FB;
  --focus-ring: color-mix(in srgb, #9C2F66 45%, transparent);
  --shadow-pop: 0 8px 24px rgba(74, 20, 46, 0.10);
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg: hsl(325 14% 7.5%);
  --surface: hsl(325 12% 10.5%);
  --surface-sunken: hsl(325 12% 9%);
  --surface-raised: hsl(325 11% 13.5%);
  --surface-hover: hsl(325 10% 15.5%);
  --sunken-hover: hsl(325 10% 15.5%);
  --surface-selected: hsl(325 10% 19%);
  --border-subtle: hsl(325 10% 15%);
  --border: hsl(325 9% 17.5%);
  --border-strong: hsl(325 8% 25%);
  --border-hover: hsl(325 7% 35%);
  --text-1: hsl(340 25% 97%);
  --text-2: hsl(335 10% 70%);
  --text-3: hsl(332 7% 48%);
  --accent: #E06BA8;
  --accent-hover: #EA88BA;
  --accent-soft: color-mix(in srgb, #E06BA8 14%, transparent);
  --ink: #E06BA8;
  --ink-hover: #EA88BA;
  --ivory: #2A0E1D;
  --focus-ring: color-mix(in srgb, #E06BA8 55%, transparent);
  --shadow-pop: 0 8px 24px rgba(0, 0, 0, 0.45);
} }
[data-theme="dark"] {
  --bg: hsl(325 14% 7.5%);
  --surface: hsl(325 12% 10.5%);
  --surface-sunken: hsl(325 12% 9%);
  --surface-raised: hsl(325 11% 13.5%);
  --surface-hover: hsl(325 10% 15.5%);
  --sunken-hover: hsl(325 10% 15.5%);
  --surface-selected: hsl(325 10% 19%);
  --border-subtle: hsl(325 10% 15%);
  --border: hsl(325 9% 17.5%);
  --border-strong: hsl(325 8% 25%);
  --border-hover: hsl(325 7% 35%);
  --text-1: hsl(340 25% 97%);
  --text-2: hsl(335 10% 70%);
  --text-3: hsl(332 7% 48%);
  --accent: #E06BA8;
  --accent-hover: #EA88BA;
  --accent-soft: color-mix(in srgb, #E06BA8 14%, transparent);
  --ink: #E06BA8;
  --ink-hover: #EA88BA;
  --ivory: #2A0E1D;
  --focus-ring: color-mix(in srgb, #E06BA8 55%, transparent);
  --shadow-pop: 0 8px 24px rgba(0, 0, 0, 0.45);
}
```

## Rules for the generating agent

**Always**

- Assemble `src/theme.css` as Base Contract + one theme block; import it first in `src/main.tsx`.
- Default to `hearth` when the customer doesn't name a theme or supply a brand.
- Use the component recipes for buttons, inputs, cards, tables, badges, chrome, and empty states — extend them with tokens, don't fork them.
- Use `--space-*` for all padding/margin/gap and `--text-*` for all font sizes.
- Use `font-variant-numeric: tabular-nums` for columns of numbers.
- Use Tabler (`@tabler/icons-react`) for every icon, sized and colored per the [Icons](#icons) section, and plan icon placement as part of the UI design.
- Keep `:focus-visible` outlines and the `prefers-reduced-motion` guard intact.

**Never**

- Hard-code a color, font family, radius, or shadow in a component — if a value isn't a token, it doesn't ship.
- Edit token values inside a theme block, mix tokens from two themes, or invent new tokens.
- Load fonts or styles from a CDN (`allowedStyleDomains` stays empty; fonts are system-stack or overlaid `woff2` assets).
- Use `--accent` for status meaning or status tokens for decoration — accent is "interactive", status channels are "state".
- Use pure white/black backgrounds — every theme's neutrals are tinted on purpose.
- Mix icon families, use emoji as UI icons, or hard-code an icon color — icons are Tabler-only and inherit `currentColor`.

**Customer brand overrides.** If the customer supplies brand colors, start from the closest theme and remap only `--accent`, `--accent-hover`, `--accent-soft`, `--ink`, `--ink-hover`, `--ivory`, and `--focus-ring` — neutrals, status channels, and shape stay. Verify text-on-fill contrast ≥ 4.5:1. If the brand demands more than an accent swap, say so and get the customer's sign-off on a bespoke palette instead of improvising token by token.
