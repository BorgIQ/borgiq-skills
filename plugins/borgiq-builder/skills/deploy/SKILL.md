---
name: deploy
description: Deploy a BorgIQ canvas bundle or workflow YAML with the borgiq CLI. Checks auth and resources, validates, pushes, builds, and reports the canvas and any server errors verbatim. Run only when the user asks.
compatibility: Requires the borgiq-builder skill, a shell, and a logged-in borgiq CLI (npm install -g @borgiq/cli).
disable-model-invocation: true
argument-hint: "[path/to/bundle-or-workflow.yaml] [--workspace <slug>]"
allowed-tools: Bash(borgiq auth*) Bash(borgiq bundle*) Bash(borgiq canvases*) Bash(borgiq canvas-actors*) Bash(borgiq workspaces*) Bash(borgiq connections*) Bash(borgiq secrets*) Bash(borgiq assets*) Bash(borgiq triggers*) Bash(borgiq flowruns*) Bash(ls*) Bash(test*)
---

# Deploy a BorgIQ canvas

Requires the `borgiq-builder` skill: the links below go into its `references/` folder. Deploy only when the user asks.

## Confirm authentication

Auth status (Claude Code fills this in; otherwise run it yourself): !`borgiq auth status 2>&1 || echo "AUTH_MISSING"`

If it printed `AUTH_MISSING` or a credentials error, stop: the user must run `borgiq auth login`. If the user named
a workspace (`--workspace <slug>`), check that it is the active one and warn if not.

## Pick the artifact

Use the path the user gave, if any: a directory containing `canvas.yaml` is a bundle; a `.yaml`/`.yml` file is a
direct document. Otherwise look for candidates (Claude Code fills this in; otherwise run it yourself):

!`find . -maxdepth 2 \( -name canvas.yaml -o -name '*.borgiq-canvas' -o -name '*.yaml' -o -name '*.yml' \) -not -path '*/.*' | head -20`

If there are several, ask which. Prefer a canvas's local bundle over any other document: git stays the source of
truth.

## Check workspace resources

A missing connection, secret or asset is the most common deploy failure. Check that each key the artifact uses (in a
bundle's `canvas.yaml` `dependencies` and `actor.yaml` files, or a document's actor configurations) exists:

```bash
borgiq connections list --json
borgiq secrets list --json
borgiq assets list --json
```

If one is missing, stop: give the user the exact key to create, then deploy again.

## Push

**Bundle.** `borgiq help bundle` must succeed (otherwise stop: the user upgrades the CLI). Then:

```bash
borgiq bundle validate <dir> --strict      # fix the file each finding names; rerun
borgiq canvases get <canvas.slug> --json   # exists? (slug from canvas.yaml)
borgiq bundle push <dir> --create --auto-layout --json   # new canvas
borgiq bundle push <dir> --json            # existing; --auto-layout if actors were added, removed or rewired
```

Add `--mode` (legacy whole-document import) only if the user asks. If the push aborts, run a bare
`borgiq bundle pull <canvas> <dir>` (it applies server-only changes and keeps local edits), then push again. If the pull
aborts too, report the conflicted actors and let the user choose `pull --replace` (server wins) or `push --force-local`
(local wins); never pick one yourself
([conflicts](../borgiq-builder/references/cli/canvas-bundles.md#incremental-sync-and-conflicts)).

**Direct document, new canvas:** `borgiq canvases create-with-data --file <file> --json`. The file must be an
ExportedCanvasData envelope (`name`, `slug`, `messageTTLInDays`, `data: { schemaVersion, actors }`); wrap a
`metadata` + `actors` document first
([create-with-data body](../borgiq-builder/references/cli/cli-data-formats.md#create-with-data-body)).

**Direct document, existing canvas:** `borgiq canvas-actors batch <canvas> --file <changes.json> --json`. Its actors are
CanvasActor-shaped: `options`, `inputs`, `vars`, `outputs` as YAML strings, `codeDir` an array
([batch body](../borgiq-builder/references/cli/cli-data-formats.md#canvas-actors-bodies)). Never `create-with-data`
against an existing canvas: its slug conflicts.

## After the push

1. Report the canvas slug; the CLI returns no URL, so do not invent one.
2. Validate on the server: `borgiq canvases validate <canvas> --json`.
3. **Deployed workspace?** If `borgiq workspaces deployment --json` shows `isDeployed: true`, the push changes nothing
   that runs until you build: run `borgiq canvases runtime-build <canvas> --json` and report each actor's result. Only
   a `ready` build serves runs; on `partially_ready` or `failed`, name the actors that did not build and why, and report
   the deploy as incomplete ([build results](../borgiq-builder/references/deployment.md#reading-a-build-result)).
   `bundle push --runtime-build` and `bundle build` push and build in one step.
4. **Run the migration trigger**, if the canvas has one (the manually run UniversalTriggerActor that creates its
   collections and streams), after the first deploy to a workspace and after adding migrations; on a deployed
   workspace, after the build
   ([running migrations](../borgiq-builder/references/collection-migrations.md#wiring-and-running-migrations)):

   ```bash
   borgiq triggers run --canvas <canvasId> --actor-id <migrationTriggerActorId> --json   # canvas ULID: metadata.id in canvases get
   borgiq flowruns summary <flowrun.id> --json   # poll until completed; errors must be empty
   ```
5. Suggest the `test` skill (`/borgiq-builder:test` in Claude Code) to check the flow runs.

## Failure modes

| Symptom | Fix |
|---|---|
| `401 Unauthorized` | The user runs `borgiq auth login`; retry |
| `Connection 'X' not found` | The user creates a connection with key `X` in the workspace; retry |
| `Schema validation failed` on the server | Run the `validate` skill (`/borgiq-builder:validate` in Claude Code): local errors are clearer |
| `Slug conflict` | Bundle: push without `--create`. Document: `canvas-actors batch` against the existing canvas |
| `Unknown actor type 'X'` | Upgrade `@borgiq/cli`; never guess an actor folder |
| A build error, or runs still execute old code | [deployment.md → Troubleshooting](../borgiq-builder/references/deployment.md#troubleshooting) |
