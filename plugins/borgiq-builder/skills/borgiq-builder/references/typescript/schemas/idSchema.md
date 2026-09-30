# schemas/idSchema

Generated from the platform's runtime types. Do not edit.

Id validators per object type: a four-character prefix plus 26 lowercase Crockford base32 characters, 30 in all.

See also: [prefix](../prefix.md).

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
  // schema for app session id (derived, not stored — see packages/core/src/lib/token/appSessionId.ts)
  appSessionId: z.string().regex(buildIdRegex(Prefix.AppSession), regMsg).length(30, lenMsg),
  // schema for template id
  actorTemplateId: z.string().regex(buildIdRegex(Prefix.ActorTemplate), regMsg).length(30, lenMsg),
  // schema for template app id
  templateAppId: z.string().regex(buildIdRegex(Prefix.TemplateApp), regMsg).length(30, lenMsg),
  // schema for template category id
  templateCategoryId: z.string().regex(buildIdRegex(Prefix.TemplateCategory), regMsg).length(30, lenMsg),
  // schema for recipe id
  recipeId: z.string().regex(buildIdRegex(Prefix.Recipe), regMsg).length(30, lenMsg),
  // schema for actor id
  actorId: z.string().regex(buildIdRegex(Prefix.Actor), regMsg).length(30, lenMsg),
  // schema for canvas id
  canvasId: z.string().regex(buildIdRegex(Prefix.Canvas), regMsg).length(30, lenMsg),
  // schema for canvas runtime build id
  canvasRuntimeBuildId: z.string().regex(buildIdRegex(Prefix.CanvasRuntimeBuild), regMsg).length(30, lenMsg),
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
  // schema for stream id
  streamId: z.string().regex(buildIdRegex(Prefix.Stream), regMsg).length(30, lenMsg),
  // schema for audit log id
  auditLogId: z.string().regex(buildIdRegex(Prefix.AuditLog), regMsg).length(30, lenMsg),
  // schema for api token id (personal access token)
  apiTokenId: z.string().regex(buildIdRegex(Prefix.Token), regMsg).length(30, lenMsg),
  // schema for source port for an actor
  sourcePortId: z.string().regex(new RegExp(`${Prefix.SourcePort}[0123456789abcdefghijklmnopqrstuvwxyz]{7}`), regMsg).length(11, 'must exactly be 11 characters long'),
  // schema for target port for an actor
  targetPortId: z.string().regex(new RegExp(`${Prefix.TargetPort}[0123456789abcdefghijklmnopqrstuvwxyz]{4}`), regMsg).length(11, 'must exactly be 11 characters long'),
};

/**
 * A build identity hash as `buildIdentityHash` (../buildIdentity.ts) produces it: `sha256:` plus 64
 * lowercase hex chars. The one shape every producer writes, so anything else is a malformed value to
 * reject at the boundary rather than a confusing equality mismatch later.
 *
 * Lives here (not in runtimeBuild.ts, its natural home) because both runtime.ts and runtimeBuild.ts
 * need it and this file is the shared leaf — importing runtimeBuild.ts from runtime.ts closes an
 * import cycle through awsLambdaFunction.ts that breaks bundlers at module init.
 */
export const BuildIdentityHashSchema = z.string().regex(/^sha256:[0-9a-f]{64}$/);
```
