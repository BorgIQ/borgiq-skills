---
name: test
description: Run a deployed BorgIQ flow with an optional JSON payload and report PASS or FAIL with its actors' output. Does not deploy. Run only when asked.
compatibility: Requires the borgiq-builder skill, a shell, a logged-in borgiq CLI (@borgiq/cli), and curl for a payload.
disable-model-invocation: true
argument-hint: "<canvasId> <triggerActorId> '<json-payload>'"
allowed-tools: Bash(borgiq triggers*) Bash(borgiq flowruns*) Bash(borgiq flowrun-jobs*) Bash(borgiq flowrun-results*) Bash(borgiq flowrun-messages*) Bash(borgiq canvases*) Bash(borgiq canvas-actors*) Bash(borgiq workspaces*) Bash(borgiq auth*)
---

# Test a deployed BorgIQ flow

Requires the `borgiq-builder` skill: the links below go into its `references/` folder. This does not deploy: use the
`deploy` skill (`/borgiq-builder:deploy` in Claude Code) first. On a deployed workspace runs execute the active build,
so build a canvas that `borgiq workspaces deployment --json` shows `outdated: true`
(`borgiq canvases runtime-build <canvas>`), or you test old code
([deployment.md](../borgiq-builder/references/deployment.md)).

## Run the flow

Use the canvas, trigger actor and payload (JSON, or a file) the user gave; ask for a missing canvas. Without a
trigger, list the actors with `borgiq canvas-actors list <canvas> --json` and ask which `…TriggerActor` to fire. Runs
need the canvas ULID: `metadata.id` in `borgiq canvases get <slug> --json`.

**No payload** (a manual run carries none); the flowrun ID is `flowrun.id`:

```bash
borgiq triggers run --canvas <canvasId> --actor-id <triggerActorId> --json
```

**With a payload**, POST it to the trigger's webhook URL; only a WebhookTriggerActor, or a UniversalTriggerActor with
`webhook.enabled: true`, has one. Take `triggerKey`, `authorizationLevel` and `allowedMethods` from
`configuration.webhook` (`borgiq canvas-actors get <canvas> <triggerActorId> --json`), and `apiUrl`, `defaultOrg`
and `defaultWorkspace` from `borgiq auth status --json`:

```bash
curl -sS -D - -X POST '<apiUrl>/msg/<org>/<workspace>/<canvasId>/<triggerActorId>/<triggerKey>' \
  -H 'Content-Type: application/json' -d '<json>'   # payload file: -d @<path>
```

The flowrun ID is the `X-BIQ-Flowrun-Id` response header. Level `public` (or none) needs no token; the others need
one the user supplies, never the CLI's stored one ([which token](../borgiq-builder/references/flowrun-job-states.md#run-a-flow)).

To run one actor on its upstream actors' latest message:
`borgiq flowrun-jobs test-run --canvas <canvasId> --actor-id <actorId> --json`.

## Wait and judge

Poll `borgiq flowruns status <flowrunId> --json` with backoff (3, 5, 10 s) while `state` is `running`; one waiting for a
callback or form submission stays `running`, so report that instead. Then read
`borgiq flowruns summary <flowrunId> --json`.

**PASS means `state` is `completed` and `errors` is empty**; `completed` alone is not success. Compare what the actors
emitted (`msg.<msgVar>`, read with `flowrun-messages list` and `data`) with what the user expects, or report the last
actor's output. Commands, fields and job attempts:
[flowrun-job-states.md](../borgiq-builder/references/flowrun-job-states.md#what-an-actor-received-and-emitted).

End with PASS or FAIL, the flowrun ID and one line per actor (its output or error). On FAIL, suggest the `debug-flow`
skill (`/borgiq-builder:debug-flow` in Claude Code) with that flowrun ID.
