# canvas

Generated from the platform's runtime types. Do not edit.

Actor type names, webhook authorization levels and the default port ids.

## canvas

**Source:** `canvas.ts`

```typescript
/**
 * NOTE:
 * Any types that is not used in the runtime is found in packages/types/src/canvas.ts
 * This file is to ONLY be used for types that is used in the runtime.
 */

/**
 * NOTE:
 * - In the UI (web), the draggable actor from the toolbox (sidebar) is of type BIQActor
 * - The actor that is part of the Canvas (an instance of BIQActor) is of type BIQCanvasActor
 * - The canvas data in the UI reactflow (editor) is an array of Node<N> and Edge<E> which is from BIQCanvasActor and BIQCanvasConnection
*/

/** the different types of actors in borgiq. */
export enum BIQActorType {
  CommentActor = 'CommentActor',
  EchoActor = 'EchoActor',
  CallableResponseActor = 'CallableResponseActor',
  CallFlowActor = 'CallFlowActor',
  HttpRequestActor = 'HttpRequestActor',
  RouterActor = 'RouterActor',
  MessageProcessorActor = 'MessageProcessorActor',
  DenoActor = 'DenoActor',
  DenoTestActor = 'DenoTestActor',
  SendEmailActor = 'SendEmailActor',
  DataStoreActor = 'DataStoreActor',
  WebhookResponseActor = 'WebhookResponseActor',
  ButtonTriggerActor = 'ButtonTriggerActor',
  CallableTriggerActor = 'CallableTriggerActor',
  ScheduledTriggerActor = 'ScheduledTriggerActor',
  UniversalTriggerActor = 'UniversalTriggerActor',
  WebhookTriggerActor = 'WebhookTriggerActor',
  EmailTriggerActor = 'EmailTriggerActor',
  InterfaceTriggerActor = 'InterfaceTriggerActor',
  InterfaceActor = 'InterfaceActor',
  InterfaceStatusActor = 'InterfaceStatusActor',
  AiActor = 'AiActor',
  AiRouterActor = 'AiRouterActor',
  AiAgentActor = 'AiAgentActor',
  /** The legacy orchestrator-loop AI agent. Deprecated + hidden from the palette; existing
   *  instances keep running. New AI agents use AiAgentActor (the Lambda implementation). */
  DeprecatedAiAgent = 'DeprecatedAiAgent',
  PythonActor = 'PythonActor',
  AgentHarnessActor = 'AgentHarnessActor',
  AppTriggerActor = 'AppTriggerActor',
  ReactAppTriggerActor = 'ReactAppTriggerActor',
  CollectionActor = 'CollectionActor',
  StreamActor = 'StreamActor',
  McpServerActor = 'McpServerActor',
}

/** Authorization level for webhook trigger actors */
export enum BIQWebhookAuthorizationLevel {
  /** Anyone can call the webhook */
  Public = 'public',
  /** Only calls with a valid app actor webhook token are allowed */
  Apps = 'apps',
  /**
   * Only calls presenting a valid API key (`Authorization: Bearer` or `X-Api-Key`) are allowed. Today the
   * accepted API key is a personal access token whose owner is a member of the trigger's workspace;
   * workspace-scoped keys slot into the same level later.
   */
  ApiKey = 'apiKey',
  /** Calls presenting either a valid app actor webhook token or a valid API key are allowed */
  AppsAndApiKey = 'appsAndApiKey',
}

/**
 * Whether a webhook authorization level admits an app actor webhook token (`x-app-actor-token`).
 * Accepts the raw stored string so callers reading un-narrowed configuration (editor stores,
 * select-option rows) can ask without casting; an unknown or missing level answers false.
 */
export const webhookLevelAcceptsAppToken = (level: string | null | undefined): boolean =>
  level === BIQWebhookAuthorizationLevel.Apps || level === BIQWebhookAuthorizationLevel.AppsAndApiKey;

/** Whether a webhook authorization level admits an API key (`Authorization: Bearer` / `X-Api-Key`). */
export const webhookLevelAcceptsApiKey = (level: string | null | undefined): boolean =>
  level === BIQWebhookAuthorizationLevel.ApiKey || level === BIQWebhookAuthorizationLevel.AppsAndApiKey;

export const DEFAULT_SOURCE_PORT_ID = 'SPRTdefault';
export const DEFAULT_TARGET_PORT_ID = 'TPRTdefault';
```
