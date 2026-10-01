# actorSchemas/task/messageProcessor/actions

Generated from the platform's runtime types. Do not edit.

The actions available for the MessageProcessorActor, and which of them use memory.

## actorSchemas/task/messageProcessor/actions

**Source:** `actorSchemas/task/messageProcessor/actions.ts`

```typescript
import { BIQJsonSchemaType, BIQSelectJsonSchema } from '../../../schemas/index.js';

export enum MessageProcessorAction {
  Inject = 'inject',
  DedupeByCount = 'dedupeByCount',
  DedupeByTime = 'dedupeByTime',
  DelayBySeconds = 'delayBySeconds',
  DelayUntil = 'delayUntil',
  Filter = 'filter',
  Fork = 'fork',
  ForkJoin = 'forkJoin',
  Collect = 'collect',
  Split = 'split',
  IssueCallbackToken = 'issueCallbackToken',
  WaitForCallbackToken = 'waitForCallbackToken',
  NotifyCallbackToken = 'notifyCallbackToken',
  RenderTemplate = 'renderTemplate',
  RegexExtract = 'regexExtract',
  DownloadFileUrl = 'downloadFileUrl',
  DownloadFileAsBase64 = 'downloadFileAsBase64',
}

// This identifies which actions have LTM and/or STM enabled
export const MessageProcessorActorActionMemory: Partial<Record<MessageProcessorAction, { ltm?: boolean; stm?: boolean }>> = {
  [MessageProcessorAction.DedupeByCount]: { ltm: true },
  [MessageProcessorAction.DedupeByTime]: { ltm: true },
  [MessageProcessorAction.ForkJoin]: { stm: true },
  [MessageProcessorAction.Collect]: { stm: true },
};

export const MessageProcessorActorActionsJsonSchema: BIQSelectJsonSchema = {
  type: BIQJsonSchemaType.String,
  title: 'Action',
  description: 'The action to perform on the Message Processor Actor',
  enum: Object.values(MessageProcessorAction),
  ui: {
    component: 'searchSelect',
    options: {
      enumLabels: {
        [MessageProcessorAction.Inject]: 'Inject',
        [MessageProcessorAction.DedupeByCount]: 'Dedupe By Count',
        [MessageProcessorAction.DedupeByTime]: 'Dedupe By Time',
        [MessageProcessorAction.DelayBySeconds]: 'Delay By Seconds',
        [MessageProcessorAction.DelayUntil]: 'Delay Until',
        [MessageProcessorAction.Filter]: 'Filter',
        [MessageProcessorAction.Fork]: 'Fork',
        [MessageProcessorAction.ForkJoin]: 'Fork Join',
        [MessageProcessorAction.Collect]: 'Collect',
        [MessageProcessorAction.Split]: 'Split',
        [MessageProcessorAction.IssueCallbackToken]: 'Issue Callback Token',
        [MessageProcessorAction.WaitForCallbackToken]: 'Wait For Callback Token',
        [MessageProcessorAction.NotifyCallbackToken]: 'Notify For Callback Token', // i.e. instead of waiting for the callback token, we notify it via actors.
        [MessageProcessorAction.RenderTemplate]: 'Render Template',
        [MessageProcessorAction.RegexExtract]: 'Regex Extract',
        [MessageProcessorAction.DownloadFileUrl]: 'Download File URL',
        [MessageProcessorAction.DownloadFileAsBase64]: 'Download File As Base64',
      },
      enumGroups: {
        'Array': [MessageProcessorAction.Collect, MessageProcessorAction.Split],
        'Dedupe': [MessageProcessorAction.DedupeByCount, MessageProcessorAction.DedupeByTime],
        'Delay': [MessageProcessorAction.DelayBySeconds, MessageProcessorAction.DelayUntil],
        'Fork': [MessageProcessorAction.Fork, MessageProcessorAction.ForkJoin],
        'Callback': [MessageProcessorAction.IssueCallbackToken, MessageProcessorAction.WaitForCallbackToken, MessageProcessorAction.NotifyCallbackToken],
        'Message': [MessageProcessorAction.Inject, MessageProcessorAction.RenderTemplate, MessageProcessorAction.RegexExtract, MessageProcessorAction.Filter],
        'File': [MessageProcessorAction.DownloadFileUrl, MessageProcessorAction.DownloadFileAsBase64],
      }
    },
  },
};
```
