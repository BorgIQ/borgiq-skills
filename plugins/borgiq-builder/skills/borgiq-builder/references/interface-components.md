# Interface Components Reference

Every component `type` an interface page can hold, with its props, grouped as the generated types are. Find the component's row, and read its linked generated module when you need exact types. Page-level rules (keys, prefill, nesting, validation, access) are in [interface-pages.md](interface-pages.md); complete pages are in [interface-examples.md](interface-examples.md).

## Contents

- [Shared props](#shared-props)
- [Text inputs](#text-inputs)
- [Choice inputs](#choice-inputs)
- [Number inputs](#number-inputs)
- [Boolean inputs](#boolean-inputs)
- [Date and time inputs](#date-and-time-inputs)
- [File inputs](#file-inputs)
- [YAML and JSON inputs](#yaml-and-json-inputs)
- [Nesting components](#nesting-components)
- [Table](#table)
- [Display components](#display-components)
- [webViewer](#webviewer)

## Shared props

Input components are every type except the display components. Exact shared types: [typescript/formComponents/base.md](typescript/formComponents/base.md).

| Prop | On | Meaning |
|---|---|---|
| `key` | every component | Required. The field name in the submitted body; unique among its siblings |
| `type` | every component | Required. One of the types below |
| `label` | inputs | Text above the input; defaults to the key (with parent keys) |
| `description` | inputs | Help text displayed below the label |
| `infoText` | inputs | Help text shown in an info tooltip |
| `required`, `disabled`, `readOnly`, `hidden` | inputs | Booleans. `readOnly` displays the value without allowing edits |
| `default` | most inputs | Initial value, typed like the component's value; supports BorgIQ expressions. Never `defaultValue` |
| `placeholder` | inputs with an empty box | Shown while the input is empty |

Value formats used below:

- **Colors** (`color`, `buttonColor`, `subtitleColor`, …): hex `#RRGGBB` or one of `red`, `pink`, `grape`, `violet`, `indigo`, `blue`, `cyan`, `teal`, `green`, `lime`, `yellow`, `orange`, `gray`, `black`, `white`.
- **Button variants**: `filled`, `outline`, `light`, `subtle`, `transparent`, `white`. **Button sizes**: `xs`–`xl` or `compact-xs`–`compact-xl`.
- **Options**: strings (each is both label and value), `{label, value}` objects, or groups `{group, items}` whose items take either form; use one form per list:

  ```yaml
  options:
    - group: Staff
      items: [Admin, Moderator]
    - group: Customers
      items:
        - label: Paying customer
          value: paying
  ```
- **String validation**: `regex`, `regexErrorMessage` (default `Invalid input`), `minLength` (default 0, or 1 when `required`), `maxLength`.

## Text inputs

| `type` | Use | Props beyond the shared ones |
|---|---|---|
| [`text`](typescript/formComponents/string/text.md) | Single line: names, titles, short answers | `variant` (`email` \| `uri`: adds an icon and validation, overriding `regex`), string validation, `copyable` |
| [`textarea`](typescript/formComponents/string/textArea.md) | Multi-line: descriptions, notes, longer feedback | string validation, `minLines`, `maxLines`, `height`, `width`, `autoResize` (default true), `copyable` |
| [`password`](typescript/formComponents/string/password.md) | Masked input | string validation, `allowUnmasking` (default true) |
| [`pin`](typescript/formComponents/string/pin.md) | One box per character, for 2FA codes and OTPs | `length` (default 4), `valueType` (`number` \| `alphanumeric`, the default), `regex`, `regexErrorMessage`, `masked` (default true), `isOTP`, `inputMode`, `submitOnComplete` (default false) |
| [`phoneNumber`](typescript/formComponents/string/phoneNumber.md) | Formatted phone number | `format` (`E.164` \| `national` \| `international`), `defaultCountry` (two-letter ISO 3166 code such as `US`), `fixedCountryCode` |
| [`code`](typescript/formComponents/string/code.md) | Code editor with syntax highlighting | `language`, string validation, `wrapLines` (default true), `minLines`, `maxLines`, `height`, `autoResize` (default true), `copyable` |
| [`codeDiff`](typescript/formComponents/string/codeDiff.md) | Edit new code against old code | `oldValue` (required; not editable), `default` (required; the editable new code), `language`, `oldCodeTitle`, `newCodeTitle`, `inline` (default false: side by side), `revertControls`, string validation, `wrapLines`, `minLines`, `maxLines`, `height`, `width`, `autoResize` |
| [`markdownInput`](typescript/formComponents/string/markdown.md) | Markdown editor | `default` (required), `preview` (default true: rendered side by side), string validation, `wrapLines`, `minLines`, `maxLines`, `height`, `width`, `autoResize`, `copyable` |

## Choice inputs

| `type` | Use | Props beyond the shared ones |
|---|---|---|
| [`select`](typescript/formComponents/string/select.md) | Dropdown, one value; for 4+ options | `options` (required), `searchable` (default false), `nothingFoundMessage` (default `No options found`) |
| [`suggest`](typescript/formComponents/string/suggest.md) | Autocomplete text; any typed value is accepted | `options`: strings or `{group, items}` of strings, never `{label, value}` objects; string validation |
| [`radio`](typescript/formComponents/string/radio.md) | One of 2–4 visible options | `options` (required), `orientation` (`horizontal`, the default, \| `vertical`) |
| [`buttonGroup`](typescript/formComponents/string/buttonGroup.md) | One choice shown as buttons, such as Approve / Reject | `options` (required): buttons `{value, label, variant, color, icon, disabled}` (`variant` default `outline`; `icon` is an image src) or `{group, items}`; `orientation` |
| [`multiSelect`](typescript/formComponents/array/multiSelect.md) | Dropdown, several values; submits an array of strings | `default` (array), `options`, `minLength`/`maxLength` (selections), `searchable`, `nothingFoundMessage`, `checkIconPosition` (`left` \| `right`) |
| [`multiCheckbox`](typescript/formComponents/array/multiCheckbox.md) | Checkboxes, several values; submits an array of strings | `default` (array), `options`, `minLength`/`maxLength`, `selectAllOption`, `selectAllOptionLabel`, `orientation` (default `horizontal`) |

A `buttonGroup` styles each option with `variant` and `color`:

```yaml
- key: decision
  type: buttonGroup
  label: Decision
  required: true
  options:
    - label: Approve
      value: approve
      variant: filled
      color: green
    - label: Reject
      value: reject
      variant: light
      color: red
```

## Number inputs

| `type` | Use | Props beyond the shared ones |
|---|---|---|
| [`number`](typescript/formComponents/number/number.md) | Numeric input | `variant` (`decimal`, the default, \| `integer`), `minimum`, `maximum`, `isExclusiveMinimum`, `isExclusiveMaximum`, `hideControls` |
| [`currency`](typescript/formComponents/number/currency.md) | Number formatted as money | the `number` props, `currencyPrefix` (default `$`) |
| [`percentage`](typescript/formComponents/number/percentage.md) | Percentage | the `number` props; `variant` `decimal` (the default: 50% submits `0.5`) \| `percentage` (submits `50`) |
| [`rating`](typescript/formComponents/number/rating.md) | Star rating | `maximum` (default 5), `fractions` (default 1: whole stars) |
| [`slider`](typescript/formComponents/number/slider.md) | Number between bounds | `minimum`, `maximum`, `step` (default 1), `marks` (`[{value, label}]`), `restrictToMarks` (default false) |

## Boolean inputs

| `type` | Use | Props beyond the shared ones |
|---|---|---|
| [`checkbox`](typescript/formComponents/boolean/checkbox.md) | Single boolean: terms acceptance, opt-in | `variant` (`filled`, the default, \| `outlined`), `color`, `inlineLabel` (default false), `labelPosition` (`left` \| `right`, the default) |
| [`switch`](typescript/formComponents/boolean/switch.md) | Toggle | `color`, `inlineLabel`, `labelPosition` |

## Date and time inputs

Values are ISO strings: a date (`'2026-07-24'`) or a datetime (`'2026-07-24T10:00:00.000Z'`); unquoted YAML dates are accepted. Range values are `{startDate, endDate}`.

| `type` | Use | Props beyond the shared ones |
|---|---|---|
| [`date`](typescript/formComponents/date/date.md) | Date picker (dropdown) | `minDate`, `maxDate`, `firstDayOfTheWeek` (0 Sunday … 6 Saturday; default 1), `highlightToday` (default true), `hideWeekdays`, `allowDeselect` (default false) |
| [`dateTime`](typescript/formComponents/date/dateTime.md) | Date and time | the `date` props except `allowDeselect`, plus `withSeconds` (default false) |
| [`time`](typescript/formComponents/date/time.md) | Time, 24-hour `HH:MM[:SS]` | `withSeconds`, `minTime`, `maxTime` |
| [`calendar`](typescript/formComponents/date/calendar.md) | Inline calendar | the `date` props, no `placeholder` |
| [`dateRange`](typescript/formComponents/date/dateRange.md) | Start and end date (dropdown) | `default: {startDate, endDate}`, `minDate`, `maxDate`, `firstDayOfTheWeek`, `highlightToday`, `hideWeekdays` |
| [`calendarRange`](typescript/formComponents/date/calendarRange.md) | Inline range calendar | the `dateRange` props, no `placeholder` |

Shared date-value type: [typescript/formComponents/date/dateValue.md](typescript/formComponents/date/dateValue.md).

## File inputs

| `type` | Use | Props beyond the shared ones |
|---|---|---|
| [`fileInput`](typescript/formComponents/file/fileInput.md) | File picker | `accept` (MIME types, comma-separated: `image/*,application/pdf`), `multiple`, `minLength`/`maxLength` (file count, with `multiple`), `maxFileSize` (bytes) |
| [`fileButton`](typescript/formComponents/file/fileButton.md) | Upload button | the `fileInput` props, `buttonText` (default `Upload file`), `buttonColor`, `buttonVariant` (default `outline`), `showUploadedFile` |
| [`fileDropzone`](typescript/formComponents/file/fileDropzone.md) | Drag-and-drop area | the `fileInput` props, `dropzoneText`, `dropzoneTextColor`, `dropzoneDescription`, `dropzoneDescriptionColor`, `showUploadedFile` (default true) |
| [`audioRecordingInput`](typescript/formComponents/file/audioRecording.md) | Record audio | `maxDuration` (seconds; unset records until the viewer stops), `mimeType` (`audio/webm`, the default, `audio/mpeg`, `audio/wav`, `audio/ogg`, `audio/aac`) |

## YAML and JSON inputs

| `type` | Use | Props beyond the shared ones |
|---|---|---|
| [`anyCodeInput`](typescript/formComponents/any/codeInput.md) | YAML or JSON editor; the text is parsed into an object | `default` (an object), `language` (`yaml` \| `json`), `wrapLines`, `minLines` (default 10), `maxLines`, `height`, `width`, `autoResize` (default true) |
| [`anyModal`](typescript/formComponents/any/modal.md) | The same editor in a modal | the `anyCodeInput` props, `openButtonText` (default `Edit`), `closeButtonText` (default `Close`), and `Color`, `Variant`, `Size` for each button (`openButtonColor`, …) |

## Nesting components

Exact types: [typescript/formComponents/form.md](typescript/formComponents/form.md). How nesting shapes the body: [interface-pages.md](interface-pages.md#layout-and-the-submitted-body).

| `type` | Use | Props beyond the shared ones |
|---|---|---|
| `section` | Group of related fields | `children` (required, array), `extendParentObject` (default false), `default` (object), `gap`, `sectionLabelOrder` (1–6), `sectionLabelColor`, `sectionDescriptionColor`, `sectionDividerColor`, `sectionDividerWeight` |
| `collapse` | Collapsible group | the `section` props without the divider ones, plus `defaultOpen` (default false) |
| `conditional` | Fields that depend on a select's value (no expression-based condition) | `conditionalField` (required, a `select`), `children` (required: a map from every option value to an array of components), `extendParentObject`, `default`, `gap` |
| `union` | One of several components, chosen with a select | `children` (required: a map from each choice to one component), `unionTypeOptions` (labels the choices; must list exactly the `children` keys; defaults to the keys), `default` |
| `arrayParent` | Repeatable entry; submits an array | `item` (required: the component repeated per entry, a `section` for several fields), `default` (array), `minItems`, `maxItems`, `uniqueItems`, `allowReorder` (default true), `gap`, `addButtonText` (default `Add Item`), `addButtonColor`, `addButtonVariant` |

Every `conditionalField` option needs a `children` entry and every entry an option, and no child may reuse the `conditionalField` key. Example: [interface-examples.md](interface-examples.md#conditional-fields).

```yaml
- key: contactMethod
  type: union
  label: Contact Method
  unionTypeOptions:
    - label: Email
      value: email
    - label: Phone
      value: phone
  children:
    email:
      key: email
      type: text
      label: Email Address
    phone:
      key: phone
      type: phoneNumber
      label: Phone Number
- key: items
  type: arrayParent
  label: Items
  addButtonText: Add an item
  item:
    key: item
    type: section
    children:
      - key: name
        type: text
        label: Item Name
      - key: quantity
        type: number
        label: Quantity
```

## Table

[`table`](typescript/formComponents/array/table.md) shows rows the viewer can edit, create or select. It submits the selected rows when `enableRowSelection` is on (prefill the selection with `default`), otherwise its rows (`data` with the viewer's edits). Example: [interface-examples.md](interface-examples.md#editable-table).

| Prop | Meaning |
|---|---|
| `data` | Required. The row objects |
| `columns` | Required. Each column: `header` and `key` (both required), `size` (pixels), `enableEditing`, `editVariant` (`text` \| `select` \| `multi-select`; the select variants need `editSelectOptions`), `filterVariant` (`text`, `checkbox`, `select`, `date-range`, `range`, …), `enableClickToCopy` |
| `enableEditing`, `editDisplayMode` | Edit rows; mode `modal`, `row`, `cell` or `table` |
| `enableCreate`, `createDisplayMode`, `createButtonText` | Add rows; mode `modal` (the default) or `row` |
| `enableRowSelection`, `enableMultiRowSelection` (default true), `selectDisplayMode` | Select rows (`checkbox`, `radio`, `switch`) |
| `columnSchema` | Column value types (`string`, `enum`, `number`, `integer`, `boolean`) that validate the submitted rows |
| `minLength`, `maxLength` | Row count |
| `initialState` | Initial filters, sorting, column order, sizes, visibility and pagination |

Sorting, filtering, grouping, pinning, pagination and toolbar switches (`enable*`, `position*`) are in the generated module.

## Display components

Display components take `key` and `type` but none of the input props, and submit nothing.

| `type` | Use | Props |
|---|---|---|
| [`header`](typescript/formComponents/display/header.md) | Title; `order` sets the hierarchy | `value` (required), `order` (1–6, default 1), `color`, `subtitle`, `subtitleColor`, `subtitleSize` (Mantine size or CSS size; default `xs`) |
| [`divider`](typescript/formComponents/display/divider.md) | Separator line | `text`, `textAlignment` (`left` \| `center`, the default, \| `right`), `color`, `weight` (default 1) |
| [`markdown`](typescript/formComponents/display/markdown.md) | Rich instructional content | `value` (required), `width`, `height`, `backgroundColor` |
| [`textDisplay`](typescript/formComponents/display/textDisplay.md) | Text, optionally copyable | `value` (required), `copyable`, `color`, `size`, `weight`, `italic`, `underline`, `strikethrough`, `transform`, `monospace` |
| [`codeViewer`](typescript/formComponents/display/code.md) | Read-only code | `value` (required), `language`, `width`, `height` |
| [`progress`](typescript/formComponents/display/progress.md) | Progress bar | `value` (required, 0–100), `steps`, `striped`, `animated`, `color`, `label`, `labelColor`, `labelSize`, `labelWeight`, `labelPosition`, `labelAlignment` |
| [`image`](typescript/formComponents/display/image.md) | Image | `src` (required: a URL or base64 content), `width`, `height` (default 100%), `borderColor`, `borderWidth`, `borderRadius` |
| [`pdfViewer`](typescript/formComponents/display/pdf.md) | PDF document | `src` (required, a URL), `width` (default 100%), `height` (default `500px`) |
| [`fileDownload`](typescript/formComponents/display/fileDownload.md) | Download button | `file` (required: a BIQFile, a `{name, mimeType, base64content}` object, or a URL), `buttonText` (default `Download`), `buttonColor`, `buttonVariant`, `buttonSize` |
| [`formButton`](typescript/formComponents/display/formButton.md) | Submit or reset button | `text` (default `Submit` or `Reset`), `actionType` (`submit`, the default, \| `reset`), `color`, `variant` (default `filled`), `size` |
| [`urlButton`](typescript/formComponents/display/urlButton.md) | Button that opens a URL | `url` (required), `text` (default `Open URL`), `openUrlInCurrentPage` (default false: a new tab), `color`, `variant` (default `outline`), `size` |
| `webViewer` | Embedded page or HTML | [webViewer](#webviewer) |

```yaml
- key: report
  type: fileDownload
  file: ${{ msg.report.downloadUrl }}
  buttonText: Download Report
```

## webViewer

Embeds a web page (`src`) or custom HTML (`html`) in an iframe inside the form. Set exactly one of `src` and `html`. Exact types: [typescript/formComponents/display/webViewer.md](typescript/formComponents/display/webViewer.md).

| Prop | Type | Default | Meaning |
|---|---|---|---|
| `src` | URL | — | Page to embed; supports expressions |
| `html` | string | — | HTML document to render |
| `width` | number \| string | `100%` | Viewer width |
| `height` | number \| string | `500px` | Viewer height |
| `fullScreen` | boolean | false | Fill the viewport and hide the other components |
| `allowedScriptDomains` | URL[] | — | Origins added to the CSP `script-src` |
| `allowedStyleDomains` | URL[] | — | Origins added to the CSP `style-src` (stylesheets only) |
| `allowInlineScripts` | boolean | false | Adds `'unsafe-inline'` to `script-src`, allowing any inline script and inline event handlers (`onclick=`). Reduces security |
| `allowInlineStyling` | boolean | false | Adds `'unsafe-inline'` to `style-src`, allowing `style="…"` attributes. Reduces security |
| `allowedPermissions` | string[] | — | Permissions-Policy directives to enable, such as `clipboard-write`, `fullscreen`, `camera`, `microphone`, `geolocation` ([all directives](typescript/actorSchemas/trigger/permissionsPolicy.md)) |

Rules for `html`:

- It runs under the app Content Security Policy: `<script>` and `<style>` blocks run, while inline event handlers, `style="…"` attributes and `eval` are blocked, external hosts need the allowlists above, and `fetch` reaches only the BorgIQ API. Modes, fixes and a CDN table: [app-trigger-actor.md](app-trigger-actor.md#content-security-policy).
- A `fetch` to a webhook URL (`<api>/msg/…`) of the same canvas gets an `X-App-Actor-Token` header automatically; set that trigger's `authorizationLevel` to `apps` ([webhook-trigger-actor.md](webhook-trigger-actor.md)).
- Style the HTML with the app theme library, [react-app-themes.md](react-app-themes.md). It is plain CSS (custom properties + component recipes), so it works in raw HTML with no React and no CDN: paste the Base Contract + one theme block (default `hearth`) into a `<style>` block and use Tabler icons as inline SVG with `stroke="currentColor"`.

```yaml
- key: preview
  type: webViewer
  height: 1000px
  src: ${{ msg.get_webpage_url.url }}
- key: help
  type: webViewer
  height: 200px
  html: |
    <!DOCTYPE html>
    <html>
    <head><style>.note { font: 14px sans-serif; }</style></head>
    <body>
      <p class="note" id="status">Not checked yet.</p>
      <button id="check">Check</button>
      <script>
        document.getElementById('check').addEventListener('click', function () {
          document.getElementById('status').textContent = 'Checked';
        });
      </script>
    </body>
    </html>
```
