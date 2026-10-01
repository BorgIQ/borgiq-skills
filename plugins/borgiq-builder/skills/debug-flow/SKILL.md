---
name: debug-flow
description: Diagnose a failed or stuck BorgIQ flowrun with the borgiq CLI. Reads the summary and the failed jobs' errors and input, finds the cause and proposes a fix. Use when the user asks to debug a run.
compatibility: Requires the borgiq-builder skill, a shell, and a logged-in borgiq CLI (npm install -g @borgiq/cli).
disable-model-invocation: true
argument-hint: "[flowrunId]"
allowed-tools: Bash(borgiq flowruns*) Bash(borgiq flowrun-jobs*) Bash(borgiq flowrun-results*) Bash(borgiq flowrun-messages*) Bash(borgiq canvas-actors*) Bash(borgiq canvases*) Bash(borgiq workspaces*) Bash(borgiq bundle*) Bash(test*) Bash(ls*)
---

# Debug a BorgIQ flowrun

Requires the `borgiq-builder` skill: the links below go into its `references/` folder. Commands, states and
fields: [flowrun-job-states.md](../borgiq-builder/references/flowrun-job-states.md).

## Pick the flowrun

Use the flowrun ID the user gave, or list the canvas's 10 newest flowruns (no outcome filter) and ask:

```bash
borgiq flowruns list --canvas <canvas> --json
```

## Read the summary

```bash
borgiq flowruns summary <flowrunId> --json
```

States are lowercase, and `completed` does not mean success. Look for:

- the jobs in `errors[]` (job state `error`: retries exhausted, or not retryable);
- actors missing from `actors[]`: never reached, often downstream of a failure;
- actors that emitted the wrong thing.

## Inspect each failed job

```bash
borgiq flowrun-results summaries --job-id <jobId> --json       # every attempt's error
borgiq flowrun-jobs source-message <jobId> --json              # the message it received...
borgiq flowrun-messages data <sourceFlowrunMessage.id> --json  # ...msg.<msgVar> of each upstream actor
borgiq flowrun-jobs runtime-data <jobId> --root-path ctx --json   # run context (ids, trigger, name, msgVar), not config
borgiq canvas-actors get <canvas> <actorId> --json            # the actor's current configuration
```

Other `--root-path` values work only on some jobs
([runtime-data](../borgiq-builder/references/flowrun-job-states.md#what-an-actor-received-and-emitted)).

Read the error literally, then match it:

| Error | Cause and fix |
|---|---|
| `401` / `403` from an HttpRequestActor | Its connection's credentials expired or lack a scope: refresh the connection, re-run |
| Old code still runs; `No built runtime available`; `imports a module outside its own code directory`; `could not be started from its workspace's runtime build` | A deployed workspace runs the last full build: [deployment.md → Troubleshooting](../borgiq-builder/references/deployment.md#troubleshooting) |
| `Timeout waiting for response` | Slow or silent upstream API: check its status; add `retryIf` to the actor's `error` block ([error-handling.md](../borgiq-builder/references/error-handling.md#the-error-block)) |
| `${{ inputs.X }}` is `undefined` | The upstream actor emitted no `X`, or its msgVar was renamed: check `msg.<msgVar>` in the message the job received |
| `Schema validation failed` on an AI output | `outputSchema` too strict for what the model produced: tighten enums, make non-essential fields optional (`borgiq-json-schema-builder` skill) |
| AiAgentActor: `Tool 'X' not found`, `collide with reserved built-in tools`, a workspace-size `endReason: 'error'`, an unexpected fresh session | `aiAgentToolActorIds` lists actor IDs, not msgVars; tool, workspace and session limits: [ai-agent-actor.md](../borgiq-builder/references/ai-agent-actor.md), `borgiq-agent-builder` skill |
| Form validation failed in an interface | A required field is missing or has the wrong shape (`borgiq-form-builder` skill) |
| `COLLECTION_NOT_FOUND` / `STREAM_NOT_FOUND` (`… "<slug>" does not exist`) | Never created (writes and appends create nothing), being deleted, or an expired stream (`persistent: true` prevents that): run or add the migration trigger ([migrations](../borgiq-builder/references/collection-migrations.md#wiring-and-running-migrations)) |

More on `continueOnError`, retries and joins: [error-handling.md](../borgiq-builder/references/error-handling.md).

## Fix it

1. Configuration or code, with a canvas bundle (`canvas.yaml` at its root) in the working directory: read its
   `README.md`, edit the responsible `actor.yaml`, `code/*` or `canvas.yaml`, then `borgiq bundle validate <dir>` and
   `borgiq bundle push <dir>` (`--dry-run` first when unsure); on a deployed workspace, build the canvas too. On a push
   conflict, run a bare `borgiq bundle pull <canvas> <dir>` and push again; never choose `--replace` or `--force-local`
   for the user ([conflicts](../borgiq-builder/references/cli/canvas-bundles.md#incremental-sync-and-conflicts)).
   Without a bundle, describe the exact change and offer to apply it with `borgiq canvas-actors batch`.
2. A workspace resource (connection, secret, asset): give the exact key to update.
3. An intermittent failure (timeout, rate limit): suggest a retry policy.

## Re-run

```bash
borgiq flowrun-jobs re-run --job-id <jobId> --json   # same flowrun, same input, current configuration
```

On a deployed workspace it runs the active build; `--no-publish` keeps its output from connected actors. Judge it by
the actor's newest job in `flowruns summary`: the original job stays in `errors`. For a fresh flowrun, use the `test`
skill (`/borgiq-builder:test` in Claude Code).

End with what failed, what you fixed and whether the re-run succeeded.
