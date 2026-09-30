# schemas/runtime

Generated from the platform's runtime types. Do not edit.

The `$.msg` object and the trigger payloads a flowrun starts from: webhook, email, schedule, interface, lifecycle, app.

See also: [actorSchemas/trigger/triggerConfig](../actorSchemas/trigger/triggerConfig.md), [actorSchemas/codeDir](../actorSchemas/codeDir.md), [schemas/file](file.md), [schemas/idSchema](idSchema.md), [schemas/ctx](ctx.md).

## schemas/runtime

**Source:** `schemas/runtime.ts`

```typescript
/** NOTE: This file is to ONLY be used for types that is used in the runtime. */
import { z } from 'zod';

import { BIQRuntimeInvocationType } from '../runtime.js';

import { WebhookConfigSchema, ScheduleConfigSchema, LifecycleConfigSchema, LIFECYCLE_TRIGGER_EVENTS, LIFECYCLE_DELETE_SCOPES } from '../actorSchemas/trigger/triggerConfig.js';
import { CodeDirSchema } from '../actorSchemas/codeDir.js';

import { BIQFileSchema } from './file.js';
import { idSchema, BuildIdentityHashSchema } from './idSchema.js';
import { RuntimeActorMemorySchema, RuntimeActorReceiveResponseSchema } from './flowrunJobResult.js';
import { RuntimeContextSchema } from './ctx.js';
import { ExternalPayloadUploadSchema, ExternalRefSchema } from './externalPayload.js';

/**
 * the global $.msg object.
 * This object contains all the accumulated messages emitted by the previous actors in the canvas for a particular flowrun.
 */
export const RuntimePrevEmittedMessagesSchema = z.record(z.string(), z.unknown());

export type RuntimePrevEmittedMessages = z.infer<typeof RuntimePrevEmittedMessagesSchema>;

/**
 * the global $.err object.
 * This object contains all the accumulated error messages emitted by the previous actors in the canvas for a particular flowrun.
 */
export const RuntimePrevEmittedErrorsSchema = z.record(z.string(), z.unknown());

export type RuntimePrevEmittedErrors = z.infer<typeof RuntimePrevEmittedErrorsSchema>;

/**
 * The authenticated caller of a webhook request, stamped on `meta.user` by the API edge when the call
 * carried a credential that identifies a BorgIQ user — an app-actor token or an API key. Absent on
 * public fires. Identity only, never authorization: the edge has already verified the credential.
 */
export const WebhookTriggerRequestUserSchema = z.object({
  id: z.string(),
  name: z.string().optional(),
  email: z.string(),
  /** the caller's app session id, lifted from the verified app-actor token (see TriggerUserSchema) */
  appSessionId: z.string().optional(),
});

export type WebhookTriggerRequestUser = z.infer<typeof WebhookTriggerRequestUserSchema>;

/**
 * Which API key authenticated a webhook request, for triggers at the `apiKey` / `appsAndApiKey`
 * authorization levels. Lives on `meta` beside `user` — both are what the platform attests about
 * the call, as opposed to the root fields, which are the HTTP request as the caller sent it.
 * Identifies the key — never carries the secret, which the API edge strips from the headers
 * before the payload is assembled. `type` discriminates the key kind so workspace-scoped keys can
 * join later without reshaping the field; today the only kind is a user's personal access token
 * (`apiToken`), whose owner is `meta.user`.
 */
export const WebhookTriggerAuthSchema = z.object({
  type: z.literal('apiToken'),
  /** the token's public id (never its hash or prefix) */
  keyId: z.string(),
  /** the name the owner gave the token, for per-caller branching in flow code */
  keyName: z.string(),
});

export type WebhookTriggerAuth = z.infer<typeof WebhookTriggerAuthSchema>;

export const FlowrunWebhookTriggerRequestSchema = z.object({
  meta: z.object({
    requestId: z.string(),
    ipAddress: z.string().optional(),
    user: WebhookTriggerRequestUserSchema.optional(),
    /** present only when an API key authenticated the call; the credential headers are already redacted */
    auth: WebhookTriggerAuthSchema.optional(),
  }),
  method: z.optional(z.string()),
  headers: z.optional(z.any()),
  body: z.optional(z.any()),
  queryParams: z.optional(z.any()),
  rawBody: z.optional(z.string()),
});

export type FlowrunWebhookTriggerRequest = z.infer<typeof FlowrunWebhookTriggerRequestSchema>;

/** Information about the email trigger actor */
export const FlowrunEmailTriggerDataSchema = z.object({
  messageId: z.string(),
  from: z.string(),
  to: z.string(),
  cc: z.string().optional(),
  subject: z.string(),
  date: z.string(),
  hasAttachments: z.boolean(),
  htmlBody: z.string().optional(),
  textBody: z.string().optional(),
  attachments: z.array(BIQFileSchema).optional(),
  headers: z.record(z.string(), z.string()).optional(),
});

export type FlowrunEmailTriggerData = z.infer<typeof FlowrunEmailTriggerDataSchema>;

/** Information about the scheduled trigger request. */
export const FlowrunScheduledTriggerDataSchema = z.object({
  /** the time the trigger started */
  triggeredAt: z.string(),
});

export type FlowrunScheduledTriggerData = z.infer<typeof FlowrunScheduledTriggerDataSchema>;

/** Information about the interface get trigger request. */
export const FlowrunInterfaceGetTriggerDataSchema = z.object({
  meta: z.object({
    user: z.object({
      id: z.string(),
      name: z.string().optional(),
      email: z.string(),
    }).optional(),
  }).optional(),
});

export type FlowrunInterfaceGetTriggerData = z.infer<typeof FlowrunInterfaceGetTriggerDataSchema>;

/** Information about the interface submission trigger request. */
export const FlowrunInterfaceTriggerDataSchema = z.object({
  meta: z.object({
    submissionInterfaceId: z.string(),
    user: z.object({
      id: z.string(),
      name: z.string().optional(),
      email: z.string(),
    }).optional(),
    ipAddress: z.string().optional(),
  }),
  body: z.record(z.string(), z.any()),
});

export type FlowrunInterfaceTriggerData = z.infer<typeof FlowrunInterfaceTriggerDataSchema>;

/**
 * Information about a lifecycle trigger request. Byte-identical to the
 * `lifecycle` TriggerEvent variant delivered to user code — the explicit `type` discriminator is
 * what lets the payload-sniffing mirrors recognise it before falling through to `manual`.
 *
 * `on-delete` always says what was deleted: `scope` is the level (the actor itself, or the canvas /
 * workspace / org it lived in) and `subject.id` that resource's id. `manual` marks a fire made by hand
 * in a development workspace, where nothing was actually deleted. The other events carry nothing more.
 */
export const FlowrunLifecycleTriggerDataSchema = z.discriminatedUnion('event', [
  z.object({
    type: z.literal('lifecycle'),
    event: z.enum(LIFECYCLE_TRIGGER_EVENTS).exclude(['on-delete']),
  }),
  z.object({
    type: z.literal('lifecycle'),
    event: z.literal('on-delete'),
    scope: z.enum(LIFECYCLE_DELETE_SCOPES),
    subject: z.object({ id: z.string() }),
    manual: z.literal(true).optional(),
  }),
]);

export type FlowrunLifecycleTriggerData = z.infer<typeof FlowrunLifecycleTriggerDataSchema>;

/** The `on-delete` member of {@link FlowrunLifecycleTriggerData}. */
export type FlowrunLifecycleDeleteTriggerData = Extract<FlowrunLifecycleTriggerData, { event: 'on-delete' }>;

/** Information about the manual trigger request. */
export const FlowrunManualTriggerDataSchema = z.object({
});

export type FlowrunManualTriggerData = z.infer<typeof FlowrunManualTriggerDataSchema>;

/** Information about the app get trigger request. */
export const FlowrunAppGetTriggerDataSchema = z.object({
  meta: z.object({
    user: z.object({
      id: z.string(),
      name: z.string().optional(),
      email: z.string(),
    }).optional(),
  }).optional(),
});

export type FlowrunAppGetTriggerData = z.infer<typeof FlowrunAppGetTriggerDataSchema>;

/** meta carried on the react-app trigger data (viewer/actor for provenance). */
const ReactAppTriggerMetaSchema = z.object({
  user: z.object({
    id: z.string(),
    name: z.string().optional(),
    email: z.string(),
  }).optional(),
}).optional();

/** Information about a react-app **build** invocation (runtime-dispatched). */
export const FlowrunReactAppBuildTriggerDataSchema = z.object({
  kind: z.literal('build'),
  meta: ReactAppTriggerMetaSchema,
});

export type FlowrunReactAppBuildTriggerData = z.infer<typeof FlowrunReactAppBuildTriggerDataSchema>;

/** Information about a react-app **serve** audit invocation (never dispatched to the runtime, §4.4.2). */
export const FlowrunReactAppServeTriggerDataSchema = z.object({
  kind: z.literal('serve'),
  meta: ReactAppTriggerMetaSchema,
});

export type FlowrunReactAppServeTriggerData = z.infer<typeof FlowrunReactAppServeTriggerDataSchema>;

/** Information about the interface orchestrator data */
export const FlowrunInterfaceOrchestratorDataSchema = z.object({
  interfaceId: z.string(),
  interfaceUrl: z.string(),
});

export type FlowrunInterfaceOrchestratorData = z.infer<typeof FlowrunInterfaceOrchestratorDataSchema>;

export const FlowrunAgentToolCallOrchestratorDataSchema = z.object({
  type: z.literal('agentToolCall'),
  input: z.any(),
});

export type FlowrunAgentToolCallOrchestratorData = z.infer<typeof FlowrunAgentToolCallOrchestratorDataSchema>;

export const RuntimeActorOrchestratorMessageSchema = z.union([
  // MUST stay FIRST. This is a plain (non-discriminated) z.union tried in order, and several members
  // below are all-optional object schemas — FlowrunInterfaceGetTriggerDataSchema,
  // FlowrunAppGetTriggerDataSchema, FlowrunWebhookTriggerRequestSchema, and the empty
  // FlowrunManualTriggerDataSchema — each of which matches ANY object and strips every key. Placed
  // after any of them, a lifecycle payload would silently parse to `{}` and degrade to a manual
  // fire with no error anywhere. This member is maximally strict (literal `type` + event enum), so
  // leading the union cannot mis-capture another payload. Pinned by a regression test in
  // __tests__/universalTrigger.test.ts.
  FlowrunLifecycleTriggerDataSchema,
  FlowrunEmailTriggerDataSchema,
  FlowrunInterfaceTriggerDataSchema,
  FlowrunInterfaceGetTriggerDataSchema,
  FlowrunAppGetTriggerDataSchema,
  FlowrunWebhookTriggerRequestSchema,
  FlowrunScheduledTriggerDataSchema,
  FlowrunManualTriggerDataSchema,
  FlowrunReactAppBuildTriggerDataSchema,
  FlowrunReactAppServeTriggerDataSchema,
  FlowrunInterfaceOrchestratorDataSchema,
  FlowrunAgentToolCallOrchestratorDataSchema,
]);

export type RuntimeActorOrchestratorMessage = z.infer<typeof RuntimeActorOrchestratorMessageSchema>;

export const ActorConnectionConfigurationSchema = z.object({
  key: z.string().optional(),
  /** the connection type(s) the actor allows — scalar for a single type, array when several types are acceptable */
  type: z.union([z.string(), z.array(z.string()).min(1)]).optional(),
}).superRefine((data, ctx) => {
  if (data.type && !data.key) {
    ctx.addIssue({
      code: z.ZodIssueCode.invalid_type,
      expected: 'string',
      received: 'undefined',
      message: 'Required',
      path: ['key'],
    });
  }
});

export type ActorConnectionConfiguration = z.infer<typeof ActorConnectionConfigurationSchema>;

export const ActorCredentialsConfigurationSchema = z.record(z.string(), z.object({
  workspaceKey: z.string(),
  type: z.string().optional(),
  source: z.enum(['secret', 'connection']),
}));

export type ActorCredentialsConfiguration = z.infer<typeof ActorCredentialsConfigurationSchema>;

export const ActorConfigurationSchema = z.object({
  aiAgentToolActorIds: z.array(z.string()).optional(),
  credentials: z.string().optional(),
  inputs: z.string().optional(),
  vars: z.string().optional(),
  options: z.string(),
  outputs: z.string().optional(),
  /** Legacy single-string source — inert. Kept optional so a pre-migration configuration still parses
   *  at the wire; the runtime reads `codeDir` only. */
  code: z.string().optional(),
  error: z.string().optional(),
  connection: z.object({
    key: z.string().optional(),
    /** the connection type(s) the actor allows — scalar for a single type, array when several types are acceptable */
    type: z.union([z.string(), z.array(z.string()).min(1)]).optional(),
  }).optional(),
  /** Static, admission-consumed webhook config for webhook/universal triggers (never interpolated). */
  webhook: WebhookConfigSchema.optional(),
  /** Static, admission-consumed schedule config for scheduled/universal triggers (never interpolated). */
  schedule: ScheduleConfigSchema.optional(),
  /** Static, admission-consumed lifecycle subscription for universal triggers. Absent ⇒ unsubscribed. */
  lifecycle: LifecycleConfigSchema.optional(),
  /** The actor's project source tree ({path, content}[]) — ReactAppTriggerActor and the code actors.
   *  NEVER interpolated: stripped before the interpolator runs and read back from the pre-interpolated
   *  config by the actor. Per-type entrypoint/reserved-path rules are deliberately not wire-level;
   *  they run where the actor type is known (save-time warnings, canvas validation, the runtime). */
  codeDir: CodeDirSchema.optional(),
  /** indicates if the actor will emit errors downstream instead of halting the flowrun */
  continueOnError: z.boolean(),
  /** indicates if the actor has long term memory (canvas memory). When enabled, the actor's messages are processed one at a time across all flowruns */
  enableLTM: z.boolean(),
  /** indicates if the actor has short term memory (flowrun memory). When enabled, the actor's messages are processed one at a time within a single flowrun */
  enableSTM: z.boolean(),
});

export type ActorConfiguration = z.infer<typeof ActorConfigurationSchema>;

export const RuntimeActorSourcePortSchema = z.object({
  id: idSchema.sourcePortId,
  name: z.string().optional(),
  description: z.string().optional()
});

export type RuntimeActorSourcePort = z.infer<typeof RuntimeActorSourcePortSchema>;

/**
 * A prebuilt runtime cache the runtime may start this actor from, attached by the orchestrator only
 * when the actor's canvas has a usable runtime build. Its **presence and `kind`** are what select the
 * execution environment's tenant key, so an absent block always means the legacy per-actor
 * environment and the legacy dependency-resolution chain.
 *
 * The runtime downloads the object, verifies it against `sha256`/`bytes` **before** extracting, and
 * refuses it if `imageBuildId` is known on both sides and differs, or if `architecture` is known and
 * differs from the runtime's own. Any failure is reported as the
 * retryable `RUNTIME_CACHE_UNAVAILABLE_ERROR_NAME` error rather than silently resolving dependencies
 * inside an environment shared by a whole canvas.
 */
export const RuntimeCacheSchema = z.object({
  /** the build the artifact came from; also the last component of the environment's tenant key */
  buildId: idSchema.canvasRuntimeBuildId,
  /**
   * `canvas` — one archive holding every Deno-family actor's work dir of the canvas plus the single
   * shared Deno dependency cache. `python-actor` — one archive per Python actor (its work dir and
   * its virtual environment), because Python actors keep per-actor tenancy. `deno-test-actor` — one
   * archive per Deno Test actor (its work dir and its OWN dependency cache): a test actor's argList
   * can grant `--allow-all`, the very permission the dynamic-import jail is built on, so it keeps
   * per-actor tenancy and must never receive the canvas archive — the shared cache's emit files
   * mirror sibling actors' source.
   */
  kind: z.enum(['canvas', 'python-actor', 'deno-test-actor']),
  /** presigned GET, minted per invoke and valid for at least 15 minutes */
  url: z.string().url(),
  /** sha256 of the artifact, hex; verified before anything is extracted */
  sha256: z.string().regex(/^[0-9a-f]{64}$/),
  /** exact byte count of the artifact; a size mismatch fails the download before hashing */
  bytes: z.number().int().positive(),
  /**
   * The build identity hash of this actor as the build recorded it. An assertion, not routing: inside
   * a pinned flowrun the actor and the build match by construction, so a mismatch means the request
   * and the artifact disagree and the cache must not be used. Only the real `sha256:<hex>` shape is
   * accepted — a block is only ever built from an `ok` actor, which always carries one.
   */
  actorHash: BuildIdentityHashSchema,
  /** the runtime image the artifact was built on; compared with the runtime's own when both are known */
  imageBuildId: z.string().optional(),
  /** the CPU architecture the artifact was built on; the runtime refuses it when it differs from its own */
  architecture: z.enum(['x86_64', 'arm64']).optional(),
  /** the runtime function's image URI at build time, carried for diagnostics */
  runtimeVersion: z.string().optional(),
});

export type RuntimeCache = z.infer<typeof RuntimeCacheSchema>;

/** The request data in the lambda invoke event */
export const RuntimeRequestSchema = z.object({
  /** the flowrun job id */
  flowrunJobId: z.string().optional(),
  /** a unique id to identify the runtime request. In the case of 'receive' requestType, remember an actor can be invoked multiple times for the same flowrun. this id uniquely identifies each invocation */
  actorInvocationId: z.string(),
  /** The type of invocation for the **actor** instance */
  actorInvocationType: z.enum(BIQRuntimeInvocationType),
  /** The global $.ctx object. The context of the call to the actor's receive method. See BIQRuntimeContext in the api. */
  ctx: RuntimeContextSchema,
  /** the source message object for trigger actors */
  actorOrchestratorMessage: z.optional(RuntimeActorOrchestratorMessageSchema),
  /** the actor source ports */
  sourcePorts: z.array(RuntimeActorSourcePortSchema),
  /** the actor runtime receive response for interpolateOutputs method to evaluate the output when the receive method is invoked by the orchestrator */
  receiveResponse: z.optional(RuntimeActorReceiveResponseSchema),
  /**
   * This is a collection of the configurations. All object values are sent as yaml strings. The configuration essentially tells
   * the Actor what to do, it will also provide the necessary parameters (including as JS expressions).
   */
  configuration: ActorConfigurationSchema,
  /** the object that represents actors long term and short term memories */
  memory: RuntimeActorMemorySchema,
  /** the global $.msg object. This object contains all the accumulated messages emitted by the previous actors in the canvas. */
  msg: RuntimePrevEmittedMessagesSchema,
  /** the global $.err object. This object contains all the accumulated error messages emitted by the previous actors in the canvas. */
  err: RuntimePrevEmittedErrorsSchema,
  /** the prebuilt runtime cache to start this actor from; absent ⇒ the legacy per-actor environment */
  runtimeCache: z.optional(RuntimeCacheSchema),
  /**
   * the grant to upload this invoke's receive output when its messages are above the workspace's
   * message soft maximum (and within its message hard maximum). Absent ⇒ the runtime answers
   * PayloadExceedAllowedSize instead. Only present on Receive and InterpolateOutputs invokes. See
   * ./externalPayload.ts
   */
  externalPayloadUpload: z.optional(ExternalPayloadUploadSchema),
  /** values the runtime must hydrate into this request (from S3, through its heap cache) before running. See ./externalPayload.ts */
  externalRefs: z.optional(z.array(ExternalRefSchema)),
  /** the hard cap in bytes for one invocation's hydrated inputs and for its uploaded output object (from the workspace's limits) */
  maxExternalPayloadSizeInBytes: z.optional(z.number().int().positive()),
});

export type RuntimeRequest = z.infer<typeof RuntimeRequestSchema>;
```
