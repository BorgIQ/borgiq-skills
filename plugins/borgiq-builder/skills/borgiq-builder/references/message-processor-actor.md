# Message Processor Actor Reference

The MessageProcessorActor is a versatile utility actor for processing, transforming, and controlling message flow within workflows.

## Table of Contents

- [Overview](#overview)
- [Configuration Structure](#configuration-structure)
- [Actions Reference](#actions-reference)
- [Message Actions](#message-actions)
- [Delay Actions](#delay-actions)
- [Array Actions](#array-actions)
- [Fork Actions](#fork-actions)
- [Dedupe Actions](#dedupe-actions)
- [Callback Actions](#callback-actions)
- [File Actions](#file-actions)
- [Memory Requirements](#memory-requirements)
- [Complete Examples](#complete-examples)
- [Advanced Patterns](#advanced-patterns)
- [Use Cases](#use-cases)

## Overview

Message Processor actors perform various data operations without making external API calls. They are used for:

- Injecting/creating data payloads
- Delaying message emission
- Filtering messages conditionally
- Splitting arrays into individual messages
- Collecting split messages back into arrays
- Forking and joining parallel execution paths
- Deduplicating messages
- Extracting data with regex
- Rendering templates
- Managing callback tokens for async workflows
- Downloading files

## Configuration Structure

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  ACTR01xxxxx:
    type: MessageProcessorActor
    version: 1
    name: Message Processor
    msgVar: message_processor
    description: Process and transform messages
    isActive: true
    continueOnError: false
    enableLTM: false  # Set true for dedupe actions
    enableSTM: false  # Set true for collect/forkJoin actions
    sourcePorts:
      - id: SPRTdefault
    configuration:
      options:
        action: inject  # Required: specifies the action type
        # Action-specific options go here
    schemas: {}
    id: ACTR01xxxxx
    position:
      x: 0
      'y': 0
    edges: {}
```

## Actions Reference

The `action` field determines the operation. Each action has specific options and output.

### Action Groups

| Group | Actions |
|-------|---------|
| **Message** | `inject`, `renderTemplate`, `regexExtract`, `filter` |
| **Delay** | `delayBySeconds`, `delayUntil` |
| **Array** | `split`, `collect` |
| **Fork** | `fork`, `forkJoin` |
| **Dedupe** | `dedupeByCount`, `dedupeByTime` |
| **Callback** | `issueCallbackToken`, `waitForCallbackToken`, `notifyCallbackToken` |
| **File** | `downloadFileUrl`, `downloadFileAsBase64` |

---

## Message Actions

### inject

Injects a custom payload as the actor's output. Use for creating data, constants, or computed values.

**Options:**
| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `action` | `"inject"` | Yes | Must be `inject` |
| `payload` | any | Yes | The value to emit as the actor's message |

**Example:**
```yaml
configuration:
  options:
    action: inject
    payload:
      now: ${{ Q.now() }}
      today: ${{ Q.currentDateTime() }}
      ulid: ${{ Q.ulid() }}
      formattedDate: ${{ Q.dateFns.format(Q.now(), 'dd-MM-yyyy') }}
```

**Emitted Message:** The `payload` value directly.

---

### renderTemplate

Renders a LiquidJS template using the actor's inputs.

**Options:**
| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `action` | `"renderTemplate"` | Yes | Must be `renderTemplate` |
| `template` | string | Yes | LiquidJS template string |

**Example:**
```yaml
configuration:
  inputs:
    name: ${{ msg.form.body.name }}
    items: ${{ msg.data.items }}
  options:
    action: renderTemplate
    template: |
      Hello {{ inputs.name }},

      Your order contains:
      {% for item in inputs.items %}
      - {{ item.name }}: ${{ item.price }}
      {% endfor %}
```

**Emitted Message:** The rendered template string.

---

### regexExtract

Extracts data from strings using regex patterns.

**Options:**
| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `action` | `"regexExtract"` | Yes | Must be `regexExtract` |
| `rules` | array | Yes | Array of extraction rules |
| `rules[].regex` | string | Yes | Valid regex pattern |
| `rules[].regexOptions` | string | No | Regex flags (e.g., `"g"`, `"i"`) |
| `rules[].extractFrom` | any | Yes | Value to run regex against |
| `rules[].extractTo` | string | Yes | Key to store extracted values |

**Example:**
```yaml
configuration:
  inputs:
    text: ${{ msg.email.body }}
  options:
    action: regexExtract
    rules:
      - regex: '[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}'
        regexOptions: gi
        extractFrom: ${{ inputs.text }}
        extractTo: emails
      - regex: '\d{3}-\d{3}-\d{4}'
        regexOptions: g
        extractFrom: ${{ inputs.text }}
        extractTo: phoneNumbers
```

**Emitted Message:**
```json
{
  "emails": ["user@example.com", "support@company.org"],
  "phoneNumbers": ["555-123-4567"]
}
```

---

### filter

Conditionally allows or blocks message flow based on a boolean expression.

**Options:**
| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `action` | `"filter"` | Yes | Must be `filter` |
| `filter` | boolean | Yes | If `true`, message passes; if `false`, message is blocked |

**Example:**
```yaml
configuration:
  options:
    action: filter
    filter: ${{ msg.webhook.body.event === 'order.created' }}
```

**Emitted Message:** `true` or `false` (only emits if filter evaluates to `true`).

---

## Delay Actions

### delayBySeconds

Delays message emission by a specified number of seconds.

**Options:**
| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `action` | `"delayBySeconds"` | Yes | Must be `delayBySeconds` |
| `seconds` | number | Yes | Seconds to delay (must be > 0) |

**Example:**
```yaml
configuration:
  options:
    action: delayBySeconds
    seconds: 10
```

**Emitted Message:**
```json
{
  "delayUntil": "2024-01-15T10:30:45.000Z"
}
```

---

### delayUntil

Delays message emission until a specific datetime.

**Options:**
| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `action` | `"delayUntil"` | Yes | Must be `delayUntil` |
| `until` | string | Yes | ISO datetime string to delay until |

**Example:**
```yaml
configuration:
  options:
    action: delayUntil
    until: ${{ Q.dateFns.addHours(Q.now(), 2).toISOString() }}
```

**Emitted Message:** Same as `delayBySeconds`.

---

## Array Actions

### split

Splits an array into individual messages, emitting one message per array element.

**Options:**
| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `action` | `"split"` | Yes | Must be `split` |
| `valueToSplit` | array | Yes | The array to split |
| `emitKey` | string | No | Key name for the split value (default: `"item"`) |
| `limit` | number | No | Maximum messages to emit (default: 1000) |

**Example:**
```yaml
configuration:
  options:
    action: split
    valueToSplit: ${{ msg.api_response.users }}
    emitKey: user
    limit: 100
```

**Emitted Message (per item):**
```json
{
  "splitId": "01HQXYZ...",
  "index": 0,
  "size": 50,
  "user": { "id": "123", "name": "John" }
}
```

---

### collect

Collects split messages back into an array. Requires `enableSTM: true`.

**Options:**
| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `action` | `"collect"` | Yes | Must be `collect` |
| `splitId` | string | Yes | The `splitId` from upstream split actor |
| `size` | number | Yes | Total size of array being collected |
| `captureValue` | any | Yes | Value to collect into the array |
| `emitKey` | string | No | Key for collected array (default: `"items"`) |
| `if` | boolean | No | Condition for including value (default: `true`) |

**Performance Note:** Keep `captureValue` small and focused. Only capture the data you actually need, as the collected array grows in memory with each split item. Capturing large objects (e.g., full API responses) can significantly slow down performance. Instead, extract only the required fields.

```yaml
# Good: Capture only needed fields
captureValue:
  id: ${{ msg.api_response.id }}
  status: ${{ msg.api_response.status }}

# Bad: Capturing entire response object
captureValue: ${{ msg.api_response }}
```

**Example:**
```yaml
configuration:
  options:
    action: collect
    splitId: ${{ msg.split_users.splitId }}
    size: ${{ msg.split_users.size }}
    captureValue: ${{ msg.process_user }}
    emitKey: processedUsers
    if: ${{ msg.process_user.status === 'success' }}
```

**Emitted Message:**
```json
{
  "processedUsers": [
    { "id": "123", "status": "success" },
    { "id": "456", "status": "success" }
  ]
}
```

---

## Fork Actions

### fork

Creates a fork point for parallel execution paths. Multiple downstream actors can process the same message independently.

**Options:**
| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `action` | `"fork"` | Yes | Must be `fork` |

**Example:**
```yaml
configuration:
  options:
    action: fork
```

**Emitted Message:**
```json
{
  "forkId": "01HQXYZ..."
}
```

---

### forkJoin

Waits for and joins results from multiple parallel paths. Requires `enableSTM: true`.

**Options:**
| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `action` | `"forkJoin"` | Yes | Must be `forkJoin` |
| `forkId` | string | Yes | The `forkId` from upstream fork actor |
| `size` | number | Yes | Number of parallel paths to wait for |

**Example:**
```yaml
configuration:
  options:
    action: forkJoin
    forkId: ${{ msg.fork_point.forkId }}
    size: 3
```

**Emitted Message:** Object with keys for each source actor's `msgVar`, containing their outputs.

**Critical: Accessing Forked Actor Messages**

**Important:** Only the messages from the actors **immediately above** `forkJoin` (i.e., the direct sources connecting to `forkJoin`) are collected. All other messages from intermediate actors in the fork path are **lost** and cannot be accessed after `forkJoin`.

Messages from actors between `fork` and `forkJoin` **cannot** be accessed directly via `msg.actorMsgVar`. Instead, you must access them through the `forkJoin` actor's output using this pattern:

```
msg.<forkJoinMsgVar>.<sourceActorMsgVar>
```

For example, if your `forkJoin` actor has `msgVar: join_ai_responses` and the forked actors have `msgVar: haiku_ai`, `msgVar: gemini_flash_ai`, and `msgVar: gpt_mini_ai`, access them like this:

```yaml
# CORRECT: Access through forkJoin actor
haikuResponse: ${{ msg.join_ai_responses.haiku_ai?.response }}
geminiResponse: ${{ msg.join_ai_responses.gemini_flash_ai?.response }}
gptResponse: ${{ msg.join_ai_responses.gpt_mini_ai?.response }}

# INCORRECT: Direct access will NOT work
haikuResponse: ${{ msg.haiku_ai?.response }}  # Returns undefined!
```

**Capturing Multiple Actor Messages in a Fork Path**

If you need to capture messages from multiple actors within a fork path (not just the last one), use a MessageProcessorActor with `inject` action at the end of each fork path to bundle all the data you need before `forkJoin`:

```yaml
# Fork creates parallel paths
ACTR01fork:
  type: MessageProcessorActor
  msgVar: fork_requests
  configuration:
    options:
      action: fork

# Path A: Multiple actors
ACTR01fetchDataA:
  type: HttpRequestActor
  msgVar: fetch_data_a
  continueOnError: true
  # ... fetches data ...

ACTR01processDataA:
  type: DenoActor
  msgVar: process_data_a
  continueOnError: true
  # ... processes data ...

# Bundle all messages from Path A before forkJoin
ACTR01bundlePathA:
  type: MessageProcessorActor
  msgVar: bundle_path_a
  continueOnError: true
  configuration:
    options:
      action: inject
      payload:
        fetchResult: ${{ msg.fetch_data_a }}
        processResult: ${{ msg.process_data_a }}

# Path B: Similar pattern
ACTR01fetchDataB:
  type: HttpRequestActor
  msgVar: fetch_data_b
  continueOnError: true

ACTR01bundlePathB:
  type: MessageProcessorActor
  msgVar: bundle_path_b
  continueOnError: true
  configuration:
    options:
      action: inject
      payload:
        fetchResult: ${{ msg.fetch_data_b }}

# ForkJoin collects the bundled results
ACTR01join:
  type: MessageProcessorActor
  msgVar: join_results
  enableSTM: true
  configuration:
    options:
      action: forkJoin
      forkId: ${{ msg.fork_requests.forkId }}
      size: 2

# Now you can access all bundled data
ACTR01downstream:
  type: MessageProcessorActor
  msgVar: final_result
  configuration:
    inputs:
      # Access bundled data from each path
      pathAFetch: ${{ msg.join_results.bundle_path_a?.fetchResult }}
      pathAProcess: ${{ msg.join_results.bundle_path_a?.processResult }}
      pathBFetch: ${{ msg.join_results.bundle_path_b?.fetchResult }}
    options:
      action: inject
      payload: ${{ inputs }}
```

**Simple Fork/ForkJoin Example (Single Actor Per Path):**

```yaml
# Fork actor creates parallel paths
ACTR01fork:
  type: MessageProcessorActor
  msgVar: fork_requests
  configuration:
    options:
      action: fork

# Parallel actors (targets of fork, sources of forkJoin)
ACTR01actorA:
  type: AiActor
  msgVar: actor_a
  continueOnError: true  # Important for forkJoin patterns
  # ... configuration ...

ACTR01actorB:
  type: AiActor
  msgVar: actor_b
  continueOnError: true
  # ... configuration ...

# ForkJoin collects results
ACTR01join:
  type: MessageProcessorActor
  msgVar: join_results
  enableSTM: true
  configuration:
    options:
      action: forkJoin
      forkId: ${{ msg.fork_requests.forkId }}
      size: 2

# Downstream actor accessing joined results
ACTR01downstream:
  type: MessageProcessorActor
  msgVar: process_results
  configuration:
    inputs:
      # Access forked actor outputs through the forkJoin msgVar
      resultA: ${{ msg.join_results.actor_a }}
      resultB: ${{ msg.join_results.actor_b }}
    options:
      action: inject
      payload:
        combined:
          - ${{ inputs.resultA }}
          - ${{ inputs.resultB }}
```

---

### When to Use Fork/ForkJoin

**USE fork/forkJoin when:**
- You fan out to multiple APIs and need ALL results combined before continuing
- Downstream processing requires data from ALL parallel paths
- You're building aggregation workflows (search multiple sources, merge results)
- The next step after parallel paths must run exactly ONCE with combined data

**Examples requiring fork/forkJoin:**
- Search 4 job portals → Normalize ALL results together
- Fetch user profile + user settings + user preferences → Merge into complete user object
- Query 3 databases → Combine into unified response
- Call multiple AI models → Compare/ensemble the results

### When NOT to Use Fork/ForkJoin

**DO NOT use fork/forkJoin when:**
- Parallel paths are independent and don't need synchronization
- You're doing fire-and-forget operations (notifications, logging)
- Each parallel result can be processed separately
- You want downstream actors to run once per upstream result (not once total)

**Examples NOT requiring fork/forkJoin:**
- Send email notification AND Slack notification (independent)
- Log to Datadog AND CloudWatch (independent)
- Trigger webhook to System A AND System B (independent)
- Process each API result separately with its own downstream flow

### Common Anti-Pattern: Using inject to "Merge"

**WRONG - This does NOT work:**
```yaml
# After parallel API calls, trying to "merge" with inject
ACTR01wrongmerge:
  type: MessageProcessorActor
  configuration:
    options:
      action: inject
      payload:
        api1: ${{ msg.api1_call }}
        api2: ${{ msg.api2_call }}
        api3: ${{ msg.api3_call }}
```

**Why it fails:**
1. This actor receives 3 separate messages (one from each API)
2. It executes 3 times, not once
3. Each execution only has ONE `msg.apiX_call` available
4. The "merge" never actually happens

**CORRECT - Use fork before and forkJoin after:**
```yaml
# Before parallel calls
ACTR01fork:
  type: MessageProcessorActor
  configuration:
    options:
      action: fork

# After parallel calls (with enableSTM: true)
ACTR01forkjoin:
  type: MessageProcessorActor
  enableSTM: true
  configuration:
    inputs:
      forkId: ${{ msg.fork.forkId }}
      forkSize: ${{ msg.fork.forkSize }}
    options:
      action: forkJoin
      forkId: ${{ inputs.forkId }}
      forkSize: ${{ inputs.forkSize }}
```

### Visual Comparison

**Without fork/forkJoin (ProcessResults runs 3 times):**
```
SetVars
   |
  /|\
 / | \
A  B  C     ← 3 parallel API calls
 \ | /
  \|/
ProcessResults  ← Executes 3 TIMES (once per API response)
```

**With fork/forkJoin (ProcessResults runs once):**
```
SetVars
   |
 Fork       ← Tracks parallel paths
  /|\
 / | \
A  B  C     ← 3 parallel API calls
 \ | /
  \|/
ForkJoin    ← Waits for all, bundles results
   |
ProcessResults  ← Executes 1 TIME with all 3 responses
```

---

## Dedupe Actions

### dedupeByCount

Deduplicates messages based on a key within a count-based lookback window. Requires `enableLTM: true`.

**Options:**
| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `action` | `"dedupeByCount"` | Yes | Must be `dedupeByCount` |
| `dedupeKey` | any | Yes | Key to deduplicate by |
| `lookbackAsCount` | number | Yes | Number of previous messages to check |
| `emitAlways` | boolean | Yes | If `true`, emit even if duplicate |

**Example:**
```yaml
configuration:
  options:
    action: dedupeByCount
    dedupeKey: ${{ msg.webhook.body.orderId }}
    lookbackAsCount: 100
    emitAlways: false
```

**Emitted Message:**
```json
{
  "dedupeKey": "ORD-12345",
  "unique": true
}
```

---

### dedupeByTime

Deduplicates messages based on a key within a time-based lookback window. Requires `enableLTM: true`.

**Options:**
| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `action` | `"dedupeByTime"` | Yes | Must be `dedupeByTime` |
| `dedupeKey` | any | Yes | Key to deduplicate by |
| `lookbackInSeconds` | number | Yes | Seconds to look back |
| `emitAlways` | boolean | Yes | If `true`, emit even if duplicate |

**Example:**
```yaml
configuration:
  options:
    action: dedupeByTime
    dedupeKey: ${{ msg.event.id }}
    lookbackInSeconds: 3600
    emitAlways: false
```

**Emitted Message:** Same structure as `dedupeByCount`.

---

## Callback Actions

### issueCallbackToken

Issues a callback token for async human-in-the-loop or external system callbacks.

**Options:**
| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `action` | `"issueCallbackToken"` | Yes | Must be `issueCallbackToken` |
| `expiresAfterInSeconds` | number | No | Token validity duration |
| `multipleResponse` | boolean | No | Allow multiple responses (default: `false`) |

**Example:**
```yaml
configuration:
  options:
    action: issueCallbackToken
    expiresAfterInSeconds: 86400
    multipleResponse: false
```

**Emitted Message:**
```json
{
  "token": "cbt_01HQXYZ...",
  "url": "https://borgiq.com/callback/cbt_01HQXYZ...",
  "expiresAt": "2024-01-16T10:30:00.000Z",
  "multipleResponse": false
}
```

---

### waitForCallbackToken

Pauses workflow execution until a callback token is resolved.

**Options:**
| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `action` | `"waitForCallbackToken"` | Yes | Must be `waitForCallbackToken` |
| `token` | string | Yes | Token from `issueCallbackToken` |
| `timeoutInSeconds` | number | Yes | Maximum wait time |

**Example:**
```yaml
configuration:
  options:
    action: waitForCallbackToken
    token: ${{ msg.issue_token.token }}
    timeoutInSeconds: 86400
```

**Emitted Message:** When the callback URL is invoked, the actor emits the HTTP request details:

```json
{
  "headers": {
    "x-forwarded-for": "203.0.113.24",
    "x-forwarded-proto": "https",
    "x-forwarded-port": "443",
    "host": "api.borgiq.com",
    "x-amzn-trace-id": "Root=1-00000000-000000000000000000000000",
    "content-length": "27",
    "accept": "application/json, text/plain, */*",
    "content-type": "application/json; charset=utf-8",
    "user-agent": "axios/1.12.2",
    "accept-encoding": "gzip, compress, deflate, br"
  },
  "body": {
    "message": "Hello, world!"
  }
}
```

The `body` contains whatever payload was sent to the callback URL. Access the response data via `msg.wait_actor.body`.

**Timeout Handling:**

To handle timeouts gracefully, set `continueOnError: true` on the actor. When a timeout occurs, the error is emitted under `err.wait_actor` with this structure:

```json
{
  "location": "orchestrator",
  "message": "waitForCallbackToken timeout error for TOKNe04a987db984a9ea396ad2d535993612ea4fbb7fc6732885017a031bcd",
  "name": "TimeoutError",
  "stack": "",
  "retry": false,
  "canEmit": true
}
```

**Example with Timeout Handling:**

Use a RouterActor downstream to handle success vs timeout scenarios:

```yaml
# Wait for callback with continueOnError
ACTR01wait:
  type: MessageProcessorActor
  msgVar: wait_for_response
  continueOnError: true  # Required for timeout handling
  configuration:
    options:
      action: waitForCallbackToken
      token: ${{ msg.issue_token.token }}
      timeoutInSeconds: 3600

# Router to handle success or timeout
ACTR01router:
  type: RouterActor
  msgVar: route_result
  sourcePorts:
    - id: SPRT001
      name: Success
    - id: SPRT002
      name: Timeout
    - id: SPRTdefault
      name: F
  configuration:
    options:
      emitType: singleRoute
      conditions:
        Success: ${{ !Q.isNil(msg.wait_for_response) }}
        Timeout: ${{ !Q.isNil(err.wait_for_response) && err.wait_for_response?.name === 'TimeoutError' }}
```

---

### notifyCallbackToken

Resolves a callback token programmatically from within a workflow.

**Options:**
| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `action` | `"notifyCallbackToken"` | Yes | Must be `notifyCallbackToken` |
| `token` | string | Yes | Token to notify |
| `payload` | any | Yes | Payload to send as callback response |

**Example:**
```yaml
configuration:
  options:
    action: notifyCallbackToken
    token: ${{ msg.issue_token.token }}
    payload:
      approved: true
      approvedBy: ${{ ctx.user.email }}
```

**Emitted Message:** The payload value.

---

## File Actions

### downloadFileUrl

Generates a temporary download URL for a BorgIQ file.

**Options:**
| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `action` | `"downloadFileUrl"` | Yes | Must be `downloadFileUrl` |
| `file` | BIQFile | Yes | BorgIQ file object |
| `expiresInMinutes` | number | No | URL validity (default: 1) |
| `downloadAsAttachment` | boolean | No | Force download vs inline (default: `false`) |

**Example:**
```yaml
configuration:
  options:
    action: downloadFileUrl
    file: ${{ msg.upload.files[0] }}
    expiresInMinutes: 60
    downloadAsAttachment: true
```

**Emitted Message:**
```json
{
  "file": { "id": "...", "name": "report.pdf", ... },
  "url": "https://..."
}
```

---

### downloadFileAsBase64

Downloads a BorgIQ file and returns it as a base64 string.

**Options:**
| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `action` | `"downloadFileAsBase64"` | Yes | Must be `downloadFileAsBase64` |
| `file` | BIQFile | Yes | BorgIQ file object |

**Example:**
```yaml
configuration:
  options:
    action: downloadFileAsBase64
    file: ${{ msg.interface_form.body.attachment }}
```

**Emitted Message:**
```json
{
  "file": { "id": "...", "name": "image.png", ... },
  "base64": "iVBORw0KGgo..."
}
```

---

## Memory Requirements

Some actions require memory to be enabled:

| Action | Memory Required |
|--------|-----------------|
| `dedupeByCount` | `enableLTM: true` |
| `dedupeByTime` | `enableLTM: true` |
| `collect` | `enableSTM: true` |
| `forkJoin` | `enableSTM: true` |

---

## Complete Examples

### Inject Sample Data

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  ACTR01kd6ckx642rwwpmfck26necjp:
    type: MessageProcessorActor
    version: 1
    name: Inject Sample Data
    msgVar: inject_sample_data
    description: Inject computed values into the workflow
    isActive: true
    continueOnError: false
    enableLTM: false
    enableSTM: false
    sourcePorts:
      - id: SPRTdefault
    configuration:
      options:
        action: inject
        payload:
          now: ${{ Q.now() }}
          today: ${{ Q.currentDateTime() }}
          ulid: ${{ Q.ulid() }}
          json: ${{ Q.toJSON(ctx) }}
          formattedDate: ${{ Q.dateFns.format(Q.now(), 'dd-MM-yyyy') }}
    schemas: {}
    id: ACTR01kd6ckx642rwwpmfck26necjp
    position:
      x: 0
      'y': 0
    edges: {}
```

### Delay Execution

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  ACTR01kd6d0w6ef8ce1qvrknexv80q:
    type: MessageProcessorActor
    version: 1
    name: Delay 10 Seconds
    msgVar: delay
    description: Delay workflow execution by 10 seconds
    isActive: true
    continueOnError: false
    enableLTM: false
    enableSTM: false
    sourcePorts:
      - id: SPRTdefault
    configuration:
      options:
        action: delayBySeconds
        seconds: 10
    schemas: {}
    id: ACTR01kd6d0w6ef8ce1qvrknexv80q
    position:
      x: 0
      'y': 0
    edges: {}
```

### Split and Collect Pattern

```yaml
# Split Actor
ACTR01split:
  type: MessageProcessorActor
  name: Split Orders
  msgVar: split_orders
  configuration:
    options:
      action: split
      valueToSplit: ${{ msg.api.orders }}
      emitKey: order

# ... processing actors in between ...

# Collect Actor (requires enableSTM: true)
ACTR01collect:
  type: MessageProcessorActor
  name: Collect Results
  msgVar: collect_results
  enableSTM: true
  configuration:
    options:
      action: collect
      splitId: ${{ msg.split_orders.splitId }}
      size: ${{ msg.split_orders.size }}
      captureValue: ${{ msg.process_order }}
      emitKey: processedOrders
```

---

## Advanced Patterns

### Accumulating State Pattern

Use a MessageProcessorActor named "State" repeatedly throughout a workflow to build up state incrementally. BorgIQ's `msg.ActorName` returns the message from the **last actor with that name**, enabling progressive state accumulation.

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  ACTR01jhe8hmqvnv9tbesaqt1sej8m:
    name: State
    type: MessageProcessorActor
    msgVar: state
    schemas: {}
    version: 1
    isActive: true
    enableLTM: false
    enableSTM: false
    description: Accumulate workflow state
    sourcePorts:
      - id: SPRTdefault
    configuration:
      inputs:
        company: ${{ msg.workflow_inputs.company }}
        company_url: ${{ msg.workflow_inputs.company_url }}
      options:
        action: inject
        payload: ${{ Object.assign({}, msg.state, inputs) }}
    continueOnError: false
    id: ACTR01jhe8hmqvnv9tbesaqt1sej8m
    position:
      x: 0
      'y': 0
    edges: {}
```

**How it works:**
1. Each "State" actor merges new data into the existing `msg.state` object
2. `Object.assign({}, msg.state, inputs)` creates a new object combining previous state with new inputs
3. Downstream actors always access the latest accumulated state via `msg.state`

**Usage in a workflow:**
```
Trigger → State (init) → API Call → State (add API data) → Process → State (add result) → Output
```

Each "State" actor adds new fields while preserving previous ones:
- First State: `{ company: "Acme", company_url: "acme.com" }`
- Second State: `{ company: "Acme", company_url: "acme.com", apiData: {...} }`
- Third State: `{ company: "Acme", company_url: "acme.com", apiData: {...}, result: {...} }`

---

### Filter as Lightweight Router

Use `filter` instead of RouterActor when you only need a single path and don't care about handling the false case. The workflow simply stops if the condition isn't met—no need to configure multiple output ports.

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  ACTR01jkrkpmb8fmzqfceksseavfca:
    name: Filter (Starts With)
    type: MessageProcessorActor
    msgVar: filter_starts_with
    schemas: {}
    version: 1
    isActive: true
    enableLTM: false
    enableSTM: false
    description: Continue only if message starts with expected prefix
    sourcePorts:
      - id: SPRTdefault
    configuration:
      inputs: ${{ msg.webhook.body.message }}
      options:
        action: filter
        filter: ${{ inputs.startsWith('Hello') }}
    continueOnError: false
    id: ACTR01jkrkpmb8fmzqfceksseavfca
    position:
      x: 0
      'y': 0
    edges: {}
```

**When to use Filter vs Router:**

| Scenario | Use |
|----------|-----|
| Single path, ignore false case | **Filter** |
| Multiple paths (if/else, switch) | RouterActor |
| Need to handle both true and false | RouterActor |
| Simple gate/guard condition | **Filter** |

**Common filter patterns:**
```yaml
# Check if array is not empty
filter: ${{ inputs.items?.length > 0 }}

# Check for specific event type
filter: ${{ inputs.event === 'order.created' }}

# Check if value exists
filter: ${{ !Q.isNil(inputs.userId) }}

# String matching
filter: ${{ inputs.email?.endsWith('@company.com') }}
```

---

## Use Cases

| Scenario | Action |
|----------|--------|
| Create constants or computed values | `inject` |
| Generate dynamic text from template | `renderTemplate` |
| Extract emails/phones from text | `regexExtract` |
| Conditionally continue workflow | `filter` |
| Wait before next step | `delayBySeconds` / `delayUntil` |
| Process array items individually | `split` |
| Recombine processed items | `collect` |
| Run parallel paths | `fork` + `forkJoin` |
| Prevent duplicate processing | `dedupeByCount` / `dedupeByTime` |
| Human approval workflows | `issueCallbackToken` + `waitForCallbackToken` |
| Get file download URL | `downloadFileUrl` |
| Get file as base64 | `downloadFileAsBase64` |
