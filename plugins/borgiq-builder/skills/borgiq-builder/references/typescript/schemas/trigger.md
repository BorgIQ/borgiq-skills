# schemas/trigger

Generated from the platform's runtime types. Do not edit.

`TriggerEvent`, the event a UniversalTriggerActor receives, discriminated on `type`.

See also: [schemas/runtime](runtime.md).

## schemas/trigger

**Source:** `schemas/trigger.ts`

```typescript
import { z } from 'zod';

import { FlowrunLifecycleTriggerDataSchema, FlowrunWebhookTriggerRequestSchema } from './runtime.js';

const TriggerUserSchema = z.object({
  id: z.string(),
  name: z.string().optional(),
  email: z.string(),
  /**
   * The caller's app session: one id per (BorgIQ login session x app actor). Stable across
   * page reloads and token refreshes, distinct per app, gone when the login ends. NOT a
   * property of the user — the same viewer in two apps produces two values; the `app` in the
   * name is what keeps that unambiguous. Present only when the fire carried an app-actor
   * token whose mint ran under a browser login; absence means "no session information".
   * Identity, not authorization: trust this server-attested field, never a session id
   * arriving in a request body or query string.
   */
  appSessionId: z.string().optional(),
});

/**
 * The trigger event passed to every trigger actor and exposed to user code on the UniversalTriggerActor as `req.trigger`.
 * Discriminated by `type`. Each trigger actor maps its orchestrator payload onto one of these variants.
 * - 'webhook'   — an HTTP request hit the webhook URL; `request` carries the parsed request; `user` is the
 *                 authenticated caller when the call carried an app-actor token (React-app endpoint calls, and
 *                 any 'apps'-level webhook fire) or an API key ('apiKey' / 'appsAndApiKey' fires, where it is
 *                 the key's owner and `request.meta.auth` names the key). The same user is also on `request.meta.user`.
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
 *                 The vocabulary grows by extending `LIFECYCLE_TRIGGER_EVENTS`, never by
 *                 adding union members, so runtime dispatch branches once on `type`. `on-delete`
 *                 also carries `scope`, `subject` and (on a hand-run test fire) `manual`.
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
  FlowrunLifecycleTriggerDataSchema,
]);

export type TriggerEvent = z.infer<typeof TriggerEventSchema>;
```
