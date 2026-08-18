# Context Variables Reference

Context variables available in BorgIQ expressions (`${{ }}`).

## Table of Contents
1. [msg](#msg)
2. [ctx](#ctx)
3. [trigger](#trigger)
4. [inputs](#inputs)
5. [vars](#vars)
6. [credentials](#credentials)
7. [connection](#connection)
8. [results](#results)
9. [err](#err)

---

## msg

Messages emitted by upstream actors. Each actor's output is stored under its `msgVar` name.

**Access:** `${{ msg }}` or `${{ msg.ActorName }}`

**Example workflow:** `TriggerActor -> FetchUser -> ProcessData`

```yaml
# In ProcessData actor
configuration:
  inputs:
    userData: ${{ msg.fetch_user.body }}
    triggerId: ${{ msg.trigger_actor.id }}
```

**Structure:**
```json
{
  "trigger_actor": {
    "id": "...",
    "data": {...}
  },
  "fetch_user": {
    "body": {...},
    "statusCode": 200,
    "headers": {...}
  }
}
```

**Accessing the previous actor's output dynamically:**

To access the directly previous actor's output without hardcoding the `msgVar` name, use:
```yaml
${{ msg[ctx.sourceActor.msgVar] }}
```

This is useful when building reusable actors that don't need to know the specific upstream actor name.

---

## ctx

Runtime context with information about the current execution environment.

**Access:** `${{ ctx }}` or `${{ ctx.workspace.id }}`

**Structure:**
```json
{
  "org": {
    "id": "ORG001...",
    "name": "Organization Name"
  },
  "workspace": {
    "id": "WKSP01...",
    "name": "Workspace Name",
    "slug": "workspace-slug",
    "denoActorTimeoutInSeconds": 240,
    "lambdaTimeoutInSeconds": 240,
    "lambdaReservedConcurrentExecutions": 5,
    "lambdaMemorySizeInMB": 2048,
    "lambdaEphemeralStorageSizeInMB": 2048
  },
  "canvas": {
    "id": "CANV01...",
    "slug": "canvas-slug",
    "name": "Canvas Name",
    "webhookTriggers": {},
    "interfaceTriggers": {...}
  },
  "flowrun": {
    "id": "FLRN01...",
    "createdAt": "2025-09-05T15:43:58.142Z"
  },
  "trigger": {
    "id": "ACTR01...",
    "type": "InterfaceTriggerActor",
    "name": "Interface Trigger",
    "msgVar": "interface_trigger",
    "isActive": true
  },
  "actor": {
    "id": "ACTR01...",
    "type": "HttpRequestActor",
    "name": "Current Actor Name",
    "msgVar": "current_actor_msgvar",
    "isActive": true
  },
  "sourceActor": {
    "id": "ACTR01...",
    "type": "PreviousActorType",
    "name": "Previous Actor",
    "msgVar": "previous_actor"
  },
  "sourceType": "actor",
  "sourceMsgId": "FMSG01..."
}
```

**Note on `sourceMsgId`:** This ID is unique per message and can be used as an idempotency key for downstream systems when you need to ensure an operation is only performed once.

**Common uses:**
```yaml
# Include workspace info in request
body:
  workspaceId: ${{ ctx.workspace.id }}
  canvasName: ${{ ctx.canvas.name }}
  runId: ${{ ctx.flowrun.id }}
```

---

## trigger

The trigger event for the current firing — a discriminated union keyed by `trigger.type`. `trigger` is a top-level variable at the same level as `ctx` and `msg`, available **inside trigger actors' own configuration** (every trigger type, not just webhooks). In task actors `trigger` is `undefined` — downstream actors read the trigger's payload via `msg.<triggerMsgVar>` instead.

> **Don't confuse** top-level `trigger` (the firing event, documented here) with `ctx.trigger` / `ctx.triggerActor` (static metadata about the workflow's trigger actor: `id`, `type`, `name`, `msgVar` — see [ctx](#ctx)).

**Access:** `${{ trigger.type }}`, `${{ trigger.request.body }}`, `${{ trigger.request.headers['x-github-event'] }}`

**Variants** (full schema: [typescript/schemas.md → schemas/trigger](typescript/schemas.md#schemastrigger)):

| `trigger.type` | Extra fields |
|---|---|
| `webhook` | `request` — the parsed inbound HTTP request (shape below) |
| `schedule` | `triggeredAt` (this fire, ISO timestamp), `lastTriggeredAt?` (previous fire, if tracked) |
| `interface` | `user?` `{ id, name?, email }`; `submission?` `{ interfaceId, body }` — present on form post, absent on initial render |
| `app` | `user?` `{ id, name?, email }` |
| `lifecycle` | `event` — the lifecycle transition: `'canvas-enabled'` or `'canvas-disabled'` |
| `callable`, `email`, `button`, `mcpServer`, `manual` | none |

> **Migration:** the old top-level `request` variable was removed. Rewrite `${{ request.body }}` → `${{ trigger.request.body }}`, `${{ request.headers[...] }}` → `${{ trigger.request.headers[...] }}`, `${{ request.queryParams }}` → `${{ trigger.request.queryParams }}`.

**Critical distinction — `trigger.request` vs `msg.<triggerMsgVar>`:**

| Where you are | Use this to read the inbound HTTP payload |
|---|---|
| **Inside the trigger's own `options.webhook.response.*` config** (with `respondImmediately: true`) | `${{ trigger.request.body }}`, `${{ trigger.request.headers }}`, `${{ trigger.request.queryParams }}` |
| **In any downstream actor** (HttpRequest, Deno, Router, WebhookResponse, …) | `${{ msg.<triggerMsgVar>.body }}`, `${{ msg.<triggerMsgVar>.headers }}`, etc. |

The reason: at response-build time the trigger actor hasn't emitted yet, so `msg.<thisActor>` does not exist. The platform exposes the firing event as `trigger` so the response config can read the parsed HTTP request directly. Once the trigger emits, downstream actors see the same payload via `msg.<triggerMsgVar>` (the `WebhookTriggerActorResult` shape).

**`trigger.request` structure** (webhook firings; same shape as `WebhookTriggerActorResult`):

```json
{
  "meta": { "requestId": "...", "ipAddress": "...", "user": { "id": "...", "name": "...", "email": "..." } },
  "method": "POST",
  "headers": { "content-type": "application/json", "x-github-event": "push", "...": "..." },
  "body": { "...": "parsed JSON / form / text" },
  "queryParams": { "...": "..." },
  "rawBody": "raw body string, only when options.webhook.emitRawBody = true"
}
```

`meta.user` is only populated for app-authorized webhooks (`configuration.webhook.authorizationLevel: 'apps'`).

**Example — Slack `url_verification` challenge (CORRECT):**

Slack sends a one-time `url_verification` request with `{ "type": "url_verification", "challenge": "abc..." }` and expects the bare challenge string echoed back in the body. The trigger must answer immediately, so the `body` template runs at response-build time — use `trigger.request`, not `msg.<thisActor>`:

```yaml
configuration:
  webhook:                      # STATIC — literals only
    authorizationLevel: public
    allowedMethods: [post]
  options:
    webhook:                    # INTERPOLATABLE response behavior
      respondImmediately: true
      emitRawBody: false
      response:
        statusCode: 200
        headers:
          content-type: text/plain; charset=utf-8
        body: ${{ trigger.request?.body?.challenge || 'OK' }}     # ✅ correct
        # body: ${{ msg.receive_slack_event?.body?.challenge || 'OK' }}   ❌ msg.<this> doesn't exist yet
```

**Example — downstream actor reading the same webhook payload:**

```yaml
# In a downstream actor — the trigger has already emitted `msg.receive_slack_event`
configuration:
  inputs:
    eventType: ${{ msg.receive_slack_event.body.event.type }}
    teamId: ${{ msg.receive_slack_event.body.team_id }}
```

**Guarding by firing type:** `trigger.request` exists only on webhook firings. When a trigger can fire via more than one path (e.g. `UniversalTriggerActor` with `webhook.enabled`, `schedule.enabled` and/or a non-empty `lifecycle.events`), branch on `${{ trigger.type === 'webhook' }}` or use optional chaining: `${{ trigger?.request?.body?.x }}`. In task actors `trigger` is always `undefined`.

---

## inputs

Actor input parameters defined in the `configuration.inputs` section.

**Access:** `${{ inputs }}` or `${{ inputs.fieldName }}`

```yaml
configuration:
  inputs:
    userId: me
    maxResults: 100
  options:
    url: https://api.example.com/users/${{ inputs.userId }}
    queryParams:
      limit: ${{ inputs.maxResults }}
```

**Best Practice:** Always use optional chaining for potentially missing inputs:
```yaml
queryParams:
  pageToken: ${{ inputs?.pageToken }}
```

---

## vars

Computed variables defined in the `vars` section. Used for intermediate calculations.

**Access:** `${{ vars }}` or `${{ vars.varName }}`

**Definition order:** Variables are processed sequentially, so later vars can reference earlier ones.

```yaml
configuration:
  vars:
    - headerParts:
        - 'From: ${{ inputs.from }}'
        - 'To: ${{ inputs.to }}'
        - '${{ inputs.cc ? `Cc: ${inputs.cc}` : undefined }}'
    - cleanHeaders: ${{ Q.lo.compact(vars.headerParts) }}
    - encodedMessage: ${{ Q.toBase64(vars.cleanHeaders.join('\r\n')) }}
  options:
    body:
      message:
        raw: ${{ vars.encodedMessage }}
```

---

## credentials

Mapped credentials from the workspace. Credentials are mapped to the actor via workspace configuration.

**Access:** `${{ credentials }}` or `${{ credentials.credentialName }}`

**Important:** BorgIQ maps workspace credentials to actor credentials. A workspace credential named `TheGitHubApiKey` can be accessed as `credentials.apiKey` based on the mapping configuration.

```yaml
# Example: Using a credential in headers (not recommended for auth - use connection instead)
options:
  headers:
    X-Custom-Header: ${{ credentials.customCredential }}
```

**Security Note:** Never log or expose credentials. Always prefer using `connection` for authentication.

---

## connection

Single connection for actor authentication. **An actor can have only ONE connection.**

**Access:** `${{ connection }}` or `${{ connection.auth }}`

**Configuration:**
```yaml
configuration:
  options:
    url: https://api.example.com
    auth: ${{connection.auth}}
  connection:
    key: workspace-connection-key
    type: gmail  # optional; string for one allowed type, string[] for several
```

**How it works:**
1. Workspace stores connections with keys (e.g., `my-gmail-connection`)
2. Actor maps the connection via `connection.key`
3. HTTP Request Actor automatically builds auth headers/params from `connection.auth`

**Typed vs Untyped Connections:**
```yaml
# Untyped connection
connection:
  key: api-key-connection

# Typed connection (for OAuth services)
connection:
  key: john-gmail
  type: gmail

# Multi-type connection (when several connection types are acceptable)
connection:
  key: github-connection
  type:
    - github-oauth2
    - github-pat
```

---

## credentials

**Key rule:** An actor can have **only ONE connection**, but **multiple credentials**. Use credentials when an actor needs multiple credentials or auth sources.

**Access:** `${{ credentials }}` or `${{ credentials.credentialKey }}`

### Regular Credentials

For API keys, tokens, and other credentials:
```yaml
configuration:
  credentials:
    openai:
      workspaceKey: my-openai-key
  options:
    code: |
      const apiKey = credentials.openai;
```

### Connections as Credentials

When an actor needs multiple OAuth/workspace connections, use `source: connection`:
```yaml
configuration:
  credentials:
    google-sheets:
      workspaceKey: my-google-sheets-connection
      source: connection
    slack:
      workspaceKey: my-slack-connection
      source: connection
  options:
    code: |
      const googleAuth = credentials['google-sheets'].auth;
      const slackAuth = credentials['slack'].auth;
```

**Note:** Actors can use both `connection` and `credentials` together. For example, use `connection` for the primary auth and `credentials` for additional credentials like a private key to verify request signatures.

---

## results

Response after the actor completes its operation. Available in `error` and `outputs` sections.

**Access:** `${{ results }}`

**Structure (HttpRequestActor):**
```json
{
  "body": {...},
  "statusCode": 200,
  "headers": {
    "content-type": "application/json",
    "cache-control": "max-age=3600"
  }
}
```

**Structure (DenoActor):**
The `results` contains whatever the Deno function returns.

**Common uses (HTTP):**
```yaml
configuration:
  # Check for errors
  error:
    if: ${{!Q.isHTTPStatusInRange(results.statusCode, ["200-299"])}}
    retryIf: ${{Q.isHTTPStatusInRange(results.statusCode, ["429", "500-599"])}}
    message: ${{Q.toJSON(results)}}

  # Transform output
  outputs: ${{ results.body.data }}
```

---

## err

Error information from upstream actors (when `continueOnError: true`).

**Access:** `${{ err }}`

**Use case:** Processing errors from previous actors that had `continueOnError` enabled.

```yaml
configuration:
  inputs:
    previousError: ${{ err?.message || 'No error' }}
```

---

## Interpolation Order Summary

1. **inputs** → Uses: `msg`, `ctx`, `err` (plus `trigger` in trigger actors)
2. **vars** → Uses: `inputs`, `msg`, `ctx`, `err` (plus `trigger` in trigger actors)
3. **options** → Uses: `inputs`, `vars`, `msg`, `ctx`, `err` (plus `trigger` in trigger actors — this is where `options.webhook.response.body` lives)
4. Actor executes, populates `results`
5. **error** → Uses: `results`, `inputs`, `vars`, `msg`, `ctx`
6. **outputs** → Uses: `results`, `inputs`, `vars`, `msg`, `ctx` (only if no error)

For trigger actors, the firing event is available as the top-level `trigger` variable (see [the `trigger` section](#trigger)); on webhook firings the inbound request is `trigger.request` — **not** `msg.<thisActor>`, which doesn't exist until the trigger emits.

---

## Q Library

The `Q` object provides utility functions in expressions. See [q-lib.md](q-lib.md) for full reference.

**Key libraries:**
- `Q.lo` - Full Lodash library
- `Q.dateFns` - Full date-fns library

---

## Expression Examples

### Basic JavaScript

```yaml
# Current timestamp
timestamp: ${{ Date.now() }}

# String template
greeting: ${{ `Hello, ${inputs.name}!` }}

# Ternary conditional
status: ${{ inputs.active ? 'Active' : 'Inactive' }}
```

### Multi-line IIFE Pattern

For complex logic, use an Immediately Invoked Function Expression:

```yaml
${{(() => {
    const persons = msg.upstream_actor.data;

    let results = Q.lo.chain(persons)
      .filter(p => p.birthYear > inputs.minYear && p.country !== 'US')
      .groupBy(p => `${p.birthYear}`)
      .value();

    return results;
  })()}}
```

### Working with Arrays

```yaml
# Concat lists
combined: ${{ Q.lo.concat(inputs.firstList, inputs.secondList) }}

# Filter and map
names: ${{ Q.lo.chain(msg.users.data).filter(u => u.active).map(u => u.name).value() }}

# Remove falsy values
clean: ${{ Q.lo.compact([1, null, 2, undefined, 3]) }}

# Unique values
unique: ${{ Q.lo.uniq(inputs.items) }}
```

### Conditional Headers/Fields

```yaml
vars:
  - headerParts:
      - 'From: ${{ inputs.from }}'
      - 'To: ${{ inputs.to }}'
      - '${{ inputs.cc ? `Cc: ${inputs.cc}` : undefined }}'
  - cleanHeaders: ${{ Q.lo.compact(vars.headerParts) }}
```

### Date Formatting

```yaml
inputs:
  formattedDate: ${{ Q.dateFns.format(Q.now(), 'yyyy-MM-dd HH:mm:ss') }}
  weekAgo: ${{ Q.dateFns.subDays(Q.now(), 7).toISOString() }}
  isRecent: ${{ Q.dateFns.isAfter(msg.record.createdAt, Q.dateFns.subDays(Q.now(), 30)) }}
```

### Data Format Conversion

```yaml
# JSON to string
jsonBody: ${{ Q.toJSON({ name: inputs.name, data: msg.upstream.body }) }}

# Parse JSON string
parsed: ${{ Q.parseJSON(msg.webhook.body) }}

# CSV conversion
csvOutput: ${{ Q.toCSV(msg.records.data) }}
```

### Error Handling with Status Codes

```yaml
error:
  if: ${{ !Q.isHTTPStatusInRange(results.statusCode, ["200-299"]) }}
  retryIf: ${{ Q.isHTTPStatusInRange(results.statusCode, ["429", "500-599"]) }}
  message: ${{ Q.toJSON(results) }}
```

### Safe Property Access

```yaml
# Optional chaining for potentially missing values
token: ${{ inputs?.pageToken }}
email: ${{ msg.user?.profile?.email || 'unknown' }}

# Lodash get with default
value: ${{ Q.lo.get(msg.response, 'data.items[0].name', 'default') }}
```

### Cryptographic Operations

```yaml
# Generate unique IDs
id: ${{ Q.uuid() }}
ulid: ${{ Q.ulid() }}

# Hash data
hash: ${{ Q.hash('SHA256', inputs.sensitiveData) }}

# Sign JWT
token: ${{ Q.jwtSign({ userId: inputs.userId }, credentials.jwtSecret, { expiresIn: '1h' }) }}
```

### Text Processing

```yaml
# HTML escaping
safe: ${{ Q.escapeHTML(inputs.userInput) }}

# Markdown to HTML
html: ${{ Q.markdownToHTML(msg.content.body) }}

# Base64 encoding
encoded: ${{ Q.toBase64(vars.rawMessage) }}
```
