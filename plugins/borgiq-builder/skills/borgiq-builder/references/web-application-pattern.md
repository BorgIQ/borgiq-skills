# Web Application Pattern

Build web applications using App Trigger and Webhook Trigger actors. This pattern creates interactive single-page applications where the frontend communicates with a backend API.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Connection Mechanism](#connection-mechanism)
- [Key Components](#key-components)
- [Pattern Implementation](#pattern-implementation)
- [Complete Example: Weather App](#complete-example-weather-app)
- [Complete Example: TODO App](#complete-example-todo-app)
- [Multiple Webhook Handlers (Resource Separation)](#multiple-webhook-handlers-resource-separation)
- [Best Practices](#best-practices)
- [Common Mistakes](#common-mistakes)
- [When to Use This Pattern](#when-to-use-this-pattern)

---

## Overview

This pattern enables building interactive web applications entirely within BorgIQ by combining:

1. **AppTriggerActor** - Hosts the frontend HTML/CSS/JS application via separate `html`, `css`, and `script` fields
2. **WebhookTriggerActor** - Provides a REST API endpoint for the frontend
3. **Task Actors** - Process API requests (DenoActor, AiActor, HttpRequestActor, etc.)
4. **WebhookResponseActor** - Returns JSON responses to the frontend

**Key insight:** App and Webhook triggers are NOT connected via edges (you cannot connect upstream actors to triggers). Instead, they are connected via the webhook URL passed to the frontend code.

**Note:** AppTriggerActor does **not** emit messages and does **not** trigger downstream actors. It purely hosts the web application. For form-based workflows that trigger downstream processing, use [InterfaceTriggerActor](interface-trigger-actor.md) instead.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Canvas (Workflow)                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────┐                                   │
│  │  AppTriggerActor         │  ← Hosts the web application      │
│  │  (Frontend)              │                                   │
│  │                          │                                   │
│  │  - html/css/script       │                                   │
│  │  - CSP configuration     │                                   │
│  └──────────────────────────┘                                   │
│              │                                                   │
│              │ fetch() via webhook URL                           │
│              │ (NOT an edge connection)                          │
│              ▼                                                   │
│  ┌──────────────────────────┐                                   │
│  │  WebhookTriggerActor     │  ← API endpoint                   │
│  │  (Backend API)           │                                   │
│  └──────────────────────────┘                                   │
│              │                                                   │
│              │ edge connection                                   │
│              ▼                                                   │
│  ┌──────────────────────────┐                                   │
│  │  Task Actor(s)           │  ← Business logic                 │
│  │  (DenoActor, AiActor,    │                                   │
│  │   HttpRequestActor, etc) │                                   │
│  └──────────────────────────┘                                   │
│              │                                                   │
│              │ edge connection                                   │
│              ▼                                                   │
│  ┌──────────────────────────┐                                   │
│  │  WebhookResponseActor    │  ← Returns JSON response          │
│  └──────────────────────────┘                                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Connection Mechanism

### How AppTriggerActor Connects to Webhook

The AppTriggerActor accesses the WebhookTriggerActor's URL through the context variable:

```yaml
# In AppTriggerActor configuration
configuration:
  inputs:
    apiURL: ${{ ctx.canvas.webhookTriggers.<webhook_msgVar>.url }}
```

This URL is then used in the frontend JavaScript (either inline in `html` or in the `script` field):

```javascript
const API_URL = '${{inputs.apiURL}}';

// Use fetch() to call the webhook
async function fetchData() {
    const response = await fetch(`${API_URL}?param=value`);
    const data = await response.json();
    // Process data...
}
```

### Context Variable Reference

| Variable | Description |
|----------|-------------|
| `ctx.canvas.webhookTriggers.<msgVar>.url` | Full webhook URL for the specified WebhookTriggerActor |

**Note:** `<msgVar>` is the `msgVar` property of the WebhookTriggerActor (e.g., `weather_api_handler`, `todo_api`).

---

## Key Components

### 1. AppTriggerActor (Frontend)

Hosts the web application with separate `html`, `css`, and `script` fields. See [app-trigger-actor.md](app-trigger-actor.md) for the full options reference.

```yaml
ACTR01appactor:
  type: AppTriggerActor
  name: My Web Application
  msgVar: my_web_application
  configuration:
    inputs:
      apiURL: ${{ ctx.canvas.webhookTriggers.my_api_handler.url }}
    options:
      html: |
        <!DOCTYPE html>
        <html>
        <head>
            <title>My Application</title>
            <link href="https://fonts.googleapis.com/css2?family=Inter&display=swap" rel="stylesheet">
        </head>
        <body>
            <!-- Application HTML -->
        </body>
        </html>
      css: |
        body { font-family: 'Inter', sans-serif; }
      script: |
        const API_URL = '${{inputs.apiURL}}';
        // Application JavaScript
      allowedStyleDomains:
        - https://fonts.googleapis.com
        - https://fonts.gstatic.com
        - https://cdn.jsdelivr.net
      allowedScriptDomains:
        - https://cdn.jsdelivr.net
```

### 2. WebhookTriggerActor (Backend API)

Receives HTTP requests from the frontend:

```yaml
ACTR01webhookactor:
  type: WebhookTriggerActor
  name: API Handler
  msgVar: api_handler
  configuration:
    options:
      allowedMethods:
        - get
        - post
      respondImmediately: false  # Wait for WebhookResponseActor
      emitRawBody: false
      response:
        statusCode: 200
        headers:
          content-type: text/plain; charset=utf-8
        body: OK
```

### 3. Task Actors (Business Logic)

Process the request with DenoActor, AiActor, HttpRequestActor, etc.:

```yaml
ACTR01processactor:
  type: DenoActor
  name: Process Request
  msgVar: process_request
  configuration:
    inputs:
      param: ${{ msg.api_handler.queryParams.param }}
    options:
      allowNet: true
    codeDir:
      - path: main.ts
        content: |
          import type { Request, Response } from "@borgiq/actors";
          export default async function receive(req: Request): Promise<Response> {
            // Process the request
            const result = await someOperation(req.inputs.param);
            return { results: result };
          }
```

### 4. WebhookResponseActor (Return Response)

Sends JSON response back to the frontend:

```yaml
ACTR01responseactor:
  type: WebhookResponseActor
  name: Return Response
  msgVar: return_response
  configuration:
    options:
      statusCode: 200
      body: ${{ msg.process_request }}
      headers:
        content-type: application/json
```

---

## Pattern Implementation

### Step-by-Step Guide

1. **Create the WebhookTriggerActor first** - This generates the webhook URL
2. **Create the AppTriggerActor** - Reference the webhook URL via `ctx.canvas.webhookTriggers.<msgVar>.url`
3. **Add Task Actors** - Connect to WebhookTriggerActor via edges
4. **Add WebhookResponseActor** - Connect to the last Task Actor

### Minimal YAML Structure

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  # Frontend - App Trigger
  ACTR01frontend:
    type: AppTriggerActor
    name: Web Application
    msgVar: web_application
    description: Hosts the web application frontend
    version: 1
    isActive: true
    enableLTM: false
    enableSTM: false
    continueOnError: false
    sourcePorts:
      - id: SPRTdefault
    configuration:
      inputs:
        apiURL: ${{ ctx.canvas.webhookTriggers.api_handler.url }}
      options:
        html: |
          <!DOCTYPE html>
          <html>
          <body>
              <div id="app"></div>
          </body>
          </html>
        script: |
          const API_URL = '${{inputs.apiURL}}';
          // Application code
    schemas: {}
    id: ACTR01frontend
    position:
      x: 0
      'y': 0
    edges: {}

  # Backend - Webhook Trigger
  ACTR01backend:
    type: WebhookTriggerActor
    name: API Handler
    msgVar: api_handler
    description: Receives API requests from the frontend
    version: 1
    isActive: true
    enableLTM: false
    enableSTM: false
    continueOnError: false
    sourcePorts:
      - id: SPRTdefault
    configuration:
      options:
        allowedMethods:
          - get
          - post
        respondImmediately: false
    schemas: {}
    id: ACTR01backend
    position:
      x: 0
      'y': 600
    edges:
      EDGE01toprocess:
        id: EDGE01toprocess
        sourceActorId: ACTR01backend
        sourcePortId: SPRTdefault
        targetActorId: ACTR01process
        targetPortId: TPRTdefault
        type: borgiqEdge

  # Business Logic - Deno Actor
  ACTR01process:
    type: DenoActor
    name: Process Request
    msgVar: process_request
    description: Processes API requests with business logic
    version: 1
    isActive: true
    enableLTM: false
    enableSTM: false
    continueOnError: false
    sourcePorts:
      - id: SPRTdefault
    configuration:
      inputs:
        query: ${{ msg.api_handler.queryParams }}
      options:
        allowNet: true
      codeDir:
        - path: main.ts
          content: |
            import type { Request, Response } from "@borgiq/actors";
            export default async function receive(req: Request): Promise<Response> {
              // Business logic here
              return { results: { result: "success", data: req.inputs.query } };
            }
    schemas: {}
    id: ACTR01process
    position:
      x: 0
      'y': 800
    edges:
      EDGE01toresponse:
        id: EDGE01toresponse
        sourceActorId: ACTR01process
        sourcePortId: SPRTdefault
        targetActorId: ACTR01response
        targetPortId: TPRTdefault
        type: borgiqEdge

  # Response - Webhook Response Actor
  ACTR01response:
    type: WebhookResponseActor
    name: Return Response
    msgVar: return_response
    description: Returns JSON response to the frontend
    version: 1
    isActive: true
    enableLTM: false
    enableSTM: false
    continueOnError: false
    sourcePorts:
      - id: SPRTdefault
    configuration:
      options:
        statusCode: 200
        body: ${{ msg.process_request }}
        headers:
          content-type: application/json
    schemas: {}
    id: ACTR01response
    position:
      x: 0
      'y': 1000
    edges: {}
```

---

## Complete Example: Weather App

A weather application that fetches weather data from external APIs.

### Flow Structure

```
AppTriggerActor (Weather App UI)
         │
         │ fetch() via webhook URL
         ▼
WebhookTriggerActor (Weather API Handler)
         │
         │ edge
         ▼
DenoActor (Fetch Weather Data)
         │
         │ edge
         ▼
WebhookResponseActor (Return Response)
```

### Key Configuration Points

**AppTriggerActor:**
```yaml
configuration:
  inputs:
    apiURL: ${{ ctx.canvas.webhookTriggers.weather_app_handler.url }}
  options:
    html: |
      <!-- Full HTML application structure -->
    script: |
      const API_URL = '${{inputs.apiURL}}';
      // fetch() calls to API_URL
    allowedStyleDomains:
      - https://fonts.googleapis.com
      - https://cdn.jsdelivr.net
```

**WebhookTriggerActor:**
```yaml
configuration:
  options:
    allowedMethods:
      - get
      - post
    respondImmediately: false
```

**DenoActor (Weather Fetcher):**
```yaml
configuration:
  inputs:
    query: ${{ msg.weather_app_handler.queryParams.city }}
  options:
    allowNet: true
    allowNetList:
      - api.weatherapi.com
      - api.open-meteo.com
```

**WebhookResponseActor:**
```yaml
configuration:
  options:
    statusCode: 200
    body: ${{ msg.fetch_weather_data }}
    headers:
      content-type: application/json
```

---

## Complete Example: TODO App

A task management application with CRUD operations.

### Flow Structure

```
AppTriggerActor (TODO App UI)
         │
         │ fetch() via webhook URL
         ▼
WebhookTriggerActor (TODO API Handler)
         │
         │ edge
         ▼
DenoActor (Handle CRUD Operations)
         │
         │ edge
         ▼
WebhookResponseActor (Return Response)
```

### API Endpoint Design

The WebhookTriggerActor can handle multiple operations based on query parameters or HTTP method:

```javascript
// In frontend JavaScript (in the script field)
async function getTodos() {
    const response = await fetch(`${API_URL}?action=list`);
    return await response.json();
}

async function addTodo(task) {
    const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'add', task })
    });
    return await response.json();
}

async function deleteTodo(id) {
    const response = await fetch(`${API_URL}?action=delete&id=${id}`);
    return await response.json();
}
```

### Backend Logic with CollectionActor

For persistent storage, use CollectionActor (see [collection-actor.md](collection-actor.md)):

```
WebhookTriggerActor
         │
         ▼
RouterActor (Route by action)
    ┌────┼────┐
    │    │    │
    ▼    ▼    ▼
  List  Add  Delete  (each with CollectionActor)
    │    │    │
    └────┼────┘
         ▼
WebhookResponseActor
```

**Actions:** Use `query` to list items, `putItem` to add, and `deleteItem` to remove. Create the collection first with `createCollection` (via the app's migration runner — see [collection-migrations.md](collection-migrations.md)).

**One collection per app:** model every entity type the app stores in a single collection with key prefixes (`task:<id>`, `user:<id>`, `config:<name>`) and query by prefix (`task:*`) — do not create one collection per entity type. The migration runner also publishes a `$meta` manifest row listing those prefixes so the collection is navigable from its first row in the UI. See [collection-api.md → Single-Collection Design](collection-api.md#single-collection-design).

---

## Simplified Architecture Variants

The full 4-actor pattern (AppTrigger → WebhookTrigger → TaskActor → WebhookResponseActor) is not always necessary. Choose the simplest architecture that fits:

### Variant 1: DenoActor with `webhookRespond` Signal

When using a DenoActor for business logic, respond directly to the webhook caller using the `webhookRespond` signal instead of adding a separate WebhookResponseActor. This saves ~300ms per request.

```
AppTriggerActor (Frontend)
         │
         │ fetch() via webhook URL
         ▼
WebhookTriggerActor (respondImmediately: false)
         │
         │ edge
         ▼
DenoActor (Process + Respond via signal)
```

The DenoActor sends the response directly:

```typescript
import type { Request, Response } from "@borgiq/actors";
import { Signal } from "@borgiq/actors";

export default async function receive(req: Request): Promise<Response> {
  const result = await processRequest(req.inputs);

  // Respond directly to the webhook caller via the returned signal
  return {
    results: result,
    signal: Signal.webhookRespond({
      statusCode: 200,
      headers: { 'Content-Type': 'application/json' },
      body: result,
    }),
  };
}
```

**When to use:** The API handler already uses a DenoActor for business logic. Eliminates the WebhookResponseActor.

### Variant 2: WebhookTrigger with Computed Response

For simple endpoints that only return context data or transform the request, compute the response directly in the WebhookTriggerActor—no downstream actors needed at all.

```
AppTriggerActor (Frontend)
         │
         │ fetch() via webhook URL
         ▼
WebhookTriggerActor (respondImmediately: true, computed body)
```

```yaml
ACTR01api:
  type: WebhookTriggerActor
  name: Apps API Handler
  msgVar: apps_api_handler
  configuration:
    options:
      allowedMethods:
        - get
      respondImmediately: true
      emitRawBody: false
      response:
        statusCode: 200
        body: >-
          ${{ { apps:
          Object.entries(ctx.canvas.interfaceTriggers).map(([msgVar, trigger])
          => ({
              id: trigger.id,
              name: trigger.name,
              description: trigger.description || '',
              url: trigger.url,
              msgVar: msgVar,
              isActive: trigger.isActive,
              type: trigger.type,
            }
          )) } }}
```

**When to use:** The response only needs `ctx` data, query parameters, or static transformations—no fetch calls, no external APIs, no stateful logic.

### Choosing the Right Variant

| Scenario | Variant |
|----------|---------|
| Response only needs context data or request params | **Variant 2** (computed response, no downstream actors) |
| Business logic in DenoActor, want faster response | **Variant 1** (`webhookRespond` signal, no WebhookResponseActor) |
| Multiple task actors in sequence before responding | **Full pattern** (WebhookResponseActor at the end) |
| Conditional routing before responding | **Full pattern** (RouterActor + WebhookResponseActor) |

---

## Multiple Webhook Handlers (Resource Separation)

For applications that manage multiple resources, use a **separate WebhookTriggerActor per resource** rather than routing everything through a single endpoint. This mirrors REST API design where each resource has its own URL.

### Why Separate Webhooks

| Concern | Single Webhook | Multiple Webhooks |
|---------|---------------|-------------------|
| **Routing** | Manual `action` field parsing in one DenoActor | Each webhook handles one resource — no routing logic |
| **Error isolation** | A bug in ticket handling can break user handling | Each resource pipeline is independent |
| **Readability** | One large router actor with branching logic | Each flow is a clear, linear pipeline |
| **Scalability** | Single bottleneck actor grows in complexity | Add new resources by adding new webhook pipelines |

### Architecture

```
┌──────────────────────────────────────────────────────────────┐
│  AppTriggerActor (Frontend)                                  │
│                                                              │
│  inputs:                                                     │
│    usersAPI:   ctx.canvas.webhookTriggers.users_api.url      │
│    ticketsAPI: ctx.canvas.webhookTriggers.tickets_api.url    │
│    commentsAPI: ctx.canvas.webhookTriggers.comments_api.url  │
└──────────────────────────────────────────────────────────────┘
         │                    │                    │
         │ fetch()            │ fetch()            │ fetch()
         ▼                    ▼                    ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ WebhookTrigger  │ │ WebhookTrigger  │ │ WebhookTrigger  │
│ (Users API)     │ │ (Tickets API)   │ │ (Comments API)  │
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ DenoActor       │ │ DenoActor       │ │ DenoActor       │
│ (User Logic)    │ │ (Ticket Logic)  │ │ (Comment Logic) │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

### Configuration

Pass each webhook URL as a separate input to the AppTriggerActor:

```yaml
# Frontend
ACTR01frontend:
  type: AppTriggerActor
  name: Project Manager
  msgVar: project_manager
  configuration:
    inputs:
      usersAPI: ${{ ctx.canvas.webhookTriggers.users_api.url }}
      ticketsAPI: ${{ ctx.canvas.webhookTriggers.tickets_api.url }}
      commentsAPI: ${{ ctx.canvas.webhookTriggers.comments_api.url }}
    options:
      script: |
        const USERS_API = '${{inputs.usersAPI}}';
        const TICKETS_API = '${{inputs.ticketsAPI}}';
        const COMMENTS_API = '${{inputs.commentsAPI}}';

        // Each resource has its own base URL
        async function getUsers() {
          return (await fetch(USERS_API)).json();
        }
        async function createTicket(data) {
          return (await fetch(TICKETS_API, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
          })).json();
        }
        async function getComments(ticketId) {
          return (await fetch(`${COMMENTS_API}?ticketId=${ticketId}`)).json();
        }
```

Each resource gets its own webhook + handler pipeline:

```yaml
# Users API
ACTR01userswebhook:
  type: WebhookTriggerActor
  name: Users API
  msgVar: users_api
  configuration:
    options:
      allowedMethods: [get, post, put, delete]
      respondImmediately: false
  edges:
    EDGE01tousers:
      targetActorId: ACTR01usershandler

ACTR01usershandler:
  type: DenoActor
  name: Handle Users
  msgVar: handle_users
  configuration:
    inputs:
      method: ${{ msg.users_api.method }}
      query: ${{ msg.users_api.queryParams }}
      body: ${{ msg.users_api.body }}
    options:
      allowNet: true
    codeDir:
      - path: main.ts
        content: |
          import type { Request, Response } from "@borgiq/actors";
          import { Signal, biqApi } from "@borgiq/actors";

          export default async function receive(req: Request): Promise<Response> {
            const { method, query, body } = req.inputs;
            // Handle user CRUD — this actor only deals with users
            let result;
            if (method === 'get') {
              result = await listUsers(query);
            } else if (method === 'post') {
              result = await createUser(body);
            }
            return {
              results: result,
              signal: Signal.webhookRespond({ statusCode: 200, headers: { 'Content-Type': 'application/json' }, body: result }),
            };
          }

# Tickets API — same pattern, separate pipeline
ACTR01ticketswebhook:
  type: WebhookTriggerActor
  name: Tickets API
  msgVar: tickets_api
  configuration:
    options:
      allowedMethods: [get, post, put, delete]
      respondImmediately: false
  edges:
    EDGE01totickets:
      targetActorId: ACTR01ticketshandler

ACTR01ticketshandler:
  type: DenoActor
  name: Handle Tickets
  msgVar: handle_tickets
  # ... ticket-specific logic
```

### When to Use Multiple Webhooks

| Scenario | Recommendation |
|----------|---------------|
| Single-resource app (e.g., TODO list) | One webhook is fine |
| 2-3 distinct resources (e.g., users + tickets) | **Use multiple webhooks** — one per resource |
| Resources with different auth or rate-limit needs | **Use multiple webhooks** — configure each independently |
| Simple action-based API (list/add/delete on same data) | One webhook with `action` query param |
| Shared logic across resources (e.g., audit logging) | Multiple webhooks, each pipeline can include shared actors via edges |

---

## Best Practices

### 1. AppTriggerActor Content Configuration

Organize your application code using the separate `html`, `css`, and `script` fields for cleaner structure:

```yaml
options:
  html: |
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
    </head>
    <body>
      <div id="app"></div>
    </body>
    </html>
  css: |
    body { font-family: system-ui, sans-serif; }
    #app { max-width: 800px; margin: 0 auto; }
  script: |
    const API_URL = '${{inputs.apiURL}}';
    // Application code
  allowedStyleDomains:
    - https://fonts.googleapis.com
    - https://cdn.jsdelivr.net
```

### 2. Content Security Policy (CSP) Configuration

AppTriggerActor enforces Content Security Policy by default to protect against XSS attacks. CSP restrictions can be relaxed using `allowAllScripts` and `allowAllStyling` based on the application's risk profile.

#### CSP Modes

| Mode | Properties | What's Allowed |
|------|-----------|----------------|
| **Strict (default)** | Neither `allowAllScripts` nor `allowAllStyling` | Only `<script>`/`<style>` tags; inline handlers, inline styles, and `eval()` are blocked |
| **Relaxed scripts** | `allowAllScripts: true` | Inline event handlers (`onclick`, etc.), `eval()`, `new Function()` |
| **Relaxed styling** | `allowAllStyling: true` | Inline `style` attributes, `element.style`, dynamically injected styles |
| **Fully relaxed** | Both set to `true` | All inline scripts and styles allowed |

**Relaxed mode example:**

```yaml
options:
  html: |
    <!DOCTYPE html>
    <html>
    <head>
      <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="p-4 font-sans">
      <button onclick="handleClick()" class="bg-blue-500 text-white px-4 py-2 rounded">
        Click Me
      </button>
      <script>
        function handleClick() {
          document.getElementById('output').textContent = 'Clicked!';
        }
      </script>
    </body>
    </html>
  allowAllScripts: true
  allowAllStyling: true
  allowedPermissions:
    - clipboard-write
    - clipboard-read
  allowedScriptDomains:
    - https://cdn.tailwindcss.com
```

#### Configuring Allowed Domains

External scripts and stylesheets from CDNs are **blocked by default** regardless of CSP mode. Whitelist domains explicitly:

```yaml
options:
  html: |
    <!-- Your HTML with external resources -->
  allowedStyleDomains:
    - https://fonts.googleapis.com
    - https://fonts.gstatic.com
    - https://cdn.jsdelivr.net
    - https://cdnjs.cloudflare.com
  allowedScriptDomains:
    - https://cdn.jsdelivr.net
    - https://unpkg.com
```

#### CSP Domain Configuration Rules

| Rule | Description |
|------|-------------|
| **HTTPS only** | All domain URLs must use `https://` protocol |
| **Full domain required** | Use `https://cdn.example.com`, not `cdn.example.com` |
| **Include all subdomains** | Google Fonts needs both `fonts.googleapis.com` (CSS) and `fonts.gstatic.com` (font files) |
| **Separate script/style domains** | Scripts and styles have different whitelists |
| **Script/style tags allowed** | `<script>` and `<style>` tags in your HTML work without whitelisting |

#### Strict Mode CSP Restrictions

When `allowAllScripts` and `allowAllStyling` are **not** enabled, the following patterns are blocked:

| Blocked Pattern | Example | Alternative |
|-----------------|---------|-------------|
| Inline event handlers | `<button onclick="fn()">` | Use `addEventListener()` or set `allowAllScripts: true` |
| Inline style attributes | `<div style="color:red">` | Use CSS classes in `<style>` tags or set `allowAllStyling: true` |
| `javascript:` URLs | `<a href="javascript:void(0)">` | Use `addEventListener('click', ...)` |
| `eval()` and similar | `eval(code)`, `new Function(code)` | Refactor to avoid dynamic code or set `allowAllScripts: true` |
| Dynamic inline styles | `element.style.color = 'red'` | Use `classList` toggling or set `allowAllStyling: true` |

#### Writing CSP-Compatible JavaScript (Strict Mode)

When not using `allowAllScripts`/`allowAllStyling`, follow these patterns:

**Event Handlers:**

```html
<!-- Blocked in strict mode (works with allowAllScripts: true) -->
<button onclick="submitForm()">Submit</button>

<!-- Always works -->
<button id="submitBtn">Submit</button>
<script>
  document.getElementById('submitBtn').addEventListener('click', submitForm);
</script>
```

**Styles:**

```html
<!-- Blocked in strict mode (works with allowAllStyling: true) -->
<div style="display: flex; gap: 1rem;">Content</div>

<!-- Always works -->
<style>
  .flex-container { display: flex; gap: 1rem; }
</style>
<div class="flex-container">Content</div>
```

#### Browser Permissions

Use `allowedPermissions` to grant specific browser APIs to the AppTriggerActor iframe:

```yaml
options:
  allowedPermissions:
    - clipboard-write
    - clipboard-read
```

**Available permissions:**

| Permission | Description |
|------------|-------------|
| `accelerometer` | Access to the Accelerometer interface |
| `ambient-light-sensor` | Access to the AmbientLightSensor interface |
| `autoplay` | Autoplay of media via HTMLMediaElement |
| `battery` | Access to the BatteryManager interface |
| `camera` | Access to video input devices |
| `clipboard-read` | Read clipboard contents via Clipboard API |
| `clipboard-write` | Write to clipboard via Clipboard API |
| `display-capture` | Screen Capture API (getDisplayMedia) |
| `encrypted-media` | Encrypted Media Extensions API |
| `fullscreen` | Fullscreen API |
| `geolocation` | Geolocation API |
| `gyroscope` | Gyroscope interface |
| `magnetometer` | Magnetometer interface |
| `microphone` | Access to audio input devices |
| `midi` | Web MIDI API |
| `payment` | Payment Request API |
| `picture-in-picture` | Picture-in-Picture API |
| `publickey-credentials-get` | Web Authentication API |
| `screen-wake-lock` | Screen Wake Lock API |
| `usb` | WebUSB API |
| `web-share` | Web Share API |
| `xr-spatial-tracking` | WebXR Device API |

#### Common CDN Configurations

| Library/Framework | allowedStyleDomains | allowedScriptDomains |
|-------------------|---------------------|----------------------|
| Google Fonts | `https://fonts.googleapis.com`, `https://fonts.gstatic.com` | - |
| Tailwind CSS | `https://cdn.jsdelivr.net` or `https://cdn.tailwindcss.com` | `https://cdn.jsdelivr.net` or `https://cdn.tailwindcss.com` |
| Chart.js | - | `https://cdn.jsdelivr.net` |
| Bootstrap | `https://cdn.jsdelivr.net` | `https://cdn.jsdelivr.net` |
| Font Awesome | `https://cdnjs.cloudflare.com` | - |
| React (CDN) | - | `https://unpkg.com`, `https://cdn.jsdelivr.net` |
| Alpine.js | - | `https://cdn.jsdelivr.net` |
| HTMX | - | `https://unpkg.com` |

#### Recommended Libraries

| Category | Recommended Libraries |
|----------|----------------------|
| Styling | The BorgIQ app theme library — see [react-app-themes.md](react-app-themes.md): inline the Base Contract + one theme block (default `hearth`); no CDN, no whitelisting |
| CSS Framework | None needed — the theme library covers app UI; reach for Tailwind/Bootstrap only on explicit customer request |
| Charts | Chart.js, ApexCharts |
| Icons | Tabler Icons as inline SVG (`stroke="currentColor"` so they inherit theme tokens) — see the Icons section of [react-app-themes.md](react-app-themes.md) |
| Animations | Animate.css, CSS transitions/keyframes |
| Reactivity | Alpine.js, HTMX, Petite Vue |
| Utilities | Day.js (dates), DOMPurify (sanitization) |

#### Configuration Examples

**Minimal (no external resources, strict CSP):**
```yaml
options:
  html: |
    <!DOCTYPE html>
    <html>
    <head>
      <style>
        body { font-family: system-ui, sans-serif; }
      </style>
    </head>
    <body>
      <script>
        // All JavaScript inline
      </script>
    </body>
    </html>
```

**Relaxed with CDNs (rapid prototyping):**
```yaml
options:
  html: |
    <!DOCTYPE html>
    <html>
    <head>
      <script src="https://cdn.tailwindcss.com"></script>
      <link href="https://fonts.googleapis.com/css2?family=Inter&display=swap" rel="stylesheet">
    </head>
    <body>...</body>
    </html>
  allowAllScripts: true
  allowAllStyling: true
  allowedScriptDomains:
    - https://cdn.tailwindcss.com
    - https://cdn.jsdelivr.net
  allowedStyleDomains:
    - https://fonts.googleapis.com
    - https://fonts.gstatic.com
```

**Strict with CDNs (production):**
```yaml
options:
  html: |
    <!DOCTYPE html>
    <html>
    <head>
      <link href="https://fonts.googleapis.com/css2?family=Inter&display=swap" rel="stylesheet">
      <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body>...</body>
    </html>
  allowedStyleDomains:
    - https://fonts.googleapis.com
    - https://fonts.gstatic.com
    - https://cdn.jsdelivr.net
  allowedScriptDomains:
    - https://cdn.jsdelivr.net
    - https://unpkg.com
```

### 3. Error Handling in Frontend

Always handle fetch errors gracefully:

```javascript
async function fetchData() {
    try {
        const response = await fetch(API_URL);
        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Fetch error:', error);
        // Show user-friendly error message
    }
}
```

### 4. Loading States

Show loading indicators during API calls:

```javascript
function showLoading() {
    document.getElementById('loading').classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loading').classList.add('hidden');
}
```

### 5. File Uploads via Multipart Form Data

Always use multipart form upload when sending files through a WebhookTriggerActor. **Never base64-encode files**—BorgIQ automatically converts multipart file uploads into BorgIQ file handles that downstream actors can use directly.

```javascript
// Correct - multipart form upload
async function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('name', file.name);

    const response = await fetch(API_URL, {
        method: 'POST',
        body: formData,
        // Do NOT set Content-Type header — browser sets it with boundary
    });
    return await response.json();
}

// Wrong - don't base64-encode files
async function uploadFileWrong(file) {
    const base64 = await toBase64(file);  // Don't do this
    await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ file: base64 }),
    });
}
```

In the downstream DenoActor, the uploaded file is available as a BorgIQ file handle via `inputs.file`, ready to use with `mountFile()`.

---

## Common Mistakes

### Mistake 1: Trying to Connect AppTriggerActor to Webhook via Edges

**WRONG:**
```yaml
# This is impossible - you cannot connect an actor to a trigger via edges
ACTR01app:
  edges:
    EDGE01wrong:
      targetActorId: ACTR01webhook  # WebhookTriggerActor is a TRIGGER
```

**CORRECT:**
```yaml
# Use ctx.canvas.webhookTriggers to get the webhook URL
configuration:
  inputs:
    apiURL: ${{ ctx.canvas.webhookTriggers.webhook_msgVar.url }}
```

### Mistake 2: Using respondImmediately: true

**WRONG:**
```yaml
configuration:
  options:
    respondImmediately: true  # Response sent immediately, before processing
```

**CORRECT:**
```yaml
configuration:
  options:
    respondImmediately: false  # Wait for WebhookResponseActor to send response
```

### Mistake 3: Missing Content-Type Header

**WRONG:**
```yaml
configuration:
  options:
    body: ${{ msg.process_data }}
    # Missing content-type header
```

**CORRECT:**
```yaml
configuration:
  options:
    body: ${{ msg.process_data }}
    headers:
      content-type: application/json
```

### Mistake 4: Forgetting CSP Domain Configuration

External CSS, fonts, and scripts will be blocked without whitelisting:

**WRONG:**
```yaml
options:
  html: |
    <link href="https://fonts.googleapis.com/css2?family=Inter" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <!-- These will be BLOCKED - no CSP domains configured -->
```

**CORRECT:**
```yaml
options:
  html: |
    <link href="https://fonts.googleapis.com/css2?family=Inter" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  allowedStyleDomains:
    - https://fonts.googleapis.com
    - https://fonts.gstatic.com  # Don't forget the font file domain!
  allowedScriptDomains:
    - https://cdn.jsdelivr.net
```

### Mistake 5: Missing Required Font Domains

Google Fonts requires TWO domains - one for CSS and one for font files:

**WRONG:**
```yaml
allowedStyleDomains:
  - https://fonts.googleapis.com
  # Missing fonts.gstatic.com - fonts won't load!
```

**CORRECT:**
```yaml
allowedStyleDomains:
  - https://fonts.googleapis.com  # CSS file
  - https://fonts.gstatic.com     # Font files
```

### Mistake 6: Using Inline Event Handlers (Strict Mode)

Inline event handlers are blocked by default. Either use `addEventListener()` or set `allowAllScripts: true`:

```html
<!-- Blocked in strict mode -->
<button onclick="handleClick()">Click</button>

<!-- Option 1: Use addEventListener (works in all modes) -->
<button id="btn">Click</button>
<script>
  document.getElementById('btn').addEventListener('click', handleClick);
</script>

<!-- Option 2: Set allowAllScripts: true in AppTriggerActor options -->
```

### Mistake 7: Using Inline Style Attributes (Strict Mode)

Inline `style` attributes are blocked by default. Either use CSS classes or set `allowAllStyling: true`:

```html
<!-- Blocked in strict mode -->
<div style="display: flex;">Content</div>

<!-- Option 1: Use CSS classes (works in all modes) -->
<style>
  .flex-container { display: flex; }
</style>
<div class="flex-container">Content</div>

<!-- Option 2: Set allowAllStyling: true in AppTriggerActor options -->
```

### Mistake 8: Using JavaScript to Set Inline Styles (Strict Mode)

Setting `element.style` properties dynamically may be blocked in strict mode. Either use `classList` or set `allowAllStyling: true`:

```javascript
// Blocked in strict mode (works with allowAllStyling: true)
element.style.display = 'none';

// Works in all modes
element.classList.add('hidden');
```

### Mistake 9: Using Libraries That Inject Inline Styles (Strict Mode)

Some libraries dynamically inject inline styles and won't work in strict mode. Either use CSS-based alternatives or set `allowAllStyling: true`:

```yaml
# Option 1: Use CSS animations instead of jQuery UI
# Option 2: Enable allowAllStyling
options:
  allowAllStyling: true
```

---

## Design System Foundations

Building web applications with consistent, professional quality requires intentional design decisions — not defaults. Before writing any HTML/CSS, establish a design system that shapes every component.

### Design Direction

Choose a direction that fits the product's purpose and audience. Each direction implies specific choices about spacing, depth, typography, and color:

| Direction | Feel | Best For | Spacing | Depth | Radius |
|-----------|------|----------|---------|-------|--------|
| **Precision & Density** | Tight, technical, monochrome | Developer tools, admin dashboards | 4px base (compact) | Borders-only | Sharp (4-6px) |
| **Warmth & Approachability** | Generous spacing, soft shadows | Collaborative tools, consumer apps | 8px base (generous) | Subtle shadows | Soft (8-12px) |
| **Sophistication & Trust** | Cool tones, layered depth | Finance, enterprise B2B | 8px base | Layered shadows | Medium (6-8px) |
| **Boldness & Clarity** | High contrast, dramatic space | Modern dashboards, data-heavy apps | 4px base | Surface color shifts | Medium (6-8px) |
| **Utility & Function** | Muted, functional density | GitHub-style tools | 4px base | Borders-only | Sharp (4-6px) |
| **Data & Analysis** | Chart-optimized, numbers-first | Analytics, BI tools | 4px base | Borders-only | Sharp (4px) |

### Token Architecture

Define a small set of CSS variable primitives. Every color in the interface should trace back to these — no random hex values:

```css
:root {
  /* Text hierarchy — use all four levels consistently */
  --foreground: /* primary text, highest contrast */;
  --secondary: /* supporting text, slightly muted */;
  --muted: /* metadata, timestamps */;
  --faint: /* disabled, placeholder, lowest contrast */;

  /* Surfaces — subtle elevation shifts, not dramatic jumps */
  --background: /* base canvas */;
  --card: /* cards, panels (barely different from background) */;
  --overlay: /* dropdowns, popovers (one step above cards) */;

  /* Borders — low opacity rgba blends with background */
  --border: /* standard separation */;
  --border-subtle: /* softer separation */;
  --border-strong: /* emphasis, hover states */;

  /* Brand & semantic */
  --primary: /* primary accent */;
  --primary-foreground: /* text on primary */;
  --danger: /* errors */;
  --success: /* confirmations */;
  --warning: /* cautions */;
}
```

### Spacing System

Pick a base unit and use only multiples. Random spacing values (14px, 17px, 22px) are the clearest sign of no design system:

| Context | 4px base scale | 8px base scale |
|---------|---------------|----------------|
| Micro (icon gaps) | 4px | 4px |
| Compact (within buttons) | 8px | 8px |
| Component (card padding) | 12-16px | 16px |
| Section (between groups) | 24px | 24-32px |
| Major (between sections) | 32-64px | 48-64px |

### Depth Strategy

Choose **one** approach and commit — mixing strategies looks inconsistent:

| Strategy | CSS Pattern | Best For |
|----------|-------------|----------|
| **Borders-only** | `border: 0.5px solid rgba(0,0,0,0.08)` | Dense tools, developer dashboards |
| **Subtle shadows** | `box-shadow: 0 1px 3px rgba(0,0,0,0.08)` | Approachable products, consumer apps |
| **Layered shadows** | Multiple shadow layers with decreasing opacity | Premium feel, financial tools |
| **Surface color shifts** | Background tints (`#fff` card on `#f8fafc` page) | Minimal, modern interfaces |

### Surface Elevation

Surfaces stack: page → card → dropdown → nested overlay. Build a numbered system where each level is only a few percentage points different in lightness:

```css
/* Dark mode example — higher elevation = slightly lighter */
--surface-0: hsl(220, 20%, 10%);   /* base canvas */
--surface-1: hsl(220, 20%, 12%);   /* cards, panels */
--surface-2: hsl(220, 20%, 15%);   /* dropdowns, popovers */
--surface-3: hsl(220, 20%, 18%);   /* nested overlays */

/* Light mode — higher elevation = subtle shadow or slight lightness shift */
--surface-0: #f8fafc;  /* base canvas */
--surface-1: #ffffff;  /* cards */
--surface-2: #ffffff;  /* dropdowns (distinguished by shadow) */
```

**Key principle:** The differences should be whisper-quiet — barely visible in isolation, but clearly perceptible when surfaces stack. If you squint at the interface and can still perceive hierarchy without any element jumping out, the layering is working.

### Typography Hierarchy

Build distinct levels using size, weight, AND letter-spacing — not size alone:

```css
/* Headlines — heavier weight, tighter tracking */
.headline { font-size: 24px; font-weight: 600; letter-spacing: -0.02em; }

/* Body — comfortable weight for readability */
.body { font-size: 14px; font-weight: 400; line-height: 1.5; }

/* Labels — medium weight, works at smaller sizes */
.label { font-size: 13px; font-weight: 500; letter-spacing: 0.01em; }

/* Data — monospace with tabular numbers for alignment */
.data { font-family: 'SF Mono', 'Consolas', monospace; font-variant-numeric: tabular-nums; }
```

### Component Patterns

Define reusable patterns once, then apply consistently. Surface treatment (border weight, shadow, radius, padding) should be uniform across all cards — only the internal structure varies per content type:

| Component | Precision & Density | Warmth & Approachability |
|-----------|-------------------|------------------------|
| **Button height** | 32px | 40px |
| **Button padding** | 8px 12px | 12px 20px |
| **Button radius** | 4px | 8px |
| **Button font** | 13px / 500 | 15px / 500 |
| **Card padding** | 12px | 20px |
| **Card radius** | 6px | 12px |
| **Input height** | 32px | 44px |
| **Table cell padding** | 8px 12px | 12px 16px |

### Applying Design System in AppTriggerActor

Put your design tokens in the `css` field and reference them throughout your `html`:

```yaml
options:
  html: |
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body>
      <div class="container">
        <h1 class="headline">Dashboard</h1>
        <div class="card">
          <span class="label">Total Users</span>
          <span class="data">1,247</span>
        </div>
      </div>
    </body>
    </html>
  css: |
    :root {
      --background: #1a2332;
      --foreground: #f1faee;
      --card: #1e2a3a;
      --border: rgba(255,255,255,0.06);
      --primary: #2d8b8b;
    }
    body { background: var(--background); color: var(--foreground); font-family: system-ui, sans-serif; }
    .container { max-width: 800px; margin: 0 auto; padding: 32px; }
    .card { background: var(--card); border: 0.5px solid var(--border); border-radius: 6px; padding: 16px; }
    .headline { font-size: 24px; font-weight: 600; letter-spacing: -0.02em; }
    .label { font-size: 13px; font-weight: 500; color: var(--muted, #a8dadc); }
    .data { font-size: 24px; font-weight: 600; font-variant-numeric: tabular-nums; }
  script: |
    const API_URL = '${{inputs.apiURL}}';
    // Application code
```

### Quality Checks

Before finalizing a web application, run these checks against your output:

| Check | What to Look For |
|-------|-----------------|
| **Squint test** | Blur your eyes — can you still perceive hierarchy? Is anything jumping out harshly? |
| **Swap test** | If you swapped the typeface/layout for a generic one, would anyone notice? Where they wouldn't = where you defaulted |
| **Spacing test** | Is every spacing value a multiple of your base unit? Random values signal no system |
| **Depth test** | Are you using your declared strategy throughout? (borders-only = no shadows anywhere) |
| **State test** | Does every interactive element have hover, focus, and disabled states? |
| **Token test** | Is every color traceable to your CSS variable primitives? No random hex values? |

---

## When to Use This Pattern

### Good Use Cases

| Scenario | Why This Pattern Works |
|----------|------------------------|
| Simple CRUD applications | Single canvas, clear frontend-backend separation |
| Data visualization dashboards | Fetch data via API, render with JS charts |
| Search interfaces | User input → API call → Display results |
| Interactive tools | Real-time processing with visual feedback |
| Internal admin tools | Quick to build, easy to customize |

### Consider Alternatives

| Scenario | Better Alternative |
|----------|-------------------|
| Multi-page forms with state | InterfaceActor with `onSubmit: nextInterface` |
| Form-based data collection that triggers workflows | InterfaceTriggerActor (emits form data to downstream actors) |
| Complex approval workflows | InterfaceActor + MessageProcessorActor callbacks |
| Public-facing production apps | Dedicated frontend + WebhookTriggerActor API |
| Heavy data processing with streaming | WebSocket or Server-Sent Events (external) |

---

## Summary

The Web Application Pattern enables building interactive single-page applications within BorgIQ:

1. **AppTriggerActor** hosts the frontend via separate `html`, `css`, and `script` fields
2. **WebhookTriggerActor** provides the API endpoint (accessed via `ctx.canvas.webhookTriggers.<msgVar>.url`)
3. **Task Actors** process requests with business logic
4. **WebhookResponseActor** returns JSON responses

The key insight is that App and Webhook triggers connect via URL reference, not edges, enabling a clean frontend-backend architecture within a single canvas. AppTriggerActor does not emit messages — it purely hosts the web application.
