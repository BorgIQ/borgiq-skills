# Interface Pages Reference

The `page` configuration used by both InterfaceTriggerActor and InterfaceActor to render web forms: page options, page colors, nesting and the submitted body, prefill, validation, access and `onSubmit`. Read it before writing any `page:` block. Component props are in [interface-components.md](interface-components.md); complete pages are in [interface-examples.md](interface-examples.md).

## Contents

- [Rules](#rules)
- [Page options](#page-options)
- [Page colors](#page-colors)
- [Layout and the submitted body](#layout-and-the-submitted-body)
- [Prefill](#prefill)
- [Validation](#validation)
- [Access](#access)
- [onSubmit](#onsubmit)

## Rules

1. Give every component a `key`, unique among its siblings (duplicates in one `children` array fail validation). The submitted `body` is keyed by component `key`; those keys are the contract between the form and the rest of the flow.
2. Prefill with `default`. Props not in a component's schema are ignored without an error (for example `defaultValue` instead of `default`, or `value` on a button); check each prop in [interface-components.md](interface-components.md).
3. Give every page that collects input a `formButton` (label in `text`): it submits the form and triggers the workflow.
4. Keep the page a form. For dashboards, SPAs or bespoke layouts build a ReactAppTriggerActor app (the `borgiq-react-app-builder` skill); a `webViewer` embeds a page or custom HTML inside a form.
5. Style custom HTML in a `webViewer` with the app theme library, [react-app-themes.md](react-app-themes.md). The native page takes only the colors below. A `webViewer`'s HTML runs under a strict Content Security Policy: its options are in [interface-components.md](interface-components.md#webviewer), the full model in [app-trigger-actor.md](app-trigger-actor.md#content-security-policy).
6. Share the page URL only with people who can open it ([Access](#access)).

## Page options

```yaml
configuration:
  options:
    page:
      pageTitle: My Form Title
      formWidth: half
      themeColor: blue
      children:
        - key: header
          type: header
          value: Form Header
        - key: fieldName
          type: text
          label: Field Label
          placeholder: Enter value...
          required: true
        - key: submit
          type: formButton
          text: Submit
    onSubmit:
      type: successMessage
```

| Option | Type | Default | Meaning |
|---|---|---|---|
| `children` | array | required | UI components, rendered in order |
| `pageTitle` | string | — | Browser tab title |
| `formWidth` | `full` \| `half` \| `adjustable` | `half` | `full` for data-dense layouts; `half` a centered half-width column for focused forms; `adjustable` a centered column the viewer can resize |
| `themeColor` | string | platform color | Primary color of buttons and inputs: hex `#RRGGBB` or a Mantine color name (`blue`, `teal`, …); other values are ignored |
| `backgroundColor` | string | — | Page background: a CSS color or a Mantine color name |

Native pages have no font setting; the platform's fonts apply. The page follows the viewer's light/dark scheme. `onSubmit`, `defaultValues`, `autoSubmitAfterSeconds` and `showProgressStatus` are actor options beside `page` ([interface-trigger-actor.md](interface-trigger-actor.md#options), [interface-actor.md](interface-actor.md#options)). Exact schema: [typescript/schemas/interface.md](typescript/schemas/interface.md).

## Page colors

To give a page a palette, set `themeColor` and `backgroundColor` from one row, and use the row's other colors as component `color` values (`header`, `divider`, buttons). Every value is a hex color, which both page options and component `color` props accept.

| Palette | `themeColor` | `backgroundColor` | Other colors |
|---|---|---|---|
| Arctic Frost | `#4a6fa5` | `#d4e4f7` | `#c0c0c0`, `#fafafa` |
| Botanical Garden | `#4a7c59` | `#f5f3ed` | `#f9a620`, `#b7472a` |
| Desert Rose | `#d4a5a5` | `#e8d5c4` | `#b87d6d`, `#5d2e46` |
| Forest Canopy | `#2d4a2b` | `#faf9f6` | `#7d8471`, `#a4ac86` |
| Golden Hour | `#f4a900` | `#d4b896` | `#c1666b`, `#4a403a` |
| Midnight Galaxy | `#a490c2` | `#2b1e3e` | `#4a4e8f`, `#e6e6fa` |
| Modern Minimalist | `#36454f` | `#ffffff` | `#708090`, `#d3d3d3` |
| Ocean Depths | `#2d8b8b` | `#1a2332` | `#a8dadc`, `#f1faee` |
| Sunset Boulevard | `#e76f51` | `#e9c46a` | `#f4a261`, `#264653` |
| Tech Innovation | `#0066ff` | `#1e1e1e` | `#00ffff`, `#ffffff` |

## Layout and the submitted body

- Group related fields with `section` (or `collapse`, which folds). `conditional` shows fields chosen by a select, `union` lets the viewer pick one of several components, and `arrayParent` repeats an `item`. Props: [interface-components.md](interface-components.md#nesting-components).
- A nested component's values nest under its own `key`. Set `extendParentObject: true` on a `section`, `collapse` or `conditional` to merge its children's values into the parent object instead. It defaults to `false`.
- An `arrayParent` submits an array of its `item`'s values. A `union` submits the chosen child's value under the union's `key`. A `conditional` adds the select's value under `conditionalField.key` beside the chosen children's values.
- Display components (`header`, `divider`, `progress`, `formButton`, `urlButton`, `image`, `markdown`, `codeViewer`, `pdfViewer`, `fileDownload`, `webViewer`, `textDisplay`) submit nothing.
- For a multi-step flow, give each step its own page and chain them with `onSubmit: nextInterface` ([interface-examples.md](interface-examples.md#multi-step-form)).

```yaml
children:
  - key: contactInfo
    type: section
    label: Contact Information
    extendParentObject: true      # body: { email, phone } — without it: { contactInfo: { email, phone } }
    children:
      - key: email
        type: text
        label: Email
      - key: phone
        type: phoneNumber
        label: Phone
```

## Prefill

A field's initial value comes from three sources, lowest precedence first:

1. The component's `default`, typed like its value (a string, a number, an array for `multiSelect`, an ISO date string for dates). It supports BorgIQ expressions: on an InterfaceActor, `default: ${{ msg.<msgVar>.<field> }}` shows data from upstream actors. An InterfaceTriggerActor has no upstream `msg`.
2. The actor's `defaultValues` option, keyed by component `key`.
3. URL query params (`?customerName=Ada`), which win. A dotted key (`?contactInfo.email=ada@example.com`) sets a nested value.

Set `readOnly: true` to display a value without allowing edits, for review and approval pages:

```yaml
- key: orderTotal
  type: number
  label: Order Total
  readOnly: true
  default: ${{ msg.calculate_total.total }}
- key: lastUpdated
  type: dateTime
  label: Last Updated
  readOnly: true
  default: ${{ msg.data?.lastUpdated || new Date().toISOString() }}
```

## Validation

- The browser validates each field against its component's rules (`required`, `regex`, `minLength`/`maxLength`, `minimum`/`maximum`, file size and count) before it submits.
- The server re-validates the submitted body against the page and answers 400 with per-field errors, which the page shows under the fields.
- Use `required: true` for mandatory fields and a `conditional` for branching.

## Access

- Every page requires a signed-in viewer: a Viewer, Member or Admin of the canvas's workspace, or an App user granted that InterfaceTriggerActor. Workspace settings cannot grant App users an InterfaceActor, so send InterfaceActor URLs only to workspace members.
- There is no anonymous or public access. For public sign-ups or anonymous intake, post from a page hosted outside BorgIQ to a WebhookTriggerActor with `configuration.webhook.authorizationLevel: public` ([webhook-trigger-actor.md](webhook-trigger-actor.md)).

## onSubmit

Required on both actors: what the viewer sees after a successful submission.

| `type` | Fields | Behavior |
|---|---|---|
| `successMessage` | `successMessage` (optional) | Show a message |
| `urlRedirect` | `url` (required) | Redirect to an external URL |
| `nextInterface` | `loadingMessage` (optional) | Show a waiting page until the first InterfaceActor that renders downstream in the same flow run replaces it |

```yaml
onSubmit:
  type: nextInterface
  loadingMessage: Processing your request...
```

With `nextInterface`, set `showProgressStatus: true` on the actor to show the flow's progress on the waiting page, and use an InterfaceStatusActor to add status components to it ([interface-actor.md](interface-actor.md#waiting-page-status)). Code actors cannot render a page.
