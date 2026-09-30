# AI Router Actor Reference

The AiRouterActor classifies its input with an LLM and emits the message on the matching route port: an AiActor and a
RouterActor in one. Use it instead of the pair when input must be sorted into categories that different downstream
flows handle. Exact types: [typescript/actorSchemas/task/aiRouter.md](typescript/actorSchemas/task/aiRouter.md).

## Rules

- One source port per route. Each port's `name` is the key of its entry in `routeDescriptions`; generate the port IDs
  with `borgiq generate id sourceport`.
- Always include the default port `SPRTdefault` as the fallback for unmatched input, and leave its name out of
  `routeDescriptions` (a default port's name there fails validation as reserved).
- Write specific, mutually exclusive route descriptions (for `singleRoute`); 2–6 routes work best, and more routes
  reduce accuracy. Test ambiguous inputs.
- Pass `input: ${{ Q.toJSON(inputs) }}`: it serializes every schema-backed input as one JSON object, so the model
  classifies on complete, structured context rather than on hand-concatenated fields.
- Set `model` ([ai-models.md](ai-models.md)): start with `claude-haiku-4-5`, and upgrade only if classification is not
  accurate enough.

## Configuration Structure

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  ACTR01example:
    type: AiRouterActor
    version: 1
    name: Support Ticket Router
    msgVar: support_ticket_router
    description: Routes support tickets to appropriate teams based on content
    isActive: true
    continueOnError: false
    enableLTM: false
    enableSTM: false
    sourcePorts:
      - id: SPRTjyka6ql
        name: Sales
        description: Sales related questions
      - id: SPRTn7gduk5
        name: Support
        description: Support related questions
      - id: SPRTdefault
        name: Others
        description: Fallback route
    configuration:
      inputs:
        message: ''
      options:
        model: claude-haiku-4-5
        input: ${{ Q.toJSON(inputs) }}
        emitType: singleRoute
        routeDescriptions:
          Sales: Choose this route if the input is related to Sales related questions
          Support: Choose this route if the input is related to Support
    schemas:
      inputs:
        type: object
        properties:
          message:
            type: string
            title: Message
            description: The message to classify and route
        required:
          - message
    id: ACTR01example
    position:
      x: 0
      'y': 0
    edges: {}
```

## Options Reference

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `model` | string | No | Any [AI model reference](ai-models.md): a known id, `<provider>/<model-id>`, or `<custom-provider-slug>/<model-id>` for a workspace [custom provider](custom-ai-providers.md). Unset: `gpt-6-luna` |
| `input` | any | Yes | The input to classify |
| `emitType` | `singleRoute` \| `multiRoute` | No | `singleRoute` (the default, most common) emits on exactly one route; `multiRoute` emits on every route the input matches |
| `routeDescriptions` | object | Yes | Route name (a source port's `name`) → when to choose that route |
| `emitInput` | boolean | No | Include the model's input messages in `meta.input` |

Use `multiRoute` when an input can belong to several categories:

```yaml
options:
  model: claude-haiku-4-5
  input: ${{ Q.toJSON(inputs) }}
  emitType: multiRoute
  routeDescriptions:
    Urgent: Content indicates urgency or time-sensitivity
    Confidential: Content contains sensitive or confidential information
    ActionRequired: Content requires a response or action
```

## Results Object

| Field | Description |
|-------|-------------|
| `route` | The name of the port the message was emitted from |
| `meta.model` | The model used to determine the route |
| `meta.usage` | Token usage: `promptTokens`, `completionTokens`, `totalTokens` |
| `meta.fromCache` | Whether the response was fetched from cache |
| `meta.input` | The input messages (with `emitInput: true`) |
