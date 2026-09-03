# Deployed workspaces and runtime builds

A BorgIQ workspace can be **deployed**. On a deployed workspace, triggers run each canvas's **active
runtime build** instead of the canvas's current code.

A runtime build is a snapshot of the canvas taken when it was last built, with every code actor
compiled and its dependencies already installed. Two things follow from that:

- **Actors start faster.** Nothing is downloaded or resolved when a trigger fires.
- **Every run of a canvas executes the same code.** A run cannot be half-old and half-new because
  somebody saved an edit while it was going.

The trade is the thing to internalise:

> **On a deployed workspace, an edit does not reach triggers until the next build finishes.**

Test runs from the editor always use the current code, so authoring is unaffected. It is only
triggered execution that is pinned.

## The rules, in one place

| | Deployed workspace | Not deployed |
|---|---|---|
| A trigger fires | runs the canvas's active runtime build | runs the canvas's current code |
| Editor test run | runs the current code | runs the current code |
| A canvas with no build, or a failed build | runs the current code | runs the current code |
| An actor that failed to build (others succeeded) | that actor runs its current code; the rest run from the build | runs the current code |

## What gets built

Only **code actors**: Deno actors, Universal Trigger actors, Python actors, and Deno Test actors.
Everything else on the canvas — HTTP requests, AI actors, routers, data stores — has nothing to
compile and is unaffected.

Deno and Universal Trigger actors are built together into one shared artifact per canvas; Python and
Deno Test actors each get their own. The difference is invisible in the build report — every code
actor shows up with its own per-actor result either way.

## Using it

```bash
borgiq workspaces deployment                       # is this workspace deployed? which canvases have builds?
borgiq workspaces deployment --enable --build-all  # deploy, and build every buildable canvas
borgiq workspaces deployment --json                # full detail, including per-actor build results

borgiq canvases runtime-build my-canvas            # build one canvas — waits for the outcome
borgiq canvases runtime-build-status my-canvas     # which build runs, and whether it is outdated
borgiq bundle push ./my-flow.borgiq-canvas --runtime-build   # push, then build, in one command
```

Building is synchronous: `runtime-build` holds until the build finishes (typically a minute or two)
and prints the per-actor outcome — there is nothing to poll. `--timeout <seconds>` bounds only how
long the command waits; the build itself finishes on the server either way.

**After any push to a deployed workspace, build.** `bundle push --runtime-build` does both; otherwise
follow the push with `borgiq canvases runtime-build <canvas>`. A push that is never followed by
a build leaves triggers running the previous code, which looks exactly like the deploy silently
failing.

## Reading a build result

Per actor, a build reports whether it built, whether its imports were verified, and whether it
actually started once:

```bash
borgiq canvases runtime-build my-canvas --json
```

| Field | Meaning |
|---|---|
| `status: ok` / `failed` | whether this actor can run from the build |
| `guard: ok` / `rejected` | whether the actor's imports stay within its own files |
| `warm: ok` / `failed` | whether the actor started successfully once during the build |
| `error` | why it failed, in the actor's own words |

A `warm: failed` on an otherwise `ok` actor means its dependencies installed but its code threw at
start-up. It is not fatal to the build — but it will throw at run time too, so fix it.

## Build statuses

| Status | Meaning |
|---|---|
| `building` | still going (a build someone else started; your own build command returns the finished result) |
| `ready` | every code actor built |
| `partially_ready` | some built; the ones that did run from the build, the rest run their current code |
| `failed` | nothing usable came out of it; the canvas keeps running its current code |
| `stale` | the workspace's runtime was updated after this build, so it no longer applies |
| `expired` | the build's stored artifacts have been cleaned up |

`partially_ready` is a **success** — `runtime-build` exits 0 for it, and prints which actors
did not build. Treat those as work to do, not as a failed deploy.

## Rolling back

Every build is kept for a while, so an earlier one can be made the running build again:

```bash
borgiq canvases runtime-build-status my-canvas --history
borgiq canvases runtime-build-activate my-canvas <buildId>
```

This is the fastest way out of a bad deploy: it changes what triggers run immediately, without
touching the canvas's code.

## Troubleshooting

| Symptom | What it means | Fix |
|---|---|---|
| `no-code-actors` | the canvas has nothing to build | expected — non-code canvases need no build |
| `runtime-too-small` | the canvas's runtime is configured below what a build needs | raise the runtime's timeout, memory and ephemeral storage in the workspace's Runtimes settings, then build again |
| `build-in-progress` (409) | a build of this canvas is already running | wait for it; builds of one canvas are serialised |
| `outdated: true` | the canvas has been edited since its running build | build again — triggers are still running the old build |
| An actor with `guard: rejected` | the actor imports a file outside its own files | move the file into the actor's own `code/`, or use an `npm:`/`jsr:` package |
| An actor with `warm: failed` | it installed, but its code threw at start-up | run the actor with a test run and fix the error |
| A trigger ran old code after a push | the push was not followed by a build | `borgiq canvases runtime-build <canvas>` |
| Occasional "runtime build could not be used" in logs | transient; the run was retried without the build | nothing to do — it self-corrects |

## Writing code actors for a deployed workspace

Two habits matter more here than elsewhere:

1. **Pin your dependency versions exactly.** `npm:escape-html@1.0.3`, not `npm:escape-html` or a `^`
   range. A build resolves the version once and every run uses that resolution, so an unpinned
   specifier means what you get depends on when you last built.
2. **Keep every import inside the actor's own files.** An import that reaches outside the actor's
   `code/` directory is refused — at build time with the offending specifier named, and at run time by
   the runtime itself. Relative imports between your own files, `@borgiq/actors`, `npm:`/`jsr:`/`node:`
   packages and approved `https:` hosts are all fine.
