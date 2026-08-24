# Email Send and Reply Workflow Example

This example demonstrates a complex workflow that sends an email via Gmail and waits for a reply (or timeout). It showcases multiple actor types working together: triggers, sub-flows, callback tokens, data storage, and routing.

## Table of Contents

- [Overview](#overview)
- [Architecture Diagram](#architecture-diagram)
- [Key Patterns Demonstrated](#key-patterns-demonstrated)
- [Complete Canvas YAML](#complete-canvas-yaml)
- [Actor Types Used](#actor-types-used)
- [Key Takeaways](#key-takeaways)

## Overview

The workflow consists of two interconnected flows:

1. **Main Flow** - Calls the sub-flow to send an email and handles the response
2. **Sub-Flow** - Sends the email, stores callback tokens, and waits for replies

Additionally, a **Polling Flow** runs every minute to detect new emails and notify waiting workflows.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              MAIN FLOW                                       │
│  ┌─────────────────┐    ┌──────────────────────┐    ┌──────────────────┐    │
│  │ CallFlowActor   │───▶│ Router (Reply)       │───▶│ DO WORK AFTER    │    │
│  │ Send Email and  │    │ - After Sending      │    │ SENDING          │    │
│  │ Handle Replies  │    │ - Reply Received     │    │                  │    │
│  └─────────────────┘    │ - Others             │    │ or AFTER REPLY   │    │
│                         └──────────────────────┘    └──────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                          SUB-FLOW (Email Send + Wait)                        │
│                                                                              │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────────┐   │
│  │CallableTrigger   │───▶│ Issue Wait Token │───▶│ Gmail: Send Email    │   │
│  │Actor             │    │ (MessageProcessor)│   │ (HttpRequestActor)   │   │
│  └──────────────────┘    └──────────────────┘    └──────────┬───────────┘   │
│                                                              │               │
│                    ┌─────────────────────────────────────────┴───────────┐   │
│                    │                                                     │   │
│                    ▼                                                     ▼   │
│  ┌──────────────────────────┐                  ┌─────────────────────────┐   │
│  │ Respond with Sent Status │                  │ Handle Reply Router     │   │
│  │ (CallableResponseActor)  │                  │ - Handle replies: yes   │   │
│  └──────────────────────────┘                  │ - Ignore               │   │
│                                                └───────────┬─────────────┘   │
│                                                            │                 │
│                                                            ▼                 │
│                                   ┌────────────────────────────────────────┐ │
│                                   │ Store Message ID and Thread ID        │ │
│                                   │ with Callback Token (CollectionActor) │ │
│                                   └───────────────────┬────────────────────┘ │
│                                                       │                      │
│                                                       ▼                      │
│                                   ┌────────────────────────────────────────┐ │
│                                   │ Wait for Event                         │ │
│                                   │ (waitForCallbackToken, 7 days timeout) │ │
│                                   └───────────────────┬────────────────────┘ │
│                                                       │                      │
│                                                       ▼                      │
│                                   ┌────────────────────────────────────────┐ │
│                                   │ Router                                 │ │
│                                   │ - Reply Received?                      │ │
│                                   │ - Wait Cancelled                       │ │
│                                   │ - Timeout                              │ │
│                                   └───────────────────┬────────────────────┘ │
│                                                       │                      │
│                              ┌────────────────────────┴────────────────┐     │
│                              ▼                                         ▼     │
│              ┌──────────────────────────┐        ┌──────────────────────┐    │
│              │ Respond with Reply Msg   │        │ Respond with Timeout │    │
│              │ (status: reply)          │        │ (status: timeout)    │    │
│              └──────────────────────────┘        └──────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                          POLLING FLOW (Email Monitor)                        │
│                                                                              │
│  ┌──────────────────┐    ┌──────────────────────┐    ┌──────────────────┐   │
│  │ScheduledTrigger  │───▶│ Gmail: Trigger on    │───▶│ Check for any    │   │
│  │ Every Minute     │    │ new emails (Deno)    │    │ Callback Token   │   │
│  └──────────────────┘    │ Uses LTM for         │    │(CollectionActor) │   │
│                          │ historyId tracking   │    └────────┬─────────┘   │
│                          └──────────────────────┘             │              │
│                                                               ▼              │
│                                   ┌────────────────────────────────────────┐ │
│                                   │ If Found? Router                       │ │
│                                   │ - Token Found: notify waiting flow     │ │
│                                   │ - No Tokens: ignore                    │ │
│                                   └───────────────────┬────────────────────┘ │
│                                                       │                      │
│                                                       ▼                      │
│                                   ┌────────────────────────────────────────┐ │
│                                   │ Notify Waiting Token for Reply         │ │
│                                   │ (notifyCallbackToken)                  │ │
│                                   └────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Key Patterns Demonstrated

### 1. Callback Token Pattern (Human-in-the-Loop)

The workflow uses `issueCallbackToken` and `waitForCallbackToken` to pause execution until an external event occurs:

```yaml
# Issue a callback token before sending the email
ACTR01jn59bxebpqetm28j8ev936r2:
  type: MessageProcessorActor
  msgVar: issue_wait_token
  configuration:
    options:
      action: issueCallbackToken

# Wait for the token to be notified (up to 7 days)
ACTR01jn59bxebpqetm28j8ev936r3:
  type: MessageProcessorActor
  msgVar: wait_for_event
  continueOnError: true  # Important: handle timeout gracefully
  configuration:
    options:
      action: waitForCallbackToken
      token: ${{msg.issue_wait_token.token}}
      timeoutInSeconds: ${{60*60*24*7}}  # 7 days
```

### 2. CollectionActor for Token Lookup

The workflow stores the callback token in a `callback-tokens` collection keyed by Gmail thread ID, enabling the polling flow to find and notify the correct waiting workflow:

```yaml
# Store token with thread ID as key
ACTR01jn59bxebpqetm28j8ev936r1:
  type: CollectionActor
  msgVar: store_message_id_and_thread_id_with_callback_token
  configuration:
    options:
      action: putItem
      collection: callback-tokens
      key: gmail-${{ msg.gmail_send_email.body.threadId }}
      value:
        token: ${{ msg.issue_wait_token.token }}
        createdAt: ${{ Q.now() }}

# Look up token by thread ID when new email arrives
ACTR01jn59bxebpqetm28j8ev936r6:
  type: CollectionActor
  msgVar: check_for_any_callback_token
  configuration:
    options:
      action: getItem
      collection: callback-tokens
      key: gmail-${{ msg.gmail_trigger_on_new_emails.threadId}}
```

### 3. DenoActor with LTM for Incremental Polling

The Gmail polling actor uses Long-Term Memory (LTM) to track the last processed `historyId`, ensuring only new emails are detected:

```yaml
ACTR01jn59bxebpqetm28j8ev936r9:
  type: DenoActor
  msgVar: gmail_trigger_on_new_emails
  enableLTM: true  # Persist historyId across flowruns
  configuration:
    codeDir:
      - path: main.ts
        content: |
          import _ from "npm:lodash@4.17.21";
          import type { Request, Response } from "@borgiq/actors";

          export default async function receive(req: Request): Promise<Response> {
            // Read the whole ltm half from incoming memory
            const ltm = req.memory.ltm ?? {};
            const storedHistoryId = ltm.historyId;

            // If first run, initialize and return empty (persist the new historyId)
            if (!storedHistoryId) {
              const profile = await fetch("...").then(r => r.json());
              ltm.historyId = profile.historyId;
              return { results: [], memory: { ltm } };   // return only the ltm half
            }

            // Fetch history since last check
            const data = await fetch(`...?startHistoryId=${storedHistoryId}`).then(r => r.json());

            // Persist historyId for next run, emit new messages (excluding sent emails)
            ltm.historyId = data.historyId;
            return {
              results: messages.filter(m => !m.labelIds?.includes("SENT")),
              memory: { ltm },
            };
          }
    options:
      emitArrayAsSingleMessage: false  # Emit each message separately
      allowNet: true
```

### 4. Sub-Flow Invocation with CallFlowActor

The main flow invokes the email-sending sub-flow and waits for a response:

```yaml
ACTR01jn59bxebpqetm28j8ev936qy:
  type: CallFlowActor
  msgVar: send_email_and_handle_replies
  configuration:
    options:
      callableTriggerActorId: ACTR01jn59bxeav3vwgxtm098wbg9m
      waitForResponse: true
      payload:
        handleReplies: true
        from: sender@example.com
        to: recipient@example.com
        subject: Test Email
        body: |
          Hi there,
          Have a great day!
      flowSlug: system-flow-gmail-send-email-and-handle-replies
      timeoutInSeconds: 3600
```

### 5. Multiple CallableResponseActors

The sub-flow returns different responses at different points:

```yaml
# Immediate response after sending (status: sent)
ACTR01jn59bxebpqetm28j8ev936qz:
  type: CallableResponseActor
  msgVar: respond_with_sent_status
  configuration:
    options:
      payload:
        status: sent
        replyToken: ${{ msg.issue_wait_token.token }}
        body: ${{ msg.gmail_send_email.body }}

# Response when reply received (status: reply)
ACTR01jn59bxebpqetm28j8ev936r5:
  type: CallableResponseActor
  msgVar: respond_with_reply_message
  configuration:
    options:
      payload:
        status: reply
        threadId: ${{ msg.gmail_send_email.body.threadId }}

# Response on timeout (status: timeout)
ACTR01jy4z0r7ygs5crhv3kc64x75s:
  type: CallableResponseActor
  msgVar: respond_with_reply_message
  configuration:
    options:
      payload:
        status: timeout
        threadId: ${{ msg.gmail_send_email.body.threadId }}
```

### 6. Error Handling with continueOnError

The `waitForCallbackToken` actor uses `continueOnError: true` to handle timeout gracefully:

```yaml
ACTR01jn59bxebpqetm28j8ev936r3:
  continueOnError: true  # Don't fail the workflow on timeout
  # ...

# Downstream router checks for timeout error
ACTR01jn59bxebpqetm28j8ev936r4:
  type: RouterActor
  configuration:
    options:
      conditions:
        Reply Received?: ${{Q.isEqual(msg.wait_for_event?.response, "reply")}}
        Wait Cancelled: ${{Q.isEqual(msg.wait_for_event?.response, "cancelled")}}
        Timeout: ${{Q.isEqual(err.wait_for_event?.name, "TimeoutError")}}
```

## Complete Canvas YAML

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  ACTR01jn59rgp3cakakd5a3hsmwmr3:
    name: Comment
    type: CommentActor
    msgVar: comment
    schemas: {}
    version: 1
    isActive: true
    enableLTM: false
    enableSTM: false
    description: '## Copy These Actors and Use it in your Flows ---->>>'
    runtimeSlug: ''
    sourcePorts: []
    configuration:
      options:
        width: 510px
        height: 115px
        bgColor: '#ffe066'
        textColor: black
    continueOnError: false
    id: ACTR01jn59rgp3cakakd5a3hsmwmr3
    position:
      x: 2342.207573084814
      'y': 69.71541192131558
    edges: {}
  ACTR01jpskpc493pyaf8mmgby52sw5:
    name: Comment
    type: CommentActor
    msgVar: comment
    schemas: {}
    version: 1
    isActive: true
    enableLTM: false
    enableSTM: false
    description: '# TODO: Support for Monitoring Multiple Inboxes (via Connection ID)'
    runtimeSlug: ''
    sourcePorts: []
    configuration:
      options:
        width: 510px
        height: 115px
        bgColor: '#ffe066'
        textColor: black
    continueOnError: false
    id: ACTR01jpskpc493pyaf8mmgby52sw5
    position:
      x: 31.62238290072543
      'y': -286.597564751664
    edges: {}
  ACTR01jn59bxeav3vwgxtm098wbg9m:
    icon:
      type: borgiq
      value: >-
        160ac19845:google-gmail
    name: Send Email and Handle Replies Trigger
    type: CallableTriggerActor
    msgVar: send_email_and_handle_replies_trigger
    schemas: {}
    version: 1
    isActive: true
    enableLTM: false
    enableSTM: false
    description: >-
      When a parent flow invokes a sub flow, the Callable Trigger actor will be
      invoked.
    runtimeSlug: ''
    sourcePorts:
      - id: SPRTdefault
    configuration:
      options: {}
    continueOnError: false
    id: ACTR01jn59bxeav3vwgxtm098wbg9m
    position:
      x: 1073.894942265701
      'y': 64.4102715103478
    edges:
      EDGE01jn59bxebpqetm28j8ev936rb:
        id: EDGE01jn59bxebpqetm28j8ev936rb
        sourceActorId: ACTR01jn59bxeav3vwgxtm098wbg9m
        sourcePortId: SPRTdefault
        targetActorId: ACTR01jn59bxebpqetm28j8ev936r2
        targetPortId: TPRTdefault
        label: ''
        type: borgiqEdge
  ACTR01jn59bxebpqetm28j8ev936qx:
    icon:
      type: borgiq
      value: >-
        160ac19845:google-gmail
    name: 'Gmail: Send email'
    type: HttpRequestActor
    msgVar: gmail_send_email
    schemas: {}
    version: 1
    isActive: true
    enableLTM: false
    enableSTM: false
    description: The HTTP Request Actor can make HTTP requests
    runtimeSlug: ''
    sourcePorts:
      - id: SPRTdefault
    configuration:
      vars:
        - emailContent:
            - 'From: ${{ inputs.from }}'
            - 'To: ${{inputs.to }}'
            - 'Subject: ${{inputs.subject}}'
            - 'Content-Type: text/plain; charset="UTF-8"'
            - ''
            - ${{inputs.body}}
        - base64Message: ${{ Q.toBase64(vars.emailContent.join('\r\n')) }}
      inputs: >-
        ${{ Q.lo.pick(msg.send_email_and_handle_replies_trigger, ['from', 'to',
        'subject', 'body']) }}
      options:
        url: https://gmail.googleapis.com/gmail/v1/users/me/messages/send
        method: POST
        headers:
          Content-Type: application/json; charset=UTF-8
        auth: ${{connection.auth}}
        body:
          raw: ${{ vars.base64Message }}
      connection:
        type: gmail
        key: my-gmail-connection
    continueOnError: false
    id: ACTR01jn59bxebpqetm28j8ev936qx
    position:
      x: 1073.44185283659
      'y': 549.5962961643365
    edges:
      EDGE01jn59bxebpqetm28j8ev936rc:
        id: EDGE01jn59bxebpqetm28j8ev936rc
        sourceActorId: ACTR01jn59bxebpqetm28j8ev936qx
        sourcePortId: SPRTdefault
        targetActorId: ACTR01jn59bxebpqetm28j8ev936qz
        targetPortId: TPRTdefault
        label: ''
        type: borgiqEdge
      EDGE01jn59bxebpqetm28j8ev936rd:
        id: EDGE01jn59bxebpqetm28j8ev936rd
        sourceActorId: ACTR01jn59bxebpqetm28j8ev936qx
        sourcePortId: SPRTdefault
        targetActorId: ACTR01jn59bxebpqetm28j8ev936r0
        targetPortId: TPRTdefault
        label: ''
        type: borgiqEdge
  ACTR01jn59bxebpqetm28j8ev936qy:
    icon:
      type: borgiq
      value: >-
        160ac19845:google-gmail
    name: Send Email and Handle Replies
    type: CallFlowActor
    msgVar: send_email_and_handle_replies
    schemas: {}
    version: 1
    isActive: true
    enableLTM: false
    enableSTM: false
    description: >-
      This actor will call another Flow. It can wait for the callable response
      actor to emit message from the other flow or does not wait for the
      response from the callable response actor.
    runtimeSlug: ''
    sourcePorts:
      - id: SPRTdefault
    configuration:
      options:
        callableTriggerActorId: ACTR01jn59bxeav3vwgxtm098wbg9m
        waitForResponse: true
        payload:
          handleReplies: true
          from: alex@example.com
          to: alexp@example.com
          subject: Test Email from BorgIQ Integration!
          body: |
            Hi there,

            Have a great day

            Today is ${{ new Date() }}

            Flow is ${{ Q.toJSON(ctx) }}

            ----
            Alex Thompson
            CEO, Acme Corp
            Sent via BorgIQ
        flowSlug: system-flow-gmail-send-email-and-handle-replies
        timeoutInSeconds: 3600
    continueOnError: false
    id: ACTR01jn59bxebpqetm28j8ev936qy
    position:
      x: 2895.337957883925
      'y': 79.92371310126576
    edges:
      EDGE01jn59m1pt3csemjfh2v1c8jmk:
        id: EDGE01jn59m1pt3csemjfh2v1c8jmk
        sourceActorId: ACTR01jn59bxebpqetm28j8ev936qy
        sourcePortId: SPRTdefault
        targetActorId: ACTR01jn59m1psy4h3v3g9ak67cff8
        targetPortId: TPRTdefault
        label: ''
        type: borgiqEdge
  ACTR01jn59bxebpqetm28j8ev936qz:
    name: Respond with Sent Status
    type: CallableResponseActor
    msgVar: respond_with_sent_status
    schemas: {}
    version: 1
    isActive: true
    enableLTM: false
    enableSTM: false
    description: >-
      The Callable Response actor allows to send messages to the parent flows
      during sub flow invocation.
    runtimeSlug: ''
    sourcePorts:
      - id: SPRTdefault
    configuration:
      options:
        payload:
          status: sent
          replyToken: ${{ msg.issue_wait_token.token }}
          body: ${{ msg.gmail_send_email.body }}
    continueOnError: false
    id: ACTR01jn59bxebpqetm28j8ev936qz
    position:
      x: 721.1526746109794
      'y': 880.1707188794103
    edges: {}
  ACTR01jn59bxebpqetm28j8ev936r0:
    name: Handle Reply
    type: RouterActor
    msgVar: handle_reply
    schemas: {}
    version: 1
    isActive: true
    enableLTM: false
    enableSTM: false
    description: The router actor will emit messages based on various expressions.
    runtimeSlug: ''
    sourcePorts:
      - id: SPRT5d5gj2s
        name: Handle replies
        description: ''
      - id: SPRTdefault
        name: Ignore
        description: ''
    configuration:
      options:
        emitType: singleRoute
        conditions:
          Handle replies: >-
            ${{Q.isEqual(msg.send_email_and_handle_replies_trigger.handleReplies,
            true)}}
    continueOnError: false
    id: ACTR01jn59bxebpqetm28j8ev936r0
    position:
      x: 1356.37536733157
      'y': 882.7130961000554
    edges:
      EDGE01jn59bxec1ktzkn9bwnpqkcry:
        id: EDGE01jn59bxec1ktzkn9bwnpqkcry
        sourceActorId: ACTR01jn59bxebpqetm28j8ev936r0
        sourcePortId: SPRT5d5gj2s
        targetActorId: ACTR01jn59bxebpqetm28j8ev936r1
        targetPortId: TPRTdefault
        label: Handle replies
        type: borgiqEdge
  ACTR01jn59bxebpqetm28j8ev936r1:
    name: Store Message ID and Thread ID with Callback Token
    type: CollectionActor
    msgVar: store_message_id_and_thread_id_with_callback_token
    schemas: {}
    version: 1
    isActive: true
    enableLTM: false
    enableSTM: false
    description: Store callback token in collection keyed by Gmail thread ID for later retrieval when a reply arrives.
    runtimeSlug: ''
    sourcePorts:
      - id: SPRTdefault
    configuration:
      options:
        action: putItem
        collection: callback-tokens
        key: gmail-${{ msg.gmail_send_email.body.threadId }}
        value:
          token: ${{ msg.issue_wait_token.token }}
          createdAt: ${{ Q.now() }}
    continueOnError: false
    id: ACTR01jn59bxebpqetm28j8ev936r1
    position:
      x: 1362.23907130014
      'y': 1118.368454922316
    edges:
      EDGE01jn59bxec1ktzkn9bwnpqkcrz:
        id: EDGE01jn59bxec1ktzkn9bwnpqkcrz
        sourceActorId: ACTR01jn59bxebpqetm28j8ev936r1
        sourcePortId: SPRTdefault
        targetActorId: ACTR01jn59bxebpqetm28j8ev936r3
        targetPortId: TPRTdefault
        label: ''
        type: borgiqEdge
  ACTR01jn59bxebpqetm28j8ev936r2:
    name: Issue Wait Token
    type: MessageProcessorActor
    msgVar: issue_wait_token
    schemas: {}
    version: 1
    isActive: true
    enableLTM: false
    enableSTM: false
    description: >-
      The message processor actor can process incoming messages and emit the
      processed messages.
    runtimeSlug: ''
    sourcePorts:
      - id: SPRTdefault
    configuration:
      options:
        action: issueCallbackToken
      connection: {}
    continueOnError: false
    id: ACTR01jn59bxebpqetm28j8ev936r2
    position:
      x: 1071.278423827589
      'y': 311.9515206115894
    edges:
      EDGE01jn59bxec1ktzkn9bwnpqkcs0:
        id: EDGE01jn59bxec1ktzkn9bwnpqkcs0
        sourceActorId: ACTR01jn59bxebpqetm28j8ev936r2
        sourcePortId: SPRTdefault
        targetActorId: ACTR01jn59bxebpqetm28j8ev936qx
        targetPortId: TPRTdefault
        label: ''
        type: borgiqEdge
  ACTR01jn59bxebpqetm28j8ev936r3:
    icon:
      type: borgiq
      value: >-
        800a6c786f:hourglass-high
    name: Wait for Event
    type: MessageProcessorActor
    msgVar: wait_for_event
    schemas: {}
    version: 1
    isActive: true
    enableLTM: false
    enableSTM: false
    description: >-
      The message processor actor can process incoming messages and emit the
      processed messages.
    runtimeSlug: ''
    sourcePorts:
      - id: SPRTdefault
    configuration:
      options:
        action: waitForCallbackToken
        token: ${{msg.issue_wait_token.token}}
        timeoutInSeconds: ${{60*60*24*7}}
      connection: {}
    continueOnError: true
    id: ACTR01jn59bxebpqetm28j8ev936r3
    position:
      x: 1362.699129330171
      'y': 1357.066434405471
    edges:
      EDGE01jn59bxec1ktzkn9bwnpqkcs1:
        id: EDGE01jn59bxec1ktzkn9bwnpqkcs1
        sourceActorId: ACTR01jn59bxebpqetm28j8ev936r3
        sourcePortId: SPRTdefault
        targetActorId: ACTR01jn59bxebpqetm28j8ev936r4
        targetPortId: TPRTdefault
        label: ''
        type: borgiqEdge
  ACTR01jn59bxebpqetm28j8ev936r4:
    name: Router
    type: RouterActor
    msgVar: router
    schemas: {}
    version: 1
    isActive: true
    enableLTM: false
    enableSTM: false
    description: The router actor will emit messages based on various expressions.
    runtimeSlug: ''
    sourcePorts:
      - id: SPRT5d5gj2s
        name: Reply Received?
        description: Reply Received
      - id: SPRTn7bjifw
        name: Wait Cancelled
        description: Wait Cancelled
      - id: SPRTyxzg7c9
        name: Timeout
        description: Timeout
      - id: SPRTdefault
        name: Unknown
        description: Unknown
    configuration:
      options:
        emitType: singleRoute
        conditions:
          Reply Received?: ${{Q.isEqual(msg.wait_for_event?.response, "reply")}}
          Wait Cancelled: ${{Q.isEqual(msg.wait_for_event?.response, "cancelled")}}
          Timeout: ${{Q.isEqual(err.wait_for_event?.name, "TimeoutError")}}
    continueOnError: false
    id: ACTR01jn59bxebpqetm28j8ev936r4
    position:
      x: 1363.3047874727
      'y': 1606.882204720453
    edges:
      EDGE01jn59bxec1ktzkn9bwnpqkcs2:
        id: EDGE01jn59bxec1ktzkn9bwnpqkcs2
        sourceActorId: ACTR01jn59bxebpqetm28j8ev936r4
        sourcePortId: SPRT5d5gj2s
        targetActorId: ACTR01jn59bxebpqetm28j8ev936r5
        targetPortId: TPRTdefault
        label: Reply Received?
        type: borgiqEdge
      EDGE01jy4z3whb4bhkqzcr7g5nc0z9:
        id: EDGE01jy4z3whb4bhkqzcr7g5nc0z9
        sourceActorId: ACTR01jn59bxebpqetm28j8ev936r4
        sourcePortId: SPRTyxzg7c9
        targetActorId: ACTR01jy4z0r7ygs5crhv3kc64x75s
        targetPortId: TPRTdefault
        label: Timeout
        type: borgiqEdge
  ACTR01jn59bxebpqetm28j8ev936r5:
    name: Respond with Reply Message
    type: CallableResponseActor
    msgVar: respond_with_reply_message
    schemas: {}
    version: 1
    isActive: true
    enableLTM: false
    enableSTM: false
    description: >-
      The Callable Response actor allows to send messages to the parent flows
      during sub flow invocation.
    runtimeSlug: ''
    sourcePorts:
      - id: SPRTdefault
    configuration:
      options:
        payload:
          status: reply
          threadId: ${{ msg.gmail_send_email.body.threadId }}
    continueOnError: false
    id: ACTR01jn59bxebpqetm28j8ev936r5
    position:
      x: 846.2953492186527
      'y': 1907.413685258727
    edges: {}
  ACTR01jn59bxebpqetm28j8ev936r6:
    name: Check for any Callback Token
    type: CollectionActor
    msgVar: check_for_any_callback_token
    schemas: {}
    version: 1
    isActive: true
    enableLTM: false
    enableSTM: false
    description: Look up callback token from collection by Gmail thread ID.
    runtimeSlug: ''
    sourcePorts:
      - id: SPRTdefault
    configuration:
      options:
        action: getItem
        collection: callback-tokens
        key: gmail-${{ msg.gmail_trigger_on_new_emails.threadId}}
    continueOnError: false
    id: ACTR01jn59bxebpqetm28j8ev936r6
    position:
      x: -0.4468318204289972
      'y': 511.2858869594179
    edges:
      EDGE01jn59bxec1ktzkn9bwnpqkcs3:
        id: EDGE01jn59bxec1ktzkn9bwnpqkcs3
        sourceActorId: ACTR01jn59bxebpqetm28j8ev936r6
        sourcePortId: SPRTdefault
        targetActorId: ACTR01jn59bxebpqetm28j8ev936r7
        targetPortId: TPRTdefault
        label: ''
        type: borgiqEdge
  ACTR01jn59bxebpqetm28j8ev936r7:
    name: If Found?
    type: RouterActor
    msgVar: if_found
    schemas: {}
    version: 1
    isActive: true
    enableLTM: false
    enableSTM: false
    description: The router actor will emit messages based on various expressions.
    runtimeSlug: ''
    sourcePorts:
      - id: SPRT5d5gj2s
        name: Token Found
        description: ''
      - id: SPRTdefault
        name: No Tokens
        description: No Tokens
    configuration:
      options:
        emitType: singleRoute
        conditions:
          Token Found: ${{ !Q.isNil(msg.check_for_any_callback_token) }}
    continueOnError: false
    id: ACTR01jn59bxebpqetm28j8ev936r7
    position:
      x: -1.060314107624436
      'y': 750.9545346420668
    edges:
      EDGE01jn59bxec1ktzkn9bwnpqkcs4:
        id: EDGE01jn59bxec1ktzkn9bwnpqkcs4
        sourceActorId: ACTR01jn59bxebpqetm28j8ev936r7
        sourcePortId: SPRT5d5gj2s
        targetActorId: ACTR01jn59bxebpqetm28j8ev936r8
        targetPortId: TPRTdefault
        label: Token Found
        type: borgiqEdge
  ACTR01jn59bxebpqetm28j8ev936r8:
    name: Notify Waiting Token for Reply
    type: MessageProcessorActor
    msgVar: notify_waiting_token_for_reply
    schemas: {}
    version: 1
    isActive: true
    enableLTM: false
    enableSTM: false
    description: >-
      The message processor actor can process incoming messages and emit the
      processed messages.
    runtimeSlug: ''
    sourcePorts:
      - id: SPRTdefault
    configuration:
      options:
        action: notifyCallbackToken
        payload:
          response: reply
          threadId: ${{ msg.gmail_trigger_on_new_emails.threadId }}
        token: ${{ msg.check_for_any_callback_token.value.token }}
      connection: {}
    continueOnError: false
    id: ACTR01jn59bxebpqetm28j8ev936r8
    position:
      x: -2.575315075902836
      'y': 1032.604395804158
    edges: {}
  ACTR01jn59bxebpqetm28j8ev936r9:
    icon:
      type: borgiq
      value: >-
        160ac19845:google-gmail
    name: 'Gmail: Trigger on new emails'
    type: DenoActor
    msgVar: gmail_trigger_on_new_emails
    schemas: {}
    version: 1
    isActive: true
    enableLTM: true
    enableSTM: false
    description: >-
      The Deno actor will execute the javascript/typescript code that is given
      in the configuration.
    runtimeSlug: ''
    sourcePorts:
      - id: SPRTdefault
    configuration:
      codeDir:
        - path: main.ts
          content: |
            import _ from "npm:lodash@4.17.21";

            import type { Request, Response } from "@borgiq/actors";


            export default async function receive(req: Request): Promise<Response> {
              // Get the stored historyId from incoming LTM
              const storedHistoryId = _.get(req.memory.ltm, "historyId");

              // If no historyId exists, initialize it
              if (!storedHistoryId) {
                // Fetch user's profile to get initial historyId
                const profileResponse = await fetch("https://gmail.googleapis.com/gmail/v1/users/me/profile", {
                  headers: {
                    Authorization: `Bearer ${req.connection.auth.values.token}`,
                  },
                });

                if (!profileResponse.ok) {
                  throw new Error(`Failed to fetch profile: ${profileResponse.statusText}`);
                }

                const profile = await profileResponse.json();

                // Store the historyId in LTM (persist via Response.memory)
                _.set(req.memory.ltm, "historyId", profile.historyId);

                // First run - don't emit any messages
                return { results: [], memory: req.memory };
              }

              // Construct the URL for history API
              const url = new URL("https://gmail.googleapis.com/gmail/v1/users/me/history");
              const params = new URLSearchParams({
                startHistoryId: storedHistoryId,
                historyTypes: "messageAdded"
              });
              url.search = params.toString();

              // Fetch history from Gmail API
              const response = await fetch(url.toString(), {
                headers: {
                  Authorization: `Bearer ${req.connection.auth.values.token}`,
                },
              });

              if (!response.ok) {
                throw new Error(`Failed to fetch history: ${response.statusText}`);
              }

              const data = await response.json();

              // Update the historyId in LTM if present in response (persist via Response.memory)
              if (data.historyId) {
                _.set(req.memory.ltm, "historyId", data.historyId);
              }

              // Extract messages from history, excluding those with SENT label
              const messages = [];
              if (data.history) {
                for (const history of data.history) {
                  if (history.messagesAdded) {
                    const filteredMessages = history.messagesAdded
                      .map(item => item.message)
                      .filter(message => !message.labelIds?.includes("SENT"));
                    messages.push(...filteredMessages);
                  }
                }
              }

              return { results: messages, memory: req.memory };
            }
      options:
        emitArrayAsSingleMessage: false
        allowNet: true
        allowNetList: []
        denyNetList: []
        allowFs: false
      connection:
        key: my-gmail-connection
    continueOnError: false
    id: ACTR01jn59bxebpqetm28j8ev936r9
    position:
      x: -0.04779327712378745
      'y': 270.4007022342582
    edges:
      EDGE01jn59bxec1ktzkn9bwnpqkcs5:
        id: EDGE01jn59bxec1ktzkn9bwnpqkcs5
        sourceActorId: ACTR01jn59bxebpqetm28j8ev936r9
        sourcePortId: SPRTdefault
        targetActorId: ACTR01jn59bxebpqetm28j8ev936r6
        targetPortId: TPRTdefault
        label: ''
        type: borgiqEdge
  ACTR01jn59bxebpqetm28j8ev936ra:
    name: Every Minute
    type: ScheduledTriggerActor
    msgVar: every_minute
    schemas: {}
    version: 1
    isActive: true
    enableLTM: false
    enableSTM: false
    description: >-
      The scheduled trigger actor will emit messages based on cron based
      schedule.
    runtimeSlug: ''
    sourcePorts:
      - id: SPRTdefault
    configuration:
      options:
        schedule: '* * * * *'
    continueOnError: false
    id: ACTR01jn59bxebpqetm28j8ev936ra
    position:
      x: 2.620945227345487
      'y': 40.228101198405206
    edges:
      EDGE01jn59bxec1ktzkn9bwnpqkcs6:
        id: EDGE01jn59bxec1ktzkn9bwnpqkcs6
        sourceActorId: ACTR01jn59bxebpqetm28j8ev936ra
        sourcePortId: SPRTdefault
        targetActorId: ACTR01jn59bxebpqetm28j8ev936r9
        targetPortId: TPRTdefault
        label: ''
        type: borgiqEdge
  ACTR01jn59m1psy4h3v3g9ak67cff8:
    name: Reply
    type: RouterActor
    msgVar: reply
    schemas: {}
    version: 1
    isActive: true
    enableLTM: false
    enableSTM: false
    description: The router actor will emit messages based on various expressions.
    runtimeSlug: ''
    sourcePorts:
      - id: SPRT5d5gj2s
        name: After Sending Message
        description: After Sending Message
      - id: SPRT9crdo1s
        name: Reply Received
        description: Reply Received
      - id: SPRTdefault
        name: Others
        description: ''
    configuration:
      options:
        emitType: singleRoute
        conditions:
          After Sending Message: ${{Q.isEqual(msg.send_email_and_handle_replies.status, "sent")}}
          Reply Received: ${{Q.isEqual(msg.send_email_and_handle_replies.status, "reply")}}
    continueOnError: false
    id: ACTR01jn59m1psy4h3v3g9ak67cff8
    position:
      x: 2892.675603856203
      'y': 334.4547376389622
    edges:
      EDGE01jpqeh8tre45tjc48b1snt01h:
        id: EDGE01jpqeh8tre45tjc48b1snt01h
        sourceActorId: ACTR01jn59m1psy4h3v3g9ak67cff8
        sourcePortId: SPRT5d5gj2s
        targetActorId: ACTR01jpqeh8tre45tjc48b1snt01g
        targetPortId: TPRTdefault
        label: After Sending Message
        type: borgiqEdge
      EDGE01jpqehjb8k26pc078nnm8dfm8:
        id: EDGE01jpqehjb8k26pc078nnm8dfm8
        sourceActorId: ACTR01jn59m1psy4h3v3g9ak67cff8
        sourcePortId: SPRT9crdo1s
        targetActorId: ACTR01jpqehjb7ryykzeb20f0eern0
        targetPortId: TPRTdefault
        label: Reply Received
        type: borgiqEdge
  ACTR01jn6jq9gvw668hwxsxftd428m:
    name: Cancel Wait
    type: MessageProcessorActor
    msgVar: cancel_wait
    schemas: {}
    version: 1
    isActive: true
    enableLTM: false
    enableSTM: false
    description: >-
      The message processor actor can process incoming messages and emit the
      processed messages.
    runtimeSlug: ''
    sourcePorts:
      - id: SPRTdefault
    configuration:
      options:
        action: notifyCallbackToken
        payload:
          status: cancel
        token: ${{msg.send_email_and_handle_replies.replyToken }}
    continueOnError: false
    id: ACTR01jn6jq9gvw668hwxsxftd428m
    position:
      x: 2628.461541609926
      'y': 944.4447882021333
    edges: {}
  ACTR01jpqeh8tre45tjc48b1snt01g:
    name: DO WORK AFTER SENDING
    type: MessageProcessorActor
    msgVar: do_work_after_sending
    schemas: {}
    version: 1
    isActive: true
    enableLTM: false
    enableSTM: false
    description: >-
      The message processor actor can process incoming messages and emit the
      processed messages.
    runtimeSlug: ''
    sourcePorts:
      - id: SPRTdefault
    configuration:
      options:
        action: inject
        payload:
          software: BorgIQ
          version: 1
    continueOnError: false
    id: ACTR01jpqeh8tre45tjc48b1snt01g
    position:
      x: 2618.495160967831
      'y': 651.3194822992439
    edges: {}
  ACTR01jpqehjb7ryykzeb20f0eern0:
    name: AFTER REPLY
    type: MessageProcessorActor
    msgVar: after_reply
    schemas: {}
    version: 1
    isActive: true
    enableLTM: false
    enableSTM: false
    description: >-
      The message processor actor can process incoming messages and emit the
      processed messages.
    runtimeSlug: ''
    sourcePorts:
      - id: SPRTdefault
    configuration:
      options:
        action: inject
        payload:
          software: BorgIQ
          version: 1
    continueOnError: false
    id: ACTR01jpqehjb7ryykzeb20f0eern0
    position:
      x: 3376.243672640555
      'y': 637.542236632467
    edges: {}
  ACTR01jy4z0r7ygs5crhv3kc64x75s:
    name: Respond with Reply Message
    type: CallableResponseActor
    msgVar: respond_with_reply_message
    schemas: {}
    version: 1
    isActive: true
    enableLTM: false
    enableSTM: false
    description: >-
      The Callable Response actor allows to send messages to the parent flows
      during sub flow invocation.
    runtimeSlug: ''
    sourcePorts:
      - id: SPRTdefault
    configuration:
      options:
        payload:
          status: timeout
          threadId: ${{ msg.gmail_send_email.body.threadId }}
    continueOnError: false
    id: ACTR01jy4z0r7ygs5crhv3kc64x75s
    position:
      x: 1760.567981165375
      'y': 1939.69332546598
    edges: {}
```

## Actor Types Used

| Actor Type | Count | Purpose |
|------------|-------|---------|
| CallableTriggerActor | 1 | Entry point for sub-flow |
| CallFlowActor | 1 | Invoke sub-flow from main flow |
| CallableResponseActor | 3 | Return responses to parent flow |
| ScheduledTriggerActor | 1 | Periodic email polling |
| DenoActor | 1 | Gmail API polling with LTM |
| HttpRequestActor | 1 | Send email via Gmail API |
| RouterActor | 4 | Conditional branching |
| CollectionActor | 2 | Store/retrieve callback tokens |
| MessageProcessorActor | 5 | Token management and data injection |
| CommentActor | 2 | Canvas annotations |

## Key Takeaways

1. **Callback tokens enable async workflows** - Use `issueCallbackToken`, `waitForCallbackToken`, and `notifyCallbackToken` for human-in-the-loop or external event patterns.

2. **CollectionActor bridges flows** - Store tokens or state in named collections with meaningful keys (like thread IDs) so other flows can look them up.

3. **LTM persists across runs** - Use Long-Term Memory for state that must survive between flowruns (like Gmail historyId).

4. **continueOnError for graceful timeouts** - Set `continueOnError: true` on wait actors and check `err.*` in downstream routers.

5. **Multiple CallableResponseActors** - Sub-flows can emit responses at different stages (immediate acknowledgment vs. final result).

6. **Polling + callback pattern** - Combine scheduled polling with callback tokens to create event-driven workflows without webhooks.
