# Deployed workspaces and runtime builds

On a **deployed** workspace every run of a canvas executes its last runtime build, not its current code, so a push
changes nothing that runs until the canvas is built again. Read this before pushing to, testing on or debugging a
deployed workspace: how to tell, how to build and roll back, and what build results and errors mean.

## Contents

- [The rules](#the-rules)
- [What gets built](#what-gets-built)
- [Build, check and roll back](#build-check-and-roll-back)
- [Reading a build result](#reading-a-build-result)
- [Build statuses](#build-statuses)
- [Troubleshooting](#troubleshooting)
- [Writing code actors for a deployed workspace](#writing-code-actors-for-a-deployed-workspace)

## The rules

A runtime build snapshots the canvas with every code actor compiled and its dependencies installed: actors start
faster, and no run is half old, half new. **An edit reaches no run, the editor's play button and test runs included,
until the next build finishes.** Treat a deployed workspace as production: author and test on a non-deployed one,
then push and build here.

| | Deployed workspace | Not deployed |
|---|---|---|
| A trigger fires (webhook, schedule, email, …), or an editor test run | runs the active runtime build | runs the current code |
| The canvas has no fully successful build | every run **fails**: "No built runtime available" | runs the current code |
| An actor failed to build, others succeeded | the partial build never serves; the previous full build keeps running (runs fail without one) | runs the current code |
| An actor was added after the last build | its runs fail until the next build | runs the current code |

## What gets built

Only **code actors**: Deno, Universal Trigger, Python, Deno Test and React App actors; HTTP, AI, router and other
actors have nothing to compile. Deno and Universal Trigger actors share one artifact per canvas, the others get one
each; the build report lists every code actor either way.

**React apps.** On a deployed workspace people open the app the active build compiled (the editor's "Build app"
install and Vite build), with its endpoints and security options frozen in. The editor's "Build app" is refused there
(`409`, "Build the canvas instead"). An app edit (source, endpoints or security options) marks the canvas
**outdated** and reaches viewers with the next canvas build. A failed app build makes the build `partially_ready`
(the previous full build, app included, keeps serving), and a rollback rolls the app back too.

## Build, check and roll back

```bash
borgiq workspaces deployment                        # deployed? per canvas: code actors, running and latest build, state
borgiq workspaces deployment --json                 # full detail (isDeployed, per-actor build results, blockedDetail)
borgiq workspaces deployment --enable               # deploy the workspace, then build each canvas; --disable undeploys

borgiq bundle build ./my-flow.borgiq-canvas         # push, then the build this workspace needs
borgiq bundle push ./my-flow.borgiq-canvas --runtime-build   # push, then the canvas build
borgiq canvases runtime-build my-canvas             # build one canvas and wait for the outcome
borgiq canvases runtime-build-status my-canvas      # which build runs, and whether the canvas is outdated
borgiq canvases runtime-build-status my-canvas --history
borgiq canvases runtime-build-activate my-canvas <buildId>   # roll back
```

- **After every push, build.** Otherwise every run stays on the previous build, which looks exactly like a silently
  failed deploy.
- **`bundle build` picks the build**: on a deployed workspace one canvas build (React apps included; `--actor` does not
  apply), elsewhere the editor's React app build. When unsure, run it.
- **`canvases runtime-build`** refuses on a non-deployed workspace (exit 2). `bundle push --runtime-build` skips the
  build there with a notice; it is ignored with `--dry-run` and `--mode`, and a failed build does not fail the push.
- **Builds are synchronous**: `runtime-build` waits (typically a minute or two) and prints the per-actor outcome, so
  there is nothing to poll. `--timeout <seconds>` (default 900) bounds only the wait; the server finishes the build and
  `runtime-build-status` shows it. Exit 0: every actor built; 1: the build failed or partly failed, or the wait timed
  out.
- **One canvas at a time**; there is no "build all". In the web app the Build button is in each canvas's editor, and
  **View runtime builds** in the canvas list menu holds the history (per-actor results, frozen canvas, rollback); the
  workspace's deployment settings hold only the deploy toggle.
- **Roll back** with `runtime-build-activate`, the fastest way out of a bad deploy: every run switches at once, the
  canvas's code untouched. Builds are kept for a while; only a `ready` build for the current runtime can be activated
  (`422` otherwise: build again).

## Reading a build result

`borgiq canvases runtime-build <canvas> --json` reports per actor:

| Field | Meaning |
|---|---|
| `status: ok` / `failed` | whether this actor can run from the build |
| `guard: ok` / `rejected` / `skipped` | whether the actor's imports stay within its own files; `skipped` means they could not be resolved at all, which fails the build (absent for Python actors) |
| `warm: ok` / `failed` / `skipped` | whether the actor started successfully once during the build |
| `error` | why it failed, in the actor's own words |

`warm: failed` on an `ok` actor means its code threw at start-up: the build does not fail, but runs will, so fix it.

## Build statuses

| Status | Meaning |
|---|---|
| `building` | still going (one someone else started; your own build command returns the finished result) |
| `ready` | every code actor built: the only status that serves runs |
| `partially_ready` | some actors failed; it never serves, and the previous full build keeps running |
| `failed` | nothing usable came out of it; the previous full build keeps running |
| `stale` | the workspace's runtime changed after this build, so it no longer applies |
| `expired` | the build's stored artifacts were cleaned up |

A `partially_ready` build is diagnostic: `runtime-build` exits non-zero and names the actors that did not build. Until
**every** actor builds, the canvas keeps its previous full build, and with none every run fails with "No built runtime
available": the deploy is not real yet.

## Troubleshooting

| Symptom | Meaning | Fix |
|---|---|---|
| `no-code-actors` | the canvas has nothing to build | expected: a canvas without code needs no build |
| `runtime-too-small` | the canvas's runtime is configured below what a build needs | raise the runtime's timeout, memory and ephemeral storage in the workspace's Runtimes settings, then build again |
| `build-in-progress` (`409`) | this canvas is already building | wait: builds of one canvas are serialised |
| `no-runtime` | the canvas has no resolvable runtime | read `blockedDetail` in `borgiq workspaces deployment --json`; it names the setting to change |
| `error` (why a canvas cannot be built) | the build could not run, for an unexpected reason | read `blockedDetail` in `borgiq workspaces deployment --json` |
| `outdated: true` | the canvas changed since its running build | build again: every run still executes the old build |
| `No built runtime available for canvas …` | deployed, and the canvas has no fully successful build | `borgiq canvases runtime-build <canvas>`, and make every actor build |
| An actor with `guard: rejected` | it imports a file outside its own files | move the file into the actor's own `code/`, or use an `npm:`/`jsr:` package |
| An actor with `warm: failed` | it installed, but its code threw at start-up | fix the start-up error (a test run of the actor shows it) and build again |
| A run executed old code after a push | the push was not followed by a build | `borgiq canvases runtime-build <canvas>` |
| "Build the canvas instead" (`409`) from the editor's Build app | the workspace is deployed; the canvas build owns the app | `borgiq canvases runtime-build <canvas>` |
| A served app is missing or stale after deploying | the canvas was not built since the app changed | build the canvas; the app serves from the active build |
| Occasional "runtime build could not be used" in logs, or "could not be started from its workspace's runtime build" | transient; the run was retried without the build | nothing: it corrects itself. If it persists, build the canvas again |

## Writing code actors for a deployed workspace

1. **Pin dependency versions exactly** (`npm:escape-html@1.0.3`, not `npm:escape-html` or a `^` range): a build
   resolves each version once, and every run uses what it got.
2. **Keep every import inside the actor's own files.** One that leaves `code/` is refused at build time (naming the
   specifier) and at run time. Your own files, `@borgiq/actors`, `npm:`/`jsr:`/`node:` packages and approved `https:`
   hosts are fine.

More on dependencies in code actors: [code-actor-runtime.md → Dependencies and deployed workspaces](code-actor-runtime.md#dependencies-and-deployed-workspaces).
