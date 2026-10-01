# actorSchemas/task/stream/actions

Generated from the platform's runtime types. Do not edit.

The actions available for the StreamActor.

## actorSchemas/task/stream/actions

**Source:** `actorSchemas/task/stream/actions.ts`

```typescript
import { BIQJsonSchemaType, BIQSelectJsonSchema } from '../../../schemas/index.js';

/** The actions available for the StreamActor */
export enum StreamActorAction {
  CreateStream = 'createStream',
  EditMetadata = 'editMetadata',
  AppendData = 'appendData',
  ReadStream = 'readStream',
  DeleteStream = 'deleteStream',
  ListStreams = 'listStreams',
  GetStreamInfo = 'getStreamInfo',
}

// This identifies which actions have LTM and/or STM enabled
export const StreamActorActionMemory: Partial<Record<StreamActorAction, { ltm?: boolean; stm?: boolean }>> = {};

export const StreamActorActionsJsonSchema: BIQSelectJsonSchema = {
  type: BIQJsonSchemaType.String,
  title: 'Action',
  description: 'The action to perform on the StreamActor',
  enum: Object.values(StreamActorAction),
  ui: {
    component: 'searchSelect',
    options: {
      enumLabels: {
        [StreamActorAction.CreateStream]: 'Create Stream',
        [StreamActorAction.EditMetadata]: 'Edit Metadata',
        [StreamActorAction.AppendData]: 'Append Data',
        [StreamActorAction.ReadStream]: 'Read Stream',
        [StreamActorAction.DeleteStream]: 'Delete Stream',
        [StreamActorAction.ListStreams]: 'List Streams',
        [StreamActorAction.GetStreamInfo]: 'Get Stream Info',
      },
      enumGroups: {
        'Stream Management': [StreamActorAction.CreateStream, StreamActorAction.EditMetadata, StreamActorAction.ListStreams, StreamActorAction.DeleteStream],
        'Records': [StreamActorAction.AppendData, StreamActorAction.ReadStream],
        'Inspection': [StreamActorAction.GetStreamInfo],
      }
    },
  },
};
```
