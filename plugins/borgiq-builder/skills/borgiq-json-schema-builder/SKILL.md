---
name: borgiq-json-schema-builder
description: Design JSON schemas for BorgIQ — AI Actor outputSchema, AI Agent tool input schemas, Collection actor item schemas, Callable sub-flow contracts, and reusable actor.schemas.inputs. Use whenever a non-trivial structured data contract needs to be defined for any BorgIQ actor that consumes or produces typed data. Triggers on "JSON schema", "outputSchema", "structured output", "tool input schema", "collection schema", "callable response schema", "AI structured output", "agent output contract".
---

# BorgIQ JSON Schema Builder

Design the JSON schemas at every contract boundary of a BorgIQ workflow. This spoke is **cross-cutting**: other spokes hand off here when their schema work goes beyond the trivial. Pair with `borgiq-builder` (hub) for wiring; with `borgiq-agent-builder` for tool design; with `borgiq-form-builder` when fields cross between forms and back-end contracts.

## Mental model

Schemas define the *shape* of data at every contract boundary: AI output, stored items, agent tool parameters, sub-flow contracts, reusable actor interfaces. Tight schemas reduce errors, guide AI behavior and document intent; loose or missing ones cause LLM hallucination, storage mismatches and brittle integrations.

BorgIQ uses standard JSON Schema (draft 7 / 2020-12) with one local convention: when you need an object whose properties aren't statically known, use **`type: any`** rather than `type: object` with an empty `properties` map (the hub's [Generation Instructions](../borgiq-builder/SKILL.md#generation-instructions)).

## The six places schemas appear

| Where | Purpose | Validated by | Guidance |
|---|---|---|---|
| **AiActor `outputSchema`** | Tells the LLM what JSON to produce | The model itself, via constrained decoding | Keep tight — every `required` field is something the model must produce. Use enums to constrain. |
| **AiAgentActor tool `schemas.inputs`** | Declares what each tool accepts; the agent reads this to choose tools | The agent, when selecting and invoking tools | The LLM reads each field's `description`: write it as docs the model will use. |
| **CollectionActor item schema** | Shape of stored items, queries, indexes | **Nothing** — collections have no schema; any JSON `value` is stored | Design keys and labels for the read patterns *first* ([collection design](../borgiq-builder/references/collection-design.md)). |
| **CallableTriggerActor `schemas.inputs`** | Input contract of a sub-flow — the payload callers must send | **Nothing at runtime** — the editor generates the CallFlowActor payload form from it; the payload passes into the sub-flow unvalidated | The sub-flow's function signature. Mirror in `configuration.inputs`; keep the caller `payload`, this schema, and downstream `msg.*` reads in lockstep by discipline — drift fails silently, not fast. |
| **CallableResponseActor response schema** | Output contract of a sub-flow | CallFlowActor when consuming the response | Parents depend on this. Enums + clear types reduce caller surprise. |
| **Actor-level `schemas.inputs`** | Reusable input interface for any actor | Framework at wire-in | Mirrors what `inputs:` declares; enables templatization and UI generation. |

> **Structured output *from* an agent:** AiAgentActor has no `outputSchema` — its done port carries `result` (free text) plus workspace/session zips. For structured output, feed `msg.<agent>.result` into a downstream **AiActor with an `outputSchema`** (extraction pass), or have the agent write a JSON file to its workspace and parse it from `outputZipFile`.

## Schema design principles — AI (AiActor, AiAgentActor)

1. **Tight beats loose.** Every `required` field is a chance for the LLM to fail. Require the minimum; add optionals only when the task genuinely sometimes lacks them.
2. **Enums over free strings.** `enum: [pending, processing, completed, failed]` constrains the output space; `type: string` lets the model invent values.
3. **Write field names and descriptions for the LLM.** The model reads them. `sentiment: { type: string, enum: [positive, negative, neutral], description: "Emotional tone of the text" }` is clearer than `s: { type: string }`.
4. **Stay flat.** Deep nesting confuses LLMs and complicates Collection partial updates (which replace the entire top-level field). Two or three levels at most.
5. **Use `$ref` for shared sub-schemas** (an `address` for both `shipping` and `billing`, below): less drift, consistent validation.
6. **Don't over-engineer for hypothetical extensibility.** Build today's contract; unused future fields cost more than they save.
7. **Set `additionalProperties: false` for output schemas.** Without it (or with `true`), the LLM may invent extra fields.

## Schema design principles — storage (CollectionActor)

Keys, labels, `$meta` and capacity are designed in [collection-design.md](../borgiq-builder/references/collection-design.md); read it first. For the item schema:

1. **Nothing validates items:** a collection has no schema, so the writing code enforces yours.
2. **List every read pattern, then design the keys for them.** The platform owns the partition key; your `key` is the sort key ([key prefixes](../borgiq-builder/references/collection-design.md#key-prefix-modeling)).
3. **Labels are a separate `labels` map**, not `value` fields; only labels are queryable ([labels](../borgiq-builder/references/collection-design.md#labels)).
4. **Keep mutable fields flat:** `updateItem` replaces a whole top-level object ([semantics](../borgiq-builder/references/collection-actor.md#semantics)).
5. **TTL goes in `options.ttl` on `putItem`** (a top-level `ttl` is dropped), for session tokens, callback ids and transient state.
6. **Denormalize for reads:** a query that needs name, email and status finds them in one item, not three.

## Storage / API contract checklist — collection-backed apps

When an app (a React app frontend + Collection storage + backend endpoints) is on the table, define the contracts in this order, *before* picking actors:

- [ ] **Define endpoint request/response schemas first.** For each endpoint the UI calls, write the request shape (query/body) and the response shape. Settle this contract the frontend codes against before deciding whether the endpoint is a webhook-enabled UniversalTriggerActor or a WebhookTriggerActor flow. Actor choice follows the contract, not the other way around (see the hub's [Universal Trigger vs Webhook Trigger](../borgiq-builder/SKILL.md#universal-trigger-vs-webhook-trigger-http-endpoints) matrix).
- [ ] **Define a Collection item schema and key strategy per read pattern** (by id, by owner, by status, recent-first; see [storage principles](#schema-design-principles--storage-collectionactor)). A read the keys don't support means a redesign.
- [ ] **Keep the AI output schema separate from the persisted item schema.** When a generation endpoint feeds storage, the AiActor `outputSchema` (what the model must produce) and the Collection item schema (what's persisted) are *different contracts*: map one to the other explicitly. The model's schema stays tight for decoding; the stored one carries the keys, labels, TTL and timestamps the model never produces.

The endpoint request/response schemas are the contracts the `borgiq-react-app-builder` spoke wires with `useEndpoint`: design them together. The item schema and keys also fix how the collection is **provisioned** (its labels, its seed rows): [collection-migrations.md](../borgiq-builder/references/collection-migrations.md).

## Common patterns

**Tight AiActor outputSchema:**
```yaml
outputSchema:
  type: object
  additionalProperties: false
  properties:
    sentiment:
      type: string
      enum: [positive, negative, neutral]
      description: Emotional tone of the text
    confidence:
      type: number
      description: Confidence score 0.0–1.0
    keywords:
      type: array
      items: { type: string }
      description: 2–5 key themes
  required: [sentiment, confidence]
```

**Tool input schema for AiAgentActor:**
```yaml
schemas:
  inputs:
    type: object
    properties:
      query:
        type: string
        description: Specific search query — avoid vague terms
      limit:
        type: integer
        default: 10
        description: Max results to return
    required: [query]
```

**Collection item — flat, denormalized, query-friendly** (`putItem` fields):
```yaml
key: user:user-001
value:
  email: alice@example.com
  firstName: Alice
  status: active           # value field: not queryable
  lastLogin: 2026-03-19T10:00:00Z
labels:
  status: active           # queryable: expression active, options.label status
```

**`$ref` for a shared shape:**
```yaml
definitions:
  address:
    type: object
    required: [city, state, zip]
    properties:
      city: { type: string }
      state: { type: string }
      zip: { type: string }
properties:
  shipping: { $ref: '#/definitions/address' }
  billing:  { $ref: '#/definitions/address' }
```

## Anti-patterns

1. **`additionalProperties: true` on AI output schemas.** Lets the LLM invent fields. Set to `false` (or omit and rely on validator default) to lock the surface.
2. **Marking every field optional then complaining the LLM skips important ones.** Optional signals "model can skip"; required signals "model must produce". Match `required` to actual intent.
3. **`type: object` with empty `properties` instead of `type: any`.** The BorgIQ convention is `type: any` for truly open-ended objects (the hub's [Generation Instructions](../borgiq-builder/SKILL.md#generation-instructions)). Clearer to readers and validators.
4. **`oneOf: [{type: string}, {type: string}]` where `enum` would do.** `oneOf` is for shape unions; `enum` is for fixed-choice strings. Use the simpler construct.
5. **Drift between tool `schemas.inputs` declaration and the tool's actual `inputs:` mapping.** The agent passes what the schema says; if the tool body reads other field names, calls silently misroute. Keep the two in lockstep.

## References

| File | What's inside |
|---|---|
| [`references/ai-actor.md`](../borgiq-builder/references/ai-actor.md) | `outputSchema` examples, structured output patterns for code/HTML generation |
| [`references/ai-agent-actor.md`](../borgiq-builder/references/ai-agent-actor.md) | Tool input schemas, `${{aiInput}}` pattern |
| [`references/collection-actor.md`](../borgiq-builder/references/collection-actor.md) | CollectionActor options, queue pattern, concurrent updates, nested-object replacement |
| [`references/collection-design.md`](../borgiq-builder/references/collection-design.md) | Key design, `$meta`, labels, capacity |
| [`references/callable-response-actor.md`](../borgiq-builder/references/callable-response-actor.md) | Sub-flow response schema contracts |

## When to hand off to other spokes

| Customer ask | Hand off to |
|---|---|
| "Wire this schema into a tool / connect to an agent / design the agent loop" | `borgiq-agent-builder` |
| "Validate this form field" / "build a form that produces this shape" | `borgiq-form-builder` (form components have their own schema model) |
| "Webhook response contract for a custom UI" | `borgiq-react-app-builder` (this spoke for the schema; react-app-builder for the frontend) |
| msgVar wiring, `inputs` vs `vars`, deploy | Hub: `borgiq-builder` |
