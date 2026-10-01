# ai/index

Generated from the platform's runtime types. Do not edit.

AI message types, thinking levels, finish reasons, and the model lists across providers.

See also: [ai/lib](lib.md), [ai/openAi](openAi.md), [ai/anthropic](anthropic.md), [ai/google](google.md), [ai/xAi](xAi.md), [schemas/file](../schemas/file.md), [ai/modelRef](modelRef.md).

## ai/index

**Source:** `ai/index.ts`

```typescript
import { z } from 'zod';

import { AiModelInformation, AiProvider } from './lib.js';
import { OpenAiModelInformationMap, OpenAiModels, OpenAiAgentModels } from './openAi.js';
import { AnthropicModelInformationMap, AnthropicModels, AnthropicAgentModels } from './anthropic.js';
import { GoogleModelInformationMap, GoogleAiModels, GoogleAgentModels } from './google.js';
import { xAiModelInformationMap, xAiModels, xAiAgentModels } from './xAi.js';
import { BIQFileSchema } from '../schemas/file.js';
import type { AiModelRef } from './modelRef.js';

export { AiProvider, AI_MODEL_PROVIDERS, AiProviderLabels } from './lib.js';
export type { AiModelProvider, AiModelInformation } from './lib.js';
export * from './modelRef.js';
export * from './providerBaseUrl.js';
export { AnthropicAgentModels } from './anthropic.js';
export { OpenAiAgentModels } from './openAi.js';
export { GoogleAgentModels } from './google.js';
export { xAiAgentModels } from './xAi.js';

export enum AiModelType {
  Chat = 'chat',
  Reasoning = 'reasoning',
}

/** Thinking / reasoning depth requested from the model by the AI Agent (Lambda) actor. pi maps
 * each level to the provider's native parameter (Anthropic thinking budget, OpenAI reasoning
 * effort, Gemini thinking budget, ...) and clamps it to what the selected model supports. `off`
 * disables thinking; leaving the option unset keeps pi's own default (`medium`). */
export const AI_AGENT_THINKING_LEVELS = ['off', 'minimal', 'low', 'medium', 'high'] as const;
export const AiAgentThinkingLevelSchema = z.enum(AI_AGENT_THINKING_LEVELS);
export type AiAgentThinkingLevel = z.infer<typeof AiAgentThinkingLevelSchema>;

export enum AiFinishReason {
  Finish = 'finished',
  MaxLoopCountReached = 'max_loop_count_reached',
  MaxLength = 'max_length',
  ToolCalls = 'tool_calls',
  ContentFilter = 'content_filter',
  Error = 'error',
  Unknown = 'unknown',
}

export const AiModel = {
  ...OpenAiModels,
  ...AnthropicModels,
  ...GoogleAiModels,
  ...xAiModels,
} as const;
export type AiModel = (typeof AiModel)[keyof typeof AiModel];

/** What the AI services accept as a model: a validated reference (`AiModelRefSchema`), or a known
 * model id, which is a valid reference by construction. */
export type AiModelRefInput = AiModelRef | AiModel;

/** Curated agent lists per provider (single source of truth, defined alongside each
 * provider's models). The first entry seeds the cross-provider default — keep it an
 * Anthropic Sonnet. */
export const AiAgentModelsByProvider = {
  [AiProvider.Anthropic]: AnthropicAgentModels,
  [AiProvider.OpenAI]: OpenAiAgentModels,
  [AiProvider.Google]: GoogleAgentModels,
  [AiProvider.xAi]: xAiAgentModels,
} as const satisfies Partial<Record<AiProvider, readonly AiModel[]>>;

/** Every proficient agent model across all providers (drives the AI Agent actor dropdown). */
export const AiAgentModels = [
  ...AnthropicAgentModels,
  ...OpenAiAgentModels,
  ...GoogleAgentModels,
  ...xAiAgentModels,
] as const;

export const AiModelInformationMap: Record<AiModel, AiModelInformation> = {
  ...OpenAiModelInformationMap,
  ...AnthropicModelInformationMap,
  ...GoogleModelInformationMap,
  ...xAiModelInformationMap,
} as const;

export const AiMessageTextSchema = z.object({
  type: z.literal('text'),
  text: z.string(),
});

export type AiMessageText = z.infer<typeof AiMessageTextSchema>;

export const AiMessageImageSchema = z.object({
  type: z.literal('image'),
  /** the base64 encoded image OR url */
  image: z.string(),
  /** the media/MIME type */
  mediaType: z.string(),
});

export type AiMessageImage = z.infer<typeof AiMessageImageSchema>;

export const AiMessageFileSchema = z.object({
  type: z.literal('file'),
  /** the base64 encoded file OR url */
  data: z.string(),
  fileName: z.string().optional(),
  /** the media/MIME type */
  mediaType: z.string(),
});

export type AiMessageFile = z.infer<typeof AiMessageFileSchema>;

export const AiUserMessageContentSchema = z.discriminatedUnion('type', [
  AiMessageTextSchema,
  AiMessageImageSchema,
  AiMessageFileSchema,
]);

export type AiUserMessageContent = z.infer<typeof AiUserMessageContentSchema>;

export const AiUserMessageSchema = z.object({
  role: z.literal('user'),
  content: z.union([
    z.string(),
    z.array(AiUserMessageContentSchema),
  ]),
});

export type AiUserMessage = z.infer<typeof AiUserMessageSchema>;

export const AiAssistantMessageReasoningSchema = z.object({
  type: z.literal('reasoning'),
  text: z.string(),
  signature: z.string(),
});

export type AiAssistantMessageReasoning = z.infer<typeof AiAssistantMessageReasoningSchema>;


export const AiAssistantMessageToolCallSchema = z.object({
  type: z.literal('tool-call'),
  toolCallId: z.string(),
  toolName: z.string(),
  input: z.any(),
  providerOptions: z.record(z.string(), z.any()).optional(),
});

export type AiAssistantMessageToolCall = z.infer<typeof AiAssistantMessageToolCallSchema>;

export const AiAssistantMessageContentSchema = z.discriminatedUnion('type', [
  AiMessageTextSchema,
  AiMessageFileSchema,
  AiAssistantMessageReasoningSchema,
  AiAssistantMessageToolCallSchema,
]);

export type AiAssistantMessageContent = z.infer<typeof AiAssistantMessageContentSchema>;

export const AiAssistantMessageSchema = z.object({
  role: z.literal('assistant'),
  content: z.union([
    z.string(),
    z.array(AiAssistantMessageContentSchema),
  ]),
});

export type AiAssistantMessage = z.infer<typeof AiAssistantMessageSchema>;

export const AiToolMessageTextResultSchema = z.object({
  type: z.literal('text'),
  value: z.string(),
});

export type AiToolMessageTextResult = z.infer<typeof AiToolMessageTextResultSchema>;


export const AiToolMessageJsonResultSchema = z.object({
  type: z.literal('json'),
  value: z.any(),
});

export type AiToolMessageJsonResult = z.infer<typeof AiToolMessageJsonResultSchema>;


export const AiToolErrorTextResultSchema = z.object({
  type: z.literal('error-text'),
  value: z.string(),
});

export type AiToolErrorTextResult = z.infer<typeof AiToolErrorTextResultSchema>;


export const AiToolErrorJsonResultSchema = z.object({
  type: z.literal('error-json'),
  value: z.any(),
});

export type AiToolErrorJsonResult = z.infer<typeof AiToolErrorJsonResultSchema>;

export const AiToolContentMediaSchema = z.object({
  type: z.literal('media'),
  /** the base64 encoded media */
  data: z.string(),
  /** the media/MIME type */
  mediaType: z.string(),
});
export type AiToolContentMedia = z.infer<typeof AiToolContentMediaSchema>;

const AiToolMessageContentSchema = z.object({
  type: z.literal('content'),
  value: z.array(z.discriminatedUnion('type', [
    AiMessageTextSchema,
    AiToolContentMediaSchema,
  ])),
});

export type AiToolMessageContent = z.infer<typeof AiToolMessageContentSchema>;

export const AiToolMessageOutputSchema = z.discriminatedUnion('type', [
  AiToolMessageTextResultSchema,
  AiToolMessageJsonResultSchema,
  AiToolErrorTextResultSchema,
  AiToolErrorJsonResultSchema,
  AiToolMessageContentSchema,
]);

export type AiToolMessageOutput = z.infer<typeof AiToolMessageOutputSchema>;

export const AiToolMessageResultSchema = z.object({
  type: z.literal('tool-result'),
  toolCallId: z.string(),
  toolName: z.string(),
  output: AiToolMessageOutputSchema,
  providerOptions: z.record(z.string(), z.any()).optional(),
});

export type AiToolMessageResult = z.infer<typeof AiToolMessageResultSchema>;

export const AiToolMessageSchema = z.object({
  role: z.literal('tool'),
  content: z.array(AiToolMessageResultSchema),
});

export type AiToolMessage = z.infer<typeof AiToolMessageSchema>;


export const AiMessageSchema = z.discriminatedUnion('role', [
  AiUserMessageSchema,
  AiAssistantMessageSchema,
  AiToolMessageSchema,
]);

export type AiMessage = z.infer<typeof AiMessageSchema>;

export const AiToolCallSchema = AiAssistantMessageToolCallSchema.omit({
  type: true,
});

export type AiToolCall = z.infer<typeof AiToolCallSchema>;

export interface AiStepOutput {
  response: string;
  toolCalls?: AiToolCall[];
  toolResults?: AiToolMessageResult[];
  inputTokens: number;
  outputTokens: number;
  totalTokens: number;
}

export interface AiOutput<T = unknown> {
  response: T;
  toolCalls?: AiToolCall[];
  steps?: AiStepOutput[];
  finishReason?: AiFinishReason;
}

export interface AiResponse<T = unknown> extends AiOutput<T> {
  inputTokens: number;
  outputTokens: number;
  totalTokens: number;
}

export interface AiChatCompletionResponse<T = unknown> extends AiResponse<T> {
  fromCache: boolean;
}

export const AiDefaultParameters = {
  model: AiModel.GPT_6_LUNA,
  temperature: 0.2,
  maxTokens: 10000,
} as const;

/** The custom types for AI enabled actors to build the message history */

export const BIQAiMessageImageSchema = z.object({
  type: z.literal('image'),
  image: BIQFileSchema,
});

export type BIQAiMessageImage = z.infer<typeof BIQAiMessageImageSchema>;

export const BIQAiMessageFileSchema = z.object({
  type: z.literal('file'),
  data: BIQFileSchema,
});

export type BIQAiMessageFile = z.infer<typeof AiMessageFileSchema>;

export const BIQAiUserMessageContentSchema = z.union([
  AiMessageTextSchema,
  AiMessageImageSchema,
  BIQAiMessageImageSchema,
  AiMessageFileSchema,
  BIQAiMessageFileSchema,
]);

export type BIQAiUserMessageContent = z.infer<typeof BIQAiUserMessageContentSchema>;

export const BIQAiUserMessageSchema = z.object({
  role: z.literal('user'),
  content: z.union([
    z.string(),
    z.array(BIQAiUserMessageContentSchema),
  ]),
});

export type BIQAiUserMessage = z.infer<typeof BIQAiUserMessageSchema>;


export const BIQAiAssistantMessageContentSchema = z.union([
  AiMessageTextSchema,
  AiMessageFileSchema,
  AiMessageImageSchema,
  AiAssistantMessageReasoningSchema,
  AiAssistantMessageToolCallSchema,
]);

export type BIQAiAssistantMessageContent = z.infer<typeof BIQAiAssistantMessageContentSchema>;

export const BIQAiAssistantMessageSchema = z.object({
  role: z.literal('assistant'),
  content: z.union([
    z.string(),
    z.array(BIQAiAssistantMessageContentSchema),
  ]),
});

export type BIQAiAssistantMessage = z.infer<typeof BIQAiAssistantMessageSchema>;

export const BIQAiToolContentMediaSchema = z.object({
  type: z.literal('media'),
  data: BIQFileSchema,
});

export type BIQAiToolContentMedia = z.infer<typeof BIQAiToolContentMediaSchema>;

export const BIQAiToolContentSchema = z.object({
  type: z.literal('content'),
  value: z.array(z.union([
    AiMessageTextSchema,
    AiToolContentMediaSchema,
    BIQAiToolContentMediaSchema,
  ])),
});

export type BIQAiToolContent = z.infer<typeof BIQAiToolContentSchema>;

export const BIQAiToolMessageOutputSchema = z.discriminatedUnion('type', [
  AiToolMessageTextResultSchema,
  AiToolMessageJsonResultSchema,
  AiToolErrorTextResultSchema,
  AiToolErrorJsonResultSchema,
  BIQAiToolContentSchema,
]);

export type BIQAiToolMessageOutput = z.infer<typeof BIQAiToolMessageOutputSchema>;


export const BIQAiToolMessageResultSchema = z.object({
  type: z.literal('tool-result'),
  toolCallId: z.string(),
  toolName: z.string(),
  output: BIQAiToolMessageOutputSchema,
});

export type BIQAiToolMessageResult = z.infer<typeof BIQAiToolMessageResultSchema>;

export const BIQAiToolMessageSchema = z.object({
  role: z.literal('tool'),
  content: z.array(BIQAiToolMessageResultSchema),
});

export type BIQAiToolMessage = z.infer<typeof BIQAiToolMessageSchema>;

export const BIQAiMessageSchema = z.discriminatedUnion('role', [
  BIQAiUserMessageSchema,
  BIQAiAssistantMessageSchema,
  BIQAiToolMessageSchema,
]);

export type BIQAiMessage = z.infer<typeof BIQAiMessageSchema>;
```
