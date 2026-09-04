---
name: deploy
description: Deploy a BorgIQ canvas bundle directory or workflow YAML to the platform via the borgiq CLI. Confirms auth status first, validates the selected artifact, surfaces server-side errors verbatim, and returns the canvas URL.
disable-model-invocation: true
argument-hint: "[path/to/bundle-or-workflow.yaml] [--workspace <slug>]"
allowed-tools: Bash(borgiq auth*) Bash(borgiq bundle*) Bash(borgiq canvases*) Bash(borgiq workspaces*) Bash(borgiq connections*) Bash(borgiq credentials*) Bash(borgiq secrets*) Bash(borgiq assets*) Bash(ls*) Bash(test*)
---

# /deploy — deploy a BorgIQ workflow

Push the current canvas bundle or workflow YAML to BorgIQ and return the canvas URL. This is a real action with side effects — invoked by you, never auto-triggered.

## Confirm authentication

!`borgiq auth status 2>&1 || echo "AUTH_MISSING"`

If the output above shows `AUTH_MISSING` or an error about credentials, stop and tell the user to run `borgiq auth login` first. Don't proceed.

If `$ARGUMENTS` includes `--workspace <slug>`, verify the active workspace matches the slug; warn if mismatched.

## Pick the deployment artifact

Classify `$ARGUMENTS[0]` in this order:

1. A directory containing `canvas.yaml` is a canvas bundle.
2. A path ending in `.yaml` or `.yml` is a direct workflow document.
3. Otherwise inspect the current directory for a bare `canvas.yaml`, `*.borgiq-canvas/` directories, and workflow YAML files in `./` or `./outputs/`:

!`test -f canvas.yaml && echo "BUNDLE:."; ls -d *.borgiq-canvas 2>/dev/null; ls outputs/*.yaml outputs/*.yml *.yaml *.yml 2>/dev/null | head -20`

If multiple candidates exist and the user did not specify one, ask which to deploy. Once a local bundle exists for a canvas, prefer it over an out-of-band document so the git copy remains the source of truth.

## Pre-deploy: discover workspace resources

The artifact may reference connections, credentials, and assets by key. For a bundle, inspect `canvas.yaml` `dependencies` and the relevant `actor.yaml` files; for a document, inspect the actor configurations. Verify the keys exist in the target workspace before deploying — a missing resource is the most common deploy failure.

```bash
borgiq connections list --json
borgiq secrets list --json
borgiq assets list --json
```

Cross-reference these against `connection.key`, credentials, and asset references. If anything is missing, stop and ask the user to create the resource (give them the exact key name to use), then re-run `/deploy`.

## Choose the right command

### Canvas bundle directory

First confirm the installed CLI supports bundles, then validate the directory:

```bash
borgiq bundle --help >/dev/null 2>&1 || echo "upgrade: npm install -g @borgiq/cli"
borgiq bundle validate <dir> --strict
```

If bundle support is missing, stop and ask the user to upgrade. Bundle validation errors are file-path-scoped: fix the named bundle file and rerun validation.

Read `canvas.slug` from `canvas.yaml` and check whether it exists with `borgiq canvases get <slug> --json`:

```bash
# Canvas does not exist yet:
borgiq bundle push <dir> --create --auto-layout --json

# Canvas already exists (add --auto-layout when actors were added, removed, or rewired):
borgiq bundle push <dir> --json
```

Existing-canvas push is incremental and conflict-aware by default (three-way, per-actor). Do not add `--mode` unless the user explicitly wants the legacy whole-document path. If the push aborts, first run bare `bundle pull <dir>` — it safely applies server-only changes and keeps local edits — then re-push. If the pull also aborts (actors with both local and server changes), never choose `--force-local` or `pull --replace` automatically; report the conflicted actors and let the user choose `bundle pull --replace` (server wins) or `push --force-local` (local wins).

### Direct YAML/YML document

**New canvas** — deploy the full workflow at once:

```bash
borgiq canvases create-with-data --file <file> --json
```

The YAML must be in **ExportedCanvasData** envelope format (`name`, `slug`, `messageTTLInDays`, `data: { schemaVersion, actors }`). If the YAML is in the raw generation format (just `metadata` + `actors` at the top), wrap it first — see `${CLAUDE_SKILL_DIR}/../borgiq-builder/references/cli/cli-data-formats.md`.

**Existing canvas** — apply changes with batch operations:
```bash
borgiq canvas-actors batch <canvasSlugOrId> --file <changes.json> --json
```

This format requires JSON with each config field as a YAML string (see the same reference doc). Don't use `create-with-data` against an existing canvas — you'll get a slug conflict.

## After deploy

1. Print the canvas URL from the deploy response so the user can open it.
2. Run a server-side validation to catch issues local validation can't:
   ```bash
   borgiq canvases validate <canvasSlugOrId> --json
   ```
3. **Check whether the workspace is deployed** — if it is, the push you just made does NOT change
   what any run executes until the canvas is built:
   ```bash
   borgiq workspaces deployment --json
   ```
   If `isDeployed` is `true`, build the canvas and report the per-actor result:
   ```bash
   borgiq canvases runtime-build <canvasSlugOrId> --json
   ```
   A `ready` build means every code actor built and the canvas now serves it. A `partially_ready`
   or `failed` build does NOT serve: the canvas keeps running its previous full build — and if it
   never had one, every run fails with "No built runtime available" until one succeeds. Name the
   actors that did not build and why, and report the deploy as incomplete rather than claiming it
   succeeded.

   (`borgiq bundle push <dir> --runtime-build` does the push and the build in one step; use it when
   you already know the workspace is deployed.)
4. If the user wants to verify the flow actually runs, suggest `/borgiq-builder:test` next.

## Failure modes

| Symptom | Fix |
|---|---|
| `401 Unauthorized` | `borgiq auth login` then retry |
| `Connection 'X' not found` | Create the connection in the workspace UI with key `X`, retry |
| `Schema validation failed` server-side | Run `/borgiq-builder:validate` locally first — local errors are easier to read |
| `Slug conflict` | For a bundle, rerun push without `--create`; for a direct document, switch to `canvas-actors batch` against the existing canvasId |
| Bundle validation reports `path` + `message` | Fix the named `canvas.yaml`, `actor.yaml`, or `code/*` file, then rerun `bundle validate` |
| `Push aborted: ... actor conflict(s)` | Run bare `bundle pull` (safe: applies server-only changes, keeps local edits), then re-push; if the pull also aborts, ask the user to choose `pull --replace` (server wins) or `push --force-local` (local wins) |
| `Unknown actor type 'X'` | Upgrade `@borgiq/cli`; do not guess an actor folder path |
| Deployed workspace, but a trigger still runs the old code | The push was not followed by a build | `borgiq canvases runtime-build <canvas>` |
| Build reports `runtime-too-small` | The canvas's runtime is configured below what a build needs | Raise the runtime's timeout, memory and ephemeral storage in the workspace's Runtimes settings, then build again |
| Build reports `build-in-progress` (409) | A build of this canvas is already running | Wait for it — builds of one canvas are serialised |
| An actor's build result has `guard: rejected` | The actor imports a file outside its own files | Move the file into the actor's own `code/`, or use an `npm:`/`jsr:` package |
| An actor's build result has `warm: failed` | Dependencies installed, but the actor's code threw at start-up | Test-run the actor and fix the error; it will throw at run time too |
