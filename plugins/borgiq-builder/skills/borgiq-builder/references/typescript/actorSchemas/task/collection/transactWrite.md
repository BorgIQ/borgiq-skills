# actorSchemas/task/collection/transactWrite

Generated from the platform's runtime types. Do not edit.

The options schema for the transactWrite action for the CollectionActor.

See also: [actorSchemas/task/collection/actions](actions.md).

## actorSchemas/task/collection/transactWrite

**Source:** `actorSchemas/task/collection/transactWrite.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { CollectionActorAction } from './actions.js';

/** The options schema for the transactWrite action for the CollectionActor */
export const CollectionActorTransactWriteOptionsSchema = z.object({
  /** Must be transactWrite to access this function */
  action: z.literal(CollectionActorAction.TransactWrite)
    .describe('Must be transactWrite to access this function'),
  items: z.array(z.object({
    operation: z.enum(['put', 'update', 'delete', 'check'])
      .describe('The operation to perform'),
    collection: z.string()
      .describe('The collection for the operation'),
    key: z.string()
      .describe('The key for the operation'),
    value: z.unknown().optional()
      .describe('The value for put/update operations'),
    labels: z.record(z.string(), z.string().nullable()).optional()
      .describe('Labels for the item'),
    ttl: z.union([z.number(), z.string(), z.null()]).optional()
      .describe('Time-to-live for the item'),
    conditions: z.record(z.string(), z.unknown()).optional()
      .describe('Conditional expressions for the operation. Applies to data fields only, not labels.'),
    atomicCounters: z.record(z.string(), z.number()).optional()
      .describe('Atomic counter increments to apply'),
  })).max(100)
    .describe('The items to transact, up to 100'),
  options: z.object({
    idempotencyKey: z.string().optional()
      .describe('An idempotency key for the transaction'),
  }).optional()
    .describe('Options for the transact write operation'),
});

export type CollectionActorTransactWriteOptions = z.infer<typeof CollectionActorTransactWriteOptionsSchema>;

export const CollectionActorTransactWriteOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      title: 'Action',
      description: 'Must be transactWrite to access this function',
      const: CollectionActorAction.TransactWrite,
    },
    items: {
      type: BIQJsonSchemaType.Array,
      title: 'Items',
      description: 'The items to transact, up to 100',
      maxItems: 100,
      items: {
        type: BIQJsonSchemaType.Object,
        title: 'Item',
        properties: {
          operation: {
            type: BIQJsonSchemaType.String,
            title: 'Operation',
            description: 'The operation to perform',
            enum: ['put', 'update', 'delete', 'check'],
            ui: { component: 'select' },
          },
          collection: {
            type: BIQJsonSchemaType.String,
            title: 'Collection',
            description: 'The collection for the operation',
          },
          key: {
            type: BIQJsonSchemaType.String,
            title: 'Key',
            description: 'The key for the operation',
          },
          value: {
            type: BIQJsonSchemaType.Any,
            title: 'Value',
            description: 'The value for put/update operations',
            ui: { options: { editInModal: true } },
          },
          labels: {
            type: BIQJsonSchemaType.Any,
            title: 'Labels',
            description: 'Labels for the item',
          },
          ttl: {
            title: 'TTL',
            description: 'Time-to-live for the item',
            anyOf: [
              { type: BIQJsonSchemaType.Number, title: 'TTL (seconds)' },
              { type: BIQJsonSchemaType.String, title: 'TTL (expression)' },
            ],
          },
          conditions: {
            type: BIQJsonSchemaType.Any,
            title: 'Conditions',
            description: 'Conditional expressions for the operation. Applies to data fields only, not labels.',
            ui: { options: { editInModal: true } },
          },
          atomicCounters: {
            type: BIQJsonSchemaType.Any,
            title: 'Atomic counters',
            description: 'Atomic counter increments to apply',
            ui: { options: { editInModal: true } },
          },
        },
        required: ['operation', 'collection', 'key'],
      },
    },
    options: {
      type: BIQJsonSchemaType.Object,
      title: 'Options',
      description: 'Options for the transact write operation',
      properties: {
        idempotencyKey: {
          type: BIQJsonSchemaType.String,
          title: 'Idempotency key',
          description: 'An idempotency key for the transaction',
        },
      },
    },
  },
  required: ['action', 'items'],
};

/** The emitted message schema for the transactWrite action for the CollectionActor */
export const CollectionActorTransactWriteResultSchema = z.object({
  processed: z.number()
    .describe('The number of items processed'),
});

export type CollectionActorTransactWriteResult = z.infer<typeof CollectionActorTransactWriteResultSchema>;
```
