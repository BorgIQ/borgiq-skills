---
name: borgiq-react-app-builder
description: Build custom app UIs on a BorgIQ canvas as a React (Vite + TypeScript) app in a ReactAppTriggerActor, compiled server-side and served in a sandboxed iframe, for dashboards, data explorers and SPAs. Also maintains legacy AppTriggerActor apps; forms go to borgiq-form-builder. Triggers on "ReactAppTriggerActor", "AppTriggerActor", "build a web app", "custom dashboard", "single-page app", "useEndpoint", "useGetSession", "useStreamTail", "vite", "app theme", "hearth theme", "app thumbnail".
---

# BorgIQ React App Builder

Build a **React SPA** inside a **ReactAppTriggerActor**: a Vite + TypeScript project that BorgIQ compiles server-side
and serves as static assets in a sandboxed iframe with a short-lived content token. Forms and data-entry pages belong
to the `borgiq-form-builder` skill. A legacy raw-HTML AppTriggerActor app is maintained, not extended:
[app-trigger-actor.md](../borgiq-builder/references/app-trigger-actor.md). This skill relies on the `borgiq-builder`
skill (the hub) for wiring and IDs, and on its shared references under `../borgiq-builder/references/`.

## Mental model

- **`configuration.codeDir`** is the source: a plain array of `{ path, content }` text files (`package.json`,
  `vite.config.ts`, `index.html`, `src/**`). It is never interpolated, so `${{ … }}` in JSX is literal text.
- **`configuration.options.files`** is an overlay applied at build time. It is interpolated with the actor's full
  scope (`assets`, `vars`, `credentials`, `secrets`, `ctx`), wins over `codeDir` on a path collision, and is how
  binaries (`${{ assets.<key> }}`) get into the build.
- **Build, then serve.** Nothing is served until a Build compiles the project and stores `dist/`; an unbuilt app
  answers `409`. The page runs in the same sandboxed iframe, `frame-ancestors` restriction and origin-checked token
  model as an AppTriggerActor. On a deployed workspace the canvas's runtime build compiles the app instead.
- **Endpoints** are named calls to webhook-capable triggers, resolved and baked into the build. The `@borgiq/actors`
  SDK calls them with the app token.
- **Streams** are workspace streams the app declares and tails live, read only, through the same SDK.

## Non-negotiables

1. **Theme every app.** Create `src/theme.css` (Base Contract + exactly one theme block, from
   [react-app-themes.md](../borgiq-builder/references/react-app-themes.md)) and import it first in `src/main.tsx`. Default to `hearth` unless the customer names `ledger`, `meridian`, `signal` or `bloom`, or
   supplies brand colors (then follow the brand-override procedure). Components use tokens only (no literal colors,
   fonts, radii or shadows) and Tabler icons. An app with hard-coded styling or no `theme.css` is incomplete: fix it
   before Build.
2. **Keep the single-file Vite settings:** `base: './'`, `cssCodeSplit: false`, `assetsInlineLimit: 0`,
   `rollupOptions.maxParallelFileOps: 20`, `output.inlineDynamicImports: true` and hash-free output names. The builder
   rejects any dist but one JS, at most one CSS and `index.html`, and icon packages fail with `EMFILE` without the cap.
3. **No secrets in overlays.** A `${{ credentials.* }}` or `${{ secrets.* }}` in `options.files` is bundled into the
   browser-visible `dist/`. Keep secrets server-side behind an endpoint; overlay only binaries and non-secret
   templated values (`${{ vars.* }}`).
4. **Fetch only through the SDK.** `useEndpoint`/`callEndpoint` and `useStreamTail`/`tailStream`/`readStream` attach
   the app token; a raw `fetch()` to a `/msg/` or `/app-streams/` URL carries none.
5. **Everything is frozen at Build.** Source, overlays, endpoints (a target's `triggerKey` included), streams and the
   CSP options take effect on the next Build, never on save. Before the first Build, serving answers `409` and
   endpoints `401`. On a deployed workspace, build the canvas.
6. **One endpoint per route, at `apps`.** Give each UI action its own declared endpoint on a webhook-capable trigger
   set to `authorizationLevel: apps` (`appsAndApiKey` if external API callers share it); never branch one endpoint on
   `?action=`. The list is the app's authorization grant: an undeclared webhook answers `401`, even on this canvas.
7. **Binaries through `src/assets`.** Overlay images and fonts under `src/assets/` and `import` them; never `public/`.
8. **`useGetSession` is display-only.** Flows authorize with the server-attested `trigger.user`, never a user or
   session id sent in a request.
9. **Declare streams narrowly.** Every viewer's token reads every declared stream, so declare exact slugs or a narrow
   prefix, and mint per-session slugs from an unguessable part, handed out through an endpoint. Apps never write
   streams, and records reach the browser as plaintext.

## Key decisions

1. **App, form or legacy.** A custom UI (dashboard, data explorer, SPA) is a ReactAppTriggerActor, built here. A form,
   survey or data-entry page goes to `borgiq-form-builder`. Keep an existing AppTriggerActor app as it is unless the
   customer asks for a rebuild.
2. **Backend per route, endpoint-first.** List every UI action (`listTasks`, `createTask`, `summarize`); each becomes
   one endpoint. Choose its trigger with the hub's
   [Universal Trigger vs Webhook Trigger](../borgiq-builder/SKILL.md#universal-trigger-vs-webhook-trigger-http-endpoints)
   matrix; one app usually mixes both:
   - CRUD and lookups: a webhook-enabled **UniversalTriggerActor** whose `receive` code validates, calls the
     collection and replies with `Signal.webhookRespond` (`options.webhook.respondImmediately: false`). No downstream
     actors.
   - AI, third-party APIs or routing: a **WebhookTriggerActor** feeding task actors and a **WebhookResponseActor**.
3. **Storage.** Back an app with **one collection** holding every entity type under key prefixes (`task:<id>`,
   `user:<id>`) plus a `$meta` manifest row; split only for a security boundary or on request. Collections are not
   implicit (`COLLECTION_NOT_FOUND` until created), so ship an idempotent migration runner that creates and seeds it.
   See the hub's [Collection migrations and provisioning](../borgiq-builder/SKILL.md#collection-migrations-and-provisioning),
   [single-collection design](../borgiq-builder/references/collection-api.md#single-collection-design) and
   [collection-migrations.md](../borgiq-builder/references/collection-migrations.md).
4. **Live data.** Tail a stream when a flow produces events the viewer should see as they happen; otherwise call an
   endpoint.

## The `options` block

```yaml
ACTR01reactapp:
  type: ReactAppTriggerActor
  configuration:
    codeDir: [...]                        # the seeded Vite project (react-app-build.md)
    options:
      files:
        - path: src/assets/logo.png       # import it from source; not public/
          content: ${{ assets.company_logo }}
      endpoints:
        - name: saveRecord                # useEndpoint('saveRecord')
          actorId: ACTR01webhookhandler…  # WebhookTriggerActor or webhook-enabled UniversalTriggerActor, at apps
          # workspaceSlug / canvasSlug: optional slugs; blank = this canvas; same org only
      streams:
        - name: activity
          slug: agent-activity            # or slugPrefix: chat- ; exactly one per entry
      allowedScriptDomains: []            # CSP options, resolved at Build
      allowedStyleDomains: []
      allowedPermissions: []
      allowWebAssembly: false
      allowBlobWorkers: false
```

The trigger it targets (the hub wires its edges to task actors and a WebhookResponseActor):

```yaml
ACTR01webhookhandler:
  type: WebhookTriggerActor
  configuration:
    webhook: { triggerKey: save-record, authorizationLevel: apps }
```

## Limits

| Limit | Value |
|---|---|
| `codeDir` | ≤ 200 files, ≤ 1 MiB, text only |
| Overlays, endpoints, stream declarations | ≤ 50 each |
| Build output | one JS, at most one CSS, `index.html`; ≤ 50 files, ≤ 100 MB |
| Content token | ~2 minutes: load assets at startup, not lazily |
| npm | installed by `deno install`; postinstall scripts do not run |

## Workflow

1. **Create** the actor in the editor, which seeds a working Vite scaffold, then `borgiq bundle pull` to work on it
   locally.
2. **Theme** first: write `src/theme.css` and replace the scaffold's sample CSS.
3. **Design the backend** endpoint-first (decision 2), build it with the hub, and add the collection's migration
   runner.
4. **Declare** endpoints, streams and asset overlays in `options`.
5. **Build**: the editor's Build button, `borgiq bundle build <dir>`, or
   `POST /v1/orgs/{org}/workspaces/{wsp}/canvases/{canvas}/apps/{actorId}/build`.
6. **Open** `/org/{org}/w/{wsp}/c/{canvas}/apps/{actorId}` and check it with real data.
7. **Thumbnail**: screenshot the built app and attach it
   ([app-thumbnail.md](../borgiq-builder/references/app-thumbnail.md)); refresh it after a visible UI change.

## Read when

| Read | When |
|---|---|
| [react-app-sdk.md](../borgiq-builder/references/react-app-sdk.md) | Writing calls to endpoints, the viewer session or streams; explaining an SDK error |
| [react-app-build.md](../borgiq-builder/references/react-app-build.md) | Creating or restructuring the project, `vite.config.ts`, a failed Build, WebAssembly or workers, every constraint |
| [react-app-themes.md](../borgiq-builder/references/react-app-themes.md) | Before writing components: tokens, Base Contract, recipes, icons, theme rules |
| [react-app-theme-blocks.md](../borgiq-builder/references/react-app-theme-blocks.md) | Copying the chosen theme's CSS (read only that block) |
| [app-trigger-actor.md → Content Security Policy](../borgiq-builder/references/app-trigger-actor.md#content-security-policy) | CDN domains, inline scripts or styles, browser permissions |
| [app-thumbnail.md](../borgiq-builder/references/app-thumbnail.md) | Capturing and attaching the thumbnail |
| [universal-trigger-actor.md](../borgiq-builder/references/universal-trigger-actor.md), [webhook-trigger-actor.md](../borgiq-builder/references/webhook-trigger-actor.md) | Configuring an endpoint's trigger |
| [deployment.md](../borgiq-builder/references/deployment.md) | The app lives on a deployed workspace |
| [app-trigger-actor.md](../borgiq-builder/references/app-trigger-actor.md) | Maintaining a legacy AppTriggerActor app |

## Boundaries

- The hub owns edges, msgVars, IDs and the trigger → task actors → response chain your endpoints target. Use it to
  build the backend flow.
- Forms and interface pages go to `borgiq-form-builder`.
