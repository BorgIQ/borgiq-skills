# React app build

How a ReactAppTriggerActor project is laid out, built and served: the seeded scaffold, the `vite.config.ts` settings
the builder requires, every build constraint, WebAssembly and workers, and build-time interpolation of the tab title
and the security options. Read it when you create or restructure an app's project, or when a Build fails.

## Contents

- [Scaffold](#scaffold)
- [Required vite.config.ts](#required-viteconfigts)
- [Building](#building)
- [Constraints](#constraints)
- [Binary assets](#binary-assets)
- [WebAssembly and workers](#webassembly-and-workers)
- [Build-time options](#build-time-options)

## Scaffold

Start from the scaffold the editor seeds: create the actor in the editor, then `borgiq bundle pull`. Do not write a
project from memory. The seeded `codeDir` holds:

| File | Why it matters |
|---|---|
| `package.json` | `"build": "tsc -b && vite build"`; `@borgiq/actors` as `file:./__borgiq_sdk_placeholder__` (the builder links the SDK there); exact versions, no ranges (no lockfile is synced) |
| `deno.json` | `"nodeModulesDir": "manual"`, `"minimumDependencyAge": "P7D"` |
| `vite.config.ts` | The [required settings](#required-viteconfigts) |
| `tsconfig.json`, `tsconfig.app.json`, `tsconfig.node.json` | `tsc -b` fails without a `tsconfig.json` |
| `index.html`, `src/main.tsx`, `src/App.tsx`, `src/vite-env.d.ts` | Entry point and a sample `useEndpoint`/`useGetSession` app |
| `src/index.css`, `src/App.css` | Sample styles with literal colors: replace them with `src/theme.css` ([react-app-themes.md](react-app-themes.md)), imported first in `src/main.tsx` |

Add a dependency (such as `@tabler/icons-react`) to `package.json` at an exact version.

## Required vite.config.ts

Keep these settings; the builder rejects any other dist shape.

```ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
export default defineConfig({
  base: './',                       // relative asset paths under the served token path
  plugins: [react()],
  resolve: { dedupe: ['react', 'react-dom'] },   // the SDK shares the app's React
  build: {
    cssCodeSplit: false,            // all CSS in one file
    assetsInlineLimit: 0,           // emit real asset files, never base64-inline
    rollupOptions: {
      maxParallelFileOps: 20,       // icon packages otherwise fail the build with EMFILE: too many open files
      output: {
        inlineDynamicImports: true, // one JS chunk
        entryFileNames: 'assets/[name].js',   // stable, hash-free names
        chunkFileNames: 'assets/[name].js',
        assetFileNames: 'assets/[name][extname]',
      },
    },
  },
})
```

Assets are served same-origin, piped through the API (no redirect to storage), so no `renderBuiltUrl` or asset-base
rebasing is needed.

## Building

Build compiles the project (`deno install`, then `deno task build`, which runs the `build` script), checks the dist
and stores every `dist/` file. Serving needs a successful build, and every change needs a new one.

- **Editor:** the Build button; the status badge shows the result and the build error.
- **CLI:** `borgiq bundle build <dir>` pushes the bundle and builds its React apps (`--actor <id>` for one).
- **API:** `POST /v1/orgs/{org}/workspaces/{wsp}/canvases/{canvas}/apps/{actorId}/build`.
- **Deployed workspace:** the app is built with the canvas's runtime build, and the editor's Build is refused
  (`409 Build the canvas instead`); `bundle build` does this for you. See [deployment.md](deployment.md).

Open the built app at `/org/{org}/w/{wsp}/c/{canvas}/apps/{actorId}`. Its tab reads `App | BorgIQ` unless the app
sets a title ([react-app-sdk.md](react-app-sdk.md#tab-title)).

## Constraints

| Constraint | Limit / rule |
|---|---|
| `codeDir` | ≤ 200 files, ≤ 1 MiB (1,048,576 bytes) in total, text only |
| Overlay files (`options.files`) | ≤ 50; they win over `codeDir` on a path collision |
| Endpoints, stream declarations | ≤ 50 each; frozen at Build ([react-app-sdk.md](react-app-sdk.md#declaring-endpoints)) |
| Build output shape | Exactly one `.js`, at most one `.css`, and `index.html`; anything else is rejected with a message naming the `vite.config.ts` settings |
| Build output size | ≤ 50 `dist` files and ≤ 100 MB in total |
| npm packages | Installed, but postinstall scripts do not run |
| Code splitting | Dynamic imports fold into the single JS, so `React.lazy` chunks are impossible. Prefer eager imports |
| Content token | Short-lived (~2 minutes) and scopes the served assets; assets are cacheable, not immutable. Fetch everything the app needs at startup |
| Serve before Build | `409 No build available` |
| Endpoint calls before Build | `401` |

## Binary assets

`codeDir` is text only. Put an image or font in an overlay under `src/assets/`, with `content: ${{ assets.<key> }}`
(an uploaded asset), then import it: `import logo from './assets/logo.png'` → `<img src={logo} />`. Do not use
`public/`: Vite serves it verbatim, never imported, and a `public/` URL needs an `import.meta.env.BASE_URL` prefix to
resolve under the token path. Overlays are interpolated with the actor's full scope (`assets`, `vars`, `credentials`,
`secrets`, `ctx`), and their content ships to the browser: never interpolate a secret into one.

## WebAssembly and workers

Both are off by default. `allowWebAssembly: true` lets `WebAssembly.compile`/`instantiate` run; `allowBlobWorkers: true`
lets inline workers start; a worker that compiles WebAssembly (SQLite WASM, for example) needs both. Their CSP effect
is in [app-trigger-actor.md → WebAssembly and workers](app-trigger-actor.md#webassembly-and-workers-react-apps-only).

- Inline every worker: `import MyWorker from './worker?worker&inline'`. `new Worker(new URL('./worker.ts',
  import.meta.url))` emits a second `.js` and fails the build.
- Ship the `.wasm` (or database file) as a same-origin dist asset; it counts toward the 50-file and 100 MB limits.
- Hand a worker an absolute URL resolved on the page, `new URL('assets/x.wasm', document.baseURI).href`: relative URLs
  do not resolve inside a `blob:` worker.
- Fetch the file at startup; after the ~2-minute token lifetime a late asset fetch fails.

## Build-time options

The actor's `options` are interpolated when the app is built, not when a page loads:

- `title`, the static browser tab title, accepts `${{ }}` and is frozen like the rest: a change shows on the next
  Build. The app's code overrides it per page ([react-app-sdk.md](react-app-sdk.md#tab-title)).
- The seven security options (`allowedScriptDomains`, `allowedStyleDomains`, `allowInlineScripts`,
  `allowInlineStyling`, `allowedPermissions`, `allowWebAssembly`, `allowBlobWorkers`) accept `${{ }}`, which the
  build resolves and freezes; a `${{ vars.* }}` change applies on the next Build. What each option does to the policy:
  [app-trigger-actor.md → Content Security Policy](app-trigger-actor.md#content-security-policy).
- Endpoint string fields (`actorId`, `workspaceSlug`, `canvasSlug`) and stream fields accept `${{ }}` too, resolved
  at Build.
- `codeDir` is never interpolated: `${{ … }}` in JSX is literal text.
