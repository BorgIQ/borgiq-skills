# App theme blocks

The CSS of the five app themes, one block each. Read [react-app-themes.md](react-app-themes.md) first (rules, token
contract, Base Contract). Then copy **exactly one** block below into `src/theme.css` after the Base Contract, unchanged.
Each block is complete: it defines every color, type and shape token for light and dark mode. Search for
`Theme: <name>` to find one.

## Contents

- [hearth](#1-hearth--the-borgiq-house-theme-default) (default)
- [ledger](#2-ledger--paper-pine-and-ruled-lines)
- [meridian](#3-meridian--slate-and-cobalt-precision)
- [signal](#4-signal--graphite-and-amber-dark-first)
- [bloom](#5-bloom--blush-plum-and-soft-edges)

## 1. `hearth` — the BorgIQ house theme (default)

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

## 2. `ledger` — paper, pine, and ruled lines

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

## 3. `meridian` — slate and cobalt precision

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

## 4. `signal` — graphite and amber, dark-first

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

## 5. `bloom` — blush, plum, and soft edges

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
