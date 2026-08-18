# Common Workflow Patterns

This reference provides templates for common workflow patterns in BorgIQ. Use these as starting points when building workflows.

## Table of Contents

- [Pattern 1: Multi-Source Data Aggregation](#pattern-1-multi-source-data-aggregation)
- [Pattern 2: Fire-and-Forget Notifications](#pattern-2-fire-and-forget-notifications)
- [Pattern 3: Conditional Branching with Router](#pattern-3-conditional-branching-with-router)
- [Pattern 4: Sequential Processing Pipeline](#pattern-4-sequential-processing-pipeline)
- [Pattern 5: Split and Collect Array Processing](#pattern-5-split-and-collect-array-processing)
- [Pattern 6: Error Handling with Continue on Error](#pattern-6-error-handling-with-continue-on-error)
- [Choosing the Right Pattern](#choosing-the-right-pattern)

---

## Pattern 1: Multi-Source Data Aggregation

**Use when:** Calling multiple APIs/sources and combining ALL results before processing.

**Examples:**
- Search multiple job portals and normalize all results
- Fetch data from 3 microservices and merge into unified response
- Query multiple databases and combine results

**Flow diagram:**
```
Trigger
    |
Set Variables
    |
Fork (action: fork)  ← REQUIRED: tracks parallel paths
    |
   /|\
  / | \
API1  API2  API3     ← Run concurrently (automatic)
  \ | /
   \|/
ForkJoin (action: forkJoin, enableSTM: true)  ← REQUIRED: combines results
    |
Process Combined Data (DenoActor or AiActor)
    |
Output
```

**Key actors:**

### Fork Actor (before parallel calls)

**Important:** MessageProcessorActor ALWAYS has only `SPRTdefault` as its sourcePort. The fork action simply injects a `forkId` into the message stream. Parallel paths are created by connecting multiple edges from the fork actor to different downstream actors—all using `sourcePortId: SPRTdefault`.

```yaml
ACTR01xxxxxxxxxxxxxxxxxxxxx:
  type: MessageProcessorActor
  version: 1
  name: Fork to Data Sources
  msgVar: fork_to_data_sources
  description: Start parallel data fetching with tracking
  isActive: true
  continueOnError: false
  enableLTM: false
  enableSTM: false
  sourcePorts:
    - id: SPRTdefault  # MessageProcessorActor ONLY has SPRTdefault
  configuration:
    options:
      action: fork  # Just the action - no paths config needed
  schemas: {}
  id: ACTR01xxxxxxxxxxxxxxxxxxxxx
  position:
    x: 0
    'y': 200
  edges:
    # Parallel paths created via multiple edges, all using SPRTdefault
    EDGE01aaaaaaaaaaaaaaaaaaaaa:
      id: EDGE01aaaaaaaaaaaaaaaaaaaaa
      sourceActorId: ACTR01xxxxxxxxxxxxxxxxxxxxx
      sourcePortId: SPRTdefault
      targetActorId: ACTR01source1actor
      targetPortId: TPRTdefault
      type: borgiqEdge
    EDGE01bbbbbbbbbbbbbbbbbbbbb:
      id: EDGE01bbbbbbbbbbbbbbbbbbbbb
      sourceActorId: ACTR01xxxxxxxxxxxxxxxxxxxxx
      sourcePortId: SPRTdefault
      targetActorId: ACTR01source2actor
      targetPortId: TPRTdefault
      type: borgiqEdge
    EDGE01ccccccccccccccccccccc:
      id: EDGE01ccccccccccccccccccccc
      sourceActorId: ACTR01xxxxxxxxxxxxxxxxxxxxx
      sourcePortId: SPRTdefault
      targetActorId: ACTR01source3actor
      targetPortId: TPRTdefault
      type: borgiqEdge
```

**How fork works:**
1. Fork actor emits a message with a unique `forkId` to ALL connected downstream actors
2. Each downstream actor receives the same message (with the `forkId`)
3. All downstream actors run concurrently
4. The `forkJoin` actor collects all messages with the same `forkId` before emitting once

### ForkJoin Actor (after parallel calls)
```yaml
ACTR01yyyyyyyyyyyyyyyyyyyyy:
  type: MessageProcessorActor
  version: 1
  name: Join Data Sources
  msgVar: join_data_sources
  description: Wait for all data sources and combine results
  isActive: true
  continueOnError: false
  enableLTM: false
  enableSTM: true  # REQUIRED for forkJoin
  sourcePorts:
    - id: SPRTdefault
  configuration:
    inputs:
      forkId: ${{ msg.fork_to_data_sources.forkId }}
      forkSize: ${{ msg.fork_to_data_sources.forkSize }}
    options:
      action: forkJoin
      forkId: ${{ inputs.forkId }}
      forkSize: ${{ inputs.forkSize }}
  schemas: {}
  id: ACTR01yyyyyyyyyyyyyyyyyyyyy
  position:
    x: 0
    'y': 600
  edges:
    EDGE01ddddddddddddddddddddd:
      id: EDGE01ddddddddddddddddddddd
      sourceActorId: ACTR01yyyyyyyyyyyyyyyyyyyyy
      sourcePortId: SPRTdefault
      targetActorId: ACTR01processactor
      targetPortId: TPRTdefault
      type: borgiqEdge
```

### Accessing Combined Results
After `forkJoin`, downstream actors access all results **through the forkJoin actor's msgVar**:
```yaml
# The forkJoin actor (msgVar: "join_data_sources") collects all upstream results
# Access pattern: msg.<forkJoin_msgVar>.<upstream_actor_msgVar>
configuration:
  inputs:
    source1_data: ${{ msg.join_data_sources.source1_api.body }}
    source2_data: ${{ msg.join_data_sources.source2_api.body }}
    source3_data: ${{ msg.join_data_sources.source3_api.body }}
```

**Common mistakes to avoid:**
```yaml
# WRONG - Direct access without forkJoin msgVar
configuration:
  inputs:
    source1_data: ${{ msg.source1_api.body }}  # Won't work!
# Must access through forkJoin's msgVar: msg.join_data_sources.source1_api.body

# ALSO WRONG - Using inject to "merge"
configuration:
  options:
    action: inject
    payload:
      source1: ${{ msg.source1_api }}
      source2: ${{ msg.source2_api }}
      source3: ${{ msg.source3_api }}
# This executes 3 times, each time only having ONE source available!
```

---

## Pattern 2: Fire-and-Forget Notifications

**Use when:** Sending to multiple destinations independently, no combined result needed.

**Examples:**
- Send email AND Slack notification
- Log to multiple monitoring systems
- Trigger webhooks to external services

**Flow diagram:**
```
Process Data
    |
   / \
  /   \
Email  Slack    ← Both run concurrently (automatic, NO fork needed)
```

**Key point:** Do NOT use fork/forkJoin here. It adds unnecessary complexity.

```yaml
# ProcessData actor edges - just connect to both notification actors
edges:
  EDGE01emailedge:
    id: EDGE01emailedge
    sourceActorId: ACTR01processdata
    sourcePortId: SPRTdefault
    targetActorId: ACTR01sendemail
    targetPortId: TPRTdefault
    type: borgiqEdge
  EDGE01slackedge:
    id: EDGE01slackedge
    sourceActorId: ACTR01processdata
    sourcePortId: SPRTdefault
    targetActorId: ACTR01sendslack
    targetPortId: TPRTdefault
    type: borgiqEdge
```

---

## Pattern 3: Conditional Branching with Router

**Use when:** Different processing paths based on data conditions.

**Examples:**
- Route by priority level (high/medium/low)
- Route by status code (success/error)
- Route by event type

**Flow diagram:**
```
Trigger
    |
Process Data
    |
Router
    |
   /|\
  / | \
High Medium Low   ← Only ONE path executes based on condition
```

**Key actor:**
```yaml
ACTR01routerxxxxxxxxxxxxx:
  type: RouterActor
  version: 1
  name: Route by Priority
  msgVar: route_by_priority
  sourcePorts:
    - id: SPRThighpri
      name: High
      description: High priority items
    - id: SPRTmedpri
      name: Medium
      description: Medium priority items
    - id: SPRTdefault
      name: Low
      description: Low priority (default)
  configuration:
    options:
      emitType: singleRoute
      conditions:
        High: ${{ msg.process_data.priority === 'high' }}
        Medium: ${{ msg.process_data.priority === 'medium' }}
```

---

## Pattern 4: Sequential Processing Pipeline

**Use when:** Each step depends on the previous step's output.

**Examples:**
- Fetch data → Transform → Validate → Save
- Extract → Analyze with AI → Format → Send

**Flow diagram:**
```
Trigger → Fetch → Transform → Validate → Save → Notify
```

**Key point:** Simple linear connections, no parallelism.

---

## Pattern 5: Split and Collect Array Processing

**Use when:** Processing array items individually, then collecting results.

**Examples:**
- Process each order in a batch
- Analyze each document in a list
- Transform each record

**Flow diagram:**
```
Trigger
    |
Fetch Array Data
    |
Split (action: split)
    |
   /|\        ← Emits N messages, one per array item
  / | \
Process Item  ← Runs N times (once per item)
  \ | /
   \|/
Collect (action: collect, enableSTM: true)
    |
Output Collected Results
```

**Key actors:**

### Split Actor
```yaml
configuration:
  options:
    action: split
    valueToSplit: ${{ msg.fetch_data.items }}
    emitKey: item
    limit: 100
```

### Collect Actor
```yaml
# MUST have enableSTM: true
enableSTM: true
configuration:
  options:
    action: collect
    splitId: ${{ msg.split_items.splitId }}
    size: ${{ msg.split_items.size }}
    captureValue:
      id: ${{ msg.process_item.id }}
      result: ${{ msg.process_item.result }}
    emitKey: processedItems
```

---

## Pattern 6: Error Handling with Continue on Error

**Use when:** Gracefully handling failures in non-critical steps.

**Examples:**
- API call might fail, continue with default
- Notification failure shouldn't stop workflow
- Optional enrichment step

**Flow diagram:**
```
Trigger
    |
Critical Step
    |
Optional Step (continueOnError: true)
    |
Router (check for error)
    |
   / \
Success  Error Handler
```

**Key configuration:**
```yaml
ACTR01optionalstep:
  continueOnError: true  # Workflow continues even if this fails
  # ...
```

**Checking for errors in Router:**
```yaml
configuration:
  options:
    conditions:
      Success: ${{ Q.isNil(err.optional_step) && !Q.isNil(msg.optional_step) }}
      # Default port handles error case
```

---

## Choosing the Right Pattern

| Scenario | Pattern | Key Indicator |
|----------|---------|---------------|
| Call multiple APIs, need ALL results combined | Multi-Source Aggregation | "combine", "merge", "all together" |
| Send to multiple destinations independently | Fire-and-Forget | "notify", "log", "trigger external" |
| Different logic based on data values | Conditional Branching | "if", "based on", "depending on" |
| Step-by-step transformation | Sequential Pipeline | "then", "after that", "next" |
| Process each item in array | Split and Collect | "each", "every", "batch", "list of" |
| Handle optional/risky steps | Error Handling | "might fail", "optional", "fallback" |

### Quick Decision Tree

```
Do you have parallel paths?
├── No → Pattern 4 (Sequential) or Pattern 3 (Router)
└── Yes → Do you need combined results from all paths?
    ├── No → Pattern 2 (Fire-and-Forget)
    └── Yes → Is it an array being processed item-by-item?
        ├── Yes → Pattern 5 (Split/Collect)
        └── No → Pattern 1 (Fork/ForkJoin)
```
