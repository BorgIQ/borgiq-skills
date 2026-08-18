---
name: borgiq-json-schema-builder
description: Design JSON schemas for BorgIQ — AI Actor outputSchema, AI Agent tool input schemas, Collection actor item schemas, Callable sub-flow contracts, and reusable actor.schemas.inputs. Use whenever a non-trivial structured data contract needs to be defined for any BorgIQ actor that consumes or produces typed data. Triggers on "JSON schema", "outputSchema", "structured output", "tool input schema", "collection schema", "callable response schema", "AI structured output", "agent output contract".
---

# BorgIQ JSON Schema Builder

Design the JSON schemas that sit at every contract boundary in a BorgIQ workflow. This spoke is **cross-cutting** — other spokes hand off here when their schema work goes beyond the trivial. Pair with `borgiq-builder` (hub) for wiring; with `borgiq-agent-builder` for tool design; with `borgiq-form-builder` when fields cross between forms and back-end contracts.

## Mental model

Schemas define the *shape* of data at every contract boundary in BorgIQ — where AI models produce output, where storage items take form, where agent tools receive parameters, where sub-flows declare contracts, where actor interfaces are reused. Tight schemas reduce errors, guide AI behavior, and document intent. Loose or missing schemas cause LLM hallucination, storage mismatches, and integration brittleness.

BorgIQ uses standard JSON Schema (draft 7 / 2020-12) with one local convention: when you need an object whose properties aren't statically known, use **`type: any`** rather than `type: object` with an empty `properties` map. (This is generation rule #12 in the hub SKILL.md.)

## The six places schemas appear

| Where | Purpose | Validated by | Guidance |
|---|---|---|---|
| **AiActor `outputSchema`** | Tells the LLM what JSON to produce | The model itself, via constrained decoding | Keep tight — every `required` field is something the model must produce. Use enums to constrain. |
| **AiAgentActor tool `schemas.inputs`** | Declares what each tool accepts; the agent reads this to choose tools | The agent, when selecting and invoking tools | Field `description` is read by the LLM — write it like docs the model will actually use. |
| **CollectionActor item schema** | Shape of stored items, queries, indexes | CollectionActor at `putItem` / `updateItem`; reads validate on retrieval | Design for query patterns *first*, not just current data shape. Plan key strategy upfront. |
| **CallableTriggerActor `schemas.inputs`** | Input contract of a sub-flow — the payload callers must send | **Nothing at runtime** — the editor generates the CallFlowActor payload form from it; the payload passes into the sub-flow unvalidated | The sub-flow's function signature. Mirror in `configuration.inputs`; keep the caller `payload`, this schema, and downstream `msg.*` reads in lockstep by discipline — drift fails silently, not fast. |
| **CallableResponseActor response schema** | Output contract of a sub-flow | CallFlowActor when consuming the response | Parents depend on this. Enums + clear types reduce caller surprise. |
| **Actor-level `schemas.inputs`** | Reusable input interface for any actor | Framework at wire-in | Mirrors what `inputs:` declares; enables templatization and UI generation. |

> **Structured output *from* an agent:** AiAgentActor has no `outputSchema` — its done port carries `result` (free text) plus workspace/session zips. To get a structured contract out of an agent run, feed `msg.<agent>.result` into a downstream **AiActor with an `outputSchema`** (extraction pass), or have the agent write a JSON file to its workspace and parse it from `outputZipFile`.

## Schema design principles — AI (AiActor, AiAgentActor)

1. **Tight beats loose.** Every `required` field is a chance for the LLM to fail. Start with the minimum required set; add optionals only if the task genuinely sometimes lacks them.
2. **Enums over free strings.** `enum: [pending, processing, completed, failed]` constrains the output space; `type: string` lets the model invent values.
3. **Write field names and descriptions for the LLM.** The model reads them. `sentiment: { type: string, enum: [positive, negative, neutral], description: "Emotional tone of the text" }` is dramatically clearer than `s: { type: string }`.
4. **Stay flat.** Deep nesting confuses LLMs and complicates Collection partial updates (which replace the entire top-level field). Two or three levels at most; use `$ref` to share shapes.
5. **Use `$ref` for shared sub-schemas.** Define an `address` once, reference it from `shipping` and `billing`. Less drift, consistent validation.
6. **Don't over-engineer for hypothetical extensibility.** Build for today's contract. Future fields cost more than they save if they're not currently used.
7. **Set `additionalProperties: false` for output schemas.** Without it (or with `true`), the LLM may invent extra fields. Lock the output surface.

## Schema design principles — storage (CollectionActor)

1. **Model for query patterns, not just current data.** Before designing the schema, list every read pattern. Add label fields, sort prefixes, and TTL where needed. A schema that satisfies writes but doesn't support reads is a redesign waiting to happen.
2. **Plan partition / sort key strategy upfront.** Keys are lexicographically sorted. Hierarchical keys (`user:U001:profile`, `user:U001:session:S123`) enable cheap prefix scans.
3. **Flat top-level fields for partial updates.** `updateItem` replaces an entire top-level field if it's an object. Keep mutable fields flat.
4. **TTL for ephemeral data.** Set `ttl: <seconds>` on session tokens, callback IDs, transient state.
5. **Denormalize for read efficiency.** A query that needs name + email + status should find them in one item, not three.

## Storage / API contract checklist — collection-backed apps

When an app (a React app frontend + Collection storage + backend endpoints) is on the table, define the contracts in this order, *before* picking actors:

- [ ] **Define endpoint request/response schemas first.** For each endpoint the UI calls, write the request shape (query/body) and the response shape. These are the contract the frontend codes against — settle them before deciding whether the endpoint is a webhook-enabled UniversalTriggerActor or a WebhookTriggerActor flow. Actor choice follows the contract, not the other way around (see the hub's [Universal Trigger vs Webhook Trigger](../borgiq-builder/SKILL.md#universal-trigger-vs-webhook-trigger-http-endpoints) matrix).
- [ ] **Define a Collection item schema and key strategy per read pattern.** List every way the app reads the data (by id, by owner, by status, recent-first), then design the keys and label fields to serve those reads (see [storage principles](#schema-design-principles--storage-collectionactor)). One read pattern the keys don't support is a redesign waiting to happen.
- [ ] **Keep the AI output schema separate from the persisted item schema.** When a generation endpoint feeds storage, the AiActor `outputSchema` (what the model must produce) and the Collection item schema (what's persisted) are *different contracts*. Map model output → stored item explicitly; don't reuse one schema for both. The model's schema stays tight for decoding; the stored schema carries keys, labels, TTL, and timestamps the model never produces.

The endpoint request/response schemas are the same contracts the `borgiq-react-app-builder` spoke wires with `useEndpoint` — design them together. Once the item schema and key strategy are set, they also define how each collection must be **provisioned** (created with the right labels, seeded with defaults) — see [collection-migrations.md](../borgiq-builder/references/collection-migrations.md).

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

**Collection item — flat, denormalized, query-friendly:**
```yaml
value:
  userId: user-001
  email: alice@example.com
  firstName: Alice
  status: active           # label query: status=active
  lastLogin: 2026-03-19T10:00:00Z
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

**Enum vs free string — when in doubt, enum:**
```yaml
# Loose — model can invent values
status: { type: string }

# Tight — model is constrained
status:
  type: string
  enum: [pending, processing, completed, failed]
```

## Anti-patterns

1. **`additionalProperties: true` on AI output schemas.** Lets the LLM invent fields. Set to `false` (or omit and rely on validator default) to lock the surface.
2. **Marking every field optional then complaining the LLM skips important ones.** Optional signals "model can skip"; required signals "model must produce". Match `required` to actual intent.
3. **`type: object` with empty `properties` instead of `type: any`.** The BorgIQ convention is `type: any` for truly open-ended objects (hub SKILL.md generation rule #12). Clearer to readers and validators.
4. **`oneOf: [{type: string}, {type: string}]` where `enum` would do.** `oneOf` is for shape unions; `enum` is for fixed-choice strings. Use the simpler construct.
5. **Drift between tool `schemas.inputs` declaration and the tool's actual `inputs:` mapping.** The agent reads the schema and infers what to pass; if the tool body uses different field names, calls silently misroute. Keep declaration and implementation in lockstep.

## References

| File | What's inside |
|---|---|
| [`references/ai-actor.md`](../borgiq-builder/references/ai-actor.md) | `outputSchema` examples, structured output patterns for code/HTML generation |
| [`references/ai-agent-actor.md`](../borgiq-builder/references/ai-agent-actor.md) | Tool input schemas, `${{aiInput}}` pattern |
| [`references/collection-actor.md`](../borgiq-builder/references/collection-actor.md) | Item schema patterns, queue/index designs, key strategies |
| [`references/collection-api.md`](../borgiq-builder/references/collection-api.md) | DynamoDB mapping, concurrent updates, nested-object replacement behavior |
| [`references/callable-response-actor.md`](../borgiq-builder/references/callable-response-actor.md) | Sub-flow response schema contracts |

## When to hand off to other spokes

| Customer ask | Hand off to |
|---|---|
| "Wire this schema into a tool / connect to an agent / design the agent loop" | `borgiq-agent-builder` |
| "Validate this form field" / "build a form that produces this shape" | `borgiq-form-builder` (form components have their own schema model) |
| "Webhook response contract for a custom UI" | `borgiq-react-app-builder` (this spoke for the schema; react-app-builder for the frontend) |
| msgVar wiring, `inputs` vs `vars`, deploy | Hub: `borgiq-builder` |
