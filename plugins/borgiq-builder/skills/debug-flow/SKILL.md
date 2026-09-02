---
name: debug-flow
description: Diagnose a failed or stuck BorgIQ flowrun. Fetches the flowrun summary, identifies failed actors, pulls runtime msg/ctx data and error details, and suggests fixes based on the actor type and error pattern.
disable-model-invocation: true
argument-hint: "[flowrunId]"
allowed-tools: Bash(borgiq flowruns*) Bash(borgiq flowrun-jobs*) Bash(borgiq flowrun-results*) Bash(borgiq canvas-actors*) Bash(borgiq bundle*) Bash(test*) Bash(ls*)
---

# /debug-flow — diagnose a failed flowrun

Pull the actual runtime state of a flowrun and figure out why it failed. Surfaces enough detail that the fix is obvious; suggests next steps when it isn't.

## Pick the flowrun

If `$ARGUMENTS` is a flowrunId, use it. Otherwise list the most recent failed flowruns and ask which one:

```bash
borgiq flowruns list --status Failed --limit 10 --json
```

## Get the summary

```bash
borgiq flowruns summary <flowrunId> --json
```

The summary tells you the overall state and per-actor counters. Identify:

- Actors in `Failed` state (the primary suspects)
- Actors in `Skipped` state (often downstream of a failure)
- Actors that ran but produced unexpected output

For the flowrun state machine, see `${CLAUDE_SKILL_DIR}/../borgiq-builder/references/flowrun-job-states.md`.

## Inspect the failed actor(s)

For each failed job:

```bash
# Actor configuration as it ran (post-interpolation)
borgiq flowrun-jobs runtime-data <jobId> --root-path ctx --json

# Interpolated inputs the actor received
borgiq flowrun-jobs runtime-data <jobId> --root-path inputs --json

# Error details
borgiq flowrun-results summaries --job-id <jobId> --json
```

Read the error message literally. The most common patterns and their fixes:

| Error pattern | Likely cause | Fix |
|---|---|---|
| `401` / `403` from HttpRequestActor | Connection has expired creds or wrong scope | Refresh the connection in the workspace; re-deploy or re-run |
| The flow runs code you already changed | The workspace is deployed, so triggers run the canvas's last runtime build; the edit has not been built | `borgiq workspaces deployment --json` to confirm, then `borgiq canvases runtime-build <canvas>` |
| `imports a module outside its own code directory` at actor start | A code actor imports a file outside its own `code/` tree | Move the file into the actor's own files, or use an `npm:`/`jsr:` package. On a deployed workspace the build names the offending specifier |
| `could not be started from its workspace's runtime build` | Transient — the prebuilt environment could not be fetched; the run was automatically retried without it | Nothing to do. If it is persistent, rebuild the canvas |
| `Timeout waiting for response` | Slow upstream API or no response | Check the API's status page; consider `retryIf` on the actor's `error` block |
| `${{ inputs.X }}` evaluates to `undefined` | Upstream actor didn't emit `X`, or msgVar was renamed | Verify with `borgiq flowrun-jobs runtime-data <jobId> --root-path inputs` |
| `Schema validation failed` on an AI output | `outputSchema` too strict, model produced extra/missing fields | See `borgiq-json-schema-builder`: tighten enums, mark non-essential as optional |
| `Tool 'X' not found` in AiAgentActor | Tool's msgVar not listed in `aiAgentToolActorIds`, or wrong reference | See `borgiq-agent-builder`: confirm tool wiring through agent boundary |
| Tool actor name(s) `collide with reserved built-in tools` | A wired tool actor's msgVar is `read`/`write`/`edit`/`bash`/`grep`/`find`/`ls`, or `deno` with `enableDenoTool: true` | Rename the tool actor's msgVar — built-in tool names are reserved. If it is `deno`, turning `enableDenoTool` off also resolves it |
| AiAgentActor ends with `endReason: 'error'` mentioning workspace size | Session workspace exceeded 20% of the runtime's ephemeral storage | Re-invoke the session with a cleanup prompt (grace mode allows deletions), or provision a runtime with more ephemeral storage |
| AiAgentActor session starts fresh unexpectedly | `sessionId` past its 7-day sliding TTL, or the actor was repointed to a different runtime | Expected behavior — persist and reuse the `sessionId` within the TTL; keep the actor on one runtime |
| Form validation failed in Interface | Required field missing or wrong shape | See `borgiq-form-builder` for component schema docs |

For full error-handling patterns (continueOnError, retry semantics, fork/forkJoin error propagation), see `${CLAUDE_SKILL_DIR}/../borgiq-builder/references/error-handling.md`.

## Suggest the fix

After diagnosis, propose a concrete fix:

1. If the fix is in actor configuration/code, first detect whether the current/target working directory is a canvas bundle (`canvas.yaml` at its root):
   - **Bundle exists:** edit the responsible `actor.yaml`, `code/*`, or `canvas.yaml` file, then run `borgiq bundle validate <dir>` and `borgiq bundle push <dir>`. This keeps the git copy as the source of truth. Preview with `--dry-run` when the change or target is uncertain. On a push conflict, first run bare `bundle pull <dir>` (safe: applies server-only changes, keeps local edits) and re-push; if the pull also aborts, report the conflicted actors and let the user choose `pull --replace` (server wins) or `push --force-local` (local wins) — never force or replace automatically.
   - **No local bundle:** describe the exact mutation and offer to apply it via `borgiq canvas-actors batch`.
2. If the fix is in a workspace resource (connection, credentials, asset), give the exact key to update.
3. If the failure is intermittent (timeout, rate limit), suggest the appropriate retry policy.

## Re-run after fixing

Once the fix is applied:

```bash
# Re-run the flow from the failed actor (preserves upstream state)
borgiq flowrun-jobs re-run --job-id <jobId> --json

# Or trigger a fresh flowrun
# (see /borgiq-builder:test)
```

End with a brief summary: what failed, what you fixed, and whether the re-run succeeded.
