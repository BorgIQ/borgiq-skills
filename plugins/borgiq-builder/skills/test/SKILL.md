---
name: test
description: Trigger a deployed BorgIQ flow with a sample payload, wait for it to complete, and report pass/fail with the final actor output. Does NOT deploy.
disable-model-invocation: true
argument-hint: "<canvasId> <triggerActorId> '<json-payload>'"
allowed-tools: Bash(borgiq triggers*) Bash(borgiq flowruns*) Bash(borgiq flowrun-jobs*) Bash(borgiq flowrun-results*) Bash(borgiq canvases*)
---

# /test — trigger a flow and assert on the result

Run a flow end-to-end against a deployed canvas, poll until completion, and report whether it produced the expected output. This is for verifying that a deployed flow actually works — not for deploying. Use `/borgiq-builder:deploy` first.

## Parse arguments

Accepted forms:

- `/borgiq-builder:test <canvasId> <triggerActorId> '{"key": "value"}'`
- `/borgiq-builder:test <canvasId> <triggerActorId> --fixture <path-to-payload.json>`
- `/borgiq-builder:test` (no args) — ask which canvas and trigger to use; default the payload to `{}`

If only the canvasId is given, list triggers in that canvas and ask the user which to fire:

```bash
borgiq canvases get <canvasSlugOrId> --json   # inspect triggers
```

## Trigger the flow

```bash
borgiq triggers run --canvas <canvasId> --actor-id <triggerActorId> --payload '<json>' --json
```

Capture the `flowrunId` from the response.

## Wait for completion

Poll until the flowrun reaches a terminal state. Don't loop in a `sleep` block — use `borgiq flowruns watch` if available, otherwise poll with reasonable backoff (3s, 5s, 10s):

```bash
borgiq flowruns status <flowrunId> --json
```

Terminal states are `Completed`, `Failed`, `Cancelled`. See `${CLAUDE_SKILL_DIR}/../borgiq-builder/references/flowrun-job-states.md` for the full state machine.

## Report the result

Once terminal, pull the summary:

```bash
borgiq flowruns summary <flowrunId> --json
```

Then assert based on the user's intent:

- If the user supplied an expected output shape, compare against it.
- If not, report what the final actor emitted and let the user judge.
- For `Failed` flowruns, surface the failing actor's `runtime-data` and the error message:
  ```bash
  borgiq flowrun-jobs runtime-data <jobId> --root-path inputs --json
  borgiq flowrun-results summaries --job-id <jobId> --json
  ```

## Exit summary

End with a clear PASS / FAIL line, plus:

- The flowrunId (so the user can re-inspect later)
- A one-line summary of what each actor emitted (or where it failed)
- If FAIL, suggest `/borgiq-builder:debug-flow <flowrunId>` for deeper inspection
