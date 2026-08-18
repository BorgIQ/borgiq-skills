# Deprecated AI Agent Reference (`DeprecatedAiAgent`)

> **DEPRECATED — do not create new instances.** This is the legacy orchestrator-loop AI agent that carried the `AiAgentActor` type name before mid-2026. It has **no filesystem, bash, or sessions** — it is a pure LLM loop over wired tool actors. It is hidden from the canvas palette; existing instances keep running under the type name `DeprecatedAiAgent`. For new work use the AI Agent — see [ai-agent-actor.md](ai-agent-actor.md), including its [migration table](ai-agent-actor.md#migrating-from-deprecatedaiagent).

This reference is kept for reading and debugging existing flows.

## Overview

DeprecatedAiAgent runs an LLM loop in the orchestrator: the model receives the prompt, decides which wired tool actors to call, the platform executes them, and the loop continues until the model finishes or `maxLoopCount` is reached. Tool wiring uses the same `aiAgentToolActorIds` + `${{aiInput}}` mechanism as the current AI Agent (see [ai-agent-actor.md](ai-agent-actor.md#connecting-borgiq-tools-with-aiagenttoolactorids) — the mechanism is unchanged).

## Configuration Structure

```yaml
ACTR01xxxxx:
  type: DeprecatedAiAgent
  version: 1
  name: Research Agent
  msgVar: research_agent
  sourcePorts:
    - id: SPRTdone000
      name: Done
    - id: SPRTdefault
      name: Status
  configuration:
    inputs:
      task: ${{ msg.normalize_request.researchTopic }}
    options:
      model: claude-sonnet-4-5
      systemPrompt: |
        You are a research assistant. Use the available tools.
      prompt: ${{ inputs.task }}
      temperature: 0.3
      maxTokens: 4000
      maxLoopCount: 10
    aiAgentToolActorIds:
      - ACTR01toolactor1
      - ACTR01toolactor2
  edges: {}
```

## Source Ports

| Port ID | Name | Description |
|---------|------|-------------|
| `SPRTdone000` | Done | Emits the final result when the loop completes |
| `SPRTdefault` | Status | Emits intermediate results during each loop iteration |

## Options Reference

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `model` | string | `gpt-4.1-nano` | The AI model to use (any `AiAgentModels` value) |
| `prompt` | string | — | The task/prompt for the agent |
| `systemPrompt` | string | — | Background context/instructions for the agent |
| `messages` | array | — | Previous conversation messages (for multi-turn) |
| `temperature` | number | 0.2 | Creativity level (lower = more deterministic) |
| `maxTokens` | integer | 10000 | Maximum tokens per generation |
| `maxLoopCount` | integer | unlimited | Maximum agent loop iterations |
| `enableTodoTool` | boolean | false | Expose a built-in todo/planning tool to the agent |

**Note:** either `prompt` or `messages` must be provided. There is no `outputSchema` option — the done port always carries the full chat history.

Tool wiring: `configuration.aiAgentToolActorIds` (sibling of `inputs`/`options`), tool inputs via `${{aiInput}}`, tool name = the tool actor's `msgVar`, tool actors keep empty `edges`.

## Results Object

### Done Port Result

```typescript
interface DeprecatedAiAgentLoopActorDoneResult {
  response: BIQAiMessage[];  // Full chat history: user/assistant/tool messages
  meta: {
    model: string;
    endReason: 'done' | 'max_loop_count_reached' | 'max_output';
    usage: {
      promptTokens: number;
      completionTokens: number;
      totalTokens: number;    // Cumulative across all loop iterations
    };
  };
}
```

### Status Port Result

```typescript
type DeprecatedAiAgentStatusPortResult =
  | {
      type: 'ai-agent-loop';
      response: string;
      toolCalls?: AiToolCall[];
      meta: {
        model: string;
        usage: { promptTokens: number; completionTokens: number; totalTokens: number };
      };
    }
  | {
      type: 'tool-result';
      toolCallId: string;
      toolName: string;
      output: AiToolMessageOutput;
    };
```

## Accessing Legacy Agent Data in Downstream Actors

```yaml
# Final result fields
configuration:
  inputs:
    agentResponse: ${{ msg.research_agent.response }}
    endReason: ${{ msg.research_agent.meta.endReason }}
    totalTokens: ${{ msg.research_agent.meta.usage.totalTokens }}
    # The last message holds the final text response:
    finalResponse: ${{ msg.research_agent.response[msg.research_agent.response.length - 1].content }}
```

## TypeScript Schema Hint

See [typescript/actor-schemas-task-core.md](typescript/actor-schemas-task-core.md) (`actorSchemas/task/deprecatedAiAgent` section) for the complete TypeScript definitions.
