---
name: borgiq-form-builder
description: Design BorgIQ interface pages and forms for signed-in users — InterfaceTriggerActor and InterfaceActor pages, form components, prefill, validation, conditional fields, page colors and the web-viewer embed. Use when building a form, signup, survey, data-entry page or approval step. Triggers on "build a form", "interface page", "approval flow", "data entry", "signup form", "survey", "feedback form", "InterfaceTriggerActor", "InterfaceActor".
---

# BorgIQ Form Builder

Build forms and interface pages for BorgIQ workflows. This skill requires the `borgiq-builder` skill (the hub), which covers flow wiring, IDs and deployment and holds the references linked below. For structured data contracts, also use the `borgiq-json-schema-builder` skill.

## Who can open a page

**Every interface page requires a signed-in viewer; there is no anonymous access.** Opening or submitting a page takes a Viewer, Member or Admin role in the canvas's workspace, or an App user grant for that InterfaceTriggerActor. Workspace settings cannot grant App users an InterfaceActor, so send approval links only to workspace members. For public sign-ups or anonymous intake, post from a page hosted outside BorgIQ to a WebhookTriggerActor with `configuration.webhook.authorizationLevel: public` ([webhook-trigger-actor.md](../borgiq-builder/references/webhook-trigger-actor.md)).

## Mental model

Two actors share one page schema:

| Actor | When it fires | Use it for |
|---|---|---|
| **InterfaceTriggerActor** | Page submission **starts** the flow | Forms for signed-in users: requests, intake, feedback, surveys |
| **InterfaceActor** | Renders **mid-flow**; its Meta port (`SPRTdefault`) emits the page URL, its Event port (`SPRTevent00`) the submission | Approvals, async review, "send a form by email" |

**Interfaces are forms, not apps.** For dashboards, SPAs or bespoke layouts, build a ReactAppTriggerActor app with the `borgiq-react-app-builder` skill. A `webViewer` embeds an external page or custom HTML *inside* a form (a help panel, a widget); never rebuild the form in it.

## Rules

1. **Trigger or actor.** A form that starts the flow is an InterfaceTriggerActor. For an approval, place an InterfaceActor, route the Meta port's `interfaceUrl` to email or Slack, and process the Event port's `body`. Set `timeoutInMinutes` to bound the wait: there is no timeout by default, and on expiry the actor fails with a `TimeoutError`.
2. **Prefill with `default`**, never `defaultValue`: props a component's schema lacks are ignored without an error. `default: ${{ msg.<msgVar>.<field> }}` works on an InterfaceActor; any page can also be prefilled by `defaultValues` or URL query params, which win. Add `readOnly: true` for display-only context.
3. **Width.** `formWidth` is `full` (data-dense layouts), `half` (default; a centered half-width column) or `adjustable` (a centered column the viewer can resize).
4. **One page first.** Group fields with `section` and `collapse`. Chain pages (`onSubmit: nextInterface` into a downstream InterfaceActor) only when steps depend on earlier answers or the page grows too long.
5. **Validation.** Mark mandatory fields `required: true`; use conditional fields for branching. The browser validates, and the server re-validates the body against the page (400 with per-field errors).
6. **Keys are the contract.** The submitted `body` is keyed by each component's `key`; a nested component's values sit under its own key unless `extendParentObject: true`. Every page that collects input needs a `formButton` (label in `text`).

## Workhorse components

`interface-components.md` has all 51 types.

| Component | Use it for |
|---|---|
| `text` | Single line; `variant: email` validates an address |
| `textarea` | Multi-line: descriptions, notes |
| `select` / `radio` | One choice: `select` for 4+ options, `radio` for 2–4 |
| `buttonGroup` | One choice as buttons, such as Approve / Reject |
| `checkbox` | Single boolean: terms, opt-in |
| `fileInput` / `fileDropzone` | File upload; drag-and-drop for several |
| `section` | Group related fields |
| `header` / `markdown` | Titles and formatted instructions |
| `formButton` | Submits the form |

## Theming

- **Native page:** `themeColor` (primary color: hex `#RRGGBB` or a Mantine color name such as `blue`) and `backgroundColor`; no font setting, and the page follows the viewer's light/dark scheme. Take a palette from the [page colors table](../borgiq-builder/references/interface-pages.md#page-colors).
- **Custom HTML in a `webViewer`:** style it with the app theme library, [react-app-themes.md](../borgiq-builder/references/react-app-themes.md) (plain CSS: the Base Contract + one theme block, default `hearth`; tokens only, never hard-coded colors).

## Wiring to downstream actors

```yaml
# A downstream actor reading a submission
inputs:
  customerName: ${{ msg.signup_form.body.fullName }}
  customerEmail: ${{ msg.signup_form.body.email }}
  submittedBy: ${{ msg.signup_form.meta.user.email }}
```

## Read when

| When you need | Read |
|---|---|
| Page options, colors, nesting and body shape, prefill, validation, access, `onSubmit` | [interface-pages.md](../borgiq-builder/references/interface-pages.md) |
| A component's props, the webViewer and its CSP options | [interface-components.md](../borgiq-builder/references/interface-components.md), then the generated module it links |
| A complete page: contact, approval, multi-step, conditional fields, editable table | [interface-examples.md](../borgiq-builder/references/interface-examples.md) |
| A form that starts a flow: options, emitted message, page URL | [interface-trigger-actor.md](../borgiq-builder/references/interface-trigger-actor.md) |
| An approval mid-flow: ports, `timeoutInMinutes`, emailing the link, waiting-page status | [interface-actor.md](../borgiq-builder/references/interface-actor.md) and [send-email-actor.md](../borgiq-builder/references/send-email-actor.md) |
| Styling custom HTML in a webViewer | [react-app-themes.md](../borgiq-builder/references/react-app-themes.md) |
| A public form with no sign-in | [webhook-trigger-actor.md](../borgiq-builder/references/webhook-trigger-actor.md) |
| Exact types | [typescript/index.md](../borgiq-builder/references/typescript/index.md) |

## When to hand off to other skills

| Customer ask | Use |
|---|---|
| "I need a custom-styled dashboard / data explorer / SPA" | `borgiq-react-app-builder` (ReactAppTriggerActor) |
| "The form fields should match a JSON schema" or "validate against this contract" | `borgiq-json-schema-builder` |
| "Wire the form to an AI agent / tool-using LLM" | `borgiq-agent-builder` |
| Edges, msgVars, fork/join, deploy | the hub, `borgiq-builder` |
