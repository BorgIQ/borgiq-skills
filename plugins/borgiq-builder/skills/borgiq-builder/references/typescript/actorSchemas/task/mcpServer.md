# actorSchemas/task/mcpServer

Generated from the platform's runtime types. Do not edit.

The options for the McpServerActor.

## actorSchemas/task/mcpServer

**Source:** `actorSchemas/task/mcpServer.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../schemas/index.js';

/** The options for the McpServerActor */
export const McpServerActorOptionsSchema = z.object({
  responseTimeoutSeconds: z.number()
    .int()
    .min(1)
    .max(300)
    .default(60)
    .describe('Maximum time in seconds to wait for a tool call to complete'),
  serverName: z.string()
    .max(128)
    .nullish()
    .describe('Custom name for the MCP server (shown to clients during initialization)'),
  serverVersion: z.string()
    .max(32)
    .default('1.0.0')
    .describe('Version string for the MCP server'),
});

export type McpServerActorOptions = z.infer<typeof McpServerActorOptionsSchema>;

export const McpServerActorOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    responseTimeoutSeconds: {
      type: BIQJsonSchemaType.Integer,
      description: 'Maximum time in seconds to wait for a tool call to complete',
      title: 'Response timeout (seconds)',
      default: 60,
      minimum: 1,
      maximum: 300,
      ui: {
        order: 0,
      },
    },
    serverName: {
      type: BIQJsonSchemaType.String,
      description: 'Custom name for the MCP server (shown to clients during initialization)',
      title: 'Server name',
      ui: {
        component: 'input',
        order: 1,
        options: {
          placeholder: 'e.g. Customer data tools',
        },
      },
    },
    serverVersion: {
      type: BIQJsonSchemaType.String,
      description: 'Version string for the MCP server',
      title: 'Server version',
      default: '1.0.0',
      ui: {
        component: 'input',
        order: 2,
      },
    },
  },
};
```
