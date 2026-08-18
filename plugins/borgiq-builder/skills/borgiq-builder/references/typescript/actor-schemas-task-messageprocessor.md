# Actor Schemas: MessageProcessorActor

Zod schemas and TypeScript types for MessageProcessorActor actions: inject, split, collect, filter, fork, forkJoin, delayBySeconds, delayUntil, dedupeByCount, dedupeByTime, issueCallbackToken, waitForCallbackToken, notifyCallbackToken, renderTemplate, regexExtract, downloadFileUrl, downloadFileAsBase64.

## Table of Contents

- [actorSchemas/task/messageProcessor/actions.ts](#actorschemastaskmessageprocessoractions)
- [actorSchemas/task/messageProcessor/collect.ts](#actorschemastaskmessageprocessorcollect)
- [actorSchemas/task/messageProcessor/dedupeByCount.ts](#actorschemastaskmessageprocessordedupebycount)
- [actorSchemas/task/messageProcessor/dedupeByTime.ts](#actorschemastaskmessageprocessordedupebytime)
- [actorSchemas/task/messageProcessor/delayBySeconds.ts](#actorschemastaskmessageprocessordelaybyseconds)
- [actorSchemas/task/messageProcessor/delayUntil.ts](#actorschemastaskmessageprocessordelayuntil)
- [actorSchemas/task/messageProcessor/downloadFileAsBase64.ts](#actorschemastaskmessageprocessordownloadfileasbase64)
- [actorSchemas/task/messageProcessor/downloadFileUrl.ts](#actorschemastaskmessageprocessordownloadfileurl)
- [actorSchemas/task/messageProcessor/filter.ts](#actorschemastaskmessageprocessorfilter)
- [actorSchemas/task/messageProcessor/fork.ts](#actorschemastaskmessageprocessorfork)
- [actorSchemas/task/messageProcessor/forkJoin.ts](#actorschemastaskmessageprocessorforkjoin)
- [actorSchemas/task/messageProcessor/index.ts](#actorschemastaskmessageprocessorindex)
- [actorSchemas/task/messageProcessor/inject.ts](#actorschemastaskmessageprocessorinject)
- [actorSchemas/task/messageProcessor/issueCallbackToken.ts](#actorschemastaskmessageprocessorissuecallbacktoken)
- [actorSchemas/task/messageProcessor/notifyCallbackToken.ts](#actorschemastaskmessageprocessornotifycallbacktoken)
- [actorSchemas/task/messageProcessor/regexExtract.ts](#actorschemastaskmessageprocessorregexextract)
- [actorSchemas/task/messageProcessor/renderTemplate.ts](#actorschemastaskmessageprocessorrendertemplate)
- [actorSchemas/task/messageProcessor/split.ts](#actorschemastaskmessageprocessorsplit)
- [actorSchemas/task/messageProcessor/waitForCallbackToken.ts](#actorschemastaskmessageprocessorwaitforcallbacktoken)

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

## actorSchemas/task/messageProcessor/collect

**Source:** `actorSchemas/task/messageProcessor/collect.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { MessageProcessorAction } from './actions.js';

/** The options schema for the collect action in the MessageProcessorActor */
export const MessageProcessorActorCollectOptionsSchema = z.object({
  action: z.literal(MessageProcessorAction.Collect)
    .describe('Must be collect to access this function'),
  splitId: z.string()
    .describe('The split ID from the upstream Message Processor Actor with the split action that the values should be collected from'),
  size: z.number().int().gt(0)
    .describe('The total size of the array being collected, can be the size from the upstream split action'),
  captureValue: z.any()
    .describe('The value to collect and insert into the array'),
  emitKey: z.string().nullish()
    .describe('The key to emit the collected array under, defaults to message'),
  if: z.boolean().nullish()
    .describe('If provided the condition must evaluate to true for the value to be collected.'),
});

export type MessageProcessorActorCollectOptions = z.infer<typeof MessageProcessorActorCollectOptionsSchema>;

export const MessageProcessorActorCollectOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      const: MessageProcessorAction.Collect,
    },
    splitId: {
      type: BIQJsonSchemaType.String,
      title: 'Split ID',
      description: 'The split ID from the upstream Message Processor Actor with the split action that the values should be collected from',
      minLength: 1,
      default: '${{msg.SPLIT_ACTOR.splitId}}',
    },
    size: {
      type: BIQJsonSchemaType.Integer,
      title: 'Size',
      description: 'The total size of the array being collected, can be the size from the upstream split action',
      exclusiveMinimum: 0,
      default: '${{msg.SPLIT_ACTOR.size}}',
    },
    captureValue: {
      type: BIQJsonSchemaType.Any,
      title: 'Capture value',
      description: 'The value to collect and insert into the array',
      default: '${{msg}}',
    },
    emitKey: {
      type: BIQJsonSchemaType.String,
      title: 'Emit key',
      description: 'The key to emit the collected array under, defaults to message',
      default: 'items',
    },
    if: {
      type: BIQJsonSchemaType.Boolean,
      title: 'If',
      description: 'If provided the condition must evaluate to true for the value to be collected.',
      default: '${{true}}',
      ui: {
        component: 'switch',
      },
    },
  },
  required: ['action', 'splitId', 'size', 'captureValue'],
};

/** The emitted message schema for the collect action in the MessageProcessActor */
export const MessageProcessorActorCollectResultSchema = z.record(z.string(),
  z.array(z.record(z.string(), z.any())),
);

export type MessageProcessorActorCollectResult = z.infer<typeof MessageProcessorActorCollectResultSchema>;
```

## actorSchemas/task/messageProcessor/dedupeByCount

**Source:** `actorSchemas/task/messageProcessor/dedupeByCount.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { MessageProcessorAction } from './actions.js';

/** The options action for the dedupeByCount action in the MessageProcessActor */
export const MessageProcessorActorDedupeByCountOptionsSchema = z.object({
  action: z.literal(MessageProcessorAction.DedupeByCount)
    .describe('Must be dedupeByCount to access this function'),
  dedupeKey: z.any()
    .describe('The key to perform the deduplicate action by'),
  lookbackAsCount: z.number().int().gt(0)
    .describe('The number of messages to look back to to check if a message has been emitted with key'),
  emitAlways: z.boolean()
    .describe('If true, the actor would emit the message even if it has been emitted before'),
});

export type MessageProcessorActorDedupeByCountOptions = z.infer<typeof MessageProcessorActorDedupeByCountOptionsSchema>;

export const MessageProcessorActorDedupeByCountOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      const: MessageProcessorAction.DedupeByCount,
    },
    dedupeKey: {
      type: BIQJsonSchemaType.Any,
      title: 'Dedupe key',
      description: 'The key to perform the deduplicate action by',
      default: '${{ }}',
    },
    lookbackAsCount: {
      type: BIQJsonSchemaType.Integer,
      title: 'Lookback as count',
      description: 'The number of messages to look back to to check if a message has been emitted with key',
      exclusiveMinimum: 0,
    },
    emitAlways: {
      type: BIQJsonSchemaType.Boolean,
      title: 'Emit always',
      description: 'If true, the actor would emit the message even if it has been emitted before',
      ui: {
        component: 'switch',
      },
    },
  },
  required: ['action', 'dedupeKey', 'lookbackAsCount', 'emitAlways'],
};

/** The emitted message schema for the dedupeByCount for the MessageProcessorActor */
export const MessageProcessorActorDedupeByCountResultSchema = z.object({
  dedupeKey: z.any()
    .describe('The key that the message was deduplicated by'),
  unique: z.boolean()
    .describe('If the message key is unique across the count, will only be false if emitAlways in the options is set to true'),
});

export type MessageProcessorActorDedupeByCountResult = z.infer<typeof MessageProcessorActorDedupeByCountResultSchema>;
```

## actorSchemas/task/messageProcessor/dedupeByTime

**Source:** `actorSchemas/task/messageProcessor/dedupeByTime.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { MessageProcessorAction } from './actions.js';

/** The options schema for the dedupeByTime action in the MessageProcessorActor */
export const MessageProcessorActorDedupeByTimeOptionsSchema = z.object({
  action: z.literal(MessageProcessorAction.DedupeByTime)
    .describe('Must be dedupeByTime to access this function'),
  dedupeKey: z.any()
    .describe('The key to perform the deduplicate action by'),
  lookbackInSeconds: z.number().gt(0)
    .describe('The number of seconds to look back to to check if a message has been emitted with key'),
  emitAlways: z.boolean()
    .describe('If true, the actor would emit the message even if it has been emitted before'),
});

export type MessageProcessorActorDedupeByTimeOptions = z.infer<typeof MessageProcessorActorDedupeByTimeOptionsSchema>;

export const MessageProcessorActorDedupeByTimeOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      const: MessageProcessorAction.DedupeByTime,
    },
    dedupeKey: {
      type: BIQJsonSchemaType.Any,
      title: 'Dedupe key',
      description: 'The key to perform the deduplicate action by',
    },
    lookbackInSeconds: {
      type: BIQJsonSchemaType.Number,
      title: 'Lookback in seconds',
      description: 'The number of seconds to look back to to check if a message has been emitted with key',
      exclusiveMinimum: 0,
    },
    emitAlways: {
      type: BIQJsonSchemaType.Boolean,
      title: 'Emit always',
      description: 'If true, the actor would emit the message even if it has been emitted before',
      default: false,
      ui: {
        component: 'switch',
      },
    },
  },
  required: ['action', 'dedupeKey', 'lookbackInSeconds', 'emitAlways'],
};

/** The emitted message schema for the dedupeByTime action in the MessageProcessorActor */
export const MessageProcessorActorDedupeByTimeResultSchema = z.object({
  dedupeKey: z.any()
    .describe('The key that the message was deduplicated by'),
  unique: z.boolean()
    .describe('If the message key is unique across the time, will only be false if emitAlways in the options is set to true'),
});

export type MessageProcessorActorDedupeByTimeResult = z.infer<typeof MessageProcessorActorDedupeByTimeResultSchema>;
```

## actorSchemas/task/messageProcessor/delayBySeconds

**Source:** `actorSchemas/task/messageProcessor/delayBySeconds.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { MessageProcessorAction } from './actions.js';

/** The options schema for the delayBySeconds action in the MessageProcessorSchema */
export const MessageProcessorActorDelayBySecondsOptionsSchema = z.object({
  /** Must be delayBySeconds to access this function */
  action: z.literal(MessageProcessorAction.DelayBySeconds)
    .describe('Must be delayBySeconds to access this function'),
  /** The number of seconds to delay emitting the message */
  seconds: z.number().gte(0)
    .describe('The number of seconds to delay emitting the message'),
});

export type MessageProcessorActorDelayBySecondsOptions = z.infer<typeof MessageProcessorActorDelayBySecondsOptionsSchema>;

export const MessageProcessorActorDelayBySecondsOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      const: MessageProcessorAction.DelayBySeconds,
    },
    seconds: {
      type: BIQJsonSchemaType.Number,
      title: 'Seconds',
      description: 'The number of seconds to delay emitting the message',
      minimum: 0,
    },
  },
  required: ['action', 'seconds'],
};

/** The emitted message schema for the delayBySeconds action in the MessageProcessorSchema */
export const MessageProcessorActorDelayResultSchema = z.object({
  /** the date the messaged emitted at as ISO formatted date time string */
  delayUntil: z.string(),
});

export type MessageProcessorActorDelayResult = z.infer<typeof MessageProcessorActorDelayResultSchema>;
```

## actorSchemas/task/messageProcessor/delayUntil

**Source:** `actorSchemas/task/messageProcessor/delayUntil.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { MessageProcessorAction } from './actions.js';

/** The options schema for the delayUntil action in the MessageProcessorSchema */
export const MessageProcessorActorDelayUntilOptionsSchema = z.object({
  action: z.literal(MessageProcessorAction.DelayUntil)
    .describe('Must be delayUntil to access this function'),
  until: z.iso.datetime()
    .describe('The time to delay emitting the message at'),
});

export type MessageProcessorActorDelayUntilOptions = z.infer<typeof MessageProcessorActorDelayUntilOptionsSchema>;

export const MessageProcessorActorDelayUntilOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      const: MessageProcessorAction.DelayUntil,
    },
    until: {
      type: BIQJsonSchemaType.String,
      format: 'date-time',
      title: 'Until',
      description: 'The time to delay emitting the message at',
    },
  },
  required: ['action', 'until'],
};
```

## actorSchemas/task/messageProcessor/downloadFileAsBase64

**Source:** `actorSchemas/task/messageProcessor/downloadFileAsBase64.ts`

```typescript
import { z } from 'zod';

import { BIQFileSchema, BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { MessageProcessorAction } from './actions.js';

/** The options schema for the download file as base64 action in the MessageProcessorActor */
export const MessageProcessorActorDownloadFileAsBase64OptionsSchema = z.object({
  action: z.literal(MessageProcessorAction.DownloadFileAsBase64)
    .describe('Must be downloadFileAsBase64 to access this function'),
  file: BIQFileSchema,
});

export type MessageProcessorActorDownloadFileAsBase64Options = z.infer<typeof MessageProcessorActorDownloadFileAsBase64OptionsSchema>;

export const MessageProcessorActorDownloadFileAsBase64OptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      const: MessageProcessorAction.DownloadFileAsBase64,
    },
    file: {
      type: BIQJsonSchemaType.Any,
      title: 'File',
      description: 'The BorgIQ file to download',
    },
  },
  required: ['action', 'file'],
};

/** The emitted message schema for the downloadFileAsBase64 action in the MessageProcessorActor */
export const MessageProcessorActorDownloadFileAsBase64ResultSchema = z.object({
  file: BIQFileSchema,
  base64: z.string().describe('The base64 encoded string of the file'),
});

export type MessageProcessorActorDownloadFileAsBase64Result = z.infer<typeof MessageProcessorActorDownloadFileAsBase64ResultSchema>;
```

## actorSchemas/task/messageProcessor/downloadFileUrl

**Source:** `actorSchemas/task/messageProcessor/downloadFileUrl.ts`

```typescript
import { z } from 'zod';

import { BIQFileSchema, BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { MessageProcessorAction } from './actions.js';

/** The options schema for the download file url action in the MessageProcessorActor */
export const MessageProcessorActorDownloadFileUrlOptionsSchema = z.object({
  action: z.literal(MessageProcessorAction.DownloadFileUrl)
    .describe('Must be downloadFileUrl to access this function'),
  file: BIQFileSchema,
  expiresInMinutes: z.number().min(1).nullish().describe('The number of minutes download URL will be valid for'),
  downloadAsAttachment: z.boolean().nullish().describe('Whether to download the file as an attachment or inline. Defaults to false.'),
});

export type MessageProcessorActorDownloadFileUrlOptions = z.infer<typeof MessageProcessorActorDownloadFileUrlOptionsSchema>;

export const MessageProcessorActorDownloadFileUrlOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      const: MessageProcessorAction.DownloadFileUrl,
    },
    file: {
      type: BIQJsonSchemaType.Any,
      title: 'File',
      description: 'The BorgIQ file to download',
    },
    expiresInMinutes: {
      type: BIQJsonSchemaType.Number,
      title: 'Expires URL after minutes',
      description: 'The number of minutes download URL will be valid for. Defaults to 1 minute.',
      default: 1,
    },
    downloadAsAttachment: {
      type: BIQJsonSchemaType.Boolean,
      title: 'Download as attachment',
      description: 'Whether the file should be downloaded as an attachment to the user\'s computer or opened in the browser. Defaults to false, open the file in the browser.',
      default: false,
    },
  },
  required: ['action', 'file'],
};

/** The emitted message schema for the downloadFileAsBase64 action in the MessageProcessorActor */
export const MessageProcessorActorDownloadFileUrlResultSchema = z.object({
  file: BIQFileSchema,
  url: z.string().describe('The download URL of the file'),
});

export type MessageProcessorActorDownloadFileUrlResult = z.infer<typeof MessageProcessorActorDownloadFileUrlResultSchema>;
```

## actorSchemas/task/messageProcessor/filter

**Source:** `actorSchemas/task/messageProcessor/filter.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { MessageProcessorAction } from './actions.js';

/** The options schema for the filter action in the MessageProcessorActor */
export const MessageProcessorActorFilterOptionsSchema = z.object({
  action: z.literal(MessageProcessorAction.Filter)
    .describe('Must be filter to access this function'),
  filter: z.boolean(),
});

export type MessageProcessorActorFilterOptions = z.infer<typeof MessageProcessorActorFilterOptionsSchema>;

export const MessageProcessorActorFilterOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      const: MessageProcessorAction.Filter,
    },
    filter: {
      type: BIQJsonSchemaType.Boolean,
      default: '${{}}',
      ui: {
        component: 'switch',
      },
    },
  },
  required: ['action', 'filter'],
};

/** The emitted message schema for the filter action in the MessageProcessorActor */
export const MessageProcessorActorFilterResultSchema = z.boolean();

export type MessageProcessorActorFilterResult = z.infer<typeof MessageProcessorActorFilterResultSchema>;
```

## actorSchemas/task/messageProcessor/fork

**Source:** `actorSchemas/task/messageProcessor/fork.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { MessageProcessorAction } from './actions.js';

/** The options schema for the fork action in the MessageProcessorActor */
export const MessageProcessorActorForkOptionsSchema = z.object({
  action: z.literal(MessageProcessorAction.Fork)
    .describe('Must be fork to access this function'),
});

export type MessageProcessorActorForkOptions = z.infer<typeof MessageProcessorActorForkOptionsSchema>;

export const MessageProcessorActorForkOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      const: MessageProcessorAction.Fork,
    },
  },
  required: ['action'],
};

/** The emitted message schema for the fork action in the MessageProcessorActor */
export const MessageProcessorActorForkResultSchema = z.object({
  forkId: z.string()
    .describe('The unique ID to be used by the downstream Message Processor Actor with the forkJoin action'),
});

export type MessageProcessorActorForkResult = z.infer<typeof MessageProcessorActorForkResultSchema>;
```

## actorSchemas/task/messageProcessor/forkJoin

**Source:** `actorSchemas/task/messageProcessor/forkJoin.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { MessageProcessorAction } from './actions.js';

/** The options for the forkJoin actor in the MessageProcessorActor */
export const MessageProcessorActorForkJoinOptionsSchema = z.object({
  action: z.literal(MessageProcessorAction.ForkJoin)
    .describe('Must be forkJoin to access this function'),
  forkId: z.string()
    .describe('The forkId emitted by the upstream MessageProcessorActor with the fork action. Messages with the same forkId will be collected in the same message'),
  size: z.number().int().gt(0)
    .describe('The number of unique actor messages it should collect, it CAN NOT be greater than the number of connected actors'),
});

export type MessageProcessorActorForkJoinOptions = z.infer<typeof MessageProcessorActorForkJoinOptionsSchema>;

export const MessageProcessorActorForkJoinOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      const: MessageProcessorAction.ForkJoin,
    },
    forkId: {
      type: BIQJsonSchemaType.String,
      title: 'Fork ID',
      description: 'The forkId emitted by the upstream MessageProcessorActor with the fork action. Messages with the same forkId will be collected in the same message',
      default: '${{msg.FORK_ACTOR.forkId}}',
    },
    size: {
      type: BIQJsonSchemaType.Integer,
      exclusiveMinimum: 0,
      title: 'Size',
      description: 'The number of unique actor messages it should collect, it CAN NOT be greater than the number of connected actors',
    },
  },
  required: ['action', 'forkId', 'size'],
};

/** The emitted message schema for the forkJoin action in the MessageProcessorActor */
/** Each key in the emitted message would be the actor that is the the source actor */
export const MessageProcessorActorForkJoinResultSchema = z.record(z.string(),
  z.array(z.record(z.string(), z.any())),
);

export type MessageProcessorActorForkJoinResult = z.infer<typeof MessageProcessorActorForkJoinResultSchema>;
```

## actorSchemas/task/messageProcessor/index

**Source:** `actorSchemas/task/messageProcessor/index.ts`

```typescript
import { z } from 'zod';

import { MessageProcessorActorCollectResult, MessageProcessorActorCollectOptionsSchema } from './collect.js';
import { MessageProcessorActorDedupeByCountResult, MessageProcessorActorDedupeByCountOptionsSchema } from './dedupeByCount.js';
import { MessageProcessorActorDedupeByTimeResult, MessageProcessorActorDedupeByTimeOptionsSchema } from './dedupeByTime.js';
import { MessageProcessorActorForkResult, MessageProcessorActorForkOptionsSchema } from './fork.js';
import { MessageProcessorActorForkJoinResult, MessageProcessorActorForkJoinOptionsSchema } from './forkJoin.js';
import { MessageProcessorActorInjectOptionsSchema } from './inject.js';
import { MessageProcessorActorIssueCallbackTokenResult, MessageProcessorActorIssueCallbackTokenOptionsSchema } from './issueCallbackToken.js';
import { MessageProcessorActorNotifyCallbackTokenResult, MessageProcessorActorNotifyCallbackTokenOptionsSchema } from './notifyCallbackToken.js';
import { MessageProcessorActorRegexExtractResult, MessageProcessorActorRegexExtractOptionsSchema } from './regexExtract.js';
import { MessageProcessorActorSplitResult, MessageProcessorActorSplitOptionsSchema } from './split.js';
import { MessageProcessorActorWaitForCallbackTokenResult, MessageProcessorActorWaitForCallbackTokenOptionsSchema } from './waitForCallbackToken.js';
import { MessageProcessorActorRenderTemplateOptionsSchema } from './renderTemplate.js';
import { MessageProcessorActorDelayResult, MessageProcessorActorDelayBySecondsOptionsSchema } from './delayBySeconds.js';
import { MessageProcessorActorDelayUntilOptionsSchema } from './delayUntil.js';
import { MessageProcessorActorFilterResult, MessageProcessorActorFilterOptionsSchema } from './filter.js';
import { MessageProcessorActorDownloadFileUrlResult, MessageProcessorActorDownloadFileUrlOptionsSchema } from './downloadFileUrl.js';
import { MessageProcessorActorDownloadFileAsBase64Result, MessageProcessorActorDownloadFileAsBase64OptionsSchema } from './downloadFileAsBase64.js';
export * from './collect.js';
export * from './dedupeByCount.js';
export * from './dedupeByTime.js';
export * from './fork.js';
export * from './forkJoin.js';
export * from './inject.js';
export * from './issueCallbackToken.js';
export * from './notifyCallbackToken.js';
export * from './regexExtract.js';
export * from './split.js';
export * from './waitForCallbackToken.js';
export * from './renderTemplate.js';
export * from './delayBySeconds.js';
export * from './delayUntil.js';
export * from './actions.js';
export * from './filter.js';
export * from './downloadFileAsBase64.js';
export * from './downloadFileUrl.js';

export const MessageProcessorActorDelayOptionsSchema = z.discriminatedUnion('action', [
  MessageProcessorActorDelayBySecondsOptionsSchema,
  MessageProcessorActorDelayUntilOptionsSchema,
]);

export type MessageProcessorActorDelayOptions = z.infer<typeof MessageProcessorActorDelayOptionsSchema>;


export const MessageProcessorActorOptionsSchema = z.discriminatedUnion(
  'action',
  [
    MessageProcessorActorSplitOptionsSchema,
    MessageProcessorActorCollectOptionsSchema,
    MessageProcessorActorDedupeByTimeOptionsSchema,
    MessageProcessorActorDedupeByCountOptionsSchema,
    MessageProcessorActorRegexExtractOptionsSchema,
    MessageProcessorActorInjectOptionsSchema,
    MessageProcessorActorIssueCallbackTokenOptionsSchema,
    MessageProcessorActorNotifyCallbackTokenOptionsSchema,
    MessageProcessorActorWaitForCallbackTokenOptionsSchema,
    MessageProcessorActorForkOptionsSchema,
    MessageProcessorActorForkJoinOptionsSchema,
    MessageProcessorActorRenderTemplateOptionsSchema,
    MessageProcessorActorDelayBySecondsOptionsSchema,
    MessageProcessorActorDelayUntilOptionsSchema,
    MessageProcessorActorFilterOptionsSchema,
    MessageProcessorActorDownloadFileUrlOptionsSchema,
    MessageProcessorActorDownloadFileAsBase64OptionsSchema,
  ]
);


export type MessageProcessorActorOptions = z.infer<typeof MessageProcessorActorOptionsSchema>;


export type MessageProcessorResult = MessageProcessorActorCollectResult | MessageProcessorActorWaitForCallbackTokenResult | MessageProcessorActorNotifyCallbackTokenResult |
MessageProcessorActorDedupeByCountResult | MessageProcessorActorDedupeByTimeResult | MessageProcessorActorDelayResult | MessageProcessorActorForkResult | MessageProcessorActorForkJoinResult |
MessageProcessorActorIssueCallbackTokenResult | MessageProcessorActorRegexExtractResult | MessageProcessorActorSplitResult | MessageProcessorActorFilterResult | MessageProcessorActorDownloadFileUrlResult | MessageProcessorActorDownloadFileAsBase64Result |
string | unknown;
```

## actorSchemas/task/messageProcessor/inject

**Source:** `actorSchemas/task/messageProcessor/inject.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { MessageProcessorAction } from './actions.js';

/** The options schema for the inject action in the MessageProcessorActor */
export const MessageProcessorActorInjectOptionsSchema = z.object({
  action: z.literal(MessageProcessorAction.Inject)
    .describe('Must be inject to access this function'),
  payload: z.any()
    .describe('The value to be the actors emit message'),
});

export type MessageProcessorActorInjectOptions = z.infer<typeof MessageProcessorActorInjectOptionsSchema>;

export const MessageProcessorActorInjectOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      const: MessageProcessorAction.Inject,
    },
    payload: {
      type: BIQJsonSchemaType.Any,
      title: 'Payload',
      description: 'The value to be the actors emit message',
      ui: {
        options: {
          editInModal: true,
        }
      }
    },
  },
  required: ['action', 'payload'],
};

/** The emitted message schema for the inject action in the MessageProcessorActor */
export const MessageProcessorActorInjectResultSchema = z.any().describe('The payload of the inject action');

export type MessageProcessorActorInjectResult = z.infer<typeof MessageProcessorActorInjectResultSchema>;
```

## actorSchemas/task/messageProcessor/issueCallbackToken

**Source:** `actorSchemas/task/messageProcessor/issueCallbackToken.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { MessageProcessorAction } from './actions.js';

/** The options schema for the issueCallbackToken action in the MessageProcessorActor */
export const MessageProcessorActorIssueCallbackTokenOptionsSchema = z.object({
  action: z.literal(MessageProcessorAction.IssueCallbackToken)
    .describe('Must be issueCallbackToken to access this function'),
  expiresAfterInSeconds: z.number().gt(0).nullish()
    .describe('How long the callback token should be valid for'),
  multipleResponse: z.boolean().nullish()
    .describe('If true, the callback token can be used to continue multiple Message Processor Actor with waitForCallbackToken action'),
});

export type MessageProcessorActorIssueCallbackTokenOptions = z.infer<typeof MessageProcessorActorIssueCallbackTokenOptionsSchema>;

export const MessageProcessorActorIssueCallbackTokenOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      const: MessageProcessorAction.IssueCallbackToken,
    },
    expiresAfterInSeconds: {
      type: BIQJsonSchemaType.Number,
      exclusiveMinimum: 0,
      title: 'Expires after in seconds',
      description: 'How long the callback token should be valid for',
    },
    multipleResponse: {
      type: BIQJsonSchemaType.Boolean,
      title: 'Multiple response',
      description: 'If true, the callback token can be used to continue multiple Message Processor Actor with waitForCallbackToken action',
      default: false,
      ui: {
        component: 'switch',
      },
    },
  },
  required: ['action'],
};

/** The emitted message schema for the issueCallbackToken action in the MessageProcessorActor */
export const MessageProcessorActorIssueCallbackTokenResultSchema = z.object({
  token: z.string()
    .describe('The generated callback token'),
  url: z.string()
    .describe('The URL to resolve the callback token'),
  expiresAt: z.string()
    .describe('The time the token would expire'),
  multipleResponse: z.boolean()
    .describe('If the token can be used to continue multiple Message Processor Actor with waitForCallbackToken action'),
});

export type MessageProcessorActorIssueCallbackTokenResult = z.infer<typeof MessageProcessorActorIssueCallbackTokenResultSchema>;
```

## actorSchemas/task/messageProcessor/notifyCallbackToken

**Source:** `actorSchemas/task/messageProcessor/notifyCallbackToken.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { MessageProcessorAction } from './actions.js';

/** The options schema for the notifyCallbackToken action in the MessageProcessorActor */
export const MessageProcessorActorNotifyCallbackTokenOptionsSchema = z.object({
  action: z.literal(MessageProcessorAction.NotifyCallbackToken)
    .describe('Must be notifyCallbackToken to access this function'),
  token: z.string().min(1)
    .describe('The token generated by the upstream Message Processor Actor with the issueCallbackToken that this actor would be notifying for'),
  payload: z.any()
    .refine((payload) => payload !== null && payload !== undefined, { message: 'Required' })
    .describe('The value to be notified for the token'),
});

export type MessageProcessorActorNotifyCallbackTokenOptions = z.infer<typeof MessageProcessorActorNotifyCallbackTokenOptionsSchema>;

export const MessageProcessorActorNotifyCallbackTokenOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      const: MessageProcessorAction.NotifyCallbackToken,
    },
    token: {
      type: BIQJsonSchemaType.String,
      minLength: 1,
      title: 'Token',
      description: 'The token generated by the upstream Message Processor Actor with the issueCallbackToken that this actor would be notifying for',
      default: '${{msg.ISSUE_CALLBACK_TOKEN.token}}',
    },
    payload: {
      type: BIQJsonSchemaType.Any,
      title: 'Payload',
      description: 'The value to be notified for the token',
      ui: {
        options: {
          editInModal: true,
        }
      }
    },
  },
  required: ['action', 'token', 'payload'],
};

export const MessageProcessorActorNotifyCallbackTokenResultSchema = z.unknown().describe('The payload of the callback token response');

export type MessageProcessorActorNotifyCallbackTokenResult = z.infer<typeof MessageProcessorActorNotifyCallbackTokenResultSchema>;
```

## actorSchemas/task/messageProcessor/regexExtract

**Source:** `actorSchemas/task/messageProcessor/regexExtract.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { MessageProcessorAction } from './actions.js';

/** The output schema of the regexExtract action in the MessageProcessorActor */
export const MessageProcessorActorRegexExtractOptionsSchema = z.object({
  action: z.literal(MessageProcessorAction.RegexExtract)
    .describe('Must be regexExtract to access this function'),
  rules: z.array(
    z.object({
      regex: z.string().refine((value) => {
        // make sure the regex is valid
        try {
          new RegExp(value);
          return true;
        } catch (_e) { // eslint-disable-line @typescript-eslint/no-unused-vars
          return false;
        }
      }, 'Invalid regex expression')
        .describe('The regex to run the value to extract, must be valid regex'),
      regexOptions: z.string().nullish()
        .describe('The optional flag for search options'),
      extractFrom: z.any()
        .describe('the value to run the regex against'),
      extractTo: z.string()
        .describe('The key to store the extracted value in the emitted message'),
    }),
  )
    .describe('The rules to extract data from the message'),
});

export type MessageProcessorActorRegexExtractOptions = z.infer<typeof MessageProcessorActorRegexExtractOptionsSchema>;

export const MessageProcessorActorRegexExtractOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      const: MessageProcessorAction.RegexExtract,
    },
    rules: {
      type: BIQJsonSchemaType.Array,
      title: 'Rules',
      description: 'The rules to extract data from the message',
      items: {
        type: BIQJsonSchemaType.Object,
        properties: {
          regex: {
            type: BIQJsonSchemaType.String,
            title: 'Regex',
            description: 'The regex to run the value to extract, must be valid regex',
            ui: {
              options: {
                placeholder: '/[A-Z]+/',
              },
            },
          },
          regexOptions: {
            type: BIQJsonSchemaType.String,
            title: 'Regex options',
            description: 'The optional flag for search options',
            ui: {
              options: {
                placeholder: 'g',
              },
            },
          },
          extractFrom: {
            type: BIQJsonSchemaType.Any,
            title: 'Extract from',
            description: 'the value to run the regex against',
          },
          extractTo: {
            type: BIQJsonSchemaType.String,
            title: 'Extract to',
            description: 'The key to store the extracted value in the emitted message',
          },
        },
        required: ['regex', 'extractFrom', 'extractTo'],
      },
    },
  },
  required: ['action', 'rules'],
};

/** The message schema for the regexExtract action in the MessageProcessorActor */
/** is the keys of the message is the `extractTo` keys provided by the rules */
export const MessageProcessorActorRegexExtractResultSchema = z.record(z.string(),
  z.array(z.string())
    .describe('The array of strings extracted when running the rule'),
);

export type MessageProcessorActorRegexExtractResult = z.infer<typeof MessageProcessorActorRegexExtractResultSchema>;
```

## actorSchemas/task/messageProcessor/renderTemplate

**Source:** `actorSchemas/task/messageProcessor/renderTemplate.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { MessageProcessorAction } from './actions.js';

/** The options schema for the renderTemplate action in the MessageProcessorActor */
export const MessageProcessorActorRenderTemplateOptionsSchema = z.object({
  action: z.literal(MessageProcessorAction.RenderTemplate)
    .describe('Must be renderTemplate to access this function'),
  template: z.string().min(1)
    .describe('The template to render using LiquidJs, it will use the actors inputs for the args'),
});

export type MessageProcessorActorRenderTemplateOptions = z.infer<typeof MessageProcessorActorRenderTemplateOptionsSchema>;

export const MessageProcessorActorRenderTemplateOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      const: MessageProcessorAction.RenderTemplate,
    },
    template: {
      type: BIQJsonSchemaType.String,
      minLength: 1,
      title: 'Template',
      description: 'The template to render using LiquidJs, it will use the actors inputs for the args',
      ui: {
        component: 'code',
        options: {
          editInModal: true,
          minLines: 3,
          maxLines: 10,
          autoResize: true,
          placeholder: 'Hello {{ inputs.name }}',
        }
      }

    },
  },
  required: ['action', 'template'],
};

/** The result schema for the renderTemplate action in the MessageProcessorActor */
export const MessageProcessorActorRenderTemplateResultSchema = z.string().describe('The rendered template');

export type MessageProcessorActorRenderTemplateResult = z.infer<typeof MessageProcessorActorRenderTemplateResultSchema>;
```

## actorSchemas/task/messageProcessor/split

**Source:** `actorSchemas/task/messageProcessor/split.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { MessageProcessorAction } from './actions.js';

/** The options schema for the split action in the MessageProcessorActor */
export const MessageProcessorActorSplitOptionsSchema = z.object({
  action: z.literal(MessageProcessorAction.Split)
    .describe('Must be split to access this function'),
  valueToSplit: z.array(z.unknown())
    .describe('The value to split'),
  emitKey: z.string().nullish()
    .describe('the key for the split values to be send under in the emitted message'),
  limit: z.number().nullish()
    .describe('The limit for the maximum number of messages that will be emitted, defaults to 1000'),
});

export type MessageProcessorActorSplitOptions = z.infer<typeof MessageProcessorActorSplitOptionsSchema>;

export const MessageProcessorActorSplitOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      const: MessageProcessorAction.Split,
    },
    valueToSplit: {
      type: BIQJsonSchemaType.Array,
      title: 'Value to split',
      description: 'The value to split',
      default: '${{}}',
      items: {
        type: BIQJsonSchemaType.Any,
      },
    },
    emitKey: {
      type: BIQJsonSchemaType.String,
      title: 'Emit key',
      description: 'The key for the split values to be send under in the emitted message',
      default: 'item',
    },
    limit: {
      type: BIQJsonSchemaType.Number,
      title: 'Limit',
      description: 'The limit for the maximum number of messages that will be emitted, defaults to 1000',
    },
  },
  required: ['action', 'valueToSplit'],
};

/** The emitted message schema for the split action in the MessageProcessorActor */
export const MessageProcessorActorSplitResultSchema = z.object({
  splitId: z.string()
    .describe('the id of the split action to be used in future Message Processor Actor with collect action, will be the same for all the emitted messages from the same array'),
  index: z.number()
    .describe('The index of the split value from the original array'),
  size: z.number()
    .describe('the total size of the array'),
});

export type MessageProcessorActorSplitResult = z.infer<typeof MessageProcessorActorSplitResultSchema> & { [key: string]: unknown };
```

## actorSchemas/task/messageProcessor/waitForCallbackToken

**Source:** `actorSchemas/task/messageProcessor/waitForCallbackToken.ts`

```typescript
import { z } from 'zod';

import { BIQJsonSchema, BIQJsonSchemaType } from '../../../schemas/index.js';

import { MessageProcessorAction } from './actions.js';

/** The options schema for the waitForCallbackToken action in the MessageProcessorActor */
export const MessageProcessorActorWaitForCallbackTokenOptionsSchema = z.object({
  action: z.literal(MessageProcessorAction.WaitForCallbackToken)
    .describe('Must be waitForCallbackToken to access this function'),
  token: z.string().min(1)
    .describe('The token generated by the upstream Message Processor Actor with the issueCallbackToken that this actor would be waiting for'),
  timeoutInSeconds: z.number().gt(0)
    .describe('How long the actor should wait for a callback token response before timing out'),
});

export type MessageProcessorActorWaitForCallbackTokenOptions = z.infer<typeof MessageProcessorActorWaitForCallbackTokenOptionsSchema>;

export const MessageProcessorActorWaitForCallbackTokenOptionsJsonSchema: BIQJsonSchema = {
  properties: {
    action: {
      type: BIQJsonSchemaType.String,
      const: MessageProcessorAction.WaitForCallbackToken,
    },
    token: {
      type: BIQJsonSchemaType.String,
      minLength: 1,
      title: 'Token',
      description: 'The token generated by the upstream Message Processor Actor with the issueCallbackToken that this actor would be waiting for',
      default: '${{msg.ISSUE_CALLBACK_TOKEN.token}}',
    },
    timeoutInSeconds: {
      type: BIQJsonSchemaType.Number,
      exclusiveMinimum: 0,
      title: 'Timeout in seconds',
      description: 'How long the actor should wait for a callback token response before timing out',
    },
  },
  required: ['action', 'token', 'timeoutInSeconds'],
};

export const MessageProcessorActorWaitForCallbackTokenResultSchema = z.unknown().describe('The body of the callback token response');

export type MessageProcessorActorWaitForCallbackTokenResult = z.infer<typeof MessageProcessorActorWaitForCallbackTokenResultSchema>;
```
