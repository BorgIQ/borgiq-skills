# actorSchemas/task/router

Generated from the platform's runtime types. Do not edit.

RouterActor options, built from the actor's source ports, and its result.

See also: [schemas/runtime](../../schemas/runtime.md), [canvas](../../canvas.md).

## actorSchemas/task/router

**Source:** `actorSchemas/task/router.ts`

```typescript
import { ZodObject, z } from 'zod';

import { RuntimeActorSourcePort } from '../../schemas/runtime.js';
import { DEFAULT_SOURCE_PORT_ID } from '../../canvas.js';

export enum RouterActorEmitType {
  SingleRoute = 'singleRoute',
  MultiRoute = 'multiRoute',
}
/** The options schema builder for the RouterActor since it changes for the sourcePorts configuration for the actor */
export const buildRouterActorOptionsSchema = (sourcePorts: RuntimeActorSourcePort[]): ZodObject<any> => z.object({ // eslint-disable-line @typescript-eslint/no-explicit-any
  emitType: z.enum(RouterActorEmitType).nullish()
    .describe('How the router actor will function, either can be singleRoute or multiRoute where singleRoute emits only on the first true condition and multiRoute emits on all true condition route. Defaults to singleRoute'),
  conditions: z.record(z.string(), z.any()).superRefine((value, ctx) => {
    const invalidRoutes: string[] = [];

    for (const routeName of Object.keys(value)) {
      const port = sourcePorts.find((port) => port.name === routeName);
      // if the port is not found, add it to the invalidRoutes list
      if (!port) {
        invalidRoutes.push(routeName);
      // if the route is the default port, add an issue
      } else if (port.id === DEFAULT_SOURCE_PORT_ID) {
        ctx.addIssue({
          code: 'invalid_value',
          path: [routeName],
          values: [routeName],
          message: `Route name '${routeName}' is reserved for the default route`,
        });
      }
    }
    // if there are no invalid ports, return the value
    if (invalidRoutes.length === 0) return;
    // if there are invalid ports, add an issue for all invalid routes
    ctx.addIssue({
      code: 'unrecognized_keys',
      keys: invalidRoutes,
      message: `Unrecognized Route name(s) in conditions: ${invalidRoutes.join(', ')}`,
    });
  })
    .describe('The conditions for the routes on if to emit, the keys for the conditions are the route name provided in the routes section, the value is the boolean condition to be evaluated and determine if the route should emit a message'),
});

export type RouterActorOptions = {
  emitType?: RouterActorEmitType,
  conditions: { [portName: string]: boolean },
};

/** The result schema for the RouterActor */
export const RouterActionResultSchema = z.string().describe('The port name that the message was emitted from');

export type RouterActionResult = z.infer<typeof RouterActionResultSchema>;
```
