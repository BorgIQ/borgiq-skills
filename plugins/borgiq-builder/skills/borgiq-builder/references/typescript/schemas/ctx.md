# schemas/ctx

Generated from the platform's runtime types. Do not edit.

The `ctx` object: org, workspace, canvas, actor, trigger actor, source actor, flowrun and parent flowrun.

See also: [canvas](../canvas.md).

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
  /** the number of distinct active actors with an edge into this actor (an actor with several edges into it counts once) */
  upstreamActorCount: z.number().int().nonnegative(),
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
