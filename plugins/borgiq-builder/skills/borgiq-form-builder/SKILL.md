---
name: borgiq-form-builder
description: Design BorgIQ interface pages, forms, form components, validation rules, conditional fields, themes, and the web-viewer embed. This is the primary BorgIQ UI surface. Use whenever the user is building an interface page, form, signup, data-entry UI, approval workflow, survey, or wants to embed another page inside an interface. Triggers on "build a form", "interface page", "approval flow", "data entry", "signup form", "survey", "feedback form", "InterfaceTriggerActor", "InterfaceActor".
---

# BorgIQ Form Builder

Build forms and interface pages — the primary user-facing surface in BorgIQ workflows. Pair this skill with the hub `borgiq-builder` (which handles flow wiring) and, when fields produce or consume structured data, `borgiq-json-schema-builder`.

## Mental model

Interface pages are the **form surface** of BorgIQ. Two actors share one page-configuration schema:

| Actor | When it fires | Use it for |
|---|---|---|
| **InterfaceTriggerActor** | Page submission **starts** the flow | Public-facing forms: signups, feedback, intake, surveys |
| **InterfaceActor** | Renders **mid-flow** with two output ports — `meta` (URL on render) and `event` (on submission) | Approvals, async review, "send a form via email" patterns |

**Interfaces are forms, not standalone apps.** Using an interface with no form fields (just display + webViewer) is no longer recommended — for interactive dashboards, SPAs, or bespoke layouts, build an app instead (see the `borgiq-react-app-builder` skill). The `webViewer` component embeds an external page or custom HTML *inside* a form, but it does not replace forms.

## Key decisions

1. **InterfaceTrigger vs InterfaceActor.** Does the form *start* the flow (Trigger) or sit *inside* it (Actor)? An InterfaceActor's `meta` port emits a URL that you can route to email/Slack and `event` fires when the user submits — this is the canonical async-approval pattern.
2. **Form width.** `formWidth: full` for data-dense layouts; `half` for focused single forms; `third` for very simple inputs (a single email field, a yes/no).
3. **Single page vs multi-step.** Group within one page using `section` and `collapse`. Reach for a wizard (chained InterfaceActors or `onSubmit: nextInterface`) only when steps depend on prior answers or the form is long enough that users would abandon a single page.
4. **Validation strategy.** `required: true` for mandatory, `readOnly: true` for display-only context, conditional fields for branching logic. Validation is client-side at submission.
5. **Theme.** Native page chrome is themed by the page config (`themeColor`, `backgroundColor`) — pick from `themes.md` (10 pre-built — Modern Minimalist, Ocean Depths, etc.). Custom HTML inside a `webViewer` is themed differently: use the app theme library (`react-app-themes.md`, default `hearth`) — it's plain CSS, no React required.
6. **webViewer scope.** Use it to embed external pages or hand-written HTML/CSS *within* the form (e.g., a help panel, a third-party widget). Don't try to rebuild the form itself in webViewer — use the native components.

## Workhorse components

Reach for these first; they cover ~80% of forms.

| Component | Use it for |
|---|---|
| `text` | Single-line input — names, titles, short answers |
| `textarea` | Multi-line — descriptions, notes, longer feedback |
| `select` | Dropdown choice when there are 4+ options |
| `radio` | Mutually exclusive choice with 2-4 options — cleaner than `select` here |
| `checkbox` | Single boolean — terms acceptance, opt-in, toggles |
| `fileInput` / `fileDropzone` | Single file or multi-file drag-and-drop upload |
| `section` | Group related fields; set `extendParentObject: true` to flatten into the parent payload |
| `header` | Title/divider text — establishes visual hierarchy |
| `markdown` | Rich instructional content (formatted help, intros) |
| `formButton` / `button` | Submit or action — required to trigger the workflow |

See [`references/interface-pages.md`](../borgiq-builder/references/interface-pages.md) for the full 40+ component catalog, including selection (`multiSelect`, `chips`), date/time, arrays, dynamic defaults, and conditional fields.

## Anti-patterns

1. **Interfaces as standalone apps.** No form fields, just webViewer/markdown for display? That's a deprecated pattern — build an app via the `borgiq-react-app-builder` skill instead.
2. **Arbitrary spacing or hex colors.** The theme's spacing scale and tokens are the contract. Hard-coded `padding: 17px` or `color: #4A90E2` outside the theme is a smell.
3. **Missing interaction states.** Every button needs hover/focus/disabled; every list needs loading/empty/error. Forms without states feel like screenshots.
4. **Sidebar with a different background color.** Fragments the visual space. Same background, subtle border for separation.
5. **Skipping the squint test.** Blur your eyes — if the hierarchy isn't visible and surfaces aren't distinguishable, the design isn't intentional yet.

## Theming, briefly

Two surfaces, two mechanisms:

- **Native page + form components** are themed by the page config (`themeColor`, `backgroundColor`); pick a palette from [`references/themes.md`](../borgiq-builder/references/themes.md). Dark mode is supported via `data-theme="dark"`.
- **Custom HTML inside a `webViewer`** uses the app theme library — [`references/react-app-themes.md`](../borgiq-builder/references/react-app-themes.md). It's framework-agnostic CSS (custom properties + class recipes), so it works in the webViewer's raw HTML+CSS with no React and no CDN: paste the Base Contract + one theme block (default `hearth`, or the theme closest to the page's palette) into the webViewer's styles, build markup on the recipe classes, and use Tabler icons as inline SVG with `stroke="currentColor"`. Never hard-code colors — tokens only, and dark mode comes wired in.

## Wiring to downstream actors

Form submissions are emitted as structured data; downstream actors consume specific fields:

```yaml
# Downstream HttpRequestActor accessing form data
inputs:
  customerName: ${{ msg.signup_form.body.fullName }}
  customerEmail: ${{ msg.signup_form.body.email }}
```

The `body` keys come from your `key:` declarations on each component in the page config. Define them with care — they're the API contract between the form and the rest of the flow.

## References

| File | What's inside |
|---|---|
| [`references/interface-pages.md`](../borgiq-builder/references/interface-pages.md) | Full page schema, all 40+ component types, dynamic defaults, conditional fields, onSubmit behavior, design guidelines |
| [`references/interface-trigger-actor.md`](../borgiq-builder/references/interface-trigger-actor.md) | InterfaceTriggerActor config, emitted message schema, downstream field access |
| [`references/interface-actor.md`](../borgiq-builder/references/interface-actor.md) | InterfaceActor config, two-port pattern, async approval workflows |
| [`references/react-app-themes.md`](../borgiq-builder/references/react-app-themes.md) | The app theme library for custom HTML in webViewer: token contract, base stylesheet, component recipes, five theme skins, Tabler icon rules |
| [`references/themes.md`](../borgiq-builder/references/themes.md) | 10 pre-built themes with palettes, typography, and best-use contexts |
| [`references/typescript/form-components.md`](../borgiq-builder/references/typescript/form-components.md) | TypeScript/Zod schemas for every form component |

## When to hand off to other spokes

| Customer ask | Hand off to |
|---|---|
| "I need a custom-styled dashboard / data explorer / SPA" | `borgiq-react-app-builder` (ReactAppTriggerActor) |
| "The form fields should match a JSON schema" or "validate against this contract" | `borgiq-json-schema-builder` |
| "Wire the form to an AI agent / tool-using LLM" | `borgiq-agent-builder` |
| Anything about edges, msgVars, fork/join, deploy | Hub: `borgiq-builder` |
