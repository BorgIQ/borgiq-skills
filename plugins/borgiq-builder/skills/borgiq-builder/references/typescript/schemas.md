# Common Schemas

Zod schemas for IDs, files, runtime types, context variables, actor definitions, JSON schema, flowrun messages, signals, and errors.

## Table of Contents

- [schemas/actor.ts](#schemasactor)
- [schemas/agentLambdaSegment.ts](#schemasagentlambdasegment)
- [schemas/awsLambdaFunction.ts](#schemasawslambdafunction)
- [schemas/connection.ts](#schemasconnection)
- [schemas/ctx.ts](#schemasctx)
- [schemas/error.ts](#schemaserror)
- [schemas/file.ts](#schemasfile)
- [schemas/flowrunJobResult.ts](#schemasflowrunjobresult)
- [schemas/flowrunMessage.ts](#schemasflowrunmessage)
- [schemas/idSchema.ts](#schemasidschema)
- [schemas/interface.ts](#schemasinterface)
- [schemas/jsonSchema.ts](#schemasjsonschema)
- [schemas/proxy.ts](#schemasproxy)
- [schemas/runtime.ts](#schemasruntime)
- [schemas/signals.ts](#schemassignals)
- [schemas/trigger.ts](#schemastrigger)
- [schemas/urlAllowlist.ts](#schemasurlallowlist)

## schemas/actor

**Source:** `schemas/actor.ts`

```typescript
/**
 * NOTE:
 * Any types that is not used in the runtime is found in packages/types/src/schemas/api/actor.ts
 * This file is to be used ONLY for types that is used in the runtime.
 */
import { z } from 'zod';

import { BIQActorType } from '../canvas.js';

import { RuntimeActorMemorySchema } from './flowrunJobResult.js';
import { ActorConfigurationSchema, RuntimeActorSourcePortSchema, RuntimeActorOrchestratorMessageSchema } from './runtime.js';
import { RuntimeContextSchema } from './ctx.js';

export const ActorArgumentsSchema = z.object({
  /** the id of the actor being invoked in the runtime */
  actorId: z.string(),
  /** the actor type being invoked in the runtime */
  actorType: z.enum(BIQActorType),
  /** the actor's current long term and short term memories */
  memory: RuntimeActorMemorySchema,
  /** unique identifier for the actor invocation */
  actorInvocationId: z.string(),
  /** The actors source ports */
  sourcePorts: z.array(RuntimeActorSourcePortSchema),
  /** the context data for the runtime invocation */
  ctx: RuntimeContextSchema,
  /** the pre-interpolated actor configuration. Carries the LTM/STM/continueOnError flags and the raw YAML strings for options/code/inputs/vars/etc. */
  configuration: ActorConfigurationSchema,
  /** the source message for trigger actors */
  actorOrchestratorMessage: z.optional(RuntimeActorOrchestratorMessageSchema),
  /** need a store to set stats on the actor, like execution time, disk usage, etc. */
  stats: z.record(z.string(), z.any()),
});

export type ActorArguments = z.infer<typeof ActorArgumentsSchema>;

export const RuntimeEnvironmentSchema = z.object({
  codeDir: z.string(),
  dataDir: z.string(),
});

export type RuntimeEnvironment = z.infer<typeof RuntimeEnvironmentSchema>;
```

## schemas/agentLambdaSegment

**Source:** `schemas/agentLambdaSegment.ts`

```typescript
/**
 * NOTE:
 * Shared between the platform (the orchestrator builds the invoke event) and
 * the lambda runtime (the segment host consumes it).
 *
 * An agent lambda segment runs one time-boxed slice of a pi coding-agent session inside the
 * workspace's own runtime Lambda function. Unlike a normal actor invoke (which carries a full
 * RuntimeRequest), a segment invoke is its own top-level discriminated event so it doesn't
 * have to fabricate a RuntimeRequest — but it reuses the same `token`/`apiUrl`/`envVars`
 * envelope so the lambda's existing borgiqApi/config/proxy-CA bootstrap applies unchanged.
 */
import { z } from 'zod';

import { RuntimeAgentLambdaSignalSchema } from './signals.js';
import { TraceContextSchema } from './awsLambdaFunction.js';
import { AiProvider } from '../ai/index.js';

/** Discriminator value distinguishing a segment invoke from a normal AwsLambdaInvokeEvent. */
export const AGENT_LAMBDA_SEGMENT_EVENT_KIND = 'agent-lambda-segment';

/** The session-specific data for one segment. Everything credential/transport-related
 * (token, apiUrl, proxy URL, CA bundle) rides in the event envelope / envVars instead. */
export const AgentLambdaSegmentPayloadSchema = z.object({
  /** Status-hook URL the segment posts heartbeats / loop / tool-result / checkpointed / complete to */
  statusHookUrl: z.string(),
  orgId: z.string(),
  workspaceId: z.string(),
  canvasId: z.string(),
  actorId: z.string(),
  flowrunId: z.string(),
  flowrunJobId: z.string(),
  sessionId: z.string(),
  /** 0-based index of this segment in the checkpoint chain */
  segmentIndex: z.number().int().nonnegative(),
  /** Random token granted per segment; stamped on every status post so the orchestrator
   * fences stale/zombie segments (a superseded segment's posts are dropped). */
  epochToken: z.string(),
  /** True when this segment resumes an existing pi session (checkpoint chain or continuation) */
  isContinuation: z.boolean(),
  /** When resuming, whether the host must deliver `signal.task` as a fresh user prompt rather
   * than silently resuming via continueFromLeaf(). True only when a NEW flowrun reuses an
   * existing sessionId (a new task to run); false for same-run checkpoint chaining. */
  deliverPrompt: z.boolean().optional(),
  /** Assistant turns already consumed across prior segments (maxLoopCount is session-wide) */
  loopCountUsed: z.number().int().nonnegative(),
  /** The runtime function's user-configured timeout. The host's budget is
   * min(context.getRemainingTimeInMillis(), functionTimeoutSeconds*1000); elapsed time =
   * functionTimeoutSeconds*1000 - getRemainingTimeInMillis(). */
  functionTimeoutSeconds: z.number().int().positive(),
  /** How long before the deadline the host starts its checkpoint sequence */
  shutdownMarginSeconds: z.number().int().positive(),
  /** The runtime function's ephemeral (/tmp) storage in MB. Used by the zip-snapshot
   * fallback to derive the durable-workspace cap (20% of ephemeral, leaving headroom to zip
   * in place) and the free-space floor. The mount mode ignores it (close = durable in
   * place, ~1x the workspace). */
  functionEphemeralStorageSizeInMB: z.number().int().positive(),
  /** LLM calls go provider-direct through the secret proxy: the host configures pi with this
   * placeholder as the provider API key; the proxy substitutes the workspace's real AI
   * credential at egress. No key material ever enters the Lambda. Optional because a
   * finalize-only invoke (below) never calls the model. */
  aiKeyPlaceholder: z.string().optional(),
  /** The AI provider the placeholder resolves to (derived from the signal model). Optional for
   * the same reason as aiKeyPlaceholder. */
  aiProvider: z.nativeEnum(AiProvider).optional(),
  /** Finalize-only invoke: skip the pi LLM loop entirely — just restore the last checkpoint and
   * re-produce the two done-port zips, then post a terminal Error carrying them + endReasonOverride.
   * Used by the orchestrator's timeout / watchdog-give-up paths so a terminated session still emits
   * its output/session zips (matching AgentHarnessActor). */
  finalizeOnly: z.boolean().optional(),
  /** The endReason a finalize-only invoke stamps on its terminal post ('timeout' for a session
   * timeout, 'error' for a watchdog-declared death). Ignored unless finalizeOnly is true. */
  endReasonOverride: z.enum(['timeout', 'error']).optional(),
  /** BIQFile id of the prior segment's combined checkpoint (workspace + .pi) to restore
   * from — carried forward by the orchestrator from the previous segment's `checkpointed`
   * post. Absent on the first segment of a session. */
  restoreFromCheckpointFileId: z.string().optional(),
  /** User-provided env exposed to the Deno tool subprocess (and bash). Decrypted by the
   * orchestrator from `signal.encryptedEnv` via KMS and passed as plaintext here — it never
   * persists (the payload rides the Event invoke, not Redis), mirroring how the harness tier
   * decrypts before handing env to the sandbox. Values are stringified. */
  toolEnv: z.record(z.string(), z.string()).optional(),
  /** The actor signal (task, model, tool filters, net flags, encrypted env, ...) */
  signal: RuntimeAgentLambdaSignalSchema,
});

export type AgentLambdaSegmentPayload = z.infer<typeof AgentLambdaSegmentPayloadSchema>;

/** The full Event-invoke payload for a segment. Sent whole (no Redis stash) — it sits well
 * under the 256 KB async-invoke cap. `proxyUrl` / CA bundle / runtime binaries ride in
 * `envVars` exactly as a normal invoke, so the lambda bootstrap is reused unchanged. */
export const AgentLambdaSegmentInvokeEventSchema = z.object({
  kind: z.literal(AGENT_LAMBDA_SEGMENT_EVENT_KIND),
  /** Segment-scoped runtime JWT (TTL = budget + finalize buffer) for status hook, file
   * proxy, invoke-tool, and the secret proxy's per-request X-Borgiq-Token. */
  token: z.string(),
  /** Borgiq runtime API base URL */
  apiUrl: z.string(),
  /** S2-dev access token for streaming the segment's stdout/stderr to the flowrun stream —
   * same channel as a normal invoke, so segment logs surface in the UI. */
  s2DevAccessToken: z.string().optional(),
  /** S2-dev basin name for the streaming above. */
  s2DevBasinName: z.string().optional(),
  /** Runtime config + proxy wiring (BORGIQ_PROXY_URL, BORGIQ_PROXY_CA_CERT, DENO_BINARY_PATH,
   * RUNTIME_LOCATION, ...) — same envelope as a normal invoke. */
  envVars: z.record(z.string(), z.union([z.string(), z.number(), z.boolean()])),
  /** OpenTelemetry trace context for distributed tracing */
  traceContext: TraceContextSchema.optional(),
  /** The session-specific segment data */
  segment: AgentLambdaSegmentPayloadSchema,
});

export type AgentLambdaSegmentInvokeEvent = z.infer<typeof AgentLambdaSegmentInvokeEventSchema>;
```

## schemas/awsLambdaFunction

**Source:** `schemas/awsLambdaFunction.ts`

```typescript
/**
 * NOTE:
 * Any types that is not used in the runtime is found in packages/types/src/schemas/runtime/awsLambdaFunction.ts
 * This file is to ONLY be used for types that is used in the runtime.
 */
import { z } from 'zod';
import { RuntimeRequestSchema } from './runtime.js';

/**
 * Schema for OpenTelemetry trace context propagation.
 * Used to continue distributed traces from the orchestrator into Lambda.
 */
export const TraceContextSchema = z.object({
  /** The trace ID (32 hex characters) */
  traceId: z.string(),
  /** The parent span ID (16 hex characters) */
  spanId: z.string(),
  /** Trace flags (typically 1 for sampled) */
  traceFlags: z.number(),
  /** Whether the context originated from a remote service */
  isRemote: z.boolean().optional(),
});

export type TraceContext = z.infer<typeof TraceContextSchema>;

export const AwsLambdaInvokeEventSchema = z.object({
  /** the invocation token from borgiq api server. need to use this token to make requests back to api */
  token: z.string(),
  /** the borgiq api url to talk to using the token */
  apiUrl: z.string(),
  /** the s2-dev access token for streaming stdout/stderr to the stream */
  s2DevAccessToken: z.string().optional(),
  /** the s2-dev basin name for streaming */
  s2DevBasinName: z.string().optional(),
  /** the environment variables allowed to be accessed by the runtime */
  envVars: z.record(z.string(), z.union([z.string(), z.number(), z.boolean()])),
  /** the request to be made to the runtime */
  request: RuntimeRequestSchema,
  /** OpenTelemetry trace context for distributed tracing (optional for backward compatibility) */
  traceContext: TraceContextSchema.optional(),
});

export type AwsLambdaInvokeEvent = z.infer<typeof AwsLambdaInvokeEventSchema>;
```

## schemas/connection

**Source:** `schemas/connection.ts`

```typescript
import { z } from 'zod';

import { BIQConnectionAuthType } from '../connection.js';

/** The schemas and types for BIQ Connection Auth */

/** Authenticate http requests using AWS Signature V4 */
export const AWSV4AuthDataSchema = z.object({
  accessKey: z.string()
    .describe('Your AWS access key ID from your AWS Console'),
  secretKey: z.string()
    .describe('Your AWS secret access key from your AWS Console'),
  sessionToken: z.string().nullish()
    .describe('Your session token from your AWS Console'),
  signQuery: z.boolean().nullish()
    .describe('to sign the query instead of adding an Authorization header, defaults to false'),
  awsRegion: z.string().nullish()
    .describe('The region of the AWS service you are accessing, will try to be calculated from hostname or host or use \'us-east-1\' if not given'),
  serviceName: z.string().nullish()
    .describe('The AWS service you are accessing, will try to be calculated from hostname or host if not given'),
});

export type AWSV4AuthData = z.infer<typeof AWSV4AuthDataSchema>;

/** Authenticate http requests using API Key */
export const APIKeyDataSchema = z.object({
  key: z.string()
    .describe('The key to add to the header or query params'),
  value: z.string()
    .describe('The value to add to the header or query params'),
  addToHeader: z.boolean()
    .describe('Add the key and value to the header instead of query params'),
});

export type APIKeyData = z.infer<typeof APIKeyDataSchema>;

/** Authenticate http requests using Bearer Token */
export const BearerDataSchema = z.object({
  token: z.string()
    .describe('The bearer token to add to the Authorization header'),
});

export type BearerData = z.infer<typeof BearerDataSchema>;

/** Authenticate http requests using OAuth1 */
export const OAuth1DataSchema = z.object({
  consumerKey: z.string()
    .describe('A value used to identify a consumer with the service provider'),
  consumerSecret: z.string()
    .describe('A value used by the consumer to establish ownership of the key. (For HMAC and PLAINTEXT signing methods.)'),
  token: z.string().nullish()
    .describe('A value used by the consumer permission to access the user\'s data'),
  tokenSecret: z.string().nullish()
    .describe('A value used by the consumer to establish ownership of a given token. (For HMAC and PLAINTEXT signing methods.)'),
  signatureMethod: z.string().nullish()
    .describe('he method the API uses to authenticate requests'),

  /** Advanced Inputs */
  callback: z.string().nullish()
    .describe('URL service provider will redirect to following user authorization. (Required if your server uses OAuth 1.0 Revision A.)'),
  verifier: z.string().nullish()
    .describe('Verification code from service provider after user auth.'),
  timestamp: z.string().nullish(),
  nonce: z.string().nullish()
    .describe('A random string generated by the client.'),
  version: z.string().nullish()
    .describe('The version of the OAuth authentication protocol (1.0).'),
  realm: z.string().nullish(),
  includeBodyHash: z.boolean().nullish()
    .describe('Hash for integrity check with request bodies other than application/x-www-form-urlencoded. (Deactivated when you\'re using callback URL / verifier.)'),
  addEmptyParamsToSign: z.boolean().nullish()
    .describe('Add empty parameters to the signature.'),
  disableHeaderEncoding: z.boolean().nullish()
    .describe('Disable header encoding.'),
  addParamsToHeader: z.boolean().nullish()
    .describe('Add parameters to the header instead of the query string.'),
});

export type OAuth1Data = z.infer<typeof OAuth1DataSchema>;

/** Authenticate http requests using OAuth2 */
export const OAuth2DataSchema = z.object({
  token: z.string()
    .describe('The oauth 2 token generated'),
  prefix: z.string()
    .describe('The prefix to add to the Authorization header'),
  addToHeader: z.boolean()
    .describe('Add the token to the header instead of query params'),
});

export type OAuth2Data = z.infer<typeof OAuth2DataSchema>;

/** Authenticate http requests using Basic Auth */
export const BasicAuthDataSchema = z.object({
  userName: z.string()
    .describe('The username to add to the Authorization header'),
  password: z.string()
    .describe('The password to add to the Authorization header'),
});

export type BasicAuthData = z.infer<typeof BasicAuthDataSchema>;

/** Authenticate http requests using Custom Auth */
export const CustomAuthDataSchema = z.object({
  headers: z.record(z.string(), z.union([z.string(), z.number(), z.boolean()])).nullish()
    .describe('The headers to add to the request. This will override any duplicate header keys.'),
  queryParams: z.record(z.string(), z.unknown()).nullish()
    .describe('The query params to add to the request. This will override any duplicate query param keys.'),
  body: z.record(z.string(), z.unknown()).nullish()
    .describe('The body keys to add to the request. This will override any duplicate body keys.'),
});

export type CustomAuthData = z.infer<typeof CustomAuthDataSchema>;

/** specify the auth schema for each BIQ connection auth type */
export const AuthDataSchema = z.discriminatedUnion('type', [
  z.object({ type: z.literal(BIQConnectionAuthType.AWS), values: AWSV4AuthDataSchema }),
  z.object({ type: z.literal(BIQConnectionAuthType.API_KEY), values: APIKeyDataSchema }),
  z.object({ type: z.literal(BIQConnectionAuthType.BEARER), values: BearerDataSchema }),
  z.object({ type: z.literal(BIQConnectionAuthType.OAUTH1), values: OAuth1DataSchema }),
  z.object({ type: z.literal(BIQConnectionAuthType.OAUTH2), values: OAuth2DataSchema }),
  z.object({ type: z.literal(BIQConnectionAuthType.BASIC), values: BasicAuthDataSchema }),
  z.object({ type: z.literal(BIQConnectionAuthType.CUSTOM), values: CustomAuthDataSchema }),
]);

export type AuthData = z.infer<typeof AuthDataSchema>;

/**
 * The MCP-valid subset of {@link AuthDataSchema}, used for per-server `auth` on remote (HTTP)
 * MCP servers consumed by the AiAgentActor and AgentHarnessActor.
 *
 * MCP JSON-RPC only ever carries auth in a request header, so this subset:
 *   - drops AWS/OAuth1 (request-signing schemes that don't map to a static header), and
 *   - restricts API_KEY / OAUTH2 to header mode (`addToHeader: true`) and CUSTOM to `headers`
 *     only (no query-param or body injection) — enforced by the superRefine below.
 *
 * `mcpOauth` connections (RFC 9728 discovery + DCR + PKCE) render `auth.type: bearer` at
 * resolution time, so they flow through the BEARER member with no new union variant.
 */
export const McpAuthDataSchema = z.discriminatedUnion('type', [
  z.object({ type: z.literal(BIQConnectionAuthType.BEARER), values: BearerDataSchema }),
  z.object({ type: z.literal(BIQConnectionAuthType.API_KEY), values: APIKeyDataSchema }),
  z.object({ type: z.literal(BIQConnectionAuthType.OAUTH2), values: OAuth2DataSchema }),
  z.object({ type: z.literal(BIQConnectionAuthType.BASIC), values: BasicAuthDataSchema }),
  z.object({ type: z.literal(BIQConnectionAuthType.CUSTOM), values: CustomAuthDataSchema }),
]).superRefine((auth, ctx) => {
  if (auth.type === BIQConnectionAuthType.API_KEY && !auth.values.addToHeader) {
    ctx.addIssue({ code: z.ZodIssueCode.custom, path: ['values', 'addToHeader'], message: 'MCP API-key auth must be sent as a header (addToHeader: true) — JSON-RPC has no query string to inject into.' });
  }
  if (auth.type === BIQConnectionAuthType.OAUTH2 && !auth.values.addToHeader) {
    ctx.addIssue({ code: z.ZodIssueCode.custom, path: ['values', 'addToHeader'], message: 'MCP OAuth2 auth must be sent as a header (addToHeader: true) — JSON-RPC has no query string to inject into.' });
  }
  if (auth.type === BIQConnectionAuthType.CUSTOM && (auth.values.queryParams || auth.values.body)) {
    ctx.addIssue({ code: z.ZodIssueCode.custom, path: ['values'], message: 'MCP custom auth may only set request headers — queryParams and body are not applied to JSON-RPC calls.' });
  }
});

export type McpAuthData = z.infer<typeof McpAuthDataSchema>;
```

## schemas/ctx

**Source:** `schemas/ctx.ts`

```typescript
import { z } from 'zod';

import { BIQActorType } from '../canvas.js';


/** information about the borgIQ Organization associated with the runtime actor being invoked. */
export const RuntimeOrgInfoSchema = z.object({
  /** id of the org */
  id: z.string(),
  /** name of the org */
  name: z.string(),
});

export type RuntimeOrgInfo = z.infer<typeof RuntimeOrgInfoSchema>;

/** information about the runtime actor being invoked. */
export const RuntimeActorInfoSchema = z.object({
  /** id of the actor */
  id: z.string(),
  /** the type of the actor */
  type: z.enum(BIQActorType),
  /** the name of the actor */
  name: z.string(),
  /** the message variable for the actor */
  msgVar: z.string(),
  /** description about the actor */
  description: z.string(),
});

export type RuntimeActorInfo = z.infer<typeof RuntimeActorInfoSchema>;

/** information about tools available for an agent type actors. */
export const AgentToolsInfoSchema = z.record(z.string(), z.object({
  id: z.string(),
  name: z.string(),
  description: z.string(),
  jsonSchema: z.any(),
}));

export type AgentToolsInfo = z.infer<typeof AgentToolsInfoSchema>;

/** information about the runtime actor being invoked. */
export const CurrentRuntimeActorInfoSchema = RuntimeActorInfoSchema.extend({
  tools: AgentToolsInfoSchema.optional(),
});

export type CurrentRuntimeActorInfo = z.infer<typeof CurrentRuntimeActorInfoSchema>;


/** information about the borgIQ workspace associated with the runtime actor being invoked. */
export const RuntimeWorkspaceInfoSchema = z.object({
  /** id of the workspace */
  id: z.string(),
  /** slug of the workspace */
  slug: z.string(),
  /** name of the workspace */
  name: z.string(),
});

export type RuntimeWorkspaceInfo = z.infer<typeof RuntimeWorkspaceInfoSchema>;


/** information about the borgIQ canvas associated with the runtime actor being invoked. */
export const RuntimeCanvasInfoSchema = z.object({
  /** id of the canvas */
  id: z.string(),
  /** slug of the canvas */
  slug: z.string(),
  /** name of the canvas */
  name: z.string(),
  /** All the http trigger actors that are available in the flowrun.data */
  webhookTriggers: z.record(
    z.string(),
    RuntimeActorInfoSchema.merge(
      z.object({
        url: z.string()
      })
    )
  ),
  /** All the interface trigger actors that are available in the flowrun.data */
  interfaceTriggers: z.record(
    z.string(),
    RuntimeActorInfoSchema.merge(
      z.object({
        url: z.string()
      })
    )
  ),
  /** All the app trigger actors that are available in the flowrun.data */
  appTriggers: z.record(
    z.string(),
    RuntimeActorInfoSchema.merge(
      z.object({
        url: z.string()
      })
    )
  ),
  /** All the universal trigger actors (webhook source enabled) that are available in the flowrun.data */
  universalTriggers: z.record(
    z.string(),
    RuntimeActorInfoSchema.merge(
      z.object({
        url: z.string()
      })
    )
  ),
});

export type RuntimeCanvasInfo = z.infer<typeof RuntimeCanvasInfoSchema>;

/** information about the borgIQ flowrun associated with the runtime actor being invoked. */
export const RuntimeFlowrunInfoSchema = z.object({
  /** id of the flowrun */
  id: z.string(),
  /** the time the flowrun was created */
  createdAt: z.string(),
});

export type RuntimeFlowrunInfo = z.infer<typeof RuntimeFlowrunInfoSchema>;

/** information about the parent flowrun associated with the runtime actor being invoked. */
export const RuntimeParentFlowrunInfoSchema = z.object({
  /** the information about the parent workspace */
  workspace: RuntimeWorkspaceInfoSchema,
  /** the information about the parent canvas */
  canvas: RuntimeCanvasInfoSchema.pick({ id: true, name: true, slug: true }),
  /** the id of the parent flowrun */
  flowrunId: z.string(),
  /** the id of the actor in the parent flowrun */
  actorId: z.string(),
  /** the id of the flowrun job in the parent flowrun */
  flowrunJobId: z.string(),
});

export type RuntimeParentFlowrunInfo = z.infer<typeof RuntimeParentFlowrunInfoSchema>;

/**
 * The context data associated with invoking any of the actor's method on the runtime.
 * NOTE: in the case of ping or validate calls, the flowrun, sourceActor, sourceMsgId, request should be undefined/null.
*/
export const RuntimeContextSchema = z.object({
  /** org associated with the flowrun */
  org: RuntimeOrgInfoSchema,
  /** workspace associated with the flowrun */
  workspace: RuntimeWorkspaceInfoSchema,
  /** canvas info and meta data of the canvas associated with the flowrun. NOTE; the webhookTriggers data needs to come from the flowrun.data NOT from canvas.data */
  canvas: RuntimeCanvasInfoSchema,
  /** information about the actor the orchestrator needs to process the response for. i.e. the actor who's being invoked in the runtime */
  actor: CurrentRuntimeActorInfoSchema,
  /** flowrun data associated with the current invocation */
  flowrun: RuntimeFlowrunInfoSchema,
  /** the information about the trigger actor which started the flowrun, subflow triggers will be defined by the subflow entry actor */
  triggerActor: RuntimeActorInfoSchema,
  /** the information about the actor who emitted the message (if the source of the message was an actor). i.e. trigger actors don't have source actors */
  sourceActor: z.optional(RuntimeActorInfoSchema),
  /**
   * When the source actor is set, this points to the id of the source actor emitted message.
   * When the current invocation is the trigger fire itself, it is null.
   */
  sourceMsgId: z.optional(z.string()),
  /** the information about the parent flowrun */
  parentFlowrun: RuntimeParentFlowrunInfoSchema.optional(),
});

export type RuntimeContext = z.infer<typeof RuntimeContextSchema>;
```

## schemas/error

**Source:** `schemas/error.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from './jsonSchema.js';


export const ActorErrorConfigurationSchema = z.object({
  if: z.boolean(),
  retryIf: z.boolean().nullish(),
  message: z.string().nullish(),
  includeResult: z.boolean().nullish(),
});

export type ActorErrorConfiguration = z.infer<typeof ActorErrorConfigurationSchema>;

export const ActorErrorConfigurationJsonSchema: BIQJsonSchema = {
  properties: {
    if: {
      type: BIQJsonSchemaType.Boolean,
      title: 'If',
      description: 'If the actor should throw an error',
      default: '${{}}',
    },
    retryIf: {
      type: BIQJsonSchemaType.Boolean,
      title: 'Retry If',
      description: 'If the error should be retried',
      default: '${{}}',
    },
    message: {
      type: BIQJsonSchemaType.String,
      title: 'Message',
      description: 'The message to show to the user',
    },
    includeResult: {
      type: BIQJsonSchemaType.Boolean,
      title: 'Include Result',
      description: 'If the error stack trace should include the result',
      default: false,
      ui: {
        component: 'switch',
      },
    },
  },
  required: ['if'],
};
```

## schemas/file

**Source:** `schemas/file.ts`

```typescript
/** NOTE: This file is to ONLY be used for types that is used in the runtime. */
import { z } from 'zod';

import { idSchema } from './idSchema.js';

import { BIQFileStatus, BIQFileStorageEngine, BIQFileUsageType } from '../common.js';

const status = z.enum(BIQFileStatus);
const usageType = z.enum(BIQFileUsageType);

export const FileInputSchema = z.object({
  id: idSchema.fileId,
  key: z.string(),
  fileName: z.string().min(1, 'must be 1 or more characters long').max(255, 'must be 255 or fewer characters long'),
  mimeType: z.string().min(1, 'must be 1 or more characters long').max(255, 'must be 255 or fewer characters long'),
  sizeInBytes: z.number().int(),
  storageEngine: z.enum(BIQFileStorageEngine).optional(),
  status: z.optional(status),
  usageType: z.optional(usageType),
  md5: z.optional(z.string()),
  sha256: z.optional(z.string()),
});

export type FileInput = z.infer<typeof FileInputSchema>;

export const BIQFileSchema = z.object({
  id: idSchema.fileId,
  fileName: z.string(),
  md5: z.string(),
  sha256: z.string(),
  mimeType: z.string(),
  sizeInBytes: z.number(),
  createdAt: z.string(),
});

export type BIQFile = z.infer<typeof BIQFileSchema>;

/** this is the input the api receives for uploading multiple files, if this updates, make sure to update the FilesRuntimeUploadedSchemaFromRuntime */
export const FilesRuntimeUploadInputSchema = z.object({
  body: z.object({
    files: z.array(FileInputSchema.extend({ uploadIndex: z.number() })),
    // Validate the flowrun id shape (FLRN-prefixed, 30 chars) rather than accepting any string —
    // this endpoint writes it straight into files.flowrun_id, so a session/sandbox id or malformed
    // value must be rejected at the boundary instead of silently persisted.
    flowrunId: idSchema.flowrunId,
  }),
});

export type FilesRuntimeUploadInput = z.infer<typeof FilesRuntimeUploadInputSchema>;

/** since the api middleware adds the id and key to each file, this is the input required to be sent from the runtime */
export const RuntimeBodyFilesUploadedInputsSchema = z.object({
  files: z.array(FileInputSchema.omit({ id: true, key: true }).extend({ uploadIndex: z.number() })),
  // Same flowrun-id shape validation as FilesRuntimeUploadInputSchema (this is the runtime-side
  // body before the API middleware adds id/key) — keep the two in sync.
  flowrunId: idSchema.flowrunId,
});

export type RuntimeBodyFilesUploaded = z.infer<typeof RuntimeBodyFilesUploadedInputsSchema>;

export const FilesRuntimeUpdateUploadsBodySchema = z.object({
  files: z.array(
    z.object({
      id: idSchema.fileId,
      status,
      md5: z.optional(z.string()),
      sha256: z.optional(z.string()),
    }).refine((data) => {
      // if the file is uploaded successfully, then the md5 and sha256 are required
      if (data.status === BIQFileStatus.UploadSuccess) {
        return data.md5 !== undefined && data.sha256 !== undefined;
      }
      return true;
    }, {
      error: 'MD5 and SHA256 are required for successful file upload.',
    }),
  ),
});

export type FilesRuntimeUpdateUploadsBody = z.infer<typeof FilesRuntimeUpdateUploadsBodySchema>;

/** this is the output the api returns for uploading multiple files, if this updates, make sure to update the FilesRuntimeUploadedSchemaFromRuntime */
export const FilesRuntimeUpdateUploadsInputsSchema = z.object({
  body: FilesRuntimeUpdateUploadsBodySchema,
});

export type FilesRuntimeUpdateUploadsInputs = z.infer<typeof FilesRuntimeUpdateUploadsInputsSchema>;
```

## schemas/flowrunJobResult

**Source:** `schemas/flowrunJobResult.ts`

```typescript
/**
 * NOTE:
 * Any types that is not used in the runtime is found in packages/types/src/schemas/runtime/flowrunJobResult.ts
 * This file is to ONLY be used for types that is used in the runtime.
 */
import { z } from 'zod';

import { BIQRuntimeErrorLocation, BIQRuntimeInvocationType, BIQRuntimeResponseStatus, BIQRuntimeRetryStrategy } from '../runtime.js';
import { RuntimeSignalSchema } from './signals.js';

/** the schema representing an actor's interpolated configuration information */
const RuntimeActorConfigurationSchema = z.object({
  // the interpolated credentials
  credentials: z.record(z.string(), z.string()),
  // the interpolated inputs
  inputs: z.record(z.string(), z.any()),
  // the interpolated vars
  vars: z.record(z.string(), z.any()),
  // the interpolated options
  options: z.any(),
  // store the code that is to be run in the runtime for the actor (ONLY NodeJS actor)
  code: z.string(),
});

export type RuntimeActorConfiguration = z.infer<typeof RuntimeActorConfigurationSchema>;

/** the schema that represents actors long term and short term memories */
export const RuntimeActorMemorySchema = z.object({
  /** Object store representing the memory of the actor scoped to the flowrun */
  stm: z.record(z.string(), z.any()),
  /** Object store representing the of the actor scoped to Canvas (Global), this memory survives subsequent execution of the flowrun */
  ltm: z.record(z.string(), z.any()),
});

export type RuntimeActorMemory = z.infer<typeof RuntimeActorMemorySchema>;

/** This defines a validation error for an actor */
const RuntimeValidationErrorSchema = z.object({
  /** the name of the configuration key */
  name: z.string(),
  /** the path to the configuration key */
  path: z.string(),
  /** the error message */
  errorMessage: z.string(),
});

export type RuntimeValidationError = z.infer<typeof RuntimeValidationErrorSchema>;

/**
 * when you want to retry invoking the actor's runtime method again, must pass this options in the error
 * immediate: retry invoking the actor's runtime method immediately.
 * fixed: wait the given number of milliseconds before retrying the actor's runtime method. (default to 5 seconds for delay interval upto maximum of 5 retries)
 * exponential: retry using an exponential back-off policy (by default, first retry starts after 5 seconds and uses backoff rate of 2. i.e. 5s, 10s, 20s, 40s, 80s. max 5 retries)
*/
const RuntimeRetryOptionsSchema = z.object({
  strategy: z.enum(BIQRuntimeRetryStrategy),
  delayInterval: z.optional(z.number()),
  maxRetries: z.optional(z.number()),
  backOffRate: z.optional(z.number()),
});

export type RuntimeRetryOptions = z.infer<typeof RuntimeRetryOptionsSchema>;

/** when there is an error invoking actor's runtime, we need to generate this error object. */
export const RuntimeErrorSchema = z.object({
  /** the location of the error. i.e. in the orchestrator or in the runtime */
  /** this indicates where the error occurred when invoking actor's runtime method. in the orchestrator or in the runtime. */
  location: z.enum(BIQRuntimeErrorLocation),
  /** name of the error */
  name: z.string(),
  /** the actual error message */
  message: z.string(),
  /** stack for the error (if available) */
  stack: z.string(),
  /** the metadata for the error */
  metadata: z.record(z.string(), z.unknown()).optional(),
  /** indicates whether the error can be emitted to the downstream actors. i.e. some errors can not be emitted and the flowrun needs to be terminated. */
  canEmit: z.boolean(),
  /** whether the actor's runtime method can be retried again */
  retry: z.boolean(),
  /** the options for retrying the actor's runtime method */
  retryOptions: z.optional(RuntimeRetryOptionsSchema),
});

export type RuntimeError = z.infer<typeof RuntimeErrorSchema>;

/**
 * RuntimeError.name emitted by the lambda runtime when a warm container cannot host the next actor
 * (memory or ephemeral-disk exhaustion after evicting idle workers) — always retryable. The
 * orchestrator keys its logging off this name and the runtime's resource-monitor produces it, so
 * both sides must use this constant rather than the string literal.
 */
export const RESOURCE_EXHAUSTED_ERROR_NAME = 'ResourceExhausted';

/** the metadata carried on a ResourceExhausted RuntimeError (see RESOURCE_EXHAUSTED_ERROR_NAME) */
export const ResourceExhaustedMetadataSchema = z.object({
  /** which resource ran out */
  resource: z.enum(['memory', 'disk', 'both']),
  memUsedBytes: z.number(),
  memLimitBytes: z.number(),
  diskUsedBytes: z.number(),
  diskLimitBytes: z.number(),
});

export type ResourceExhaustedMetadata = z.infer<typeof ResourceExhaustedMetadataSchema>;

/** the schema for the response from the receive method of an actor (is also used for the data to run the interpolateOutputs method) */
export const RuntimeActorReceiveResponseSchema = z.object({
  status: z.enum(BIQRuntimeResponseStatus),
  messages: z.record(z.string(), z.unknown()),
  signal: z.optional(RuntimeSignalSchema),
  error: z.optional(RuntimeErrorSchema),
  validationErrors: z.optional(z.array(RuntimeValidationErrorSchema)),
});

const RuntimeResponseMetadataSchema = z.object({
  // The response JSON schema version number
  schemaVersion: z.number(),
  // The runtime environment the actor is running. i.e. node16 | python3 | etc...
  environment: z.string(),
  // the id of the runtime invocation. remember an actor can be invoked multiple times for the same flowrun. this id uniquely identifies the invocation
  actorInvocationId: z.string(),
  /** The type of invocation for an actor. It is basically in invocation of a particular function in an actor instance. i.e. actor.receive(), actor.interpolate(), etc... */
  actorInvocationType: z.enum(BIQRuntimeInvocationType),
  // The id of the lambda container issued by first invoke
  runnerId: z.string(),
  // The time the runtime execution started at. i.e. new Date().toISOString() -> '2021-02-20T19:44:24.977Z'
  startedAt: z.string(),
  // The time the runtime execution ended at. i.e. new Date().toISOString() -> '2021-02-20T19:44:24.977Z'
  endedAt: z.string(),
  // general stats from the invocation of the actor
  stats: z.record(z.string(), z.string()),
  /** the response status for invoking the runtime. indicates whether the runtime invocation was successful or failure */
  status: z.enum(BIQRuntimeResponseStatus),
});

export type RuntimeResponseMetadata = z.infer<typeof RuntimeResponseMetadataSchema>;

/**
 * The response data that is sent back by the runtime.
 * when there is an unknown error there might not be any response data to be sent back.
*/
export const RuntimeResponseDataSchema = z.union([
  z.object({
    error: RuntimeErrorSchema,
  }),
  z.object({
    /** if there was an error invoking the runtime method */
    error: z.optional(RuntimeErrorSchema),
    /** errors from running validation on the actor configuration data. Present for 'validate' or 'receive' method calls */
    validationErrors: z.array(RuntimeValidationErrorSchema),
  }),
  z.object({
    /** if there was an error invoking the runtime method */
    error: z.optional(RuntimeErrorSchema),
    /** this is present when calling actor's 'interpolate' method. this is the interpolated actor configuration data */
    interpolatedConfiguration: RuntimeActorConfigurationSchema.omit({ credentials: true }),
  }),
  z.object({
    /** if there was an error invoking the runtime method */
    error: z.optional(RuntimeErrorSchema),
    /** the response from calling actor's ping method */
    pingMsg: z.string(),
  }),
  z.object({
    /** if there was an error invoking the runtime method */
    error: z.optional(RuntimeErrorSchema),
    /** errors from running validation on the actor configuration data. Present for 'validate' or 'receive' method calls */
    validationErrors: z.array(RuntimeValidationErrorSchema),
    /** the updated short term and long term memories */
    memory: RuntimeActorMemorySchema,
    /** The array of new messages emitted by the actor due to the invocation of the `receive` method */
    messages: z.record(z.string(), z.array(z.unknown())),
    /** We need to signal the orchestrator to do some work (i.e delay, wait for external events, etc) **/
    signal: z.optional(RuntimeSignalSchema),
  }),
]);

export type RuntimeResponseData = z.infer<typeof RuntimeResponseDataSchema>;

/**
 * The response that is sent back by the runtime.
 * when there is an unknown error there might not be any response data to be sent back.
*/
export const RuntimeResponseSchema = z.intersection(
  RuntimeResponseMetadataSchema,
  RuntimeResponseDataSchema,
);

export type RuntimeResponse = z.infer<typeof RuntimeResponseSchema>;
```

## schemas/flowrunMessage

**Source:** `schemas/flowrunMessage.ts`

```typescript
/**
 * NOTE:
 * Any types that is not used in the runtime is found in packages/types/src/schemas/flowrun/flowrunMessage.ts
 * This file is to ONLY be used for types that is used in the runtime.
 */
import { z } from 'zod';


import { MESSAGE_TYPES, TRIGGER_MESSAGE_TYPES } from '../flowrun.js';

export const TriggerMessageTypeSchema = z.enum(TRIGGER_MESSAGE_TYPES);

export const MessageTypeSchema = z.enum(MESSAGE_TYPES);

export type TriggerMessageType = z.infer<typeof TriggerMessageTypeSchema>;

export type MessageType = z.infer<typeof MessageTypeSchema>;
```

## schemas/idSchema

**Source:** `schemas/idSchema.ts`

```typescript
/** NOTE: This file is to ONLY be used for types that is used in the runtime. */
import { z } from 'zod';

import Prefix from '../prefix.js';

const regMsg = 'must follow the pattern for id';
const lenMsg = 'must be exactly 30 characters long';

/** !IMPORTANT: make sure to update the regex in packages/db/src/ts when updating these methods */
/** get the regExp for verifying model remember ULID does not include the letters I, L, O, and U */
const buildIdRegex = (prefix: Prefix): RegExp => {
  return new RegExp(`${prefix}[0123456789abcdefghjkmnpqrstvwxyz]{26}$`);
};


export const idSchema = {
  // schema for org id
  orgId: z.string().regex(buildIdRegex(Prefix.Org), regMsg).length(30, lenMsg),
  // schema for workspace id
  workspaceId: z.string().regex(buildIdRegex(Prefix.Workspace), regMsg).length(30, lenMsg),
  // schema for ai settings id
  aiSettingsId: z.string().regex(buildIdRegex(Prefix.AiSetting), regMsg).length(30, lenMsg),
  // schema for org membership id
  orgMembershipId: z.string().regex(buildIdRegex(Prefix.OrgMembership), regMsg).length(30, lenMsg),
  // schema for workspace membership id
  workspaceMembershipId: z.string().regex(buildIdRegex(Prefix.WorkspaceMembership), regMsg).length(30, lenMsg),
  // schema for org invitation id
  orgAndWorkspaceInvitationId: z.string().regex(buildIdRegex(Prefix.OrgAndWorkspaceInvitation), regMsg).length(30, lenMsg),
  // schema for user id
  userId: z.string().regex(buildIdRegex(Prefix.User), regMsg).length(30, lenMsg),
  // schema for user auth session
  userAuthSessionId: z.string().regex(buildIdRegex(Prefix.UserAuthSession), regMsg).length(30, lenMsg),
  // schema for template id
  actorTemplateId: z.string().regex(buildIdRegex(Prefix.ActorTemplate), regMsg).length(30, lenMsg),
  // schema for template app id
  templateAppId: z.string().regex(buildIdRegex(Prefix.TemplateApp), regMsg).length(30, lenMsg),
  // schema for template category id
  templateCategoryId: z.string().regex(buildIdRegex(Prefix.TemplateCategory), regMsg).length(30, lenMsg),
  // schema for actor id
  actorId: z.string().regex(buildIdRegex(Prefix.Actor), regMsg).length(30, lenMsg),
  // schema for canvas id
  canvasId: z.string().regex(buildIdRegex(Prefix.Canvas), regMsg).length(30, lenMsg),
  // schema for connection edge id
  edgeId: z.string().regex(buildIdRegex(Prefix.Edge), regMsg).length(30, lenMsg),
  // schema for flowrun id
  flowrunId: z.string().regex(buildIdRegex(Prefix.Flowrun), regMsg).length(30, lenMsg),
  // schema for flowrun callback token response id
  flowrunCallbackTokenResponseId: z.string().regex(buildIdRegex(Prefix.FlowrunCallbackTokenResponse), regMsg).length(30, lenMsg),
  // schema for token. i.e. TOKN{crypto.randomBytes(29).toString('hex')} since we are only having a HEX string we only have chars from 0-9 and a-f
  token: z.string().regex(new RegExp(`${Prefix.Token}[0123456789abcdef]{58}$`), regMsg).length(62, 'invalid token size'),
  // schema for page token. i.e. PAGE{crypto.randomBytes(16).toString('hex')} since we are only having a HEX string we only have chars from 0-9 and a-f
  interfaceId: z.string().regex(new RegExp('[0123456789abcdef]{32}$'), regMsg).length(32, 'invalid token size'),
  // schema for flowrun job id
  flowrunJobId: z.string().regex(buildIdRegex(Prefix.FlowrunJob), regMsg).length(30, lenMsg),
  // schema for flowrun job log id
  flowrunJobLogId: z.string().regex(buildIdRegex(Prefix.FlowrunJobLog), regMsg).length(30, lenMsg),
  // schema for flowrun job result id
  flowrunJobResultId: z.string().regex(buildIdRegex(Prefix.FlowrunJobResult), regMsg).length(30, lenMsg),
  // schema for flowrun message id
  flowrunMessageId: z.string().regex(buildIdRegex(Prefix.FlowrunMessage), regMsg).length(30, lenMsg),
  // schema for asset id
  assetId: z.string().regex(buildIdRegex(Prefix.Asset), regMsg).length(30, lenMsg),
  // schema for file id
  fileId: z.string().regex(buildIdRegex(Prefix.File), regMsg).length(30, lenMsg),
  // schema for aws lambda runtime record id
  awsLambdaRuntimeId: z.string().regex(buildIdRegex(Prefix.AwsLambdaRuntime), regMsg).length(30, lenMsg),
  // schema for secret id
  secretId: z.string().regex(buildIdRegex(Prefix.Secret), regMsg).length(30, lenMsg),
  // schema for connection id
  connectionId: z.string().regex(buildIdRegex(Prefix.Connection), regMsg).length(30, lenMsg),
  // schema for data store id
  dataStoreId: z.string().regex(buildIdRegex(Prefix.DataStore), regMsg).length(30, lenMsg),
  // schema for audit log id
  auditLogId: z.string().regex(buildIdRegex(Prefix.AuditLog), regMsg).length(30, lenMsg),
  // schema for api token id (personal access token)
  apiTokenId: z.string().regex(buildIdRegex(Prefix.Token), regMsg).length(30, lenMsg),
  // schema for source port for an actor
  sourcePortId: z.string().regex(new RegExp(`${Prefix.SourcePort}[0123456789abcdefghijklmnopqrstuvwxyz]{7}`), regMsg).length(11, 'must exactly be 11 characters long'),
  // schema for target port for an actor
  targetPortId: z.string().regex(new RegExp(`${Prefix.TargetPort}[0123456789abcdefghijklmnopqrstuvwxyz]{4}`), regMsg).length(11, 'must exactly be 11 characters long'),
};
```

## schemas/interface

**Source:** `schemas/interface.ts`

```typescript
import { z } from 'zod';
import { biqFormComponentArrayZodSchema } from '../formComponents/index.js';

export const BIQInterfacePageDataSchema = z.object({
  formWidth: z.enum(['full', 'half', 'adjustable']).optional(),
  children: biqFormComponentArrayZodSchema,
  pageTitle: z.string().optional(),
  themeColor: z.string().optional(),
  backgroundColor: z.string().optional(),
});

export type BIQInterfacePageData = z.infer<typeof BIQInterfacePageDataSchema>;

export const InterfaceOnSubmitWaitForInterfaceSchema = z.object({
  type: z.literal('nextInterface'),
  loadingMessage: z.string().optional(),
});

export type InterfaceOnSubmitWaitForInterface = z.infer<typeof InterfaceOnSubmitWaitForInterfaceSchema>;

export const InterfaceOnSubmitSuccessMessageSchema = z.object({
  type: z.literal('successMessage'),
  successMessage: z.string().optional(),
});

export type InterfaceOnSubmitSuccessMessage = z.infer<typeof InterfaceOnSubmitSuccessMessageSchema>;

export const InterfaceOnSubmitUrlRedirectSchema = z.object({
  type: z.literal('urlRedirect'),
  url: z.string(),
});

export type InterfaceOnSubmitUrlRedirect = z.infer<typeof InterfaceOnSubmitUrlRedirectSchema>;

export const InterfaceOnSubmitSchema = z.discriminatedUnion('type', [
  InterfaceOnSubmitWaitForInterfaceSchema,
  InterfaceOnSubmitSuccessMessageSchema,
  InterfaceOnSubmitUrlRedirectSchema,
]);

export type InterfaceOnSubmit = z.infer<typeof InterfaceOnSubmitSchema>;
```

## schemas/jsonSchema

**Source:** `schemas/jsonSchema.ts`

```typescript
/**
 * NOTE: This file is to ONLY be used for types that is used in the runtime.
 **/

import { z } from 'zod';

/** The BIQ Json Schema Types for each component in the form rendered by the JSON schema */
export enum BIQJsonSchemaType {
  /** different string type schemas */
  String = 'string',
  
  /** different number type schemas */
  Number = 'number',
  Integer = 'integer',
  
  Boolean = 'boolean',

  /** different object type schemas */
  Object = 'object',
  Array = 'array',
  Any = 'any',
}


const BIQBaseJsonSchemaZodSchema = z.object({
  /** The title of the section */
  title: z.string().optional(),
  /** The description of the section */
  description: z.string().optional(),
  /** default value for the schema */
  default: z.any().optional(),
});

/** The base values available for all schema types */
interface BIQBaseJsonSchema {
  title?: string;
  description?: string;
  default?: unknown;
}

/** color values for the UI */
const BIQColorZodSchema = z.union([
  z.string().regex(/^#[0-9A-Fa-f]{6}$/, {
    error: 'Color must be a valid hex code (e.g., #FF0000)'
  }),
  z.enum(['red', 'pink', 'grape', 'violet', 'indigo', 'blue', 'cyan', 'teal', 'green', 'lime', 'yellow', 'orange', 'gray'], {
    error: 'Color must be one of: red, pink, grape, violet, indigo, blue, cyan, teal, green, lime, yellow, orange, gray',
  }),
], {
  error: 'If color is required, it must be a valid hex code or a valid color name',
});

// --------------------------------- String Input Schemas ---------------------------------
/** the basic string input schema that would return a string */
const BIQStringJsonSchemaZodSchema = BIQBaseJsonSchemaZodSchema.extend({
  /** The type of the schema */
  type: z.literal(BIQJsonSchemaType.String),
  /** if the value is a const */
  const: z.string().optional(),
  /** The minimum length of the string */
  minLength: z.number().optional(),
  /** The maximum length of the string */
  maxLength: z.number().optional(),
  /** The pattern of the string */
  pattern: z.string().optional(),
  /** The format of the string that will also verify the type */
  format: z.enum(['email', 'uri']).optional(),
  /** other options to format the ui for the component */
  ui: z.object({
    /** if the component is hidden */
    hidden: z.boolean().optional(),
    /** the order level where 0 is closer to the top and higher numbers are closer to the bottom order between same number wont be guaranteed */
    order: z.number().optional(),
    /** The component of how to render the text input */
    component: z.enum(['input', 'textarea', 'password', 'markdown']).optional(),
    /** other options to format the ui for the component */
    options: z.object({
      /** if the component is disabled */
      disabled: z.boolean().optional(),
      /** allow to copy the value of the input */
      copyable: z.boolean().optional(),
      /** the placeholder value for the input */
      placeholder: z.any().optional(),
      /** the minimum lines of the textarea and markdown defaults to 1 */
      minLines: z.number().optional(),
      /** the maximum lines of the textarea and markdown defaults to infinite */
      maxLines: z.number().optional(),
      /** allow to open the textarea/markdown input in a modal to edit the value */
      editInModal: z.boolean().optional(),
      /** the set height of the input for textarea and markdown */
      height: z.union([z.number(), z.string()]).optional(),
      /** the width of the input defaults to 100% */
      width: z.union([z.number(), z.string()]).optional(),
      /** if the component is a text area let it auto-resize to fit content */
      autoResize: z.boolean().optional(),
      /** if the component is a markdown input if the lines should be wrapped */
      wrapLines: z.boolean().optional(),
      /** for markdown input show a preview of markdown */
      preview: z.boolean().optional(),
    }).optional(),
  }).optional(),
});

export type BIQStringJsonSchema = z.infer<typeof BIQStringJsonSchemaZodSchema>;

/** the basic string input schema that would return a string */
const BIQCodeJsonSchemaZodSchema = BIQBaseJsonSchemaZodSchema.extend({
  /** The type of the schema */
  type: z.literal(BIQJsonSchemaType.String),
  /** if the value is a const */
  const: z.string().optional(),
  /** The minimum length of the string */
  minLength: z.number().optional(),
  /** The maximum length of the string */
  maxLength: z.number().optional(),
  /** other options to format the ui for the component */
  ui: z.object({
    /** the order level where 0 is closer to the top and higher numbers are closer to the bottom order between same number wont be guaranteed */
    order: z.number().optional(),
    /** The component of how to render the text input */
    component: z.literal('code'),
    /** other options to format the ui for the component */
    options: z.object({
      /** the language of the code */
      language: z.string().optional(),
      /** if the component is disabled */
      disabled: z.boolean().optional(),
      /** allow to copy the value of the input */
      copyable: z.boolean().optional(),
      /** the placeholder value for the input */
      placeholder: z.any().optional(),
      /** the minimum lines of the input defaults to 1 */
      minLines: z.number().optional(),
      /** the maximum lines of the input defaults to infinite */
      maxLines: z.number().optional(),
      /** allow to open the code input in a modal to edit the value */
      editInModal: z.boolean().optional(),
      /** the set height of the input */
      height: z.union([z.number(), z.string()]).optional(),
      /** the width of the input defaults to 100% */
      width: z.union([z.number(), z.string()]).optional(),
      /** if the component is a text area let it auto-resize to fit content */
      autoResize: z.boolean().optional(),
      /** if the component is a codemirror input if the lines should be wrapped */
      wrapLines: z.boolean().optional(),
    }).optional(),
  }).optional(),
});

export type BIQCodeJsonSchema = z.infer<typeof BIQCodeJsonSchemaZodSchema>;

/** a date time input schema that would return a string of the date time */
const BIQDateTimeJsonSchemaZodSchema = BIQBaseJsonSchemaZodSchema.extend({
  /** The type of the schema */
  type: z.literal(BIQJsonSchemaType.String),
  /** The format of the date-time string that will also verify the type */
  format: z.enum(['date-time', 'date', 'time']),
  /** other options to format the ui for the component */
  ui: z.object({
    /** if the component is hidden */
    hidden: z.boolean().optional(),
    /** the order level where 0 is closer to the top and higher numbers are closer to the bottom order between same number wont be guaranteed */
    order: z.number().optional(),
    /** The component of how to render the date input it is ignored for date-time and time inputs */
    component: z.enum(['input', 'calendar']).optional(),
    /** other options to format the ui for the component */
    options: z.object({
      /** the placeholder value for the input */
      placeholder: z.any().optional(),
    }).optional(),
  }).optional(),
});

export type BIQDateTimeJsonSchema = z.infer<typeof BIQDateTimeJsonSchemaZodSchema>;

/** a suggestion input schema that would return a string but has a dropdown of suggestions */
const BIQSuggestionJsonSchemaZodSchema = BIQBaseJsonSchemaZodSchema.extend({
  /** The type of the schema */
  type: z.literal(BIQJsonSchemaType.String),
  /** The enum values of the string */
  /** other options to format the ui for the component */
  ui: z.object({
    /** if the component is hidden */
    hidden: z.boolean().optional(),
    /** the order level where 0 is closer to the top and higher numbers are closer to the bottom order between same number wont be guaranteed */
    order: z.number().optional(),
    /** The component of how to render the select input  */
    component: z.literal('suggestion'),
    /** other options to format the ui for the component */
    options: z.object({
      /** the placeholder value for the input */
      placeholder: z.any().optional(),
      /** the suggestions to display in the dropdown */
      suggestions: z.array(z.string()),
      /** labels for the select for suggestions inputs where the key is the suggestion value and the value is the label */
      suggestionLabels: z.record(z.string(), z.string()).optional(),
      /** the groups for suggestions labels where the key is the group name and the value is an array of the suggestion values */
      suggestionGroups: z.record(z.string(), z.array(z.string())).optional(),
    }),
  }),
});

export type BIQSuggestionJsonSchema = z.infer<typeof BIQSuggestionJsonSchemaZodSchema>;

/** a select input schema that would return a string of the selected value */
const BIQSelectJsonSchemaZodSchema = BIQBaseJsonSchemaZodSchema.extend({
  /** The type of the schema */
  type: z.literal(BIQJsonSchemaType.String),
  /** The enum values of the string */
  enum: z.array(z.string()),
  /** other options to format the ui for the component */
  ui: z.object({
    /** if the component is hidden */
    hidden: z.boolean().optional(),
    /** the order level where 0 is closer to the top and higher numbers are closer to the bottom order between same number wont be guaranteed */
    order: z.number().optional(),
    /** The component of how to render the select input  */
    component: z.enum(['select', 'searchSelect', 'radio', 'radioVertical']).optional(),
    /** other options to format the ui for the component */
    options: z.object({
      /** the placeholder value for the input */
      placeholder: z.any().optional(),
      /** labels for the select for enum inputs where the key is the enum value and the value is the label */
      enumLabels: z.record(z.string(), z.string()).optional(),
      /** the subtitles for the select for enum inputs where the key is the enum value and the value is the subtitle */
      enumSubtitles: z.record(z.string(), z.string()).optional(),
      /** the groups for enum labels where the key is the group name and the value is an array of the enum values */
      enumGroups: z.record(z.string(), z.array(z.string())).optional(),
      /** Name of a sibling field whose value filters this select's options (e.g. 'harness'). */
      optionsFilterField: z.string().optional(),
      /** Allowed enum values per sibling-field value, used with optionsFilterField.
       *  Key is the sibling value (e.g. 'codex'); value is the list of allowed enum values. */
      optionsByFieldValue: z.record(z.string(), z.array(z.string())).optional(),
    }).optional(),
  }).optional(),
});

export type BIQSelectJsonSchema = z.infer<typeof BIQSelectJsonSchemaZodSchema>;

/** a diff input schema that would return a string of the "new" code in the diff */
const BIQDiffJsonSchemaZodSchema = BIQBaseJsonSchemaZodSchema.extend({
  /** The type of the schema */
  type: z.literal(BIQJsonSchemaType.String),
  /** the ui options for the component */
  ui: z.object({
    /** the order level where 0 is closer to the top and higher numbers are closer to the bottom order between same number wont be guaranteed */
    order: z.number().optional(),
    /** Make sure its rendered as a diff */
    component: z.literal('diff'),
    /** other options to format the ui for the component */
    options: z.object({
      /** The old value of the diff */
      oldValue: z.string(),
      /** the supported languages of the diff component */
      language: z.string().optional(),
      /** the placeholder value for the input */
      placeholder: z.any().optional(),
      /** if the component is read only (value would be defined by default) */
      readOnly: z.boolean().optional(),
      /** minimum lines of the diff */
      minLines: z.number().optional(),
      /** maximum lines of the diff */
      maxLines: z.number().optional(),
      /** allow to open the diff input in a modal to edit the value */
      editInModal: z.boolean().optional(),
      /** The height of the diff */
      height: z.union([z.number(), z.string()]).optional(),
      /** The width of the diff */
      width: z.union([z.number(), z.string()]).optional(),
      /** if the diff should auto-resize to fit content */
      autoResize: z.boolean().optional(),
      /** if the component is a codemirror input if the lines should be wrapped */
      wrapLines: z.boolean().optional(),
      /** whether to render the revert controls (only would render is readOnly is undefined or false)  */
      revertControls: z.boolean().optional(),
    }),
  }),
});

export type BIQDiffJsonSchema = z.infer<typeof BIQDiffJsonSchemaZodSchema >;

// --------------------------------- Number Input Schemas ---------------------------------

/** a basic number input schema that would return a number */
const BIQNumberJsonSchemaZodSchema = BIQBaseJsonSchemaZodSchema.extend({
  /** The type of the schema */
  type: z.enum([BIQJsonSchemaType.Number, BIQJsonSchemaType.Integer]),
  /** The minimum value of the number */
  minimum: z.number().optional(),
  /** The maximum value of the number */
  maximum: z.number().optional(),
  /** The exclusive minimum value of the number */
  exclusiveMinimum: z.number().optional(),
  /** The exclusive maximum value of the number */
  exclusiveMaximum: z.number().optional(),
  /** other options to format the ui for the component */
  ui: z.object({
    /** if the component is hidden */
    hidden: z.boolean().optional(),
    /** The component of how to render the number input  */
    component: z.enum(['number', 'currency', 'percent', 'phoneNumber', 'rating', 'slider']).optional(),
    /** the order level where 0 is closer to the top and higher numbers are closer to the bottom order between same number wont be guaranteed */
    order: z.number().optional(),
    /** other options to format the ui for the component */
    options: z.object({
      /** if the component type  is currency, this would be the prefix for the number */
      currencyPrefix: z.string().optional(),
      /** the placeholder value for the input */
      placeholder: z.any().optional(),
      /** whether to hide the number controls */
      hideControls: z.boolean().optional(),
      /** for a slider component, the step value */
      step: z.number().positive().optional(),
    }).optional(),
  }).optional(),
});

export type BIQNumberJsonSchema = z.infer<typeof BIQNumberJsonSchemaZodSchema>;

// --------------------------------- Boolean Input Schemas ---------------------------------

/** a basic boolean input schema that would return a boolean */
const BIQBooleanJsonSchemaZodSchema = BIQBaseJsonSchemaZodSchema.extend({
  /** The type of the schema */
  type: z.literal(BIQJsonSchemaType.Boolean),
  /** options to format the ui for the component */
  ui: z.object({
    /** if the component is hidden */
    hidden: z.boolean().optional(),
    /** The component of how to render the number input.  Defaults to switch */
    component: z.enum(['checkbox', 'switch']).optional(),
    /** the order level where 0 is closer to the top and higher numbers are closer to the bottom order between same number wont be guaranteed */
    order: z.number().optional(),
  }).optional(),
});

export type BIQBooleanJsonSchema = z.infer<typeof BIQBooleanJsonSchemaZodSchema>;

// --------------------------------- Any Input Schemas ---------------------------------

/** an any input schema that would return the yaml or json as an object */
const BIQAnyJsonSchemaZodSchema = BIQBaseJsonSchemaZodSchema.extend({
  /** The type of the schema */
  type: z.enum([BIQJsonSchemaType.Any]),
  /** options to format the ui for the component */
  ui: z.object({
    component: z.enum(['input', 'modal']).optional(),
    /** the order level where 0 is closer to the top and higher numbers are closer to the bottom order between same number wont be guaranteed */
    order: z.number().optional(),
    /** other options to format the ui for the component */
    options: z.object({
      /** the placeholder value for the input */
      placeholder: z.any().optional(),
      /** the language of the any type (defaults to yaml) */
      language: z.enum(['yaml', 'json']).optional(),
      /** if the component is a codemirror input if the lines should be wrapped */
      wrapLines: z.boolean().optional(),
      /** let  the code editor component auto-resize to fit content */
      autoResize: z.boolean().optional(),
      /** the minimum lines of the textarea and codemirror defaults to 1 */
      minLines: z.number().optional(),
      /** the maximum lines of the textarea and codemirror defaults to infinite */
      maxLines: z.number().optional(),
      /** edit the value in a modal */
      editInModal: z.boolean().optional(),
    }).optional(),
  }).optional(),
});

export type BIQAnyJsonSchema = z.infer<typeof BIQAnyJsonSchemaZodSchema>;

// --------------------------------- Object Input Schemas (Files) ---------------------------------

/** a file input that would return an object with the structure of a BIQFile */
const BIQFileJsonSchemaZodSchema = BIQBaseJsonSchemaZodSchema.extend({
  /** The type of the schema */
  type: z.literal(BIQJsonSchemaType.Object),
  /** the ui options for the component */
  ui: z.object({
    /** the order level where 0 is closer to the top and higher numbers are closer to the bottom order between same number wont be guaranteed */
    order: z.number().optional(),
    /** Make sure the component is rendered as a file input */
    component: z.literal('file'),
    /** other options to format the ui for the component */
    options: z.object({
      /** if multiple files can be uploaded at once */
      multiple: z.boolean().optional(),
      /** the allowed file types */
      accept: z.string().optional(),
      /** the type of file component */
      type: z.enum(['input', 'button']).optional(),
    }).optional(),
  })
});

export type BIQFileJsonSchema = z.infer<typeof BIQFileJsonSchemaZodSchema>;

/** an audio recording input that would return an object with the structure of a BIQAudioRecording */
const BIQAudioFileJsonSchemaZodSchema = BIQBaseJsonSchemaZodSchema.extend({
  /** The type of the schema */
  type: z.literal(BIQJsonSchemaType.Object),
  /** the ui options for the component */
  ui: z.object({
    /** the order level where 0 is closer to the top and higher numbers are closer to the bottom order between same number wont be guaranteed */
    order: z.number().optional(),
    /** Make sure the component is rendered as a audio recording input */
    component: z.literal('audioRecording'),
    /** other options to format the ui for the component */
    options: z.object({
      /** the max duration the audio recording can be */
      maxDuration: z.number().optional(),
    }).optional(),
  })
});

export type BIQAudioRecordingFileJsonSchema = z.infer<typeof BIQAudioFileJsonSchemaZodSchema>;

// --------------------------------- String Display Schemas ---------------------------------

/** a display text input that would not return anything but would display a title and/or description in the form */
const BIQDisplayTextJsonSchemaZodSchema = BIQBaseJsonSchemaZodSchema.extend({
  /** The type of the schema */
  type: z.literal(BIQJsonSchemaType.String),
  /** the ui options for the component */
  ui: z.object({
    /** the order level where 0 is closer to the top and higher numbers are closer to the bottom order between same number wont be guaranteed */
    order: z.number().optional(),
    /** Make sure its rendered as a display text */
    component: z.literal('display'),
    /** other options to format the ui for the component */
    options: z.object({
      /** The title color of the display text */
      titleColor: BIQColorZodSchema.optional(),
      /** The title order of the display text */
      titleOrder: z.union([z.literal(0), z.literal(1), z.literal(2), z.literal(3), z.literal(4), z.literal(5), z.literal(6)]).optional(),
      /** The description color of the display text */
      descriptionColor: BIQColorZodSchema.optional(),
    }).optional(),
  }),
});

export type BIQDisplayTextJsonSchema = z.infer<typeof BIQDisplayTextJsonSchemaZodSchema>;

/** a divider input that would not return anything but would display a divider in the form */
const BIQDividerJsonSchemaZodSchema = BIQBaseJsonSchemaZodSchema.extend({
  /** The type of the schema */
  type: z.literal(BIQJsonSchemaType.String),
  /** the ui options for the component */
  ui: z.object({
    /** the order level where 0 is closer to the top and higher numbers are closer to the bottom order between same number wont be guaranteed */
    order: z.number().optional(),
    /** Make sure its rendered as a divider */
    component: z.literal('divider'),
    /** other options to format the ui for the component */
    options: z.object({
      /** The color of the divider */
      color: BIQColorZodSchema.optional(),
      /** The weight of the divider */
      weight: z.number().optional(),
      /** The text alignment of the divider */
      textAlignment: z.enum(['left', 'center', 'right']).optional(),
    }).optional(),
  }),
});

export type BIQDividerJsonSchema = z.infer<typeof BIQDividerJsonSchemaZodSchema>;

/**
 * a button input that would not return anything but would complete the action of the button
 * this is the component that would be used to submit the form with the action type of submit
 **/
const BIQButtonJsonSchemaZodSchema = BIQBaseJsonSchemaZodSchema.extend({
  /** The type of the schema */
  type: z.literal(BIQJsonSchemaType.String),
  /** the ui options for the component */
  ui: z.object({
    /** the order level where 0 is closer to the top and higher numbers are closer to the bottom order between same number wont be guaranteed */
    order: z.number().optional(),
    /** Make sure its rendered as a button */
    component: z.literal('button'),
    /** other options to format the ui for the component */
    options: z.object({
      /** The action type of the button */
      actionType: z.enum(['button', 'reset', 'submit']).optional(),
      /** The variant of the button */
      variant: z.enum(['default', 'filled', 'light', 'outline', 'subtle', 'transparent', 'white']).optional(),
      /** The color of the button */
      color: BIQColorZodSchema.optional(),
      /** The url of the button */
      url: z.string().optional(),
      /** The open url in current tab of the button */
      openUrlInCurrentTab: z.boolean().optional(),
    }).optional(),
  }),
});

export type BIQButtonJsonSchema = z.infer<typeof BIQButtonJsonSchemaZodSchema>;

/** a image input that would return nothing but would display an image */
const BIQImageJsonSchemaZodSchema = BIQBaseJsonSchemaZodSchema.extend({
  /** The type of the schema */
  type: z.literal(BIQJsonSchemaType.String),
  /** the ui options for the component */
  ui: z.object({
    /** the order level where 0 is closer to the top and higher numbers are closer to the bottom order between same number wont be guaranteed */
    order: z.number().optional(),
    /** Make sure its rendered as an image */
    component: z.literal('image'),
    /** other options to format the ui for the component */
    options: z.object({
      /** The src of the image */
      src: z.string(),
      /** The width of the image */
      width: z.union([z.number(), z.string()]).optional(),
      /** The height of the image */
      height: z.union([z.number(), z.string()]).optional(),
    }).optional(),
  }),
});

export type BIQImageJsonSchema = z.infer<typeof BIQImageJsonSchemaZodSchema>;

/** a markdown viewer input that would return nothing but would display a markdown component */
const BIQMarkdownViewerJsonSchemaZodSchema = BIQBaseJsonSchemaZodSchema.extend({
  /** The type of the schema */
  type: z.literal(BIQJsonSchemaType.String),
  /** the file name for the pdf */
  title: z.string().optional(),
  /** the markdown string to display */
  default: z.string(),
  /** the ui options for the component */
  ui: z.object({
    /** the order level where 0 is closer to the top and higher numbers are closer to the bottom order between same number wont be guaranteed */
    order: z.number().optional(),
    /** Make sure its rendered as an image */
    component: z.literal('markdownViewer'),
    /** other options to format the ui for the component */
    options: z.object({
      /** The width of the markdown component */
      width: z.union([z.number(), z.string()]).optional(),
      /** The height of the markdown component */
      height: z.union([z.number(), z.string()]).optional(),
    }).optional(),
  }),
});

export type BIQMarkdownViewerJsonSchema = z.infer<typeof BIQMarkdownViewerJsonSchemaZodSchema>;

/** a code viewer input that would return nothing but would display a code markdown component */
const BIQCodeViewerJsonSchemaZodSchema = BIQBaseJsonSchemaZodSchema.extend({
  /** The type of the schema */
  type: z.literal(BIQJsonSchemaType.String),
  /** the title of the code */
  title: z.string().optional(),
  /** the code string to display */
  default: z.string(),
  /** the ui options for the component */
  ui: z.object({
    /** the order level where 0 is closer to the top and higher numbers are closer to the bottom order between same number wont be guaranteed */
    order: z.number().optional(),
    /** Make sure its rendered as an image */
    component: z.literal('codeViewer'),
    /** other options to format the ui for the component */
    options: z.object({
      /** The language of the code */
      language: z.string().optional(),
      /** The width of the markdown component */
      width: z.union([z.number(), z.string()]).optional(),
      /** The height of the markdown component */
      height: z.union([z.number(), z.string()]).optional(),
    }).optional(),
  }),
});

export type BIQCodeViewerJsonSchema = z.infer<typeof BIQCodeViewerJsonSchemaZodSchema>;

/** a pdf viewer input that would return nothing but would display a pdf */
const BIQPdfViewerJsonSchemaZodSchema = BIQBaseJsonSchemaZodSchema.extend({
  /** The type of the schema */
  type: z.literal(BIQJsonSchemaType.String),
  /** the file name for the pdf */
  title: z.string().optional(),
  /** the ui options for the component */
  ui: z.object({
    /** the order level where 0 is closer to the top and higher numbers are closer to the bottom order between same number wont be guaranteed */
    order: z.number().optional(),
    /** Make sure its rendered as an image */
    component: z.literal('pdfViewer'),
    /** other options to format the ui for the component */
    options: z.object({
      /** The src of the pdf */
      src: z.string(),
      /** The width of the pdf */
      width: z.union([z.number(), z.string()]).optional(),
      /** The height of the pdf */
      height: z.union([z.number(), z.string()]).optional(),
    }),
  }),
});

export type BIQPdfViewerJsonSchema = z.infer<typeof BIQPdfViewerJsonSchemaZodSchema>;

// --------------------------------- Object Input Schemas ---------------------------------

/** an object input that would return an object with the structure of the properties */
const BIQObjectJsonSchemaZodSchema: z.ZodObject<Record<string, z.ZodTypeAny>> = BIQBaseJsonSchemaZodSchema.extend({
  /** The type of the schema */
  type: z.literal(BIQJsonSchemaType.Object),
  /** The properties of the object */
  properties: z.record(z.string(), z.lazy(() => z.union(
    [
      BIQStringJsonSchemaZodSchema, BIQCodeJsonSchemaZodSchema, BIQDateTimeJsonSchemaZodSchema, BIQSuggestionJsonSchemaZodSchema, BIQSelectJsonSchemaZodSchema, BIQDiffJsonSchemaZodSchema,
      BIQNumberJsonSchemaZodSchema,
      BIQBooleanJsonSchemaZodSchema,
      BIQAnyJsonSchemaZodSchema, BIQObjectJsonSchemaZodSchema, BIQArrayJsonSchemaZodSchema, BIQAnyOfJsonSchemaZodSchema,
      BIQFileJsonSchemaZodSchema, BIQAudioFileJsonSchemaZodSchema,
      BIQDisplayTextJsonSchemaZodSchema, BIQDividerJsonSchemaZodSchema, BIQButtonJsonSchemaZodSchema, BIQImageJsonSchemaZodSchema, BIQPdfViewerJsonSchemaZodSchema, BIQMarkdownViewerJsonSchemaZodSchema, BIQCodeViewerJsonSchemaZodSchema
    ]))).optional(),
  /** The required properties of the object */
  required: z.array(z.string()).optional(),
  /** the ui options for the component */
  ui: z.object({
    /** the order level where 0 is closer to the top and higher numbers are closer to the bottom order between same number wont be guaranteed */
    order: z.number().optional(),
    options: z.object({
      /** if to render the object in a section, defaults to true */
      section: z.boolean().optional(),
    }).optional(),
  }).optional(),
});

/** the typing for the object input schema since the ZodSchema schema is created dynamically */
export interface BIQObjectJsonSchema extends BIQBaseJsonSchema {
  type: BIQJsonSchemaType.Object;
  properties?: Record<string, BIQPropertyJsonSchemas>;
  required?: string[];
  ui?: {
    order?: number;
    options?: {
      section?: boolean;
    };
  }
}

// --------------------------------- Array Input Schemas ---------------------------------
/** a form array input that would return an array with the structure of the items */
const BIQArrayJsonSchemaZodSchema: z.ZodObject<Record<string, z.ZodTypeAny>> = BIQBaseJsonSchemaZodSchema.extend({
  /** The type of the schema */
  type: z.literal(BIQJsonSchemaType.Array),
  /** The items of the array */
  items: z.lazy(() => z.union(
    [
      BIQStringJsonSchemaZodSchema, BIQCodeJsonSchemaZodSchema, BIQDateTimeJsonSchemaZodSchema, BIQSuggestionJsonSchemaZodSchema, BIQSelectJsonSchemaZodSchema, BIQDiffJsonSchemaZodSchema,
      BIQNumberJsonSchemaZodSchema,
      BIQBooleanJsonSchemaZodSchema,
      BIQAnyJsonSchemaZodSchema, BIQObjectJsonSchemaZodSchema, BIQArrayJsonSchemaZodSchema, BIQAnyOfJsonSchemaZodSchema,
      BIQFileJsonSchemaZodSchema, BIQAudioFileJsonSchemaZodSchema,
      BIQDisplayTextJsonSchemaZodSchema, BIQDividerJsonSchemaZodSchema, BIQButtonJsonSchemaZodSchema, BIQImageJsonSchemaZodSchema, BIQPdfViewerJsonSchemaZodSchema, BIQMarkdownViewerJsonSchemaZodSchema, BIQCodeViewerJsonSchemaZodSchema
    ])),
  /** The min items of the array */
  minItems: z.number().optional(),
  /** The max items of the array */
  maxItems: z.number().optional(),
  /** if all the items must be unique */
  uniqueItems: z.boolean().optional(),
  /** the ui options for the component */
  ui: z.object({
    /** the order level where 0 is closer to the top and higher numbers are closer to the bottom order between same number wont be guaranteed */
    order: z.number().optional(),
  }).optional(),
});

/** the typing for the array input schema since the ZodSchema schema is created dynamically */
export interface BIQArrayJsonSchema extends BIQBaseJsonSchema {
  type: BIQJsonSchemaType.Array;
  items: BIQPropertyJsonSchemas;
  minItems?: number;
  maxItems?: number;
  uniqueItems?: boolean;
  ui?: {
    order?: number;
  }
}

export const BIQAnyOfJsonSchemaZodSchema = BIQBaseJsonSchemaZodSchema.extend({
  /** The key of the value to discriminate by if it is a discriminated union, the key value must be of type string and contain a constant value */
  discriminatorKey: z.string().optional(),
  /** The array of the anyOf */
  anyOf: z.array(z.lazy(() => z.union(
    [
      BIQStringJsonSchemaZodSchema, BIQCodeJsonSchemaZodSchema, BIQDateTimeJsonSchemaZodSchema, BIQSuggestionJsonSchemaZodSchema, BIQSelectJsonSchemaZodSchema, BIQDiffJsonSchemaZodSchema,
      BIQNumberJsonSchemaZodSchema,
      BIQBooleanJsonSchemaZodSchema,
      BIQAnyJsonSchemaZodSchema, BIQObjectJsonSchemaZodSchema, BIQArrayJsonSchemaZodSchema, BIQAnyJsonSchemaZodSchema,
      BIQFileJsonSchemaZodSchema, BIQAudioFileJsonSchemaZodSchema,
      BIQDisplayTextJsonSchemaZodSchema, BIQDividerJsonSchemaZodSchema, BIQButtonJsonSchemaZodSchema, BIQImageJsonSchemaZodSchema, BIQPdfViewerJsonSchemaZodSchema, BIQMarkdownViewerJsonSchemaZodSchema, BIQCodeViewerJsonSchemaZodSchema
    ]))),
  /** the ui options for the component */
  ui: z.object({
    /** the order level where 0 is closer to the top and higher numbers are closer to the bottom order between same number wont be guaranteed */
    order: z.number().optional(),
  }).optional(),
}).superRefine((data, ctx) => {
  if (!data.discriminatorKey) return;
  // Ensure all schemas in anyOf are properly formatted
  for (const schema of (data.anyOf as BIQPropertyJsonSchemas[])) {
    // check if the schema is an object and has properties (since there needs to be a key with the value of the discriminatorKey)
    if (!('type' in schema) || schema.type !== BIQJsonSchemaType.Object || !('properties' in schema)) {
      ctx.addIssue({
        code: 'custom',
        message: 'All schemas in anyOf must be of type object when using discriminatorKey',
        path: ['anyOf'],
      });
      return;
    }

    // check if the schema has the discriminatorKey in its properties
    if (!schema.properties || !(data.discriminatorKey in schema.properties)) {
      ctx.addIssue({
        code: 'custom',
        message: `All schemas in anyOf must have the discriminatorKey "${data.discriminatorKey}" in their properties`,
        path: ['anyOf'],
      });
    }

    // check if the discriminatorKey property is of type string and has a const value
    const discriminatorProperty = schema.properties?.[data.discriminatorKey];
    if (!discriminatorProperty || !('type' in discriminatorProperty) || discriminatorProperty.type !== BIQJsonSchemaType.String || !('const' in discriminatorProperty)) {
      ctx.addIssue({
        code: 'custom',
        message: 'The discriminatorKey property must be of type string and have a const value',
        path: ['anyOf'],
      });
    }
  }

  // Check for duplicate discriminator values
  const discriminatorValues = new Set();
  for (const schema of (data.anyOf as BIQPropertyJsonSchemas[])) {
    if (!('properties' in schema) || !schema.properties) continue;
    const discriminatorProperty = schema.properties[data.discriminatorKey];
    if (!('const' in discriminatorProperty) || discriminatorProperty.const === undefined) continue;
    const discriminatorValue = discriminatorProperty.const;
    if (discriminatorValues.has(discriminatorValue)) {
      ctx.addIssue({
        code: 'custom',
        message: `Duplicate discriminator value "${discriminatorValue}" found`,
        path: ['anyOf'],
      });
    }
    discriminatorValues.add(discriminatorValue);
  }
});

export interface BIQAnyOfJsonSchema extends BIQBaseJsonSchema {
  discriminatorKey?: string;
  anyOf: BIQPropertyJsonSchemas[];
  ui?: {
    order?: number;
  }
}

export const BIQPropertiesJsonSchemaZodSchema = z.union([
  BIQStringJsonSchemaZodSchema, BIQCodeJsonSchemaZodSchema, BIQDateTimeJsonSchemaZodSchema, BIQSuggestionJsonSchemaZodSchema, BIQSelectJsonSchemaZodSchema, BIQDiffJsonSchemaZodSchema,
  BIQNumberJsonSchemaZodSchema,
  BIQBooleanJsonSchemaZodSchema,
  BIQAnyJsonSchemaZodSchema, BIQObjectJsonSchemaZodSchema, BIQArrayJsonSchemaZodSchema, BIQAnyOfJsonSchemaZodSchema,
  BIQFileJsonSchemaZodSchema, BIQAudioFileJsonSchemaZodSchema,
  BIQDisplayTextJsonSchemaZodSchema, BIQDividerJsonSchemaZodSchema, BIQButtonJsonSchemaZodSchema, BIQImageJsonSchemaZodSchema, BIQPdfViewerJsonSchemaZodSchema, BIQMarkdownViewerJsonSchemaZodSchema, BIQCodeViewerJsonSchemaZodSchema
]);

/** the BIQ schema across all the different types */
export type BIQPropertyJsonSchemas = BIQStringJsonSchema | BIQCodeJsonSchema | BIQDateTimeJsonSchema | BIQSuggestionJsonSchema | BIQSelectJsonSchema | BIQNumberJsonSchema | BIQBooleanJsonSchema |
BIQAnyJsonSchema | BIQObjectJsonSchema | BIQArrayJsonSchema | BIQFileJsonSchema | BIQAudioRecordingFileJsonSchema | BIQDisplayTextJsonSchema | BIQDividerJsonSchema |
BIQButtonJsonSchema | BIQImageJsonSchema | BIQPdfViewerJsonSchema | BIQMarkdownViewerJsonSchema | BIQCodeViewerJsonSchema | BIQDiffJsonSchema | BIQAnyOfJsonSchema;

/** the ZodSchema schema for the custom BIQ json schema */
export const BIQJsonSchemaZodSchema = BIQBaseJsonSchemaZodSchema.extend({
  /** The properties of the object */
  properties: z.record(z.string(), BIQPropertiesJsonSchemaZodSchema),
  /** The required properties of the object */
  required: z.array(z.string()).optional(),
  /** the ui options for the component */
  ui: z.object({
    /** an image to be displayed at the top of the form (above the title and description) */
    topImage: z.object({
      /** The src of the image */
      src: z.string(),
      /** The width of the image */
      width: z.union([z.number(), z.string()]).optional(),
      /** The height of the image */
      height: z.union([z.number(), z.string()]).optional(),
    }).optional(),
    options: z.object({
      /** The base theme color for the entire form */
      themeColor: BIQColorZodSchema.optional(),
      /** The background color of the form */
      backgroundColor: BIQColorZodSchema.optional(),
      /** The color of the title */
      titleColor: BIQColorZodSchema.optional(),
      /** The order of the title */
      titleOrder: z.union([z.literal(0), z.literal(1), z.literal(2), z.literal(3), z.literal(4), z.literal(5), z.literal(6)]).optional(),
      /** The color of the description */
      descriptionColor: BIQColorZodSchema.optional(),
      /** the width of the form */
      width: z.enum(['full', 'half']).optional(),
    }).optional(),
  }).optional(),
});

/** the typing for the BIQ json schema since the ZodSchema schema is created dynamically */
export interface BIQJsonSchema extends BIQBaseJsonSchema {
  type?: BIQJsonSchemaType.Object;
  properties: Record<string, BIQPropertyJsonSchemas>;
  required?: string[];
  ui?: {
    topImage?: {
      src: string;
      width?: number | string;
      height?: number | string;
    }
    options?: {
      themeColor?: string;
      backgroundColor?: string;
      titleColor?: string;
      titleOrder?: 1 | 2 | 3 | 4 | 5 | 6;
      descriptionColor?: string;
      width?: 'full' | 'half';
    }
  }
}
```

## schemas/proxy

**Source:** `schemas/proxy.ts`

```typescript
import { createHash } from 'crypto';
import { z } from 'zod';

import { BIQConnectionAuthType } from '../connection.js';
import { AiProvider } from '../ai/index.js';

/**
 * Generate a short deterministic hash suffix from a string.
 * Used to disambiguate placeholders when different keys normalize to the same string
 * (e.g., "my-github" and "my_github" both normalize to "MY_GITHUB").
 */
function shortHash(input: string): string {
  return createHash('sha256').update(input).digest('hex').slice(0, 8);
}

/** Placeholder map entry for a connection sensitive field */
export const PlaceholderConnectionEntrySchema = z.object({
  /** the workspace connection key */
  workspaceKey: z.string(),
  /** the path within the decrypted connection result to the sensitive field — either a
   * dot-path string (e.g., "auth.values.token") or an array of segments for record leaves
   * whose keys may themselves contain dots (e.g., ["auth", "values", "headers", "X-Api-Key"]) */
  fieldPath: z.union([z.string(), z.array(z.string())]),
  /** per-credential URL allowlist (Feature A) — normalized entries, present only when non-empty.
   * The proxy 403s a request that uses this placeholder against a non-matching target. Optional so
   * maps already in Redis and the schema copy in the lambda runtime keep parsing unchanged. */
  allowedUrls: z.array(z.string()).optional(),
});

export type PlaceholderConnectionEntry = z.infer<typeof PlaceholderConnectionEntrySchema>;

/** Placeholder map entry for a credential (secret) */
export const PlaceholderCredentialEntrySchema = z.object({
  /** the workspace secret key */
  workspaceKey: z.string(),
  /** per-credential URL allowlist (Feature A) — normalized entries, present only when non-empty.
   * See PlaceholderConnectionEntrySchema.allowedUrls. */
  allowedUrls: z.array(z.string()).optional(),
});

export type PlaceholderCredentialEntry = z.infer<typeof PlaceholderCredentialEntrySchema>;

/** Placeholder map entry for a workspace AI provider credential (agent lambda segments).
 * The proxy resolves it via resolveAiCredential at request time — key material never
 * lands in Redis. */
export const PlaceholderAiProviderEntrySchema = z.object({
  /** the AI provider whose workspace credential the placeholder resolves to */
  provider: z.nativeEnum(AiProvider),
});

export type PlaceholderAiProviderEntry = z.infer<typeof PlaceholderAiProviderEntrySchema>;

/** The placeholder map stored in Redis — maps placeholder strings to resolution info */
export const PlaceholderMapSchema = z.object({
  /** Connection placeholders — maps placeholder string to connection resolution info */
  connections: z.record(z.string(), PlaceholderConnectionEntrySchema),
  /** Credential placeholders — maps placeholder string to credential resolution info */
  credentials: z.record(z.string(), PlaceholderCredentialEntrySchema),
  /** AI provider placeholders — maps placeholder string to the provider whose workspace
   * AI credential substitutes it (agent lambda LLM calls) */
  aiProviders: z.record(z.string(), PlaceholderAiProviderEntrySchema).optional(),
  /** Network access control — if set, proxy rejects requests to unlisted hosts */
  allowNetList: z.array(z.string()).optional(),
});

export type PlaceholderMap = z.infer<typeof PlaceholderMapSchema>;

/**
 * Generate a placeholder string for a connection sensitive field.
 * Format: BORGIQ_CONNECTION_{KEY}_{HASH}_{FIELD}
 * The hash covers both the key and the field path so distinct fields that normalize to the
 * same string (e.g., custom-auth record keys "x-api-key" and "x_api_key") never collide.
 * @param workspaceKey - the workspace connection key (e.g., "my-github")
 * @param fieldName - the field path within auth.values (e.g., "token", "headers.X-Api-Key")
 */
export function connectionPlaceholder(workspaceKey: string, fieldName: string): string {
  const normalizedKey = workspaceKey.toUpperCase().replace(/[^A-Z0-9]/g, '_');
  const normalizedField = fieldName.toUpperCase().replace(/[^A-Z0-9]/g, '_');
  return `BORGIQ_CONNECTION_${normalizedKey}_${shortHash(`${workspaceKey}:${fieldName}`)}_${normalizedField}`;
}

/**
 * Generate a placeholder string for a credential (secret).
 * Format: BORGIQ_CREDENTIAL_{KEY}_{HASH}
 * @param workspaceKey - the workspace secret key (e.g., "my-api-key")
 */
export function credentialPlaceholder(workspaceKey: string): string {
  const normalizedKey = workspaceKey.toUpperCase().replace(/[^A-Z0-9]/g, '_');
  return `BORGIQ_CREDENTIAL_${normalizedKey}_${shortHash(workspaceKey)}`;
}

/**
 * Generate a placeholder string for a workspace AI provider credential.
 * Format: BORGIQ_AI_KEY_{PROVIDER}_{HASH}. The hash includes a caller-supplied nonce so
 * each segment grant mints a distinct placeholder (a leaked placeholder string from one
 * segment is useless once its map expires).
 * @param provider - the AI provider (e.g., "anthropic")
 * @param nonce - per-grant nonce (e.g., the segment's invocation id)
 */
export function aiProviderPlaceholder(provider: string, nonce: string): string {
  const normalizedProvider = provider.toUpperCase().replace(/[^A-Z0-9]/g, '_');
  return `BORGIQ_AI_KEY_${normalizedProvider}_${shortHash(`${provider}:${nonce}`)}`;
}

/** Check if a string is a BorgIQ placeholder (uses prefix matching) */
export function isPlaceholder(value: string): boolean {
  return value.startsWith('BORGIQ_CONNECTION_') || value.startsWith('BORGIQ_CREDENTIAL_') || value.startsWith('BORGIQ_AI_KEY_');
}

/**
 * Validate that a target URL's hostname is in the allowNetList.
 * If allowNetList is undefined or empty, all hosts are allowed.
 * @throws Error if the hostname is not allowed or the URL is invalid
 */
export function validateTargetHost(targetUrl: string, allowNetList?: string[]): void {
  if (!allowNetList || allowNetList.length === 0) return;

  let hostname: string;
  try {
    hostname = new URL(targetUrl).hostname;
  } catch {
    throw new Error(`Invalid target URL: ${targetUrl}`);
  }

  if (!allowNetList.includes(hostname)) {
    throw new Error(`Target hostname '${hostname}' is not in the allowed network list`);
  }
}

/**
 * Sensitive field names per connection auth type.
 * Only these fields within `auth.values` are replaced with placeholders.
 * Non-sensitive fields (flags, config, regions, etc.) remain visible to the runtime.
 *
 * Keyed by `BIQConnectionAuthType` rather than `string` deliberately: this map is a security
 * boundary — a missing entry means the credential is handed to the runtime in the clear. Typing it
 * to the enum makes adding an auth type without a redaction rule a compile error instead of a
 * silent leak discovered later.
 */
export const CONNECTION_AUTH_SENSITIVE_FIELDS: Record<BIQConnectionAuthType, string[]> = {
  [BIQConnectionAuthType.BEARER]: ['token'],
  [BIQConnectionAuthType.API_KEY]: ['value'],
  [BIQConnectionAuthType.BASIC]: ['userName', 'password'],
  [BIQConnectionAuthType.OAUTH2]: ['token'],
  // mcpOauth connections resolve to a bearer token; only the access token is sensitive.
  [BIQConnectionAuthType.MCP_OAUTH]: ['token'],
  [BIQConnectionAuthType.OAUTH1]: ['consumerKey', 'consumerSecret', 'token', 'tokenSecret', 'verifier'],
  [BIQConnectionAuthType.AWS]: ['accessKey', 'secretKey', 'sessionToken'],
  [BIQConnectionAuthType.AWS_ROLE]: ['accessKey', 'secretKey', 'sessionToken'],
  [BIQConnectionAuthType.CUSTOM]: ['headers', 'queryParams', 'body'],
  [BIQConnectionAuthType.NONE]: [],
};

/**
 * Sensitive fields for an auth type read from the database, where it is typed as a plain `string`.
 *
 * The single place the DB string is narrowed to the enum, so the cast is documented once instead of
 * repeated at each call site. An unrecognised value returns `[]`, which redacts nothing — safe only
 * because {@link CONNECTION_AUTH_SENSITIVE_FIELDS} is now keyed by the enum, making a new auth type
 * without a redaction rule a compile error rather than something that reaches here at runtime.
 */
export function connectionAuthSensitiveFields(authType: string): string[] {
  return CONNECTION_AUTH_SENSITIVE_FIELDS[authType as BIQConnectionAuthType] ?? [];
}
```

## schemas/runtime

**Source:** `schemas/runtime.ts`

```typescript
/** NOTE: This file is to ONLY be used for types that is used in the runtime. */
import { z } from 'zod';

import { BIQRuntimeInvocationType } from '../runtime.js';

import { WebhookConfigSchema, ScheduleConfigSchema, LifecycleConfigSchema, LIFECYCLE_TRIGGER_EVENTS } from '../actorSchemas/trigger/triggerConfig.js';
import { ReactAppCodeDirSchema } from '../actorSchemas/trigger/reactApp.js';

import { BIQFileSchema } from './file.js';
import { idSchema } from './idSchema.js';
import { RuntimeActorMemorySchema, RuntimeActorReceiveResponseSchema } from './flowrunJobResult.js';
import { RuntimeContextSchema } from './ctx.js';

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

export const FlowrunWebhookTriggerRequestSchema = z.object({
  meta: z.object({
    requestId: z.string(),
    ipAddress: z.string().optional(),
    user: z.object({
      id: z.string(),
      name: z.string().optional(),
      email: z.string(),
    }).optional(),
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
 */
export const FlowrunLifecycleTriggerDataSchema = z.object({
  type: z.literal('lifecycle'),
  event: z.enum(LIFECYCLE_TRIGGER_EVENTS),
});

export type FlowrunLifecycleTriggerData = z.infer<typeof FlowrunLifecycleTriggerDataSchema>;

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
  /** ReactAppTriggerActor project source tree. NEVER interpolated (§2.1) — stripped before the
   *  interpolator runs and read from the pre-interpolated config by the actor (§4.3.5). */
  codeDir: ReactAppCodeDirSchema.optional(),
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
});

export type RuntimeRequest = z.infer<typeof RuntimeRequestSchema>;
```

## schemas/signals

**Source:** `schemas/signals.ts`

```typescript
import { z } from 'zod';

import { BIQRuntimeSignalType } from '../signal.js';
import { AiModel, BIQAiMessageSchema } from '../ai/index.js';
import { BIQInterfacePageDataSchema, InterfaceOnSubmitSchema } from './interface.js';
import { BIQFileSchema } from './file.js';
import { McpAuthDataSchema } from './connection.js';
import { BIQSandboxProviders, BIQAgentHarnessType, BIQAgentHarnessTypeSchema } from '../sandbox.js';

/** MCP server names key the gateway route, the session stash and the JWT claim, and are interpolated
 * into a harness config key + shell guard — so they must be safe in a URL segment, a config key, and a
 * shell word. Mirrors the actor-schema regex; enforced here too as defense-in-depth on the runtime signal. */
const MCP_SERVER_NAME_REGEX = /^[a-zA-Z0-9_-]+$/;

/** signal value for invoking another flow */
const RuntimeCallFlowSignalSchema = z.object({
  workspaceSlug: z.string(),
  canvasSlug: z.string(),
  callableTriggerActorId: z.string(),
  waitForResponse: z.boolean(),
  timeoutInSeconds: z.number().optional(),
  payload: z.record(z.string(), z.any()),
});

export type RuntimeCallFlowSignal = z.infer<typeof RuntimeCallFlowSignalSchema>;

/** signal value for callable response */
const RuntimeCallableResponseSignalSchema = z.object({
  payload: z.record(z.string(), z.any()),
  throwError: z.boolean().optional(),
});

export type RuntimeCallableResponseSignal = z.infer<typeof RuntimeCallableResponseSignalSchema>;

/** signal value for delay emitting the message */
const RuntimeDelayUntilSignalSchema = z.object({
  delayUntil: z.string(), // ISO 8601 string, i.e. new Date().toISOString()
});

export type RuntimeDelayUntilSignal = z.infer<typeof RuntimeDelayUntilSignalSchema>;

/** signal value for waiting for callback token response */
const RuntimeWaitForCallbackTokenSignalSchema = z.object({
  token: z.string(),
  timeoutInSeconds: z.number(),
});

export type RuntimeWaitForCallbackTokenSignal = z.infer<typeof RuntimeWaitForCallbackTokenSignalSchema>;

/** signal value for notifying callback token with message payload */
const RuntimeNotifyCallbackTokenSignalSchema = z.object({
  token: z.string(),
  payload: z.any(),
});

export type RuntimeNotifyCallbackTokenSignal = z.infer<typeof RuntimeNotifyCallbackTokenSignalSchema>;

/** signal to respond to webhook request */
const RuntimeWebhookRespondSignalSchema = z.object({
  statusCode: z.number(),
  headers: z.record(z.string(), z.any()).optional(),
  body: z.any().optional(),
});

/** signal value for returning interface trigger data */
const RuntimeInterfaceGetSignalSchema = z.object({
  page: BIQInterfacePageDataSchema,
  defaultValues: z.record(z.string(), z.any()).optional(),
  autoSubmitAfterSeconds: z.number().optional(),
});

export type RuntimeInterfaceGetSignal = z.infer<typeof RuntimeInterfaceGetSignalSchema>;

/** signal value for returning interface trigger data */
const RuntimeInterfacePostSignalSchema = z.object({
  submissionInterfaceId: z.string(),
  showProgressStatus: z.boolean().optional(),
  onSubmit: z.discriminatedUnion('type', [
    z.object({
      type: z.literal('nextInterface'),
      /** The message to show while the interface is loading */
      loadingMessage: z.string().optional(),
    }),
    z.object({
      type: z.literal('successMessage'),
      successMessage: z.string().optional(),
    }),
    z.object({
      type: z.literal('urlRedirect'),
      url: z.string(),
    }),
  ]),
});

export type RuntimeInterfacePostSignal = z.infer<typeof RuntimeInterfacePostSignalSchema>;

/** signal value for returning interface trigger data */
const RuntimeInterfaceRenderSignalSchema = z.object({
  interfaceId: z.string(),
  interfaceUrl: z.string(),
  page: BIQInterfacePageDataSchema,
  defaultValues: z.record(z.string(), z.any()).optional(),
  autoSubmitAfterSeconds: z.number().int().min(0).optional(),
  timeoutInMinutes: z.number().min(0).optional(),
  showProgressStatus: z.boolean().optional(),
  onSubmit: InterfaceOnSubmitSchema,
});

export type RuntimeInterfaceRenderSignal = z.infer<typeof RuntimeInterfaceRenderSignalSchema>;

/** signal value for returning ai agent data */
const RuntimeAiAgentSignalSchema = z.object({
  model: z.enum(AiModel).optional(),
  prompt: z.string().optional(),
  temperature: z.number().min(0).max(2).optional(),
  maxTokens: z.number().int().positive().optional(),
  systemPrompt: z.string().optional(),
  messages: z.array(BIQAiMessageSchema).optional(),
  maxLoopCount: z.number().int().positive().optional(),
  enableTodoTool: z.boolean().optional(),
});

export type RuntimeAiAgentSignal = z.infer<typeof RuntimeAiAgentSignalSchema>;

/** signal value for returning ai agent data */
const RuntimeAiSignalSchema =  z.object({
  model: z.enum(AiModel).optional(),
  prompt: z.string().optional(),
  temperature: z.number().min(0).max(2).optional(),
  maxTokens: z.number().int().positive().optional(),
  systemPrompt: z.string().optional(),
  tools: z.array(z.object({
    name: z.string(),
    description: z.string(),
    jsonSchemaParameters: z.any().optional()
  })).optional(),
  messages: z.array(BIQAiMessageSchema).optional(),
  maxRetries: z.number().int().positive().optional(),
  outputSchema: z.any().optional(),
  jsonMode: z.boolean().optional(),
  emitInput: z.boolean().optional(),
});

export type RuntimeAiSignal = z.infer<typeof RuntimeAiSignalSchema>;

/** Schema for encrypted environment variables passed through the signal */
export const EncryptedEnvSchema = z.object({
  /** RSA-OAEP encrypted AES-256 symmetric key (base64) */
  encryptedKey: z.string(),
  /** AES-GCM initialization vector (base64) */
  iv: z.string(),
  /** AES-256-GCM encrypted env data as JSON string (base64) */
  encryptedData: z.string(),
});

export type EncryptedEnv = z.infer<typeof EncryptedEnvSchema>;

/** Generic per-harness configuration. All fields are shared across CLIs; each
 * adapter maps them onto its own CLI flags. CLI-specific knobs go in harnessOptions.
 */
const HarnessConfigSchema = z.object({
  model: z.string().optional(),
  maxTokens: z.number().int().positive().optional(),
  temperature: z.number().min(0).max(1).optional(),
  systemPrompt: z.string().optional(),
  maxLoopCount: z.number().int().positive().optional(),
  /** Working directory for the harness, relative to /workspace where volume zip is extracted */
  workingDirectory: z.string().optional(),
  allowedTools: z.array(z.string()).optional(),
  disallowedTools: z.array(z.string()).optional(),
  /** MCP servers wired to the harness — remote (gateway-proxied), borgiq (an internal McpServerActor,
   * gateway-fronted but dispatched in-process) or stdio (in-sandbox subprocess).
   * `type` is absent on stdio entries emitted by older runtimes, which are stdio by definition.
   * Secrets are stripped from this config in transit: a stdio server's `env` values are blanked and
   * travel in `encryptedMcpEnv`, and an http server's LITERAL auth values are blanked and travel in
   * `encryptedMcpAuth` (connection-backed auth fields stay here as placeholders, which are not
   * secrets). A borgiq server carries no secret at all. The orchestrator reunites them at launch. */
  mcpServers: z.array(z.union([
    z.object({
      type: z.literal('http'),
      name: z.string().regex(MCP_SERVER_NAME_REGEX),
      url: z.string(),
      auth: McpAuthDataSchema.optional(),
    }),
    z.object({
      type: z.literal('borgiq'),
      name: z.string().regex(MCP_SERVER_NAME_REGEX),
      actorId: z.string(),
      workspaceSlug: z.string().optional(),
      canvasSlug: z.string().optional(),
    }),
    z.object({
      type: z.literal('stdio').optional(),
      name: z.string().regex(MCP_SERVER_NAME_REGEX),
      command: z.string(),
      args: z.array(z.string()).optional(),
      env: z.record(z.string(), z.string()).optional(),
    }),
  ])).min(1).optional(),
  /** CLI-specific knobs that don't fit the generic shape (e.g. codex reasoningEffort). */
  harnessOptions: z.record(z.string(), z.unknown()).optional(),
});

export type HarnessConfig = z.infer<typeof HarnessConfigSchema>;

/** signal value for agent harness execution (Claude Code, Codex, OpenCode, Pi) */
const RuntimeAgentHarnessSignalSchema = z.object({
  /** Session ID to continue or create a session with custom ID. Auto-generated if empty. */
  sessionId: z.string().max(64).optional(),
  /** BorgIQ file containing the zip archive to populate the sandbox volume */
  volumeZipFile: BIQFileSchema.optional(),
  /** The task/prompt for the harness to execute */
  task: z.string(),
  /** Timeout in minutes before the sandbox execution is forcefully stopped */
  timeoutInMinutes: z.number().int().positive().optional().default(30),
  /** Agent harness CLI to run. Defaults to 'claude' for backward compatibility. */
  harness: BIQAgentHarnessTypeSchema.optional().default(BIQAgentHarnessType.Claude),
  /** Sandbox provider to use. Configured per-actor. */
  provider: z.nativeEnum(BIQSandboxProviders),
  /** Generic configuration shared by all harness CLIs. */
  harnessConfig: HarnessConfigSchema.optional(),
  /** @deprecated Back-compat alias for harnessConfig. Old runtimes emit this; prefer harnessConfig.
   *  Use resolveHarnessConfig() to read the effective config. */
  claudeCodeConfig: HarnessConfigSchema.optional(),
  /** Encrypted environment variables to pass to the sandbox */
  encryptedEnv: EncryptedEnvSchema.optional(),
  /** Env for stdio MCP servers, keyed by server name — `{ [name]: JSON.stringify(envMap) }` encrypted
   * with the workspace public key (same path as `encryptedEnv`). Previously these values rode the
   * signal — and the Claude `--mcp-config` CLI arg — in plaintext. The orchestrator decrypts them and
   * reattaches them to the stdio configs only at sandbox launch. */
  encryptedMcpEnv: EncryptedEnvSchema.optional(),
  /** Literal auth values for remote MCP servers, keyed by server name — `{ [name]: <auth JSON> }`
   * encrypted with the workspace public key. Stored verbatim on the session stash and decrypted only
   * when the gateway forwards a request; the sandbox never sees them. Connection-backed auth is NOT
   * here — it stays a placeholder on `harnessConfig.mcpServers` and resolves per request. */
  encryptedMcpAuth: EncryptedEnvSchema.optional(),
  /** Whether to allow network access in the sandbox (default true) */
  allowNet: z.boolean().optional(),
  /** If set, only these hosts/CIDRs are allowed for outbound access (plus system endpoints) */
  allowNetList: z.array(z.string()).optional(),
  /** Hosts/CIDRs to block from outbound access (system endpoints are auto-excluded) */
  denyNetList: z.array(z.string()).optional(),
  /** Whether to include the workspace zip file in the done port result (default true) */
  returnOutputZipFile: z.boolean().optional(),
  /** Whether to include the harness session data file in the done port result (default true) */
  returnSessionDataFile: z.boolean().optional(),
  /** @deprecated Back-compat alias for returnSessionDataFile. */
  returnClaudeSessionDataFile: z.boolean().optional(),
});

export type RuntimeAgentHarnessSignal = z.infer<typeof RuntimeAgentHarnessSignalSchema>;

/** Resolve the effective harness config, preferring harnessConfig over the deprecated
 * claudeCodeConfig alias (for in-flight signals serialized by an older runtime).
 * This accessor is the sanctioned place to read the legacy alias, so we read it
 * through a non-deprecated view to avoid surfacing the deprecation hint here.
 */
export function resolveHarnessConfig(
  signal: RuntimeAgentHarnessSignal
): HarnessConfig | undefined {
  const legacy = (signal as { claudeCodeConfig?: HarnessConfig }).claudeCodeConfig;
  return signal.harnessConfig ?? legacy;
}

/** Resolve whether the harness session data file should be returned, preferring the
 * new flag over the deprecated alias. Defaults to true when neither is set.
 */
export function resolveReturnSessionDataFile(
  signal: RuntimeAgentHarnessSignal
): boolean {
  const legacy = (signal as { returnClaudeSessionDataFile?: boolean }).returnClaudeSessionDataFile;
  return signal.returnSessionDataFile ?? legacy ?? true;
}

/** signal value for agent lambda execution (pi coding agent running inside the
 * agent-sessions Lambda in checkpointed segments). */
export const RuntimeAgentLambdaSignalSchema = z.object({
  /** Session ID to continue or create a session with custom ID. Auto-generated if empty. */
  sessionId: z.string().max(64).optional(),
  /** BorgIQ file containing the zip archive extracted into the session workspace at creation */
  volumeZipFile: BIQFileSchema.optional(),
  /** The task/prompt for the agent to execute */
  task: z.string(),
  /** The model to use; provider resolved at the BorgIQ AI gateway */
  model: z.enum(AiModel).optional(),
  /** System prompt appended to the agent's system prompt */
  systemPrompt: z.string().optional(),
  /** Session timeout in minutes, measured across lambda segments */
  timeoutInMinutes: z.number().int().positive().optional().default(30),
  /** Working directory relative to the session workspace */
  workingDirectory: z.string().optional(),
  /** Maximum number of assistant turns */
  maxLoopCount: z.number().int().positive().optional(),
  /** Allowed built-in tools (empty = all) */
  allowedTools: z.array(z.string()).optional(),
  /** Disallowed built-in tools */
  disallowedTools: z.array(z.string()).optional(),
  /** Whether the tool runtime (Deno + in-process bash) may access the network (default false) */
  allowNet: z.boolean().optional().default(false),
  /** Whether the deno one-shot script tool is enabled (default false) */
  enableDenoTool: z.boolean().optional().default(false),
  /** If set, only these hosts/CIDRs are allowed for the tool runtime (plus system endpoints) */
  allowNetList: z.array(z.string()).optional(),
  /** Hosts/CIDRs to block for the tool runtime (system endpoints are auto-excluded) */
  denyNetList: z.array(z.string()).optional(),
  /** Encrypted environment variables exposed to tools/bash */
  encryptedEnv: EncryptedEnvSchema.optional(),
  /** Whether to include the workspace zip in the done port result (default true) */
  returnOutputZipFile: z.boolean().optional(),
  /** Whether to include the pi session data zip in the done port result (default true) */
  returnSessionDataFile: z.boolean().optional(),
  /** BorgIQ tool actors wired to this agent (resolved orchestrator-side from
   * `aiAgentToolActorIds`). Each becomes a customTool the model can call; the segment host
   * bridges the call to the tool actor via the runtime API (`/sandbox/invoke-tool`).
   * `.min(1)` encodes the no-empty-array contract in the type: a no-tools agent MUST leave this
   * undefined, never `[]` — the enqueue Lua round-trips eventData through cjson, which encodes an
   * empty array as `{}`, so an empty `toolActors` would arrive at the host as a non-array. */
  toolActors: z.array(z.object({
    id: z.string(),
    name: z.string(),
    description: z.string().optional(),
    jsonSchema: z.record(z.string(), z.unknown()).optional(),
  })).min(1).optional(),
  /** MCP server CONFIG the agent author wired — remote (name + endpoint + interpolated auth) or
   * borgiq (an internal McpServerActor target, no auth). Carried from the actor options to
   * `AiAgent.processSignal`, which consumes it (discovery + a session-keyed stash for the worker) and
   * then STRIPS it before stamping the per-segment payload — so the server URL never reaches the
   * Lambda segment. Connection-backed auth fields arrive here as placeholder strings (not secrets);
   * literal secrets are blanked and travel in `encryptedMcpAuth`. */
  mcpServers: z.array(z.union([
    z.object({
      type: z.literal('borgiq'),
      name: z.string().regex(MCP_SERVER_NAME_REGEX),
      actorId: z.string(),
      workspaceSlug: z.string().optional(),
      canvasSlug: z.string().optional(),
    }),
    z.object({
      type: z.literal('http').optional(),
      name: z.string().regex(MCP_SERVER_NAME_REGEX),
      url: z.string(),
      transport: z.enum(['streamable-http']).optional(),
      auth: McpAuthDataSchema.optional(),
    }),
  ])).min(1).optional(),
  /** Literal (non-placeholder) MCP auth secrets, keyed by server name — `{ [name]: <auth JSON> }`
   * encrypted by the runtime with the workspace public key, the SAME path as `encryptedEnv`.
   * `processSignal` decrypts these (KMS), folds them into the session stash re-encrypted, and strips
   * them before the segment payload, so MCP credentials never reach the Lambda segment. */
  encryptedMcpAuth: EncryptedEnvSchema.optional(),
  /** External MCP-server tools wired to this agent, resolved orchestrator-side at session start
   * (the MCP `tools/list` discovery in `AiAgent.processSignal`). Each becomes a customTool the model
   * can call; the segment host bridges the call to the orchestrator via the runtime API
   * (`/sandbox/invoke-tool`, MCP branch), which makes the actual `tools/call`. Definitions ONLY —
   * the server URL and credentials never leave the orchestrator. `name` is the namespaced name the
   * model sees (`mcp__{server}__{tool}`); `mcpServerName`/`mcpToolName` route the call back.
   * Same no-empty-array (`.min(1)`) cjson contract as `toolActors`. */
  mcpTools: z.array(z.object({
    name: z.string(),
    description: z.string().optional(),
    jsonSchema: z.record(z.string(), z.unknown()).optional(),
    mcpServerName: z.string(),
    mcpToolName: z.string(),
  })).min(1).optional(),
});

export type RuntimeAgentLambdaSignal = z.infer<typeof RuntimeAgentLambdaSignalSchema>;

/** Content field that can be either an inline string or a BIQFile reference */
const AppContentFieldSchema = z.union([z.string(), BIQFileSchema]);

/** signal value for returning app trigger data (html, css, script + security settings) */
const RuntimeAppGetSignalSchema = z.object({
  /** HTML content — inline string or BIQFile reference */
  html: AppContentFieldSchema,
  /** CSS content — inline string or BIQFile reference */
  css: AppContentFieldSchema.optional(),
  /** JavaScript content — inline string or BIQFile reference */
  script: AppContentFieldSchema.optional(),
  /** Security settings */
  allowedScriptDomains: z.array(z.string()).optional(),
  allowedStyleDomains: z.array(z.string()).optional(),
  allowInlineScripts: z.boolean().optional(),
  allowInlineStyling: z.boolean().optional(),
  allowedPermissions: z.array(z.string()).optional(),
});

export type RuntimeAppGetSignal = z.infer<typeof RuntimeAppGetSignalSchema>;

/** the signal value for the MCP Server actor */
export const RuntimeMcpServerSignalSchema = z.object({
  toolName: z.string(),
  toolActorId: z.string(),
  input: z.record(z.string(), z.unknown()),
  toolCallRequestId: z.string(),
});

export type RuntimeMcpServerSignal = z.infer<typeof RuntimeMcpServerSignalSchema>;

/**
 * Build manifest emitted by the ReactAppTriggerActor after a successful `deno task build`.
 * The orchestrator commits this as the actor's long-term memory — the canvas hash field
 * `${actorId}:ltm` — inside `store.persist()`'s single MULTI (§15.3.3); it is no longer written to the
 * old `${actorId}:reactAppBuild` field.
 * NOTE: kept small by design — it holds BIQFile handles, not bytes (serialized ≤ 128 KB, §4.1.1).
 */
export const RuntimeReactAppBuildSignalSchema = z.object({
  schemaVersion: z.literal(1),
  /** = the build flowrun id */
  buildId: z.string(),
  /** ISO timestamp */
  builtAt: z.string(),
  /** dist-relative entry document, e.g. 'index.html' */
  entry: z.string(),
  files: z.array(z.object({
    /** dist-relative, '/'-separated, e.g. 'assets/index-D64VDMd1.js' */
    path: z.string(),
    file: BIQFileSchema,
  })),
  totalSizeInBytes: z.number(),
  buildDurationMs: z.number().optional(),
  // Security options, evaluated by the build-time runtime invocation for AppTrigger interpolation
  // parity (§12.1). Mirror the five fields on RuntimeAppGetSignalSchema — the same options AppTrigger
  // evaluates per serve, frozen into the manifest here until the next Build. Optional so pre-§12.1
  // manifests remain valid; the serve path reads them from the manifest only (§15.3.4).
  allowedScriptDomains: z.array(z.string()).optional(),
  allowedStyleDomains: z.array(z.string()).optional(),
  allowInlineScripts: z.boolean().optional(),
  allowInlineStyling: z.boolean().optional(),
  allowedPermissions: z.array(z.string()).optional(),
  // Endpoints interpolated at build time AND resolved slug→id to concrete /msg/ URLs (via the runtime
  // resolveEndpoints API, §15.3.2a). This is now the SINGLE source of truth for the serve path,
  // verifyWebhook allowlist, and the baked SDK — it replaces every raw-yaml `endpoints` read in the
  // API server (§15.3.4). Optional so pre-§15 manifests stay parseable (a rebuild backfills them).
  endpoints: z.record(z.string(), z.union([
    z.object({
      /** full /msg/ URL (Config.getWebhookTriggerActorUrl construction) */
      url: z.string(),
      /** 'apps' | 'public' — surfaced to the SDK/editor */
      authorizationLevel: z.string(),
      /** id-keyed allowlist coordinates for verifyWebhook (§15.3.4) */
      targetCanvasId: z.string(),
      targetActorId: z.string(),
    }),
    /** unresolvable at build time — the hook fails loudly by name */
    z.object({ error: z.string() }),
  ])).optional(),
});

export type ReactAppBuildManifest = z.infer<typeof RuntimeReactAppBuildSignalSchema>;

/** the schema for runtime signal */
export const RuntimeSignalSchema = z.discriminatedUnion('type', [
  z.object({ type: z.literal(BIQRuntimeSignalType.DelayUntil), value: RuntimeDelayUntilSignalSchema }),
  z.object({ type: z.literal(BIQRuntimeSignalType.CallFlow), value: RuntimeCallFlowSignalSchema }),
  z.object({ type: z.literal(BIQRuntimeSignalType.WaitForCallbackToken), value: RuntimeWaitForCallbackTokenSignalSchema }),
  z.object({ type: z.literal(BIQRuntimeSignalType.NotifyCallbackToken), value: RuntimeNotifyCallbackTokenSignalSchema }),
  z.object({ type: z.literal(BIQRuntimeSignalType.WebhookRespond), value: RuntimeWebhookRespondSignalSchema }),
  z.object({ type: z.literal(BIQRuntimeSignalType.InterfaceGet), value: RuntimeInterfaceGetSignalSchema }),
  z.object({ type: z.literal(BIQRuntimeSignalType.InterfacePost), value: RuntimeInterfacePostSignalSchema }),
  z.object({ type: z.literal(BIQRuntimeSignalType.InterfaceRender), value: RuntimeInterfaceRenderSignalSchema }),
  z.object({ type: z.literal(BIQRuntimeSignalType.CallableResponse), value: RuntimeCallableResponseSignalSchema }),
  z.object({ type: z.literal(BIQRuntimeSignalType.AiAgent), value: RuntimeAiAgentSignalSchema }),
  z.object({ type: z.literal(BIQRuntimeSignalType.Ai), value: RuntimeAiSignalSchema }),
  z.object({ type: z.literal(BIQRuntimeSignalType.AgentHarness), value: RuntimeAgentHarnessSignalSchema }),
  z.object({ type: z.literal(BIQRuntimeSignalType.AgentLambda), value: RuntimeAgentLambdaSignalSchema }),
  z.object({ type: z.literal(BIQRuntimeSignalType.AppGet), value: RuntimeAppGetSignalSchema }),
  z.object({ type: z.literal(BIQRuntimeSignalType.ReactAppBuild), value: RuntimeReactAppBuildSignalSchema }),
  z.object({ type: z.literal(BIQRuntimeSignalType.McpServer), value: RuntimeMcpServerSignalSchema }),
]);

export type RuntimeSignal = z.infer<typeof RuntimeSignalSchema>;
```

## schemas/trigger

**Source:** `schemas/trigger.ts`

```typescript
import { z } from 'zod';

import { LIFECYCLE_TRIGGER_EVENTS } from '../actorSchemas/trigger/triggerConfig.js';

import { FlowrunWebhookTriggerRequestSchema } from './runtime.js';

const TriggerUserSchema = z.object({
  id: z.string(),
  name: z.string().optional(),
  email: z.string(),
});

/**
 * The trigger event passed to every trigger actor and exposed to user code on the UniversalTriggerActor as `req.trigger`.
 * Discriminated by `type`. Each trigger actor maps its orchestrator payload onto one of these variants.
 * - 'webhook'   — an HTTP request hit the webhook URL; `request` carries the parsed request; `user` is the
 *                 authenticated caller when the call carried an app-actor token (React-app endpoint calls, and
 *                 any 'apps'-level webhook fire)
 * - 'schedule'  — the cron schedule fired; `triggeredAt` is this fire's timestamp; `lastTriggeredAt` is the previous fire if tracked
 * - 'interface' — the interface trigger fired; `submission` is present when the user submitted a form (post), absent for the initial render (get)
 * - 'app'       — the app trigger fired (only the get render path exists today)
 * - 'reactAppBuild' — the react-app trigger's Build action fired (the serve path never reaches the runtime)
 * - 'callable'  — invoked by a CallFlow actor in another flow
 * - 'email'     — fired by an incoming email
 * - 'button'    — fired by the button actor's emit
 * - 'mcpServer' — fired by an MCP server request
 * - 'manual'    — the user clicked Invoke in the canvas
 * - 'lifecycle' — a canvas or actor lifecycle transition; `event` names the transition. Delivered only to
 *                 UniversalTriggerActors that listed it in `configuration.lifecycle.events`.
 *                 The vocabulary grows by extending {@link LIFECYCLE_TRIGGER_EVENTS}, never by
 *                 adding union members, so runtime dispatch branches once on `type`.
 */
export const TriggerEventSchema = z.discriminatedUnion('type', [
  z.object({ type: z.literal('webhook'), user: TriggerUserSchema.optional(), request: FlowrunWebhookTriggerRequestSchema }),
  z.object({ type: z.literal('schedule'), triggeredAt: z.string(), lastTriggeredAt: z.string().optional() }),
  z.object({
    type: z.literal('interface'),
    user: TriggerUserSchema.optional(),
    submission: z.object({
      interfaceId: z.string(),
      body: z.record(z.string(), z.any()),
    }).optional(),
  }),
  z.object({ type: z.literal('app'), user: TriggerUserSchema.optional() }),
  z.object({ type: z.literal('reactAppBuild'), user: TriggerUserSchema.optional() }),
  z.object({ type: z.literal('callable') }),
  z.object({ type: z.literal('email') }),
  z.object({ type: z.literal('button') }),
  z.object({ type: z.literal('mcpServer') }),
  z.object({ type: z.literal('manual') }),
  z.object({ type: z.literal('lifecycle'), event: z.enum(LIFECYCLE_TRIGGER_EVENTS) }),
]);

export type TriggerEvent = z.infer<typeof TriggerEventSchema>;
```

## schemas/urlAllowlist

**Source:** `schemas/urlAllowlist.ts`

```typescript
/**
 * Per-credential URL allowlist — the normative matcher (Feature A of the credential-usage
 * restrictions PRD). One module owns entry validation, normalization, and matching so the API,
 * web, and secret proxy agree exactly; it is a security boundary, so the rules below are strict
 * by design (relaxing later only adds matches and is backward compatible; tightening is not).
 *
 * An entry restricts which target URLs an `httpOnly` credential may be resolved into:
 *   https://api.github.com          any path on exactly this host (https, default port)
 *   https://api.github.com/repos    /repos and anything under it, but not /repos-evil
 *   https://*.github.com            any subdomain of github.com (any depth), NOT the apex
 *   https://internal.example:8443   non-default ports must be listed explicitly
 *
 * An empty/absent list means unrestricted.
 */
import { z } from 'zod';

/** A credential may carry at most this many allowlist entries. */
export const ALLOWED_URLS_MAX_ENTRIES = 50;

/** A single allowlist entry may be at most this many characters. */
export const ALLOWED_URL_ENTRY_MAX_LENGTH = 2048;

/** Structured, normalized form of a validated entry — used internally by the matcher. */
interface ParsedEntry {
  protocol: 'http:' | 'https:';
  /** hostname, punycoded + lowercased; keeps a leading `*.` for wildcard entries */
  hostname: string;
  isWildcard: boolean;
  /** `URL.port` string: '' for the scheme-default port, otherwise the explicit port */
  port: string;
  /** path with a trailing slash stripped; '' means "any path" (host-only entry) */
  path: string;
  /** the canonical string form that gets stored */
  normalized: string;
}

type ParseResult = { ok: true; entry: ParsedEntry } | { ok: false; reason: string };

/**
 * Parse + validate + normalize one entry. Shared by `validateAllowedUrlEntry` (surfaces the
 * reason) and the matcher (ignores entries that fail to parse). Normalization rides WHATWG
 * `new URL()`: scheme/host lowercased, IDN hosts punycoded, dot-segments resolved, default
 * ports stripped.
 */
function parseEntry(rawEntry: string): ParseResult {
  if (typeof rawEntry !== 'string') return { ok: false, reason: 'must be a string' };
  if (rawEntry.length === 0) return { ok: false, reason: 'must not be empty' };
  if (rawEntry.length > ALLOWED_URL_ENTRY_MAX_LENGTH) {
    return { ok: false, reason: `must be at most ${ALLOWED_URL_ENTRY_MAX_LENGTH} characters` };
  }

  let url: URL;
  try {
    url = new URL(rawEntry);
  } catch {
    return { ok: false, reason: 'is not a valid URL' };
  }

  if (url.protocol !== 'http:' && url.protocol !== 'https:') {
    return { ok: false, reason: 'scheme must be http or https' };
  }
  if (url.username || url.password) {
    return { ok: false, reason: 'must not contain embedded credentials' };
  }
  if (url.search) return { ok: false, reason: 'must not contain a query string' };
  if (url.hash) return { ok: false, reason: 'must not contain a fragment' };

  const isWildcard = url.hostname.includes('*');
  if (isWildcard) {
    if (!url.hostname.startsWith('*.')) {
      return { ok: false, reason: 'wildcard * is only allowed as the entire leftmost label' };
    }
    const base = url.hostname.slice(2);
    if (base.includes('*')) {
      return { ok: false, reason: 'wildcard * is only allowed as the entire leftmost label' };
    }
    if (base.split('.').length < 2) {
      return { ok: false, reason: 'wildcard host must have at least two labels after "*."' };
    }
  }

  const port = url.port ? `:${url.port}` : '';
  const path = url.pathname === '/' ? '' : url.pathname.replace(/\/+$/, '');
  const scheme = url.protocol.slice(0, -1); // 'http' | 'https'
  const normalized = `${scheme}://${url.hostname}${port}${path}`;

  return {
    ok: true,
    entry: { protocol: url.protocol, hostname: url.hostname, isWildcard, port: url.port, path, normalized },
  };
}

/**
 * Validate a single entry and return its normalized form, or a human-readable reason it was
 * rejected. Used by API/web input validation and the connection-type importer.
 */
export function validateAllowedUrlEntry(
  entry: string,
): { ok: true; normalized: string } | { ok: false; reason: string } {
  const result = parseEntry(entry);
  if (!result.ok) return result;
  return { ok: true, normalized: result.entry.normalized };
}

/** True when one decoding layer contains a separator/backslash or dot-segment escape attempt. */
function hasDangerousPathLayer(path: string): boolean {
  if (path.includes('\\') || /%2f/i.test(path) || /%5c/i.test(path)) return true;
  for (const segment of path.split('/')) {
    const decodedDots = segment.replace(/%2e/gi, '.');
    if (decodedDots === '.' || decodedDots === '..') return true;
  }
  return false;
}

/**
 * Fail closed when any recursive percent-decoding layer exposes a path separator, backslash, or
 * dot segment. Checking until stable prevents `%252e%252e%252f` and deeper encodings from escaping
 * a path prefix after an upstream performs more decoding than WHATWG URL parsing. A successful
 * decode that changes the string strictly shortens percent escapes, so rawPath.length is a hard
 * upper bound; malformed encoding and an impossible non-converging path are rejected too.
 */
function hasEncodedTraversal(rawPath: string): boolean {
  let layer = rawPath;
  for (let iteration = 0; iteration <= rawPath.length; iteration++) {
    if (hasDangerousPathLayer(layer)) return true;

    let decoded: string;
    try {
      decoded = decodeURIComponent(layer);
    } catch {
      return true;
    }
    if (decoded === layer) return false;
    layer = decoded;
  }
  return true;
}

/** Match a parsed target URL against one parsed entry per the normative rules (PRD §5.2). */
function matchesEntry(target: URL, entry: ParsedEntry): boolean {
  // 1. Scheme — exact (an https entry never matches an http target)
  if (target.protocol !== entry.protocol) return false;

  // 2. Port — exact string compare; entry without a port matches only the scheme-default port
  if (target.port !== entry.port) return false;

  // 3. Host — exact, or wildcard subdomain at any depth (apex excluded)
  if (entry.isWildcard) {
    const base = entry.hostname.slice(2); // strip '*.'
    const suffix = `.${base}`;
    if (!(target.hostname.endsWith(suffix) && target.hostname.length > suffix.length)) return false;
  } else if (target.hostname !== entry.hostname) {
    return false;
  }

  // 4. Path — host-only entry matches any path; otherwise segment-aware, case-sensitive prefix
  if (entry.path === '') return true;
  if (hasEncodedTraversal(target.pathname)) return false; // 5. encoded-traversal guard, fail closed
  return target.pathname === entry.path || target.pathname.startsWith(`${entry.path}/`);
}

/**
 * True if `targetUrl` is allowed by `allowedUrls`. An empty/absent list is unrestricted.
 * Entries are expected to be normalized (as stored); any entry that fails to parse is ignored
 * rather than throwing, and an unparseable target matches nothing. Never throws.
 */
export function urlMatchesAllowlist(targetUrl: string, allowedUrls?: string[]): boolean {
  if (!allowedUrls || allowedUrls.length === 0) return true;

  let target: URL;
  try {
    target = new URL(targetUrl);
  } catch {
    return false;
  }
  if (target.protocol !== 'http:' && target.protocol !== 'https:') return false;

  for (const raw of allowedUrls) {
    const parsed = parseEntry(raw);
    if (parsed.ok && matchesEntry(target, parsed.entry)) return true;
  }
  return false;
}

/**
 * Zod schema for a single allowlist entry: validates and rewrites to the normalized form.
 * Consumed by `allowedUrlsSchema` on connection/secret input bodies and connection-type defaults.
 */
export const allowedUrlEntrySchema = z.string().transform((val, ctx) => {
  const result = validateAllowedUrlEntry(val);
  if (!result.ok) {
    ctx.addIssue({ code: 'custom', message: `invalid allowed URL "${val}": ${result.reason}` });
    return z.NEVER;
  }
  return result.normalized;
});

/** Zod schema for the stored/submitted `allowedUrls` array (per-entry validation + count cap). */
export const allowedUrlsSchema = z
  .array(allowedUrlEntrySchema)
  .max(ALLOWED_URLS_MAX_ENTRIES, `must have at most ${ALLOWED_URLS_MAX_ENTRIES} entries`);
```
