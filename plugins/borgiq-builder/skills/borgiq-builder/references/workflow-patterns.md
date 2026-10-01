# Workflow Patterns

An index of the common flow shapes: when each applies and where its rules and example live. Read it when you plan a
multi-actor flow; to pick the actor types themselves, see [choosing-actors.md](choosing-actors.md).

## Patterns

| Pattern | Use when | Shape | Rules and example |
|---|---|---|---|
| Sequential pipeline | Each step needs the previous step's output (fetch → transform → validate → save) | `Trigger → A → B → C` | plain edges |
| Fire-and-forget | Several independent destinations: email **and** Slack, several logs or webhooks | `A → B`, `A → C`; no fork | [fan-out](message-processor-actor.md#fork-actions) |
| Multi-source aggregation | One step needs the results of **all** parallel calls (search several portals, merge several services) | `fork → A, B, C → forkJoin → process` | [forkJoin](message-processor-actor.md#forkjoin) |
| Conditional branching | Different paths by data (priority, status code, event type); one path runs | `Router → High / Medium / Low` | [router-actor.md](router-actor.md) |
| Split and collect | Each item of an array is processed, then the results are recombined | `split → process item → collect` | [split and collect](message-processor-actor.md#split-and-collect) |
| Error handling | A step may fail and the flow should continue or branch | step with `continueOnError: true` → Router on `err.<msgVar>` | [error-handling.md](error-handling.md) |
| Human approval / external callback | The flow waits for a person or another system | `issueCallbackToken → send the link → waitForCallbackToken → Router` | [callback pattern](message-processor-actor.md#human-approval-pattern) |
| Sub-flow | Reuse a flow, or split a large one | `CallFlowActor → CallableTriggerActor … CallableResponseActor` | [call-flow-actor.md](call-flow-actor.md) |
| Webhook API | Receive a request, route it, answer it | `WebhookTrigger → Router → WebhookResponse` | [workflow-example.md](workflow-example.md) |

Rules that apply to all of them:

- Fan-out is automatic: an actor reached by N edges runs N times. Use `fork`/`forkJoin` only to join.
- Every actor between `split` and `collect`, or `fork` and `forkJoin`, needs `continueOnError: true`
  ([why](error-handling.md#joins-hang-when-a-branch-fails)).
- Read a joined result through the join: `msg.<forkJoinMsgVar>.<sourceMsgVar>`.

## Pick a pattern by the request's wording

| Wording | Pattern |
|---|---|
| "combine", "merge", "all together" | Multi-source aggregation |
| "notify", "log", "trigger external" | Fire-and-forget |
| "if", "based on", "depending on" | Conditional branching |
| "then", "after that", "next" | Sequential pipeline |
| "each", "every", "batch", "list of" | Split and collect |
| "might fail", "optional", "fallback" | Error handling |
| "approve", "wait for a reply" | Human approval |

```
Parallel paths?
├── No → Sequential pipeline, or Conditional branching
└── Yes → Does a later step need the results of all paths?
    ├── No → Fire-and-forget
    └── Yes → Is it one array processed item by item?
        ├── Yes → Split and collect
        └── No → Multi-source aggregation (fork/forkJoin)
```
