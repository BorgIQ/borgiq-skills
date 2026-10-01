# sandbox

Generated from the platform's runtime types. Do not edit.

Agent-harness sandbox types: harness types, sandbox status, and the status updates the Status port emits.

See also: [ai/index](ai/index.md), [schemas/file](schemas/file.md).

## sandbox

**Source:** `sandbox.ts`

```typescript
/**
 * Sandbox types shared between the platform and the lambda runtime.
 * NOTE: This file is to ONLY be used for types needed in both the platform and the lambda runtime.
 */
import { z } from 'zod';

import { AiToolCallSchema, BIQAiToolMessageOutputSchema } from './ai/index.js';
import { BIQFileSchema } from './schemas/file.js';


/** Agent harness provider options for display in UI */
export enum BIQSandboxProviders {
  E2B = 'e2b',
  DAYTONA = 'daytona',
  /** AgentLambdaActor sessions: segments run in the agent-sessions Lambda function, not a
   * sandbox VM. Never valid for SandboxProviderFactory — it exists so SandboxSessionData
   * can carry the session's runtime kind. */
  LAMBDA = 'lambda',
}

/** Agent harness CLI type. Selects which coding-agent CLI runs in the sandbox.
 * Defaults to 'claude' everywhere for backward compatibility.
 */
export enum BIQAgentHarnessType {
  Claude = 'claude',
  Codex = 'codex',
  OpenCode = 'opencode',
  Pi = 'pi',
}

export const BIQAgentHarnessTypeSchema = z.nativeEnum(BIQAgentHarnessType);

/** Status of a sandbox instance */
export enum BIQSandboxStatus {
  Creating = 'creating',
  Running = 'running',
  Idle = 'idle',
  ShuttingDown = 'shutting_down',
  Stopped = 'stopped',
  Error = 'error',
}

export const BIQSandboxStatusSchema = z.enum(BIQSandboxStatus);

/** Status update types from sandbox to orchestrator.
 * These values match what the Claude Code hooks script sends to the status endpoint.
 */
export enum BIQAgentHarnessStatusUpdateType {
  /** Loop result with accumulated response and tool calls (from pre-tool-use hook) */
  AgentHarnessLoop = 'agent-harness-loop',
  /** Tool execution result (from post-tool-use and post-tool-use-failure hooks) */
  ToolResult = 'tool-result',
  /** Execution completed successfully (from stop hook) */
  Complete = 'complete',
  /** Notification from Claude Code - permission prompts, etc. (from notification hook) */
  Notification = 'notification',
  /** Error occurred during execution */
  Error = 'error',
  /** Agent lambda segment liveness signal (~60s cadence); reschedules the watchdog */
  Heartbeat = 'heartbeat',
  /** Agent lambda segment reached its deadline margin and persisted state; the
   * orchestrator should launch the next segment */
  Checkpointed = 'checkpointed',
}

export const BIQAgentHarnessStatusUpdateTypeSchema = z.enum(BIQAgentHarnessStatusUpdateType);

/** Output stream type */
export enum BIQSandboxOutputStream {
  Stdout = 'stdout',
  Stderr = 'stderr',
}

export const BIQSandboxOutputStreamSchema = z.enum(BIQSandboxOutputStream);

/** Basic session info returned to the runtime */
export const SandboxSessionInfoSchema = z.object({
  sessionId: z.string(),
  sandboxId: z.string(),
  status: BIQSandboxStatusSchema,
});

export type SandboxSessionInfo = z.infer<typeof SandboxSessionInfoSchema>;

/** Content type for content status updates.
 * @deprecated Never produced by any hook or sidecar and never read by the orchestrator. Kept so
 * old payloads still parse; reasoning travels on `SandboxStatusUpdateDataSchema.reasoning`. */
export const SandboxContentTypeSchema = z.enum(['thinking', 'response', 'partial']);
export type SandboxContentType = z.infer<typeof SandboxContentTypeSchema>;

/** Data for sandbox status update */
export const SandboxStatusUpdateDataSchema = z.object({
  // Tool-related fields (from PostToolUse hook - legacy)
  toolName: z.string().optional(),
  toolCallId: z.string().optional(),
  toolInput: z.unknown().optional(),
  toolOutput: z.unknown().optional(),

  // New aligned format fields (for agent-harness-loop and tool-result messages)
  /** Accumulated response text before this event (for agent-harness-loop) */
  response: z.string().optional(),
  /** Tool calls data (for agent-harness-loop) - array of concurrent tool calls */
  toolCalls: z.array(AiToolCallSchema).optional(),
  /** Tool output (for tool-result) */
  output: BIQAiToolMessageOutputSchema.optional(),
  /** Whether the tool call resulted in an error (for tool-result) */
  isError: z.boolean().optional(),
  /** The model's thinking / reasoning for this turn (for agent-harness-loop). Posted by the
   * lambda segment host (pi thinking blocks) and the harness hook/sidecars (Claude transcript
   * thinking blocks, Codex reasoning items, pi/OpenCode reasoning parts). Clipped by the
   * orchestrator before it is persisted. */
  reasoning: z.string().optional(),

  // Generic message field
  message: z.string().optional(),
  exitCode: z.number().optional(),

  // Content/thinking fields (legacy)
  /** @deprecated Never produced; use `response` (text) and `reasoning` (thinking) instead. */
  generatedContent: z.string().optional(),
  /** @deprecated Never produced; see SandboxContentTypeSchema. */
  contentType: SandboxContentTypeSchema.optional(),

  // Notification fields (from Notification hook)
  /** Type of notification (e.g., 'permission_prompt', 'idle_prompt', 'auth_success') */
  notificationType: z.string().optional(),
  /** Notification title */
  title: z.string().optional(),

  // Working directory (provided by all hooks)
  /** Current working directory in the sandbox */
  cwd: z.string().optional(),

  // Raw hook data for debugging/extensibility
  /** Raw hook data when event type is unknown */
  hookData: z.unknown().optional(),

  // Agent lambda segment fields (heartbeat / checkpointed / complete posts)
  /** The segment index this post belongs to; stale-segment posts are dropped */
  segmentIndex: z.number().int().nonnegative().optional(),
  /** The epoch token granted to this segment; must match the session record */
  epochToken: z.string().optional(),
  /** Workspace size as last measured by the segment host (feeds the AgentSession ledger) */
  workspaceSizeInBytes: z.number().int().optional(),
  /** Workspace file count as last measured by the segment host */
  workspaceFileCount: z.number().int().optional(),
  /** Workspace zip the segment uploaded at finalize (complete posts only) */
  outputZipFile: BIQFileSchema.optional(),
  /** Pi session zip the segment uploaded at finalize (complete posts only) */
  sessionDataFile: BIQFileSchema.optional(),
  /** Zip-fallback mode: BIQFile id of the combined checkpoint the segment uploaded
   * (checkpointed posts only); the orchestrator carries it into the next segment. */
  checkpointFileId: z.string().optional(),
  /** Why the run ended, set by the segment host on a terminal post (complete/error).
   * Drives the done-port `meta.endReason`; defaults to completed/error when absent. */
  endReason: z.enum(['completed', 'timeout', 'error', 'max-loop-count']).optional(),
  /** Host-reported LLM token usage for THIS segment (per-segment delta of pi's session stats —
   * not cumulative, so the orchestrator writes one aiLog row per segment without double-counting).
   * Posted on checkpointed + complete. */
  usageReport: z.object({
    promptTokens: z.number().int().nonnegative(),
    completionTokens: z.number().int().nonnegative(),
    totalTokens: z.number().int().nonnegative(),
    cacheReadTokens: z.number().int().nonnegative().optional(),
    cacheWriteTokens: z.number().int().nonnegative().optional(),
    /** Subset of cacheWriteTokens written with 1-hour retention (Anthropic only; priced 2x). */
    cacheWrite1hTokens: z.number().int().nonnegative().optional(),
  }).optional(),
  /** Host-estimated Lambda billing for this segment. Event invokes return no LogResult, so the
   * host reports its own wall-clock (billedDurationMs) + function memory; the orchestrator accrues
   * cost from it via the lambda-cost map. Posted on checkpointed + complete. */
  lambdaBilling: z.object({
    billedDurationMs: z.number().nonnegative(),
    memoryMB: z.number().int().positive(),
    /** Function ephemeral storage (/tmp) size — the host knows it from its segment payload;
     * carried here so the orchestrator can price the invoke without re-resolving runtime config. */
    ephemeralMB: z.number().int().positive(),
    /** The architecture the host ran on (`x86_64` | `arm64`), so the orchestrator prices the segment
     * at the right rate. Absent from hosts predating arm64 support (priced as x86_64). */
    architecture: z.enum(['x86_64', 'arm64']).optional(),
  }).optional(),
  /** Assistant turns consumed across ALL segments so far (this segment's count seeded by the prior
   * segments' total). Reported on checkpointed + complete; the orchestrator persists it to the
   * session and forwards it to the next segment so maxLoopCount is enforced session-wide rather
   * than reset per segment. */
  loopCountUsed: z.number().int().nonnegative().optional(),
});

export type SandboxStatusUpdateData = z.infer<typeof SandboxStatusUpdateDataSchema>;

/** Sandbox status update payload */
export const AgentHarnessStatusUpdateSchema = z.object({
  sessionId: z.string(),
  // Accept both enum values and string literals for new message types
  type: BIQAgentHarnessStatusUpdateTypeSchema,
  data: SandboxStatusUpdateDataSchema,
});

export type AgentHarnessStatusUpdate = z.infer<typeof AgentHarnessStatusUpdateSchema>;

/** Sandbox output stream payload */
export const SandboxOutputStreamPayloadSchema = z.object({
  sessionId: z.string(),
  stream: BIQSandboxOutputStreamSchema,
  chunk: z.string(),
});

export type SandboxOutputStreamPayload = z.infer<typeof SandboxOutputStreamPayloadSchema>;

/** External tool invocation request from sandbox */
export const SandboxExternalToolInvokeSchema = z.object({
  sessionId: z.string(),
  toolCallId: z.string(),
  toolName: z.string(),
  toolInput: z.unknown(),
});

export type SandboxExternalToolInvoke = z.infer<typeof SandboxExternalToolInvokeSchema>;

/** Tool definition passed to Claude Code in sandbox */
export const SandboxExternalToolDefinitionSchema = z.object({
  name: z.string(),
  description: z.string(),
  jsonSchema: z.record(z.string(), z.unknown()).optional(),
  actorId: z.string(),
});

export type SandboxExternalToolDefinition = z.infer<typeof SandboxExternalToolDefinitionSchema>;
```
