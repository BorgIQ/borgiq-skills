# actorSchemas/task/messageProcessor/index

Generated from the platform's runtime types. Do not edit.

MessageProcessorActor options, a discriminated union on `action`, and its result types.

See also: [actorSchemas/task/messageProcessor/collect](collect.md), [actorSchemas/task/messageProcessor/dedupeByCount](dedupeByCount.md), [actorSchemas/task/messageProcessor/dedupeByTime](dedupeByTime.md), [actorSchemas/task/messageProcessor/fork](fork.md), [actorSchemas/task/messageProcessor/forkJoin](forkJoin.md), [actorSchemas/task/messageProcessor/inject](inject.md), [actorSchemas/task/messageProcessor/issueCallbackToken](issueCallbackToken.md), [actorSchemas/task/messageProcessor/notifyCallbackToken](notifyCallbackToken.md), [actorSchemas/task/messageProcessor/regexExtract](regexExtract.md), [actorSchemas/task/messageProcessor/split](split.md), [actorSchemas/task/messageProcessor/waitForCallbackToken](waitForCallbackToken.md), [actorSchemas/task/messageProcessor/renderTemplate](renderTemplate.md), [actorSchemas/task/messageProcessor/delayBySeconds](delayBySeconds.md), [actorSchemas/task/messageProcessor/delayUntil](delayUntil.md), [actorSchemas/task/messageProcessor/filter](filter.md), [actorSchemas/task/messageProcessor/downloadFileUrl](downloadFileUrl.md), [actorSchemas/task/messageProcessor/downloadFileAsBase64](downloadFileAsBase64.md), [actorSchemas/task/messageProcessor/actions](actions.md).

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
