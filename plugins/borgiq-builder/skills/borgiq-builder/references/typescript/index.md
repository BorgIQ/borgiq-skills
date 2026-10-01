# TypeScript type references

Generated from the platform's runtime types. Do not edit.

Exact option, result and shared types, one file per platform source module: `actorSchemas/task/aiAgent.ts` is [actorSchemas/task/aiAgent.md](actorSchemas/task/aiAgent.md). Find the need below and read only the files it names. Each file opens with a one-line summary and links the modules it imports.

| Need | Read |
|---|---|
| AiAgentActor options, tools, MCP servers, sessions, compaction | [actorSchemas/task/aiAgent.md](actorSchemas/task/aiAgent.md) |
| AgentHarnessActor options, models per harness, MCP servers | [actorSchemas/task/agentHarness.md](actorSchemas/task/agentHarness.md) |
| AgentHarnessActor Status port updates | [sandbox.md](sandbox.md) |
| AiActor options and result | [actorSchemas/task/ai.md](actorSchemas/task/ai.md) |
| AiRouterActor | [actorSchemas/task/aiRouter.md](actorSchemas/task/aiRouter.md) |
| McpServerActor | [actorSchemas/task/mcpServer.md](actorSchemas/task/mcpServer.md) |
| Model references (`<slug>/<model-id>`), custom providers | [ai/modelRef.md](ai/modelRef.md) + [ai/lib.md](ai/lib.md) |
| Model ids and prices of one provider | [ai/anthropic.md](ai/anthropic.md) + [ai/openAi.md](ai/openAi.md) + [ai/google.md](ai/google.md) + [ai/xAi.md](ai/xAi.md) — read the one you need |
| AI messages, thinking levels | [ai/index.md](ai/index.md) |
| DenoActor | [actorSchemas/task/deno.md](actorSchemas/task/deno.md) + [actorSchemas/codeDir.md](actorSchemas/codeDir.md) |
| DenoTestActor | [actorSchemas/task/denoTest.md](actorSchemas/task/denoTest.md) + [actorSchemas/codeDir.md](actorSchemas/codeDir.md) |
| PythonActor | [actorSchemas/task/python.md](actorSchemas/task/python.md) + [actorSchemas/codeDir.md](actorSchemas/codeDir.md) |
| UniversalTriggerActor and the `TriggerEvent` it receives | [actorSchemas/trigger/universalTrigger.md](actorSchemas/trigger/universalTrigger.md) + [actorSchemas/trigger/triggerConfig.md](actorSchemas/trigger/triggerConfig.md) + [schemas/trigger.md](schemas/trigger.md) |
| Code-actor source files (`codeDir`): limits, entrypoints, reserved paths | [actorSchemas/codeDir.md](actorSchemas/codeDir.md) |
| HttpRequestActor options and result | [actorSchemas/task/httpRequest/index.md](actorSchemas/task/httpRequest/index.md) |
| HTTP and connection auth (`auth: { type, values }`) | [schemas/connection.md](schemas/connection.md) + [connection.md](connection.md) |
| RouterActor | [actorSchemas/task/router.md](actorSchemas/task/router.md) |
| Sub-flows: CallFlowActor, CallableTriggerActor, CallableResponseActor | [actorSchemas/task/callFlow.md](actorSchemas/task/callFlow.md) + [actorSchemas/trigger/callable.md](actorSchemas/trigger/callable.md) + [actorSchemas/task/callableResponse.md](actorSchemas/task/callableResponse.md) |
| WebhookTriggerActor | [actorSchemas/trigger/webhook.md](actorSchemas/trigger/webhook.md) + [actorSchemas/trigger/triggerConfig.md](actorSchemas/trigger/triggerConfig.md) |
| WebhookResponseActor | [actorSchemas/task/webhookResponse.md](actorSchemas/task/webhookResponse.md) |
| ScheduledTriggerActor | [actorSchemas/trigger/scheduled.md](actorSchemas/trigger/scheduled.md) + [actorSchemas/trigger/triggerConfig.md](actorSchemas/trigger/triggerConfig.md) |
| EmailTriggerActor message | [actorSchemas/trigger/email.md](actorSchemas/trigger/email.md) |
| ButtonTriggerActor | [actorSchemas/trigger/button.md](actorSchemas/trigger/button.md) |
| SendEmailActor | [actorSchemas/task/sendEmail.md](actorSchemas/task/sendEmail.md) |
| InterfaceTriggerActor (a form page) | [actorSchemas/trigger/interface.md](actorSchemas/trigger/interface.md) + [schemas/interface.md](schemas/interface.md) |
| InterfaceActor (a page mid-flow), InterfaceStatusActor | [actorSchemas/task/interface.md](actorSchemas/task/interface.md) + [actorSchemas/task/interfaceStatus.md](actorSchemas/task/interfaceStatus.md) + [schemas/interface.md](schemas/interface.md) |
| Form component *T* | `formComponents/<group>/<T>.md` + [formComponents/base.md](formComponents/base.md) — nested groups (array, section, collapse, union): `formComponents/form.md` |
| ReactAppTriggerActor options, endpoints, stream grants, CSP | [actorSchemas/trigger/reactApp.md](actorSchemas/trigger/reactApp.md) + [actorSchemas/trigger/permissionsPolicy.md](actorSchemas/trigger/permissionsPolicy.md) |
| AppTriggerActor (legacy raw-HTML app) | [actorSchemas/trigger/app.md](actorSchemas/trigger/app.md) + [actorSchemas/trigger/permissionsPolicy.md](actorSchemas/trigger/permissionsPolicy.md) |
| CollectionActor action *A* | `actorSchemas/task/collection/<action>.md` (batchGetItem, batchWriteItem, createCollection, deleteCollection, deleteItem, getItem, listCollections, putItem, query, transactGet, transactWrite, updateCollection, updateItem) + [actorSchemas/task/collection/actions.md](actorSchemas/task/collection/actions.md) + [actorSchemas/task/collection/index.md](actorSchemas/task/collection/index.md) |
| Collection label slots | [actorSchemas/task/collection/labelSlots.md](actorSchemas/task/collection/labelSlots.md) |
| StreamActor action *A* | `actorSchemas/task/stream/<action>.md` (appendData, createStream, deleteStream, editMetadata, getStreamInfo, listStreams, readStream) + [actorSchemas/task/stream/actions.md](actorSchemas/task/stream/actions.md) + [actorSchemas/task/stream/index.md](actorSchemas/task/stream/index.md) |
| Stream limits; the stream summary management actions return | [actorSchemas/task/stream/limits.md](actorSchemas/task/stream/limits.md) + [actorSchemas/task/stream/summary.md](actorSchemas/task/stream/summary.md) |
| MessageProcessorActor action *A* | `actorSchemas/task/messageProcessor/<action>.md` (collect, dedupeByCount, dedupeByTime, delayBySeconds, delayUntil, downloadFileAsBase64, downloadFileUrl, filter, fork, forkJoin, inject, issueCallbackToken, notifyCallbackToken, regexExtract, renderTemplate, split, waitForCallbackToken) + [actorSchemas/task/messageProcessor/actions.md](actorSchemas/task/messageProcessor/actions.md) + [actorSchemas/task/messageProcessor/index.md](actorSchemas/task/messageProcessor/index.md) |
| CommentActor | [actorSchemas/other/comment.md](actorSchemas/other/comment.md) |
| EchoActor (debugging) | [actorSchemas/other/echo.md](actorSchemas/other/echo.md) |
| `ctx` | [schemas/ctx.md](schemas/ctx.md) |
| `$.msg` and trigger payloads | [schemas/runtime.md](schemas/runtime.md) |
| Error handling (`if`, `retryIf`, `message`, `includeResult`) | [schemas/error.md](schemas/error.md) |
| Files (`BIQFile`) | [schemas/file.md](schemas/file.md) |
| Ids and id prefixes | [schemas/idSchema.md](schemas/idSchema.md) + [prefix.md](prefix.md) |
| Actor type names, webhook authorization levels, default ports | [canvas.md](canvas.md) |

## All files

- `(top level)`: canvas, connection, prefix, sandbox
- `actorSchemas/`: codeDir
- `actorSchemas/other/`: comment, echo
- `actorSchemas/task/`: agentHarness, ai, aiAgent, aiRouter, callableResponse, callFlow, deno, denoTest, interface, interfaceStatus, mcpServer, python, router, sendEmail, webhookResponse
- `actorSchemas/task/collection/`: actions, batchGetItem, batchWriteItem, createCollection, deleteCollection, deleteItem, getItem, index, labelSlots, listCollections, putItem, query, transactGet, transactWrite, updateCollection, updateItem
- `actorSchemas/task/httpRequest/`: index
- `actorSchemas/task/messageProcessor/`: actions, collect, dedupeByCount, dedupeByTime, delayBySeconds, delayUntil, downloadFileAsBase64, downloadFileUrl, filter, fork, forkJoin, index, inject, issueCallbackToken, notifyCallbackToken, regexExtract, renderTemplate, split, waitForCallbackToken
- `actorSchemas/task/stream/`: actions, appendData, createStream, deleteStream, editMetadata, getStreamInfo, index, limits, listStreams, readStream, summary
- `actorSchemas/trigger/`: app, button, callable, email, interface, permissionsPolicy, reactApp, scheduled, triggerConfig, universalTrigger, webhook
- `ai/`: anthropic, google, index, lib, modelRef, openAi, xAi
- `formComponents/`: base, form
- `formComponents/any/`: codeInput, modal
- `formComponents/array/`: multiCheckbox, multiSelect, table
- `formComponents/boolean/`: checkbox, switch
- `formComponents/date/`: calendar, calendarRange, date, dateRange, dateTime, dateValue, time
- `formComponents/display/`: code, divider, fileDownload, formButton, header, image, markdown, pdf, progress, textDisplay, urlButton, webViewer
- `formComponents/file/`: audioRecording, fileButton, fileDropzone, fileInput
- `formComponents/number/`: currency, number, percentage, rating, slider
- `formComponents/string/`: buttonGroup, code, codeDiff, markdown, password, phoneNumber, pin, radio, select, suggest, text, textArea
- `schemas/`: connection, ctx, error, file, idSchema, interface, runtime, trigger

Not listed: internal modules that only carry formats between platform services (an import from one names a type you never write), and `legacy/`, which holds the types of legacy actors and the editor's option-form dialect; only the notes on those legacy actors link into it.
