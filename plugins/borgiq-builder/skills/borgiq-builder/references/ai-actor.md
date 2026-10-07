# AI Actor Reference

The AiActor makes one LLM call per message and returns text, structured JSON, or tool calls it does not execute. Read
it to configure one. Models are in [ai-models.md](ai-models.md), schema design for `outputSchema` in the
`borgiq-json-schema-builder` skill, exact types in [typescript/actorSchemas/task/ai.md](typescript/actorSchemas/task/ai.md).
For a loop that calls tools, use an [AiAgentActor](ai-agent-actor.md).

## Contents

- [Configuration Structure](#configuration-structure)
- [Options Reference](#options-reference)
- [Results Object](#results-object)
- [Structured Output](#structured-output)
- [Message Format](#message-format)
- [Tools (Function Calling)](#tools-function-calling)

## Configuration Structure

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  ACTR01example:
    type: AiActor
    version: 1
    name: Summarize text with AI
    msgVar: summarize_text_with_ai
    description: Use AI to summarize provided text
    isActive: true
    continueOnError: false
    enableLTM: false
    enableSTM: false
    sourcePorts:
      - id: SPRTdefault
    configuration:
      inputs:
        text: ''
        maxLength: 100
      options:
        model: claude-haiku-4-5
        systemPrompt: |
          You are a text summarization assistant.
          Provide concise summaries while preserving key information.
        prompt: |
          Summarize the following text in no more than ${{ inputs.maxLength }} words:

          ${{ inputs.text }}
        maxTokens: 500
    schemas:
      inputs:
        type: object
        properties:
          text:
            type: string
            title: Text to Summarize
            description: The text content to summarize
          maxLength:
            type: integer
            title: Max Length
            description: Maximum words in summary
            default: 100
        required:
          - text
    id: ACTR01example
    position:
      x: 0
      'y': 0
    edges: {}
```

## Options Reference

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `model` | string | `gpt-6-luna` | A known model id, `<provider>/<model-id>`, or `<custom-provider-slug>/<model-id>` for a workspace [custom provider](custom-ai-providers.md). Set it: start with `claude-haiku-4-5` and step up only when the task needs more reasoning ([ai-models.md](ai-models.md)) |
| `prompt` | string | — | The prompt, sent as the last user message |
| `systemPrompt` | string | — | Background context and instructions: the model's role, the task, the output rules |
| `messages` | array | — | Previous conversation messages (multi-turn); `prompt` is appended after them |
| `temperature` | number (0–2) | — (the editor fills in 0.2) | Sampling temperature; lower is more deterministic. Unset, the model's default applies. Claude models take at most 1 (a higher value is sent as 1). Ignored by models that take none: OpenAI reasoning models (o-series, GPT-5 and later, so the default `gpt-6-luna`) and Claude Opus 4.7 and later, Sonnet 5, Fable 5 and Haiku 5.5 |
| `maxTokens` | integer | — (the editor fills in 10000) | Maximum tokens to generate |
| `jsonMode` | boolean | false | Return the response as a JSON object |
| `outputSchema` | object | — | JSON Schema the response must match; overrides `jsonMode` |
| `tools` | array | — | Tool definitions the model may call ([below](#tools-function-calling)) |
| `maxRetries` | integer | — (the editor fills in 0) | Retries after a failed attempt; `0` makes a single attempt. Unset, the provider SDK's default applies (2) |
| `emitInput` | boolean | false | Include the input messages in `meta.input`, for debugging |

Either `prompt` or `messages` must be provided. A failed call fails the job; rate-limit errors are retried first. With
`continueOnError: true` the error goes to the connected actors instead, as `err.<msgVar>`: see
[error-handling.md](error-handling.md).

## Results Object

| Field | Description |
|-------|-------------|
| `response` | The generated text, or the parsed object with `jsonMode` / `outputSchema` |
| `toolCalls` | Tool calls the model made, when `tools` were given (`toolCallId`, `toolName`, `input`) |
| `meta.input` | Input messages sent to the model (with `emitInput: true`) |
| `meta.model` | The model used |
| `meta.usage` | `promptTokens`, `completionTokens`, `totalTokens`: watch them to control cost |
| `meta.fromCache` | Whether the response came from the cache: an identical call is answered from a cache |

## Structured Output

- Use `outputSchema` whenever the response feeds another actor, a UI or a file. It overrides `jsonMode`, so you need
  not set both; `jsonMode` alone returns some JSON object with no contract.
- Put content that is used directly (code, HTML, an email body, a single value) in a string property, and tell the
  model in `systemPrompt` to return only that content: no markdown code fences (no triple backticks) and no
  explanations. Otherwise models wrap code and HTML in fences or add prose that breaks downstream processing.
- Require only the fields you need, and still validate the content downstream.

```yaml
options:
  model: claude-haiku-4-5
  systemPrompt: |
    You are an expert researcher. Today is ${{ new Date().toISOString() }}.
  prompt: |
    Generate at most ${{ inputs.numQueries }} distinct search queries to research: ${{ inputs.query }}
  outputSchema:
    type: object
    properties:
      queries:
        type: array
        description: Search queries, at most ${{ inputs.numQueries }}
        items:
          type: object
          properties:
            query:
              type: string
              description: The search query
            researchGoal:
              type: string
              description: What this query should find out, and where to go next
          required:
            - query
            - researchGoal
    required:
      - queries
```

`response` is then `{ queries: [{ query, researchGoal }, …] }`. `${{ }}` works inside the schema too.

## Message Format

```yaml
messages:
  - role: user
    content: What is the capital of France?
  - role: assistant
    content: The capital of France is Paris.
  - role: user                        # content can be a list of parts
    content:
      - type: text
        text: What's in this image?
      - type: image
        image: ${{ inputs.imageFile }}
  - role: tool                        # the result of a tool call the model made
    content:
      - type: tool-result
        toolCallId: call_abc123
        toolName: get_weather
        output:
          type: json
          value:
            temperature: 22
            conditions: sunny
```

For a multi-turn conversation, pass the history in `messages` (e.g. `${{ inputs.conversationHistory }}`) and the new
user message in `prompt`.

## Tools (Function Calling)

The model can answer with tool calls instead of text. The AiActor only returns them in `toolCalls`: run them
yourself and send the results back as `role: tool` messages, or use an AiAgentActor, which runs its tools in a loop.

```yaml
options:
  model: claude-haiku-4-5
  systemPrompt: You are a helpful assistant with access to tools.
  prompt: ${{ inputs.userRequest }}
  tools:
    - name: get_weather
      description: Get the current weather for a location
      jsonSchemaParameters:
        type: object
        properties:
          location:
            type: string
            description: The city and country
          unit:
            type: string
            enum:
              - celsius
              - fahrenheit
        required:
          - location
```
