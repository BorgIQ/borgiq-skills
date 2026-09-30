# Migration from Automation Platforms (n8n, Zapier, Make)

This guide maps concepts from n8n, Zapier, and Make to their BorgIQ equivalents, helping you migrate existing automations.

## Table of Contents

- [Core Concept Mapping](#core-concept-mapping)
- [Integration Migration: Use HttpRequestActor](#integration-migration-use-httprequestactor)
  - [Why HttpRequestActor Over Native Connectors](#why-httprequestactor-over-native-connectors)
  - [Authentication Migration](#authentication-migration)
  - [Migration Examples by Platform](#migration-examples-by-platform)
- [Data Transformation: Use MessageProcessorActor](#data-transformation-use-messageprocessoractor)
  - [Expression Migration](#expression-migration)
  - [Common Transformation Patterns](#common-transformation-patterns)
- [Trigger Migration](#trigger-migration)
- [Flow Control Migration](#flow-control-migration)
- [BorgIQ Capabilities to Consider During Migration](#borgiq-capabilities-to-consider-during-migration)
- [Migration Checklist](#migration-checklist)

---

## Core Concept Mapping

| n8n | Zapier | Make | **BorgIQ** |
|-----|--------|------|------------|
| Workflow | Zap | Scenario | **Canvas** (contains one or more workflows) |
| Trigger Node | Trigger | Trigger Module | **Trigger Actor** (one per workflow) |
| Node | Action | Module | **Task Actor** |
| Connection | — | Route | **Edge** (connection between actors) |
| Execution | Zap run | Execution | **Flowrun** |
| Credential | Connection | Connection | **Connection** (auth credentials) |
| Expression `{{ }}` | Formatter / Paths | `{{ }}` | **`${{ }}` expressions** with Q-lib |
| Code Node | Code by Zapier | Code Module | **DenoActor** or **PythonActor** |
| HTTP Request Node | Webhooks by Zapier | HTTP Module | **HttpRequestActor** |
| IF Node | Filter / Paths | Router / Filter | **RouterActor** or MessageProcessorActor (`filter`) |
| Switch Node | Paths | Router | **RouterActor** (multiple sourcePorts) |
| Set Node | Formatter | Set Variable | **MessageProcessorActor** (`inject`) |
| Split In Batches | Looping | Iterator | **MessageProcessorActor** (`split` / `collect`) |
| Merge Node | — | Aggregator | **MessageProcessorActor** (`forkJoin`) |
| Wait Node | Delay | Sleep | **MessageProcessorActor** (`delayBySeconds`) |
| Webhook Node | Webhooks by Zapier | Webhook | **WebhookTriggerActor** |
| Schedule Trigger | Schedule by Zapier | Schedule Module | **ScheduledTriggerActor** |
| Sub-workflow | — | Scenario link | **CallFlowActor** → **CallableTriggerActor** |
| — | Tables / Storage by Zapier | Data Store | **CollectionActor** |
| — | — | — | **AiActor** (LLM-powered tasks) |
| — | — | — | **AiAgentActor** (autonomous AI agent) |
| — | — | — | **AgentHarnessActor** (Claude in a Box) |

---

## Integration Migration: Use HttpRequestActor

### Why HttpRequestActor Over Native Connectors

In n8n, Zapier, and Make, each SaaS integration has a dedicated connector (e.g., "Slack Node", "Gmail Action", "Google Sheets Module"). In BorgIQ, **search the template catalog first** (`borgiq templates apps --search "<vendor>"`, and, with `@borgiq/cli` 0.13.0 or later, `borgiq recipes list` for a multi-actor flow): a template is a vetted, preconfigured actor, usually an HttpRequestActor. Hand-build an **HttpRequestActor** — a universal REST client — only when no template fits.

**Advantages:**
- Works with any API that has REST endpoints (which is virtually all of them)
- Full control over headers, query params, body, and auth
- No waiting for connector updates when APIs change
- One actor type to learn instead of hundreds of connector-specific UIs

**When to use something else:**
| Scenario | Use Instead |
|----------|-------------|
| Send email | **SendEmailActor** (built-in, no SMTP config needed) |
| AI text generation, summarization, classification | **AiActor** |
| Complex multi-step AI tasks with tools | **AiAgentActor** |
| Store/retrieve structured data | **CollectionActor** |
| Custom logic requiring code | **DenoActor** or **PythonActor** |

### Authentication Migration

BorgIQ Connections map directly to platform credentials. HttpRequestActor accesses auth via `${{ connection.auth }}`.

| Platform Auth | BorgIQ Connection Type | HttpRequestActor Usage |
|---------------|----------------------|----------------------|
| OAuth2 token | OAuth2 | `auth: ${{ connection.auth }}` — automatically refreshes and injects Bearer token |
| API key in header | API Key (Header) | `auth: ${{ connection.auth }}` — injects as configured header |
| API key in query | API Key (Query) | `auth: ${{ connection.auth }}` — appends to query params |
| Basic auth | Basic Auth | `auth: ${{ connection.auth }}` — injects Authorization header |
| Custom headers | Custom Auth | `auth: ${{ connection.auth }}` — injects custom headers/params |

### Migration Examples by Platform

The examples below are actor fragments (`type`, `name`, `msgVar`, `configuration`); see [Common Actor Structure](../SKILL.md#common-actor-structure) for the full actor.

#### n8n: Slack "Send Message" Node → BorgIQ

**n8n configuration:**
```
Node: Slack → Send Message
Channel: #general
Text: Hello from n8n!
Authentication: OAuth2
```

**BorgIQ equivalent:**
```yaml
type: HttpRequestActor
name: Send Slack message
msgVar: send_slack_message
configuration:
  options:
    url: https://slack.com/api/chat.postMessage
    method: POST
    auth: ${{ connection.auth }}
    contentType: json
    body:
      channel: general
      text: Hello from BorgIQ!
  connection:
    key: my-slack              # the workspace connection's key
    type: slack-oauth2         # a registered connection type
  error:
    if: ${{ !Q.isHTTPStatusInRange(results.statusCode, ["200-299"]) }}
    retryIf: ${{ Q.isHTTPStatusInRange(results.statusCode, ["429", "500-599"]) }}
    includeResult: true
    message: ${{ Q.toJSON(results) }}
```

#### Zapier: Google Sheets "Create Row" → BorgIQ

**Zapier configuration:**
```
App: Google Sheets → Create Spreadsheet Row
Spreadsheet: Sales Tracker
Worksheet: Sheet1
Fields: Name, Email, Amount
```

**BorgIQ equivalent:**
```yaml
type: HttpRequestActor
name: Add Google Sheets row
msgVar: add_google_sheets_row
configuration:
  inputs:
    spreadsheetId: ${{ msg.trigger.body.spreadsheetId }}
    name: ${{ msg.trigger.body.name }}
    email: ${{ msg.trigger.body.email }}
    amount: ${{ msg.trigger.body.amount }}
  options:
    url: https://sheets.googleapis.com/v4/spreadsheets/${{ inputs.spreadsheetId }}/values/Sheet1!A1:append
    method: POST
    auth: ${{ connection.auth }}
    contentType: json
    queryParams:
      valueInputOption: USER_ENTERED
    body:
      values:
        - - ${{ inputs.name }}
          - ${{ inputs.email }}
          - ${{ inputs.amount }}
  connection:
    key: my-google-sheets
    type: google-sheets
```

#### Make: Airtable "Create Record" → BorgIQ

**Make configuration:**
```
Module: Airtable → Create a Record
Base: CRM
Table: Contacts
Fields: Name, Company, Status
```

**BorgIQ equivalent:**
```yaml
type: HttpRequestActor
name: Create Airtable record
msgVar: create_airtable_record
configuration:
  inputs:
    baseId: ${{ msg.trigger.body.baseId }}
    name: ${{ msg.trigger.body.name }}
    company: ${{ msg.trigger.body.company }}
  options:
    url: https://api.airtable.com/v0/${{ inputs.baseId }}/Contacts
    method: POST
    auth: ${{ connection.auth }}
    contentType: json
    body:
      fields:
        Name: ${{ inputs.name }}
        Company: ${{ inputs.company }}
        Status: New
  connection:
    key: my-airtable-token     # a bearer connection; omit `type` to accept any connection
```

---

## Data Transformation: Use MessageProcessorActor

In other platforms, data transformation happens through platform-specific expression syntax or dedicated "Formatter" / "Set" nodes. In BorgIQ, **MessageProcessorActor with the `inject` action** is the standard for data transformation.

### Expression Migration

| n8n | Zapier | Make | **BorgIQ** |
|-----|--------|------|------------|
| `{{ $json.field }}` | `{{steps.trigger.field}}` | `{{1.field}}` | `${{ msg.actor_name.field }}` |
| `{{ $now }}` | — | `{{now}}` | `${{ Q.now() }}` |
| `{{ $json.items.length }}` | — | `{{length(1.items)}}` | `${{ msg.actor_name.items.length }}` |
| `{{ $json.name.toUpperCase() }}` | Formatter: Transform Text | `{{upper(1.name)}}` | `${{ msg.actor_name.name.toUpperCase() }}` |
| `{{ DateTime.now().toFormat('yyyy-MM-dd') }}` | Formatter: Date | `{{formatDate(now; "YYYY-MM-DD")}}` | `${{ Q.dateFns.format(Q.now(), 'yyyy-MM-dd') }}` |

### Common Transformation Patterns

#### Reshape API response (n8n "Set" / Zapier "Formatter" / Make "Set Variable")

```yaml
type: MessageProcessorActor
name: Transform response
msgVar: transform_response
configuration:
  options:
    action: inject
    payload:
      fullName: ${{ msg.api_call.body.first_name + ' ' + msg.api_call.body.last_name }}
      email: ${{ msg.api_call.body.email_address }}
      createdDate: ${{ Q.dateFns.format(msg.api_call.body.created_at, 'yyyy-MM-dd') }}
      isActive: ${{ msg.api_call.body.status === 'active' }}
```

#### Process array items (n8n "Split In Batches" / Make "Iterator + Aggregator")

```yaml
# Split array into individual items
- type: MessageProcessorActor
  name: Split items
  msgVar: split_items
  configuration:
    options:
      action: split
      valueToSplit: ${{ msg.api_call.body.records }}
      emitKey: record
      limit: 100

# Process each item (e.g., call an API per item)
- type: HttpRequestActor
  name: Process each item
  msgVar: process_item
  continueOnError: true        # or collect waits forever for a failed item
  configuration:
    options:
      url: https://api.example.com/items/${{ msg.split_items.record.id }}
      method: PUT
      body:
        status: processed

# Recombine results
- type: MessageProcessorActor
  name: Collect results
  msgVar: collect_results
  enableSTM: true
  configuration:
    options:
      action: collect
      splitId: ${{ msg.split_items.splitId }}
      size: ${{ msg.split_items.size }}
      captureValue: ${{ msg.process_item ?? err.process_item }}
      emitKey: processedItems
```

#### Conditional filtering (n8n "IF" / Zapier "Filter" / Make "Filter")

```yaml
# Simple filter — stops message if condition is false
- type: MessageProcessorActor
  name: Filter active only
  msgVar: filter_active
  configuration:
    options:
      action: filter
      filter: ${{ msg.api_call.body.status === 'active' }}

# Multi-branch routing — use RouterActor instead
- type: RouterActor
  name: Route by status
  msgVar: route_by_status
  sourcePorts:                 # one port per route; conditions are keyed by port name
    - id: SPRTactive0          # borgiq generate id sourceport
      name: Active
    - id: SPRTinactiv
      name: Inactive
    - id: SPRTdefault          # fallback: takes no condition
      name: Pending
  configuration:
    options:
      emitType: singleRoute
      conditions:
        Active: ${{ msg.api_call.body.status === 'active' }}
        Inactive: ${{ msg.api_call.body.status === 'inactive' }}
```

---

## Trigger Migration

| Platform Trigger | BorgIQ Trigger |
|-----------------|----------------|
| Webhook / "Catch Hook" | **WebhookTriggerActor** — receives HTTP POST/GET from external services |
| Schedule / Cron | **ScheduledTriggerActor** — cron expression or interval |
| Email received | **EmailTriggerActor** — fires on inbound email to workspace address |
| Manual / Button | **ButtonTriggerActor** — manual trigger from BorgIQ UI |
| Form submission | **InterfaceTriggerActor** — renders a form, triggers on submit |
| Web app interaction | **ReactAppTriggerActor** — React app compiled and hosted on the canvas (AppTriggerActor for legacy raw-HTML apps) |
| Sub-workflow call | **CallableTriggerActor** — invoked by CallFlowActor from another workflow |

**Zapier-specific note:** Zapier's polling triggers (which check APIs on intervals) map to **ScheduledTriggerActor → HttpRequestActor** in BorgIQ. Set up a scheduled trigger and make the API call explicitly.

**Make-specific note:** Make's "Watch" modules (e.g., "Watch New Rows") also map to either **WebhookTriggerActor** (if the service supports webhooks) or **ScheduledTriggerActor → HttpRequestActor** (polling pattern).

---

## Flow Control Migration

### Parallel Execution

| Platform | How | BorgIQ |
|----------|-----|--------|
| n8n | Explicit "Split" or multiple outputs | **Automatic** — connect one actor to multiple downstream actors |
| Zapier | Paths | **Automatic** — all downstream actors run concurrently |
| Make | Router module | **Automatic** — or use **RouterActor** for conditional branching |

BorgIQ executes all downstream actors concurrently by default. No configuration needed.

### Combining Parallel Results

| Platform | How | BorgIQ |
|----------|-----|--------|
| n8n | Merge Node | **MessageProcessorActor** (`fork` → parallel paths → `forkJoin`) |
| Zapier | — | **MessageProcessorActor** (`forkJoin`) |
| Make | Aggregator | **MessageProcessorActor** (`collect` or `forkJoin`) |

### Error Handling

| Platform | How | BorgIQ |
|----------|-----|--------|
| n8n | Error Trigger, try/catch node | **`error` block** on any actor — `if`, `retryIf`, `message`, `includeResult` — plus `continueOnError: true` to route the failure to `err.<msgVar>` |
| Zapier | Auto-replay | **`error.retryIf`** with status code checks |
| Make | Error handler route, Break/Resume | **`error` block** + **RouterActor** for conditional error handling |

```yaml
# Standard error handling pattern for API calls
type: HttpRequestActor
name: API call
msgVar: api_call
configuration:
  options:
    url: https://api.example.com/data
    method: GET
    auth: ${{ connection.auth }}
  connection:
    key: my-api-connection
  error:
    if: ${{ !Q.isHTTPStatusInRange(results.statusCode, ["200-299"]) }}
    retryIf: ${{ Q.isHTTPStatusInRange(results.statusCode, ["429", "500-599"]) }}
    includeResult: true
    message: ${{ Q.toJSON(results) }}
```

### Sub-workflows / Reusable Components

| Platform | How | BorgIQ |
|----------|-----|--------|
| n8n | Sub-workflow node | **CallFlowActor** → **CallableTriggerActor** (+ **CallableResponseActor** to return data) |
| Zapier | Sub-Zaps | **CallFlowActor** across canvases/workspaces |
| Make | Scenario link | **CallFlowActor** with `workspaceSlug` / `canvasSlug` |

---

## BorgIQ Capabilities to Consider During Migration

Rather than porting every workflow one-to-one, look for steps these capabilities can replace or upgrade:

| Capability | Actor | What It Does |
|-----------|-------|-------------|
| **AI-powered tasks** | AiActor | LLM text generation, classification, structured extraction as a workflow node |
| **Autonomous AI agents** | AiAgentActor | AI coding agent with a private workspace (filesystem + bash) that also calls tools (other actors) until the task is done; sessions continue via `sessionId` |
| **Claude in a Box** | AgentHarnessActor | Runs Claude Code in a sandbox — any business process codified as a skill becomes a workflow node |
| **Persistent storage** | CollectionActor | Built-in key-value collections with queries, TTL, labels, and transactions |
| **Custom web apps** | ReactAppTriggerActor | React app compiled server-side and served on the canvas, calling flows through webhook endpoints (AppTriggerActor for legacy raw-HTML apps) |
| **Rich forms** | InterfaceTriggerActor / InterfaceActor | Configurable form components (text, select, date, file upload, etc.) as triggers or mid-flow |
| **AI routing** | AiRouterActor | Route messages using LLM classification instead of hardcoded conditions |
| **Human-in-the-loop** | MessageProcessorActor | `issueCallbackToken` / `waitForCallbackToken` for approval workflows |
| **Webhook responses** | WebhookResponseActor | Return dynamic HTTP responses to webhook callers (status, headers, body) |

---

## Migration Checklist

1. **Inventory your automations** — list all workflows, their triggers, and integrations used
2. **Map triggers** — identify the BorgIQ trigger type for each workflow (see [Trigger Migration](#trigger-migration))
3. **Map integrations** — for each SaaS connector, search templates (and recipes) first; when none fits, build an HttpRequestActor:
   - Find the API documentation for the service
   - Note the endpoint URL, method, and required headers
   - Set up a BorgIQ Connection with the appropriate auth type
4. **Map data transformations to MessageProcessorActor** — replace Formatter/Set/Code nodes:
   - Simple field mapping → `inject` action with `${{ }}` expressions
   - Array processing → `split` / `collect`
   - Conditional logic → `filter` or RouterActor
5. **Map flow control** — parallel paths are automatic; use `fork`/`forkJoin` only when combining results
6. **Consider AI upgrades** — look for workflows that could benefit from:
   - AiActor for classification, extraction, or summarization steps
   - AiAgentActor for complex multi-step decisions
   - AgentHarnessActor for processes already codified as Claude Code skills
7. **Test incrementally** — migrate one workflow at a time, verify outputs match
