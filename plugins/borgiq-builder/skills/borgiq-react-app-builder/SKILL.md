---
name: borgiq-react-app-builder
description: Build custom app UIs on a BorgIQ canvas with a React (Vite + TypeScript) app inside a ReactAppTriggerActor — compiled server-side, served in a sandboxed iframe. This is the standard surface for dashboards, data explorers, SPAs, and any bespoke frontend; it also covers maintaining legacy raw-HTML AppTriggerActor apps. Forms and data-entry pages stay in `borgiq-form-builder`. Triggers on "ReactAppTriggerActor", "React app in BorgIQ", "build a web app", "custom dashboard", "single-page app", "data explorer UI", "AppTriggerActor", "vite", "useEndpoint", "useGetSession", "react SPA on a canvas", "multi-file app", "tsx component app", "app theme", "hearth theme", "consistent app styling".
---

# BorgIQ React App Builder

Build a **React SPA** inside a **ReactAppTriggerActor** — the standard surface for custom app UIs on a canvas. The actor holds a real Vite + TypeScript project that BorgIQ **compiles server-side** (`deno install` + `deno task build`) and serves as static `dist/` assets in a sandboxed iframe with a short-lived content token.

A data-entry form belongs in `borgiq-form-builder`. The legacy raw-HTML **AppTriggerActor** (no build step) remains supported for maintaining existing apps — its configuration is documented in the hub's [`app-trigger-actor.md`](../borgiq-builder/references/app-trigger-actor.md) and [`web-application-pattern.md`](../borgiq-builder/references/web-application-pattern.md) references, and it uses the same theme library — but new apps are built here.

## Mental model

Two edit surfaces, one actor:

- **`configuration.codeDir`** — the React/TypeScript source: a plain array of `{ path, content }` files (`package.json`, `vite.config.ts`, `index.html`, `src/**`). **Never interpolated** — so JSX containing `${{ ... }}` is safe literal text, and user source can't smuggle `${{ credentials.* }}` exfiltration. Text only.
- **`configuration.options.files`** — an overlay of asset-backed or templated files, applied onto the project at build time. These **are** interpolated — with this actor's **full** expression scope (`assets`, `vars`, `credentials`, `secrets`, `ctx`), not just assets — so `content: ${{ assets.<key> }}` resolves an uploaded asset into a real binary (a BIQFile — images, fonts). Overlay files **win over `codeDir`** on a path collision. This is how binaries get into the build (codeDir is text-only). **⚠ Never interpolate a secret into an overlay's `content`**: the resolved value is bundled into the client-served `dist/` output (browser-visible JavaScript), so `${{ credentials.* }}` / `${{ secrets.* }}` in an overlay leaks the secret to every visitor. Keep secrets server-side behind a webhook backend and pass the browser only what it may see.

**Build → serve.** A ReactAppTriggerActor does nothing until you **Build** it: the build compiles the project and persists every `dist/` file as a durable artifact. **Serving requires a successful build** — a fresh actor returns `409 No build available` until you build. Rendering then uses the same sandboxed iframe, `frame-ancestors` restriction, and origin-checked short-lived content token as AppTriggerActor. Rebuild after every source change to publish it.

**Calling backends.** The app talks to backends the web-application-pattern way: declare **endpoints** on the actor targeting a **webhook-capable trigger** (a **WebhookTriggerActor**, or a **UniversalTriggerActor** with its webhook source enabled), and call them by name with the `@borgiq/actors` SDK (`useEndpoint`/`callEndpoint`). Endpoints are **resolved and baked into the built artifact at Build time**, and the SDK attaches the `X-App-Actor-Token` to **its own fetches only** — a raw `fetch()` to a `/msg/` URL is **not** token-bridged, so always call through the SDK. Because endpoints are frozen into the build, **editing the endpoint list takes effect on the next Build**, not the next save.

## Key decisions

1. **App vs. form.** Custom app UI (dashboard, data explorer, SPA, bespoke frontend) → ReactAppTriggerActor, here. A form/survey/data-entry page → `borgiq-form-builder`. An existing raw-HTML AppTriggerActor app → maintain it via the hub's `app-trigger-actor.md` reference; don't rebuild it in React unless the customer asks.
2. **codeDir (source) vs. options.files (overlay).** Author all `.tsx/.ts/.css/.html/.json` in `codeDir`. Use `options.files` **only** for (a) binaries via `${{ assets.<key> }}`, or (b) a file whose content must be templated at build from **non-secret** values (e.g. `${{ vars.* }}`). **Never** put `${{ credentials.* }}` / `${{ secrets.* }}` in an overlay — the resolved value ships to the browser in the built `dist/`. Remember overlay wins on collision.
3. **Endpoints + `authorizationLevel: 'apps'`.** Every backend call pairs an endpoint with a webhook-capable trigger — a `WebhookTriggerActor`, or a `UniversalTriggerActor` with its webhook source enabled — set to `authorizationLevel: 'apps'` (only tokened app calls fire it). A WebhookTriggerActor replies via downstream actors → a **WebhookResponseActor**; a UniversalTriggerActor can instead reply from its own `receive` code (`Signal.webhookRespond`) with no downstream chain — choose per route, see [Designing the backend — endpoint-first](#designing-the-backend--endpoint-first). `'public'` webhooks skip token verification entirely — only use them for genuinely public endpoints.
4. **Endpoints are the authorization grant — per app-actor, frozen at Build.** An app can fire **only** the webhooks it declares as endpoints: the webhook allowlist is baked into the build manifest, so the API returns `401` for any undeclared webhook — even one on the same canvas (and `401` until the app is built at all). Leave an endpoint's workspace/canvas blank to target a webhook on **this** canvas (the common case), or set them (by **slug**) to target another canvas/workspace **in the same org** (org is the hard boundary). Endpoint edits — including a target's `triggerKey` — take effect on the **next Build**, not the next save.
5. **Every app ships a theme — no exceptions.** Create `src/theme.css` (Base Contract + exactly one theme block from [react-app-themes.md](../borgiq-builder/references/react-app-themes.md)) and import it first in `src/main.tsx`. **Default to the `hearth` theme** unless the customer names one of the five themes (`hearth`, `ledger`, `meridian`, `signal`, `bloom`) or supplies brand colors (then apply the reference's brand-override procedure). Components use only the theme's tokens — never literal colors, fonts, radii, or shadows. An app with hard-coded styling or no `theme.css` is incomplete; fix it before Build.
6. **Keep `vite.config.ts`'s single-file build settings.** `base: './'`, `cssCodeSplit: false`, `rollupOptions.output.inlineDynamicImports: true`, and the stable hash-free `output` file names are what guarantee the required **one JS, at most one CSS, and `index.html`** dist shape (the builder rejects anything else). Assets are served **same-origin, piped through the API** (no 302-to-S3), so no `renderBuiltUrl`/`__BIQ_ASSET_BASE__` rebasing is needed.

## Anatomy of a ReactAppTriggerActor

```yaml
ACTR01reactapp:
  type: ReactAppTriggerActor
  configuration:
    # ---- SOURCE (never interpolated; text only) --------------------------------
    codeDir:
      - path: package.json
        content: |
          {
            "name": "my-app", "private": true, "type": "module",
            "scripts": { "build": "tsc -b && vite build" },
            "dependencies": {
              "react": "^19", "react-dom": "^19",
              "@borgiq/actors": "file:./__borgiq_sdk_placeholder__"
            },
            "devDependencies": {
              "typescript": "^5", "vite": "^7", "@vitejs/plugin-react": "^5"
            }
          }
      - path: vite.config.ts
        content: |
          import { defineConfig } from 'vite'
          import react from '@vitejs/plugin-react'
          export default defineConfig({
            base: './',                       // REQUIRED: relative asset paths under the token root
            plugins: [react()],
            resolve: { dedupe: ['react', 'react-dom'] },
            build: {
              cssCodeSplit: false,            // REQUIRED: merge all CSS into one file
              assetsInlineLimit: 0,           // REQUIRED: emit real asset files, never base64-inline
              rollupOptions: {
                output: {
                  inlineDynamicImports: true, // REQUIRED: fold dynamic imports into one JS chunk
                  entryFileNames: 'assets/[name].js',   // stable, hash-free names
                  chunkFileNames: 'assets/[name].js',
                  assetFileNames: 'assets/[name][extname]',
                },
              },
            },
          })
      - path: index.html
        content: |
          <!doctype html>
          <html><head><meta charset="UTF-8" /><title>My App</title></head>
          <body><div id="root"></div><script type="module" src="/src/main.tsx"></script></body></html>
      - path: src/main.tsx
        content: |
          import { StrictMode } from 'react'
          import { createRoot } from 'react-dom/client'
          import './theme.css'                     // REQUIRED: theme import comes before App
          import App from './App.tsx'
          createRoot(document.getElementById('root')!).render(<StrictMode><App /></StrictMode>)
      - path: src/theme.css
        content: |
          /* REQUIRED in every app: Base Contract + exactly ONE theme block, both
             copied verbatim from references/react-app-themes.md (hub skill).
             Default theme: hearth — use it unless the customer names another
             theme or supplies brand colors. Never author components with literal
             colors/fonts/radii; use the tokens this file defines. */
      - path: src/App.tsx
        content: |
          import { useEndpoint, useGetSession } from '@borgiq/actors'
          export default function App() {
            // Who is viewing the app: { id, userId, email, name, appSessionId }. Passive — resolves on mount, no trigger().
            // Null outside the BorgIQ iframe (local dev), so gate identity UI on it.
            const { data: session } = useGetSession()
            // browser-fetch semantics: search (query) + init (method/headers/body/signal). body passes through.
            const { trigger, loading, error, data } = useEndpoint('saveRecord', undefined, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ hi: 1 }),
            })
            return (
              <main>
                <h1>My App</h1>
                {session && <p>Signed in as {session.name || session.email}</p>}
                <button disabled={loading} onClick={() => { void trigger().catch(() => {}) }}>
                  {loading ? 'Saving…' : 'Save'}
                </button>
                {error && <p>{error.message}</p>}
                {data != null && <pre>{JSON.stringify(data, null, 2)}</pre>}
              </main>
            )
          }
    # ---- OPTIONS (interpolated overlays + wiring) ------------------------------
    options:
      files:
        - path: src/assets/logo.png               # NOT public/ — import it from source (see note below)
          content: ${{ assets.company_logo }}     # binary from an uploaded asset (BIQFile)
      endpoints:
        - name: saveRecord                          # <- useEndpoint('saveRecord')
          actorId: ACTR01webhookhandler…            # a WebhookTriggerActor (or webhook-enabled UniversalTriggerActor), authorizationLevel: 'apps'
          # workspaceSlug / canvasSlug: optional, SLUGS, blank = this canvas; same org only
      allowedScriptDomains: []                    # ${{ vars.cdn_host }} works here — evaluated at build
      allowedStyleDomains: []
      allowedPermissions: []
```

Pair it with a backend (standard web-application pattern — the hub wires the edges):

```yaml
ACTR01webhookhandler:
  type: WebhookTriggerActor
  configuration:
    webhook:
      triggerKey: save-record
      authorizationLevel: apps          # only tokened app calls fire this
# … edges: webhook -> (task actors) -> WebhookResponseActor (returns JSON to trigger())
```

## Designing the backend — endpoint-first

Design the backend **endpoint-first**, not actor-first:

1. **List the UI actions.** Walk the frontend and enumerate every distinct thing it calls the backend for — `listTasks`, `createTask`, `deleteTask`, `summarizeWithAI`, etc. Each becomes one declared endpoint on the actor.
2. **Choose the trigger per endpoint** (see the hub's [Universal Trigger vs Webhook Trigger](../borgiq-builder/SKILL.md#universal-trigger-vs-webhook-trigger-http-endpoints) matrix). Decide route by route — a single app commonly mixes both:
   - **CRUD / storage endpoints** (list, get, create, update, delete a Collection item) → a **webhook-enabled UniversalTriggerActor** at `authorizationLevel: 'apps'`. Parsing, validation, the Collection call, and the JSON reply (`Signal.webhookRespond`, with `options.webhook.respondImmediately: false`) all live in the trigger's `receive` code. No downstream actors.
   - **AI / generation endpoints** (summarize, draft, classify, call a third-party API) → a **WebhookTriggerActor** at `authorizationLevel: 'apps'` feeding task actors and a **WebhookResponseActor**. The route needs an AiActor / integration actor / router, so it enters a real flow.
3. **Declare one endpoint per route** in the actor's `endpoints:` list and call each by name with `useEndpoint`/`callEndpoint`. Don't funnel the whole app through a single endpoint that branches on a `?action=` query param — separate endpoints keep latency, response shape, and orchestration independent per route, and since the endpoint list is the app's authorization grant, the allowlist stays explicit.

This keeps fast CRUD routes off the AI critical path and avoids cramming AI/integration logic into trigger code just to save an actor — or the reverse, spinning up a multi-actor flow for a route one trigger's code handles fine.

**If the app is backed by Collections, use ONE collection for the whole app and ship a migration actor with it.** Model every entity type the app stores in a single collection with key prefixes (`task:<id>`, `user:<id>`, `config:<name>`) plus a `$meta` manifest row that lists those prefixes — never one collection per entity type; split only for a security boundary or an explicit user request (see [single-collection design](../borgiq-builder/references/collection-api.md#single-collection-design)). Collections aren't implicit — endpoints fail with `COLLECTION_NOT_FOUND` until the collection is created. Add an idempotent provisioning step (create the app's collection + seed defaults, safe to re-run per workspace/deploy) before the app goes live. See the hub's [Collection migrations and provisioning](../borgiq-builder/SKILL.md#collection-migrations-and-provisioning) and [collection-migrations.md](../borgiq-builder/references/collection-migrations.md).

## Calling endpoints — the `@borgiq/actors` SDK

The SDK ships with every React app (injected as a `file:` dep). Endpoints are baked into the built
artifact and the `X-App-Actor-Token` is attached to **SDK fetches only** — a raw `fetch()` to a `/msg/`
URL is **not** token-bridged, so always call through the SDK. The surface follows **browser `fetch`**:

```tsx
import { useEndpoint, callEndpoint } from '@borgiq/actors'

// Hook form — request state included. Does NOT auto-fetch; call trigger() to fire.
//   useEndpoint(name, search?, init?)
//   - search: appended to the endpoint URL's query (string | URLSearchParams | Record<string,string>)
//   - init:   RequestInit subset (method, headers, body, signal); body passes through untouched
//             (URLSearchParams → form-encoded, FormData → multipart, string/Blob as-is)
const { trigger, loading, error, data } = useEndpoint('saveRecord', '?page=1', {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: new URLSearchParams({ name: 'Ada' }),
})
await trigger()                          // resolves with the parsed response body (JSON or text)
await trigger({ body: JSON.stringify({ name: 'Bob' }), headers: { 'Content-Type': 'application/json' } }) // per-call override

// Non-hook form — anywhere (event handlers, effects, non-component code):
const result = await callEndpoint('saveRecord', '?page=1', { method: 'POST', body: new URLSearchParams({ name: 'Ada' }) })
```

- `getBasename()` → router basename for the token path (from `document.baseURI`; feed it to a React Router `basename`).
- Non-2xx → `EndpointHttpError` (carries `status` + parsed `body`). The body resolves as JSON when the content-type says so, else text.
- Errors thrown: `EndpointNotFoundError` (name not declared), `EndpointResolutionError` (the endpoint baked an `{ error }` because the target couldn't be resolved at Build), `EndpointHttpError` (non-2xx), `TokenTimeoutError`, `SessionUnavailableError` (see below).
- Each declared endpoint should point at a webhook-capable trigger — a `WebhookTrigger`, or a `UniversalTrigger` with its webhook source enabled — at `authorizationLevel: 'apps'`, wired `→ … → WebhookResponse`.

### Who is viewing the app — `useGetSession`

```tsx
import { useGetSession, getSession } from '@borgiq/actors'

// Hook form — passive data, resolved on mount. Unlike useEndpoint there is NO trigger().
const { data: session, loading, error } = useGetSession()
if (session) return <p>Hello, {session.name || session.email}</p>

// Non-hook form — parity with callEndpoint; rejects instead of returning an error state.
const viewer = await getSession()   // { id, userId, email, name, appSessionId }
```

- Resolves the **signed-in viewer** as `{ id, userId, email, name, appSessionId }` — the same identity flows behind the endpoints see at `trigger.user`. `userId` is an alias of `id`; prefer it in new code, since it cannot be confused with `appSessionId`. `name` may be `''`; `data` is `null` until it resolves and on error.
- **`appSessionId` identifies the visit, not the person: one id per (BorgIQ login × this app).** It is stable across page reloads and token refreshes, a different app under the same login gets a different id, and a new BorgIQ login gets a new one. Use it to key per-visit state — a draft, a wizard position, a chat thread, a scoped cache — typically as a collection key, with `userId` alongside when the data belongs to the person rather than the visit. Two consequences worth knowing before they surprise you: **multiple tabs of the same app share one id** (derive your own per-tab suffix if you need tab identity), and **a new login is a new id** — including a session handoff, so per-visit state does not follow the viewer across logins.
- `appSessionId` may be **absent** (older tokens predate it) — treat absence as "no session information" and degrade gracefully, never crash.
- Decoded from the app token the SDK already holds, so it costs **no extra request** and needs no configuration. The result is cached for the login: a profile rename shows the old `name` until reload, but a re-login in the parent (even without a reload) refreshes the session on the next read.
- Outside the BorgIQ iframe there is no viewer — under a local `npm run dev` it settles **immediately** with `SessionUnavailableError` rather than waiting on the token bridge. Gate identity UI on `session` so the page still renders locally.
- **Do not use it as an authorization check — and `appSessionId` is not an authorization token.** Both are display-level identity; enforce access on the canvas side (`authorizationLevel: 'apps'` endpoints + per-app grants), where `trigger.user` is server-attested. Flows must trust `trigger.user.appSessionId` and never a session id arriving in a request body or query string — the first was lifted from a signature-verified token, the second is whatever the caller typed.

## Theming — required on every app

Full token sets, base stylesheet, component recipes, and rules live in
[react-app-themes.md](../borgiq-builder/references/react-app-themes.md). The short version:

- **Always create `src/theme.css`** = the reference's Base Contract + exactly one theme block, imported **first** in `src/main.tsx`. Never skip this, even for a "quick" app — an unthemed app is a bug.
- **Default: `hearth`** (the BorgIQ house look). Use it whenever the customer doesn't name a theme or supply a brand.
- Customer picks by name or genre: `hearth` (internal tools, default) · `ledger` (finance/ops, paper + pine + serif) · `meridian` (enterprise data, slate + cobalt) · `signal` (monitoring, dark-first graphite + amber) · `bloom` (portals/surveys, blush + plum, rounded).
- Components use **tokens only** (`--bg`, `--surface-*`, `--text-1/2/3`, `--accent`, `--ink`/`--ivory`, `--space-*`, `--radius-*`) and the reference's component recipes. No literal colors, fonts, radii, or shadows in components.
- Light + dark come free: every theme block carries both modes wired to `prefers-color-scheme` with `data-theme` overrides.
- **Icons: Tabler only** (`@tabler/icons-react`), planned as part of the UI design — nav items, action buttons, empty states — per the reference's Icons section. Icons inherit `currentColor` (never hard-code an icon color); keep one size/stroke per context; icon-only buttons need `aria-label`; no emoji-as-icons and no second icon family.
- Customer brand colors → start from the closest theme and remap only the accent/ink token group per the reference's brand-override procedure; neutrals, status channels, and shape stay.
- Do not confuse with [themes.md](../borgiq-builder/references/themes.md) (presentation/marketing palettes) — React apps use the token library above.

## Constraints

| Constraint | Limit / rule |
|---|---|
| `codeDir` file count | ≤ 200 files |
| `codeDir` total size | ≤ 1 MiB (1,048,576 bytes; text only — no binaries) |
| Binaries (images, fonts) | overlay them under `src/assets/…` via `options.files` + `${{ assets.<key> }}`, then **import** from source (`import logo from './assets/logo.png'` → `<img src={logo} />`). **Do not use `public/`** — Vite serves `public/` verbatim (never `import`ed), and a `public/` asset needs a `import.meta.env.BASE_URL`-prefixed URL to resolve under the token base path. Max 50 overlay files |
| Endpoints | ≤ 50 per actor; an app fires **only** its declared endpoints, frozen into the build (undeclared ⇒ `401`; unbuilt ⇒ `401`) |
| Endpoint `name` | a valid identifier — letters, digits, underscore, not starting with a digit (it's the `useEndpoint('<name>')` key) |
| Build output shape | **exactly one `.js`, at most one `.css`, and `index.html`** — the builder rejects a multi-file build with an actionable message. Keep the `vite.config.ts` single-file settings |
| Theming | **every app ships `src/theme.css`** (Base Contract + one theme block from [react-app-themes.md](../borgiq-builder/references/react-app-themes.md)), imported first in `main.tsx`; default theme `hearth`; components use tokens only — no literal colors/fonts/radii |
| Build output size | ≤ 100 MB total; ≤ 50 `dist` files (static assets — a single-JS/single-CSS build leaves plenty) |
| CSP / permissions options | **interpolatable, evaluated at build time** — `${{ }}` in the five security options (`allowedScriptDomains`, `allowedStyleDomains`, `allowInlineScripts`, `allowInlineStyling`, `allowedPermissions`) is resolved by the build and frozen into the manifest; a `${{ vars.* }}` change takes effect on the **next Build**, not the next page load |
| Endpoint options | **interpolatable** — `${{ }}` is allowed in `endpoints` string fields (`actorId`/`workspaceSlug`/`canvasSlug`), resolved at Build; an unresolvable target bakes an `{ error }` that makes `useEndpoint` throw `EndpointResolutionError` by name |
| `vite.config.ts` | must keep `base: './'`, `cssCodeSplit: false`, `inlineDynamicImports: true`, and the stable hash-free `output` names |
| Serving | dist assets are **piped same-origin through the API** (no 302-to-S3, no S3 origin in the CSP) |
| npm packages | installed, but **postinstall scripts do not run** (unsupported) |
| Token TTL / late asset fetch | the content token is short-lived (~2 minutes) and scopes the served assets; assets are cacheable but not immutable. Prefer eager imports; a `React.lazy` chunk isn't possible anyway (dynamic imports fold into the single JS) |
| Serve before build | returns `409` — you must Build first, and rebuild after every source edit or endpoint change |

## Workflow

1. **Create** the actor from the template (drag `ReactAppTriggerActor` onto a canvas — the file tree pre-seeds with a working Vite scaffold).
2. **Edit** files in the full-page React editor (file tree + code editor) or via the `borgiq` CLI. Create `src/theme.css` from [react-app-themes.md](../borgiq-builder/references/react-app-themes.md) (default `hearth`) before writing components. Declare **endpoints** in the options form (or YAML) and asset overlays under `options.files`.
3. **Build** — the editor's Build button, or `POST /v1/orgs/{org}/workspaces/{wsp}/canvases/{canvas}/apps/{actorId}/build`. Watch the status badge; on failure the editor surfaces the build error.
4. **Open** the running app at `/org/{org}/w/{wsp}/c/{canvas}/apps/{actorId}`.

## Boundaries with the hub and sibling skills

- **Wiring is the hub's job.** `borgiq-builder` owns edges, msgVars, IDs, and connecting the WebhookTrigger → task actors → WebhookResponse chain your endpoints target. Ask it to build the backend flow.
- **Forms/interface pages → `borgiq-form-builder`.** Legacy raw-HTML AppTriggerActor apps are maintained via the hub's [`app-trigger-actor.md`](../borgiq-builder/references/app-trigger-actor.md) reference.
- Same iframe/token/CSP model as AppTriggerActor — the security posture and `allowed*Domains` / `allowedPermissions` semantics are documented in the hub's [`app-trigger-actor.md`](../borgiq-builder/references/app-trigger-actor.md).
