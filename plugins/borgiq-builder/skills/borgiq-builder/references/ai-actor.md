# AI Actor Reference

The AiActor invokes AI models (LLMs) to generate responses, process text, and perform AI-powered tasks within BorgIQ workflows.

## Table of Contents

- [Configuration Structure](#configuration-structure)
- [Options Reference](#options-reference)
- [TypeScript Schema Definition](#typescript-schema-definition)
- [Available Models](#available-models)
- [Results Object](#results-object)
- [Common Patterns](#common-patterns)
- [Message Format](#message-format)
- [Temperature Guide](#temperature-guide)
- [Input Schemas](#input-schemas)
- [Error Handling](#error-handling)
- [Direct Response Usage](#direct-response-usage)
- [Best Practices](#best-practices)
- [Examples](#examples)

## Configuration Structure

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  ACTR01xxxxx:
    type: AiActor
    version: 1
    name: Actor Name Here
    msgVar: actor_name_here
    description: What this actor does
    isActive: true
    continueOnError: false
    enableLTM: false
    enableSTM: false
    sourcePorts:
      - id: SPRTdefault
    configuration:
      inputs:
        key: value
      options:
        model: claude-haiku-4-5
        systemPrompt: You are a helpful assistant...
        prompt: ${{ inputs.userPrompt }}
        temperature: 0.7
        maxTokens: 1000
        jsonMode: false
        maxRetries: 0
        emitInput: false
    schemas:
      inputs:
        type: object
        properties:
          userPrompt:
            type: string
            title: User Prompt
            description: The prompt to send to the AI model
        required:
          - userPrompt
    id: ACTR01xxxxx
    position:
      x: 0
      'y': 0
    edges: {}
```

## Options Reference

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `model` | string | gpt-4o-mini | The AI model to use |
| `prompt` | string | - | The prompt to send to the AI model |
| `systemPrompt` | string | - | Background context/instructions for the AI model |
| `messages` | array | - | Previous conversation messages (for multi-turn) |
| `temperature` | number | 0.7 | Creativity level (0-1, lower = more deterministic) |
| `maxTokens` | integer | - | Maximum tokens to generate |
| `jsonMode` | boolean | false | Output response as JSON object |
| `outputSchema` | object | - | JSON Schema for structured output (overrides jsonMode) |
| `tools` | array | - | Tools/functions the AI can call |
| `maxRetries` | integer | 0 | Retry attempts on failure |
| `emitInput` | boolean | false | Include input messages in output |

**Note:** Either `prompt` or `messages` must be provided.

## TypeScript Schema Definition

The complete TypeScript schema for AiActor options:

```typescript
import { z } from 'zod';

/** The options for the AiActor */
export const AiActorOptionsSchema = z.object({
  model: z.enum(AiModel).nullish()
    .describe('The model to use for the AI provider. Defaults to gpt-4o-mini if not provided'),
  prompt: z.string().nullish()
    .describe('The prompt to send to the AI model to generate a response'),
  temperature: z.number().min(0).max(1).nullish()
    .describe('The temperature to use for the AI model (0-1)'),
  maxTokens: z.number().int().positive().nullish()
    .describe('The maximum number of tokens to generate'),
  systemPrompt: z.string().nullish()
    .describe('The system prompt to provide as a background information to the AI model'),
  tools: z.array(z.object({
    name: z.string(),
    description: z.string(),
    jsonSchemaParameters: z.any().nullish()
      .describe('The parameters of the tool as a json schema'),
  })).nullish()
    .describe('The tools to use for the AI model'),
  messages: z.array(BIQAiMessageSchema).nullish()
    .describe('The previous messages to provide to the AI model'),
  maxRetries: z.number().int().positive().nullish()
    .describe('The maximum number of retries to attempt if the AI model fails'),
  outputSchema: z.any().nullish()
    .describe('The json schema to use for the AI model output, overrides jsonMode if provided'),
  jsonMode: z.boolean().nullish()
    .describe('Whether to output the response as a json object'),
  emitInput: z.boolean().nullish()
    .describe('Whether to emit the input messages to the AI model'),
}).superRefine((data, ctx) => {
  if (!data.prompt && !data.messages) {
    ctx.addIssue({
      code: 'custom',
      message: 'Either prompt or messages must be provided',
    });
  }
});

/** The response schema for the AiActor */
export const AiActorResultSchema = z.object({
  response: z.any()
    .describe('The generated content from the AI model'),
  toolCalls: z.array(AiToolCallSchema).nullish()
    .describe('The tool calls made by the AI model'),
  meta: z.object({
    input: z.array(z.union([BIQAiMessageSchema, z.object({
      role: z.literal('system'),
      content: z.string(),
    })])).nullish()
      .describe('The input messages to the AI model'),
    model: z.string()
      .describe('The model used to generate the response'),
    usage: z.object({
      promptTokens: z.number().int()
        .describe('The number of tokens in the prompt'),
      completionTokens: z.number().int()
        .describe('The number of tokens in the completion'),
      totalTokens: z.number().int()
        .describe('The total number of tokens used'),
    }),
    fromCache: z.boolean()
      .describe('Whether the response was fetched from the cache'),
  }),
});
```

## Available Models

**Default:** Always start with `claude-haiku-4-5` unless the task requires more advanced reasoning capabilities.

| Provider | Models |
|----------|--------|
| Anthropic | claude-opus-4-6, claude-sonnet-4-6, claude-opus-4-5, claude-sonnet-4-5, claude-haiku-4-5 |
| Google | gemini-2.5-pro, gemini-2.5-flash, gemini-3-pro-preview, gemini-3-flash-preview |
| OpenAI | gpt-5.4, gpt-5.4-mini, gpt-5.4-nano, gpt-5.4-pro, gpt-5.2, gpt-5.2-pro, gpt-5.1, gpt-5, gpt-5-mini, gpt-5-nano, gpt-4.1, gpt-4.1-mini, gpt-4.1-nano, o3, o3-mini, o3-pro, o4-mini |
| xAI | grok-4, grok-4-fast-reasoning, grok-4-fast-non-reasoning, grok-code-fast-1 |

**OpenAI model tiers:**
- **gpt-5.4** — Latest flagship (128K output, $2.50/$15 per M tokens). Best for complex reasoning.
- **gpt-5.4-mini** — Cost-effective mid-tier ($0.75/$4.50 per M tokens). Good default for most tasks.
- **gpt-5.4-nano** — Ultra-cheap ($0.20/$1.25 per M tokens). Best for simple classification/extraction.
- **gpt-5.4-pro** — Extended thinking ($30/$180 per M tokens). For research-grade tasks.
- **o3/o3-pro/o4-mini** — Reasoning models with chain-of-thought. Use for math, code, logic.

## Results Object

After the AI actor executes, the `results` object contains:

```json
{
  "response": "The generated text or structured output...",
  "toolCalls": [...],
  "meta": {
    "input": [...],
    "model": "gpt-4o-mini",
    "usage": {
      "promptTokens": 150,
      "completionTokens": 200,
      "totalTokens": 350
    },
    "fromCache": false
  }
}
```

| Field | Description |
|-------|-------------|
| `response` | The generated content from the AI model |
| `toolCalls` | Array of tool calls made by the AI (if tools were provided) |
| `meta.input` | Input messages sent to the model (if `emitInput: true`) |
| `meta.model` | The model that was used |
| `meta.usage` | Token usage statistics |
| `meta.fromCache` | Whether the response was cached |

## Common Patterns

### Simple Text Generation

```yaml
options:
  model: claude-haiku-4-5
  systemPrompt: You are a helpful assistant that summarizes text concisely.
  prompt: ${{ inputs.textToSummarize }}
  temperature: 0.3
  maxTokens: 500
```

### Structured Output with JSON Mode

```yaml
options:
  model: claude-haiku-4-5
  systemPrompt: Extract key information from the provided text.
  prompt: ${{ inputs.document }}
  jsonMode: true
  temperature: 0
```

### Structured Output with Schema

```yaml
options:
  model: claude-haiku-4-5
  systemPrompt: Analyze the sentiment of the provided text.
  prompt: ${{ inputs.text }}
  outputSchema:
    type: object
    properties:
      sentiment:
        type: string
        enum:
          - positive
          - negative
          - neutral
      confidence:
        type: number
      keywords:
        type: array
        items:
          type: string
    required:
      - sentiment
      - confidence
```

### Multi-turn Conversation

```yaml
options:
  model: claude-haiku-4-5
  systemPrompt: You are a customer support agent.
  messages: ${{ inputs.conversationHistory }}
  prompt: ${{ inputs.userMessage }}
```

### Using Tools (Function Calling)

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
    - name: search_database
      description: Search the product database
      jsonSchemaParameters:
        type: object
        properties:
          query:
            type: string
          limit:
            type: integer
        required:
          - query
```

## Message Format

Messages follow a structured format with roles:

### User Message

```yaml
messages:
  - role: user
    content: What is the capital of France?
```

### User Message with Image

```yaml
messages:
  - role: user
    content:
      - type: text
        text: What's in this image?
      - type: image
        image: ${{ inputs.imageFile }}
```

### Assistant Message

```yaml
messages:
  - role: assistant
    content: The capital of France is Paris.
```

### Tool Result Message

```yaml
messages:
  - role: tool
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

## Temperature Guide

| Temperature | Use Case |
|-------------|----------|
| 0.0 - 0.3 | Factual, deterministic responses (data extraction, classification) |
| 0.3 - 0.7 | Balanced creativity (general Q&A, summarization) |
| 0.7 - 1.0 | Creative tasks (brainstorming, creative writing) |

## Input Schemas

Define input schemas for validation and UI generation:

```yaml
schemas:
  inputs:
    type: object
    properties:
      userPrompt:
        type: string
        title: User Prompt
        description: The question or request for the AI
      context:
        type: string
        title: Context
        description: Additional context for the AI
      temperature:
        type: number
        title: Temperature
        description: Creativity level (0-1)
        default: 0.7
    required:
      - userPrompt
```

## Error Handling

There is no error handling for the AiActor. If the actor fails, the error will be emitted on the output port.

## Direct Response Usage

When the AiActor's response will be used directly (e.g., passed to another actor, rendered in UI, or saved to a file), use structured output to ensure clean, predictable formatting.

### Why Structured Output Matters

By default, LLMs may wrap code, HTML, or other content in markdown formatting (triple backticks), add explanatory text, or include other artifacts that break downstream processing. Using `jsonMode: true` or `outputSchema` forces the model to return only the requested content.

### Code/HTML Generation Pattern

When generating code, HTML, CSS, or any content that will be used directly:

```yaml
options:
  model: claude-haiku-4-5
  systemPrompt: |
    You are a code generator. Return ONLY the requested code.
    Do NOT wrap the output in markdown code blocks (no triple backticks).
    Do NOT include explanations or comments outside the code.
    Return raw, executable code only.
  prompt: |
    Generate a Python function that ${{ inputs.requirement }}
  jsonMode: true
  outputSchema:
    type: object
    properties:
      code:
        type: string
        description: The raw code without markdown formatting
    required:
      - code
  temperature: 0.2
```

### HTML Template Generation

```yaml
options:
  model: claude-haiku-4-5
  systemPrompt: |
    You generate HTML content. Return ONLY valid HTML.
    Never wrap output in ```html or ``` blocks.
    Do not include explanations before or after the HTML.
  prompt: |
    Create an HTML email template for: ${{ inputs.emailPurpose }}
  outputSchema:
    type: object
    properties:
      html:
        type: string
        description: Raw HTML content without markdown code blocks
      subject:
        type: string
        description: Suggested email subject line
    required:
      - html
      - subject
  temperature: 0.3
```

### Simple Text Extraction

When you need a single value without any wrapper:

```yaml
options:
  model: claude-haiku-4-5
  systemPrompt: |
    Extract the requested information. Return ONLY the value, nothing else.
  prompt: |
    Extract the company name from this text: ${{ inputs.text }}
  jsonMode: true
  outputSchema:
    type: object
    properties:
      value:
        type: string
    required:
      - value
  temperature: 0
```

### Key Guidelines for Direct Usage

1. **Always use `outputSchema`** - Provides the most control over response format
2. **Explicitly instruct against markdown** - Tell the model not to use triple backticks
3. **Use low temperature** - Set `temperature: 0` or `0.2` for deterministic output
4. **Be specific in system prompt** - Reinforce the formatting requirements
5. **Validate downstream** - Even with structured output, validate the content before use

### Common Pitfalls

| Problem | Solution |
|---------|----------|
| Response wrapped in \`\`\` | Add "no markdown code blocks" to system prompt + use outputSchema |
| Extra explanatory text | Use outputSchema with specific field for the content |
| Inconsistent formatting | Set temperature to 0 for deterministic output |
| JSON with extra fields | Define strict outputSchema with only required fields |

## Best Practices

1. **Use appropriate models** - Choose smaller models (gpt-4o-mini) for simple tasks, larger models for complex reasoning
2. **Set temperature intentionally** - Lower for factual tasks, higher for creative tasks
3. **Use structured output** - Use `outputSchema` when you need predictable response formats
4. **Provide clear system prompts** - Give the AI clear context about its role and task
5. **Handle tool calls** - When using tools, implement proper handling for tool call responses
6. **Monitor token usage** - Check `meta.usage` to optimize costs
7. **Use caching** - Check `meta.fromCache` to understand cache behavior
8. **Use structured output for direct usage** - When responses will be used directly (code, HTML, data), always use `jsonMode: true` with `outputSchema` and explicitly instruct the model to avoid markdown formatting

## Examples

See [ai-actor-examples.md](ai-actor-examples.md) for complete examples including:
- Generate System Prompt (prompt engineering with upstream actor data)
- Generate SERP Queries (structured output with outputSchema)
- Gmail Filter Query Generator (natural language to domain-specific syntax)

## Quick Example

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
        temperature: 0.3
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
