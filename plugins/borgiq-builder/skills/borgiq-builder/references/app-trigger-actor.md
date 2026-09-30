# AppTriggerActor (legacy raw-HTML app) and app CSP

The AppTriggerActor serves a raw HTML/CSS/JS page, with no build step, in a sandboxed iframe. It is legacy: **new web
apps are ReactAppTriggerActor apps, built with the `borgiq-react-app-builder` skill.** Read this file to maintain an
existing AppTriggerActor app, and for the Content Security Policy of every sandboxed app surface: the legacy app, the
React app and the interface `webViewer`.

## Contents

- [Rules](#rules)
- [Configuration](#configuration)
- [Backend wiring](#backend-wiring)
- [Content Security Policy](#content-security-policy)
- [Thumbnail](#thumbnail)
- [Example](#example)

## Rules

1. Build new apps as ReactAppTriggerActor apps. Maintain an existing AppTriggerActor app here; do not rebuild it in
   React unless the user asks.
2. The actor emits no messages and has no form semantics (no `page`, `onSubmit` or submission data). A form is an
   InterfaceTriggerActor or InterfaceActor (the `borgiq-form-builder` skill); a page for anonymous visitors is hosted
   outside BorgIQ and calls a WebhookTriggerActor; a live feed is a React app tailing a stream (`useStreamTail`).
3. Reach backends by URL, never by edges (an edge cannot target a trigger): pass the trigger's URL in through
   `inputs` and `fetch` it.
4. Set every backend trigger to `authorizationLevel: apps`, so only calls carrying a viewer's app token fire it.
   `public` accepts anyone.
5. Give each resource or route its own trigger; do not branch one endpoint on an `action` parameter. CRUD and lookups
   go to a webhook-enabled UniversalTriggerActor that answers from its own code; AI, integrations and routing go to a
   WebhookTriggerActor feeding task actors and a WebhookResponseActor. Pipelines may share an actor (audit logging)
   through edges. See the hub's
   [Universal Trigger vs Webhook Trigger](../SKILL.md#universal-trigger-vs-webhook-trigger-http-endpoints).
6. Style the page with the app theme library: paste the Base Contract and one theme block (default `hearth`) from
   [react-app-themes.md](react-app-themes.md) into `css`, and use Tabler icons as inline SVG with
   `stroke="currentColor"`. No CDN fonts or CSS framework unless the user asks.
7. Upload files as multipart `FormData`, never as base64 in JSON.
8. Write code that runs under the strict [Content Security Policy](#content-security-policy): no inline event
   handlers, `style="…"` attributes or `eval`.

## Configuration

Exact schema: [typescript/actorSchemas/trigger/app.md](typescript/actorSchemas/trigger/app.md).

| Option | Type | Default | Meaning |
|---|---|---|---|
| `html` | string or BIQFile | required | The page: a full document, or a fragment the server wraps in one |
| `css` | string or BIQFile | — | Served as a same-origin stylesheet, linked at the end of `<head>` |
| `script` | string or BIQFile | — | Served as a same-origin script, loaded before `</body>` |
| `allowedScriptDomains`, `allowedStyleDomains` | string[] | `[]` | CSP allowlists, see [Domain allowlists](#domain-allowlists) |
| `allowInlineScripts`, `allowInlineStyling` | boolean | `false` | CSP relaxations, see [Modes](#modes) |
| `allowedPermissions` | string[] | `[]` | Browser features, see [Browser permissions](#browser-permissions) |

- Put everything in `html` (inline `<style>` and `<script>` blocks run: the server hashes them), or split it into
  `html`, `css` and `script`, which suits larger apps and lets each field be a BIQFile.
- A BIQFile field is the file object (`id`, `fileName`, `mimeType`, …; [schema](typescript/schemas/file.md)), not a
  string. The server downloads its text when it serves the page.
- Options are interpolated: `const API_URL = '${{ inputs.apiURL }}';` inside `script` reads an input.

## Backend wiring

Pass each trigger's URL as an input. A WebhookTriggerActor's URL is `${{ ctx.canvas.webhookTriggers.<msgVar>.url }}`;
a UniversalTriggerActor's (with `configuration.webhook.enabled: true`) is
`${{ ctx.canvas.universalTriggers.<msgVar>.url }}`. Several resources mean several inputs (`usersAPI`, `ticketsAPI`).

**The app token.** The server injects a script that adds the viewer's `X-App-Actor-Token` header to every `fetch` whose
URL is a **string** starting with the BorgIQ webhook prefix (`…/msg/`). An `apps` trigger accepts that token when it
is on the same canvas as the app, and the request's `meta.user` then names the viewer. `XMLHttpRequest`, and
`fetch` given a `URL` or `Request` object, get no token.

**The trigger.** Static fields in `configuration.webhook`, response behavior in `configuration.options.webhook`:

```yaml
configuration:
  webhook:
    triggerKey: 01KD298E3VRBDAZN9X5ETV4R6G   # borgiq generate id webhooktriggerkey
    authorizationLevel: apps
    allowedMethods: [get, post]
  options:
    webhook:
      respondImmediately: false             # a downstream actor answers
```

**The answer.** With `respondImmediately: false`, end the flow in a WebhookResponseActor with
`headers: { content-type: application/json }` and `body: ${{ msg.<task>.<field> }}`, or return
`Signal.webhookRespond({...})` from a code actor or the UniversalTriggerActor itself. With `respondImmediately: true`
the trigger answers at once, from a `response` template that may compute the body from `trigger.request` and `ctx`.
Both are in [webhook-trigger-actor.md → Response Modes](webhook-trigger-actor.md#response-modes).

**Files.** Send `FormData` and do not set `Content-Type` (the browser adds the boundary). On a POST or PUT, each file
part reaches the trigger's `body` as a BIQFile under its field name (`msg.<trigger>.body.file`); pass it to a code
actor as an input and open it with `mountFile()`.

**In the page,** check `response.ok` on every call, and show a loading state and a readable error.

## Content Security Policy

The policy of every sandboxed app page, sent by the server with each page. The options relax it.

| Surface | Where the options live |
|---|---|
| AppTriggerActor | `configuration.options` |
| ReactAppTriggerActor | `configuration.options`. `${{ }}` is allowed; they are resolved at Build and frozen into the build, so a change needs a rebuild |
| Interface `webViewer` with `html` | the component itself. A `webViewer` with `src` frames that URL under its own policy |

### Modes

| Mode | Set | Adds | What runs |
|---|---|---|---|
| Strict (default) | neither flag | `script-src`/`style-src` `'self'`, a SHA-256 hash of each inline block, the allowlists | `<script>` and `<style>` blocks in the served HTML (the server hashes each), same-origin files, allowlisted hosts |
| Inline scripts | `allowInlineScripts: true` | `'unsafe-inline'` in `script-src` and `script-src-attr` | also inline event handlers (`onclick`) and scripts added at runtime |
| Inline styling | `allowInlineStyling: true` | `'unsafe-inline'` in `style-src` and `style-src-attr` | also `style="…"` attributes and styles injected at runtime |

`eval()`, `new Function()` and string timers are blocked in every mode; no option allows them.

What strict mode blocks, and the fix that works in every mode:

| Blocked | Example | Instead |
|---|---|---|
| Inline event handler | `<button onclick="save()">` | `addEventListener('click', save)` in a `<script>` block, or `allowInlineScripts` |
| `javascript:` URL | `<a href="javascript:void(0)">` | a click listener |
| `style` attribute | `<div style="display:flex">`, `setAttribute('style', …)`, `el.style.cssText = …` | a class in the stylesheet, or `allowInlineStyling` |
| Style or script added at runtime | libraries that inject `<style>` (the Tailwind Play CDN, older jQuery UI) | a CSS-file alternative, or `allowInlineStyling` |
| Runtime code compilation | `eval(code)`; standard Alpine.js and Petite Vue, which compile expressions with `new Function` | plain DOM code, or Alpine's CSP build |

Setting a single style property from script (`el.style.display = 'none'`) is not blocked in any mode; toggling a class
(`el.classList.add('hidden')`) keeps styling in the stylesheet.

**Fixed directives.** `connect-src` is `'self'` plus the BorgIQ API, so `fetch` reaches only BorgIQ: call third-party
APIs through a trigger. It also covers a CDN script's source map (`.map`, common on jsDelivr), which then fails with a
console warning only; cdnjs builds usually avoid it. `img-src` allows `'self'`, `data:`, `blob:` and any HTTPS host; `font-src`
allows `'self'`, `data:` and any HTTPS host. Only the BorgIQ web app may frame the page (`frame-ancestors`).

### Domain allowlists

External scripts and stylesheets are blocked in every mode until their host is listed.

- `allowedScriptDomains` feeds `script-src`; `allowedStyleDomains` feeds `style-src` (stylesheets only: font files are
  covered by `font-src`). The two lists are separate.
- Give `https://` origins: `https://cdn.example.com`, not `cdn.example.com`. A path is cut to its origin. An entry
  that is not a URL, a CSP keyword or `blob:`/`data:` is dropped (a `webViewer` rejects a non-URL at save).
- `https://cdn.tailwindcss.com` is always in `style-src`.
- A themed app loads no fonts or styles from a CDN ([react-app-themes.md](react-app-themes.md)).

| Library | `allowedStyleDomains` | `allowedScriptDomains` |
|---|---|---|
| Google Fonts | `https://fonts.googleapis.com` | — |
| Tailwind CSS | `https://cdn.jsdelivr.net` or `https://cdn.tailwindcss.com` | the same |
| Chart.js, Alpine.js (CSP build) | — | `https://cdn.jsdelivr.net` |
| Bootstrap | `https://cdn.jsdelivr.net` | `https://cdn.jsdelivr.net` |
| Font Awesome | `https://cdnjs.cloudflare.com` | — |
| React (CDN) | — | `https://unpkg.com`, `https://cdn.jsdelivr.net` |
| HTMX | — | `https://unpkg.com` |

Libraries that suit the policy: Chart.js, ApexCharts, HTMX, Day.js, DOMPurify, Animate.css or CSS transitions.

### WebAssembly and workers (React apps only)

`ReactAppTriggerActor` has two further opt-ins; the legacy AppTriggerActor and `webViewer` do not. Both are frozen into
the build, and neither widens the allowlists.

| Option | CSP change | What's allowed |
|---|---|---|
| `allowWebAssembly: true` | `script-src … 'wasm-unsafe-eval'` | `WebAssembly.compile` / `instantiate`. JavaScript `eval()` / `new Function()` stay blocked |
| `allowBlobWorkers: true` | `worker-src 'self' blob:` | Web Workers started from `blob:` URLs, i.e. Vite `?worker&inline` workers (the single-JS build rule rules out separate worker files) |
| both | both | A blob worker inherits the app's CSP, so it can compile WebAssembly only when both are on |

`connect-src` does not change, so serve a `.wasm` or database file as a same-origin app asset.

### Browser permissions

`allowedPermissions` grants browser features, each sent as `Permissions-Policy: <directive>=(self)`, e.g.
`[clipboard-write, clipboard-read]`. Directives: `accelerometer`, `ambient-light-sensor`, `autoplay`, `battery`,
`camera`, `clipboard-read`, `clipboard-write`, `display-capture`, `encrypted-media`, `fullscreen`, `geolocation`,
`gyroscope`, `magnetometer`, `microphone`, `midi`, `payment`, `picture-in-picture`, `publickey-credentials-get`,
`screen-wake-lock`, `usb`, `web-share`, `xr-spatial-tracking`
([schema](typescript/actorSchemas/trigger/permissionsPolicy.md)).

## Thumbnail

An AppTriggerActor carries a thumbnail like a React app: see [app-thumbnail.md](app-thumbnail.md).

## Example

A task list backed by a webhook-enabled UniversalTriggerActor, msgVar `tasks_api`, whose code lists and adds tasks and
answers with `Signal.webhookRespond` ([universal-trigger-actor.md](universal-trigger-actor.md)). The app actor:

```yaml
ACTR01kd298z8kq4yd67m5pddd9cyp:
  type: AppTriggerActor
  version: 1
  name: Task Tracker
  msgVar: task_tracker
  isActive: true
  continueOnError: false
  enableLTM: false
  enableSTM: false
  sourcePorts:
    - id: SPRTdefault
  configuration:
    inputs:
      apiURL: ${{ ctx.canvas.universalTriggers.tasks_api.url }}
    options:
      html: |
        <!DOCTYPE html>
        <html>
        <head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"></head>
        <body>
          <form id="add"><input id="task" required><button class="btn btn-primary">Add task</button></form>
          <ul id="list"></ul>
        </body>
        </html>
      css: |
        /* Base Contract + the hearth block from react-app-themes.md */
      script: |
        const API_URL = '${{ inputs.apiURL }}';
        async function load() {
          const res = await fetch(API_URL);
          if (!res.ok) return;
          const { tasks } = await res.json();
          const list = document.getElementById('list');
          list.replaceChildren(...tasks.map((t) => Object.assign(document.createElement('li'), { textContent: t })));
        }
        document.getElementById('add').addEventListener('submit', async (e) => {
          e.preventDefault();
          const input = document.getElementById('task');
          await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ task: input.value }),
          });
          input.value = '';
          load();
        });
        load();
  schemas: {}
  id: ACTR01kd298z8kq4yd67m5pddd9cyp
  position: { x: 0, 'y': 0 }
  edges: {}
```

The trigger sets `webhook: { enabled: true, triggerKey: …, authorizationLevel: apps, allowedMethods: [get, post] }`
and branches on `req.trigger.request.method`.
