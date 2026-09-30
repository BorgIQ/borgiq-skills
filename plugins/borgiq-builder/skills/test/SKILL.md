---
name: test
description: Trigger a deployed BorgIQ flow with a sample payload, wait for it to complete, and report pass/fail with the final actor output. Does NOT deploy.
disable-model-invocation: true
argument-hint: "<canvasId> <triggerActorId> '<json-payload>'"
allowed-tools: Bash(borgiq triggers*) Bash(borgiq flowruns*) Bash(borgiq flowrun-jobs*) Bash(borgiq flowrun-results*) Bash(borgiq flowrun-messages*) Bash(borgiq canvases*) Bash(borgiq canvas-actors*) Bash(borgiq workspaces*) Bash(borgiq auth*)
---

# /test — trigger a flow and assert on the result

Run a flow end-to-end against a deployed canvas, poll until completion, and report whether it produced the expected output. This is for verifying that a deployed flow actually works — not for deploying. Use `/borgiq-builder:deploy` first.

> **On a deployed workspace, every run — `borgiq triggers run` and editor test runs alike — executes
> the canvas's active runtime build, not its current code.** If the flow was edited since the last
> build, this tests the OLD code and the result will not reflect your changes; a canvas with no fully
> successful build fails with "No built runtime available". Build the canvas first
> (`borgiq canvases runtime-build <canvas>` — it waits for the build). Check with
> `borgiq workspaces deployment --json`; a canvas showing `outdated: true` is exactly this situation.

## Parse arguments

Accepted forms:

- `/borgiq-builder:test <canvasId> <triggerActorId> '{"key": "value"}'`
- `/borgiq-builder:test <canvasId> <triggerActorId> --fixture <path-to-payload.json>`
- `/borgiq-builder:test` (no args) — ask which canvas and trigger to use; run without a payload

If only the canvasId is given, list the canvas's actors and ask which trigger (a type ending in `TriggerActor`) to fire:

```bash
borgiq canvas-actors list <canvasSlugOrId> --json
```

`triggers run` takes the canvas ID (ULID), not the slug; `borgiq canvases get <slug> --json` returns it as `metadata.id`.

## Trigger the flow

**No payload** — a manual run carries no request data:

```bash
borgiq triggers run --canvas <canvasId> --actor-id <triggerActorId> --json
```

The flowrun ID is `flowrun.id` in the response.

**With a payload** — `triggers run` cannot send one. POST it to the trigger's webhook URL; only a WebhookTriggerActor, or a UniversalTriggerActor with `webhook.enabled: true`, has one. Take `triggerKey`, `authorizationLevel` and `allowedMethods` (default POST) from `configuration.webhook` in `borgiq canvas-actors get <canvas> <triggerActorId> --json`, and `apiUrl`, `defaultOrg`, `defaultWorkspace` from `borgiq auth status --json`:

```bash
curl -sS -D - -X POST '<apiUrl>/msg/<org>/<workspace>/<canvasId>/<triggerActorId>/<triggerKey>' \
  -H 'Content-Type: application/json' -d '<json>'   # --fixture: -d @<path>
```

The flowrun ID is the `X-BIQ-Flowrun-Id` response header. An `authorizationLevel` of `public`, or none, needs no credentials; `apiKey` and `appsAndApiKey` need `-H 'Authorization: Bearer <token>'` with a personal access token the user supplies (never read the CLI's stored token); an `apps` trigger accepts only app tokens, so test it through its app.

To test one actor on the latest message its upstream actors emitted, use `borgiq flowrun-jobs test-run --canvas <canvasId> --actor-id <actorId> --json` (`--publish` passes its output on).

## Wait for completion

Poll with backoff (3s, 5s, 10s), not a `sleep` loop:

```bash
borgiq flowruns status <flowrunId> --json
```

`state` is lowercase: `running` while any of its `counters` is above zero, then `completed` (or `user-interrupted`). A flowrun waiting for a callback token or an interface submission (a human step) stays `running`; report that rather than polling on. See `${CLAUDE_SKILL_DIR}/../borgiq-builder/references/flowrun-job-states.md` for the full state machine.

## Report the result

Once terminal, pull the summary:

```bash
borgiq flowruns summary <flowrunId> --json
```

`completed` does not mean success: PASS means `state` is `completed` and `errors` is empty. `errors[]` lists `actorId`, `actorName`, `jobId` and `error`; `actors[].jobs[]` gives each job's `state`, `status` and `error`.

To show what an actor emitted, read one of its messages in this flowrun; its output is `msg.<msgVar>`:

```bash
borgiq flowrun-messages list --canvas <canvasSlugOrId> --actor-id <actorId> --flowrun-id <flowrunId> --json
borgiq flowrun-messages data <messageId> --json
```

Then assert based on the user's intent:

- If the user supplied an expected output shape, compare against it.
- If not, report what the final actor emitted and let the user judge.
- For each entry in `errors`, report the actor and its error; `borgiq flowrun-results summaries --job-id <jobId> --json` lists every attempt of that job.

## Exit summary

End with a clear PASS / FAIL line, plus:

- The flowrunId (so the user can re-inspect later)
- A one-line summary of what each actor emitted (or where it failed)
- If FAIL, suggest `/borgiq-builder:debug-flow <flowrunId>` for deeper inspection
