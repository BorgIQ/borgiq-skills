# App Trigger Actor Reference

The AppTriggerActor hosts a web application (HTML/CSS/JS) in a sandboxed iframe. It is purpose-built for interactive single-page applications, dashboards, and tools.

## Table of Contents

- [Overview](#overview)
- [Configuration Structure](#configuration-structure)
- [Options Reference](#options-reference)
- [TypeScript Schema Definition](#typescript-schema-definition)
- [No Emitted Messages](#no-emitted-messages)
- [Content Security Policy](#content-security-policy)
  - [Browser Permissions](#browser-permissions)
- [Connecting to a Backend API](#connecting-to-a-backend-api)
- [BIQFile References](#biqfile-references)
- [AppTriggerActor vs InterfaceTriggerActor](#apptriggeractor-vs-interfacetriggeractor)
- [Use Cases](#use-cases)
- [Quick Example](#quick-example)

## Overview

AppTriggerActor is the dedicated trigger type for hosting web applications in BorgIQ. Use it when you need to build:

- Interactive single-page applications (SPAs)
- Dashboards and data visualization tools
- Internal admin tools and utilities
- Any web-based UI that communicates with backend APIs

**Key characteristics:**
- Separate `html`, `css`, and `script` configuration fields for clean code organization
- Content can be inline strings or BIQFile references (for larger applications)
- Built-in Content Security Policy (CSP) with configurable relaxation
- Does **not** emit messages or trigger downstream actors
- Does **not** have form semantics (no `page`, `onSubmit`, or form submission data)

**For form-based workflows** (collecting structured input, triggering downstream processing on submit), use [InterfaceTriggerActor](interface-trigger-actor.md) instead.

## Configuration Structure

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  ACTR01xxxxx:
    type: AppTriggerActor
    version: 1
    name: My Web Application
    msgVar: my_web_application
    description: Hosts an interactive web application
    isActive: true
    continueOnError: false
    enableLTM: false
    enableSTM: false
    sourcePorts:
      - id: SPRTdefault
    configuration:
      inputs:
        apiURL: ${{ ctx.canvas.webhookTriggers.my_api.url }}
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
          body { font-family: system-ui, sans-serif; margin: 0; padding: 1rem; }
          #app { max-width: 800px; margin: 0 auto; }
        script: |
          const API_URL = '${{inputs.apiURL}}';

          async function loadData() {
            const res = await fetch(API_URL);
            const data = await res.json();
            document.getElementById('app').textContent = JSON.stringify(data);
          }
          loadData();
        allowedStyleDomains:
          - https://fonts.googleapis.com
          - https://fonts.gstatic.com
        allowedScriptDomains:
          - https://cdn.jsdelivr.net
        allowInlineScripts: true
        allowInlineStyling: true
    schemas: {}
    id: ACTR01xxxxx
    position:
      x: 0
      'y': 0
    edges: {}
```

## Options Reference

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `html` | string or BIQFile | Yes | HTML content for the application. Can be an inline string or a BIQFile reference. |
| `css` | string or BIQFile | No | CSS styles. Can be an inline string or a BIQFile reference. |
| `script` | string or BIQFile | No | JavaScript code. Can be an inline string or a BIQFile reference. |
| `allowedScriptDomains` | string[] | No | Whitelisted domains for external scripts (CSP `script-src`) |
| `allowedStyleDomains` | string[] | No | Whitelisted domains for external stylesheets/fonts (CSP `style-src`) |
| `allowInlineScripts` | boolean | No | Adds `'unsafe-inline'` to CSP `script-src` instead of hash-based verification. Enables inline event handlers (`onclick`, etc.), `eval()`, `new Function()`, and dynamically generated scripts. Default: `false`. |
| `allowInlineStyling` | boolean | No | Adds `'unsafe-inline'` to CSP `style-src` instead of hash-based verification. Enables inline `style` attributes, `element.style`, and dynamically injected styles. Default: `false`. |
| `allowedPermissions` | string[] | No | Browser Permissions-Policy directives to enable for the iframe (see [Browser Permissions](#browser-permissions)) |

### Content Fields

You can organize your application code in two ways:

**All-in-one:** Put everything in the `html` field with embedded `<style>` and `<script>` tags:

```yaml
options:
  html: |
    <!DOCTYPE html>
    <html>
    <head>
      <style>body { font-family: sans-serif; }</style>
    </head>
    <body>
      <div id="app"></div>
      <script>
        // Application code here
      </script>
    </body>
    </html>
```

**Separated:** Use `html` for markup, `css` for styles, and `script` for JavaScript:

```yaml
options:
  html: |
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body>
      <div id="app"></div>
    </body>
    </html>
  css: |
    body { font-family: sans-serif; }
    #app { max-width: 800px; margin: 0 auto; }
  script: |
    // Application code here
    document.getElementById('app').textContent = 'Hello';
```

The separated approach is cleaner for larger applications and enables BIQFile references for each field.

## TypeScript Schema Definition

The complete TypeScript schema for AppTriggerActor options and results:

```typescript
import { z } from 'zod';
import { BIQFileSchema } from '../../schemas/file.js';
import { PermissionsPolicyDirectiveZodSchema } from './permissionsPolicy.js';

/** Content field that can be either an inline string or a BIQFile reference */
const AppContentFieldSchema = z.union([z.string(), BIQFileSchema]);

/** The options schema for the AppTriggerActor */
export const AppTriggerActorOptionsSchema = z.object({
  /** HTML content or file */
  html: AppContentFieldSchema
    .describe('The HTML content for the app. Can be an inline string or a BIQFile reference.'),
  /** CSS content or file */
  css: AppContentFieldSchema.nullish()
    .describe('CSS styles for the app. Can be an inline string or a BIQFile reference.'),
  /** JavaScript content or file */
  script: AppContentFieldSchema.nullish()
    .describe('JavaScript code for the app. Can be an inline string or a BIQFile reference.'),
  /** allowed domains for external scripts */
  allowedScriptDomains: z.array(z.string()).nullish(),
  /** allowed domains for external stylesheets */
  allowedStyleDomains: z.array(z.string()).nullish(),
  /** Enable unsafe-inline for scripts, bypassing hash verification */
  allowInlineScripts: z.boolean().nullish(),
  /** Enable unsafe-inline for styles, bypassing hash verification */
  allowInlineStyling: z.boolean().nullish(),
  /** Permissions-Policy directives to enable */
  allowedPermissions: z.array(PermissionsPolicyDirectiveZodSchema).nullish(),
});

export type AppTriggerActorOptions = z.infer<typeof AppTriggerActorOptionsSchema>;

/** AppTriggerActor does not emit any result */
export const AppTriggerActorResultSchema = z.object({});

export type AppTriggerActorResult = z.infer<typeof AppTriggerActorResultSchema>;
```

## No Emitted Messages

**AppTriggerActor does NOT emit messages.** It purely hosts a web application and does not trigger any downstream actors. There is no form submission, no result data, and no `msg.<msgVar>` output for downstream actors to consume.

This is a key difference from InterfaceTriggerActor, which emits form submission data (`meta` + `body`) to downstream actors.

If your web application needs to communicate with a backend, use the [Web Application Pattern](web-application-pattern.md) with a WebhookTriggerActor as the API endpoint.

## Content Security Policy

AppTriggerActor enforces CSP by default. The CSP configuration is at the actor options level.

### CSP Modes

| Mode | Properties | CSP Directive | What's Allowed |
|------|-----------|---------------|----------------|
| **Strict (default)** | Neither flag set | `script-src 'self' 'sha256-...'` | Only `<script>`/`<style>` tags whose content matches a SHA-256 hash; inline handlers, inline styles, and `eval()` are blocked |
| **Relaxed scripts** | `allowInlineScripts: true` | `script-src 'self' 'unsafe-inline'`; `script-src-attr 'unsafe-inline'` | Inline event handlers (`onclick`, etc.), `eval()`, `new Function()`, dynamically generated scripts |
| **Relaxed styling** | `allowInlineStyling: true` | `style-src 'self' 'unsafe-inline'`; `style-src-attr 'unsafe-inline'` | Inline `style` attributes, `element.style`, dynamically injected styles |
| **Fully relaxed** | Both set to `true` | Both `'unsafe-inline'` directives | All inline scripts and styles allowed |

### Configuring Allowed Domains

External scripts and stylesheets are blocked by default. Whitelist domains explicitly:

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
  allowedScriptDomains:
    - https://cdn.jsdelivr.net
```

### Domain Configuration Rules

| Rule | Description |
|------|-------------|
| **HTTPS only** | All domain URLs must use `https://` protocol |
| **Full domain required** | Use `https://cdn.example.com`, not `cdn.example.com` |
| **Include all subdomains** | Google Fonts needs both `fonts.googleapis.com` (CSS) and `fonts.gstatic.com` (font files) |
| **Separate script/style domains** | Scripts and styles have different whitelists |

### Common CDN Configurations

| Library/Framework | allowedStyleDomains | allowedScriptDomains |
|-------------------|---------------------|----------------------|
| Google Fonts | `https://fonts.googleapis.com`, `https://fonts.gstatic.com` | - |
| Tailwind CSS | `https://cdn.jsdelivr.net` or `https://cdn.tailwindcss.com` | `https://cdn.jsdelivr.net` or `https://cdn.tailwindcss.com` |
| Chart.js | - | `https://cdn.jsdelivr.net` |
| Bootstrap | `https://cdn.jsdelivr.net` | `https://cdn.jsdelivr.net` |
| Alpine.js | - | `https://cdn.jsdelivr.net` |

### Browser Permissions

Use `allowedPermissions` to grant specific browser APIs to the iframe:

```yaml
options:
  allowedPermissions:
    - clipboard-write
    - clipboard-read
```

Available permissions (from `PermissionsPolicyDirective` enum):

| Directive | Description |
|-----------|-------------|
| `accelerometer` | Access to the Accelerometer interface |
| `ambient-light-sensor` | Access to the AmbientLightSensor interface |
| `autoplay` | Autoplay of media requested through HTMLMediaElement |
| `battery` | Access to the BatteryManager interface |
| `camera` | Access to video input devices |
| `clipboard-read` | Access to read clipboard contents via Clipboard API |
| `clipboard-write` | Access to write to clipboard via Clipboard API |
| `display-capture` | Access to use the Screen Capture API (getDisplayMedia) |
| `encrypted-media` | Access to the Encrypted Media Extensions API |
| `fullscreen` | Access to the Fullscreen API |
| `geolocation` | Access to the Geolocation API |
| `gyroscope` | Access to the Gyroscope interface |
| `magnetometer` | Access to the Magnetometer interface |
| `microphone` | Access to audio input devices |
| `midi` | Access to the Web MIDI API |
| `payment` | Access to the Payment Request API |
| `picture-in-picture` | Access to the Picture-in-Picture API |
| `publickey-credentials-get` | Access to the Web Authentication API |
| `screen-wake-lock` | Access to the Screen Wake Lock API |
| `usb` | Access to the WebUSB API |
| `web-share` | Access to the Web Share API |
| `xr-spatial-tracking` | Access to WebXR Device API |

## Connecting to a Backend API

AppTriggerActor applications typically communicate with a WebhookTriggerActor for backend processing. See [web-application-pattern.md](web-application-pattern.md) for the full pattern.

### Connection Mechanism

Pass the webhook URL to your application via `inputs`:

```yaml
configuration:
  inputs:
    apiURL: ${{ ctx.canvas.webhookTriggers.my_api_handler.url }}
  options:
    html: |
      <div id="app"></div>
    script: |
      const API_URL = '${{inputs.apiURL}}';

      async function fetchData() {
        const response = await fetch(API_URL);
        const data = await response.json();
        // Process data...
      }
```

**Important:** App and Webhook triggers connect via URL reference, NOT via edges (you cannot connect an actor to a trigger).

## BIQFile References

For larger applications, content fields can reference BIQFile objects instead of inline strings. This is useful when HTML, CSS, or JavaScript files are managed as separate assets:

```yaml
options:
  html:
    id: FILE01abc123
    name: app.html
    mimeType: text/html
  css:
    id: FILE01def456
    name: styles.css
    mimeType: text/css
  script:
    id: FILE01ghi789
    name: app.js
    mimeType: application/javascript
```

## AppTriggerActor vs InterfaceTriggerActor

| Feature | AppTriggerActor | InterfaceTriggerActor |
|---------|----------------|----------------------|
| **Purpose** | Web applications (SPA, dashboards, tools) | Form-based workflows (data collection, submissions) |
| **Content model** | Separate `html`, `css`, `script` fields | `page.children` with form components |
| **Emits messages** | No (does not trigger downstream actors) | Yes (emits `meta` + `body` with form data) |
| **`onSubmit` config** | No | Yes (required) |
| **BIQFile support** | Yes (content can be a file reference) | No (inline only) |
| **CSP config location** | Actor options level | Nested in webViewer component |
| **Form components** | Not available | Full set (text, select, checkbox, etc.) |

**Use AppTriggerActor when:**
- Building interactive web applications
- Creating dashboards or data visualization tools
- Building internal tools that communicate with APIs
- The UI doesn't follow a form-submit workflow

**Use InterfaceTriggerActor when:**
- Collecting structured input via forms
- Triggering workflows based on form submissions
- Building multi-step form workflows
- You need form submission data (user info, field values) in downstream actors

## Use Cases

### Interactive Dashboard

Build a real-time dashboard that fetches data from APIs and displays charts.

### Internal Admin Tool

Create tools for managing data, reviewing content, or performing operations.

### Search Interface

Build a search UI that queries an API and displays results dynamically.

### Data Visualization

Render charts, graphs, and interactive visualizations using libraries like Chart.js.

### CRUD Application

Build a full create-read-update-delete application backed by a webhook API.

## Quick Example

A minimal task tracker application with an API backend:

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  ACTR01kd298z8kq4yd67m5pddd9cyp:
    type: AppTriggerActor
    version: 1
    name: Task Tracker
    msgVar: task_tracker
    description: Interactive task tracking web application
    isActive: true
    continueOnError: false
    enableLTM: false
    enableSTM: false
    sourcePorts:
      - id: SPRTdefault
    configuration:
      inputs:
        apiURL: ${{ ctx.canvas.webhookTriggers.tasks_api.url }}
      options:
        html: |
          <!DOCTYPE html>
          <html>
          <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Task Tracker</title>
          </head>
          <body>
            <h1>Task Tracker</h1>
            <form id="taskForm">
              <input type="text" id="taskInput" placeholder="New task..." required>
              <button type="submit">Add</button>
            </form>
            <ul id="taskList"></ul>
          </body>
          </html>
        css: |
          body {
            font-family: system-ui, -apple-system, sans-serif;
            max-width: 600px;
            margin: 2rem auto;
            padding: 0 1rem;
          }
          form { display: flex; gap: 0.5rem; margin-bottom: 1rem; }
          input { flex: 1; padding: 0.5rem; }
          button { padding: 0.5rem 1rem; cursor: pointer; }
          ul { list-style: none; padding: 0; }
          li { padding: 0.5rem 0; border-bottom: 1px solid #eee; }
        script: |
          const API_URL = '${{inputs.apiURL}}';

          document.getElementById('taskForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const input = document.getElementById('taskInput');
            await fetch(API_URL, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ action: 'add', task: input.value })
            });
            input.value = '';
            loadTasks();
          });

          async function loadTasks() {
            try {
              const res = await fetch(`${API_URL}?action=list`);
              const data = await res.json();
              const list = document.getElementById('taskList');
              list.innerHTML = (data.tasks || [])
                .map(t => `<li>${t}</li>`).join('');
            } catch (err) {
              console.error('Failed to load tasks:', err);
            }
          }

          loadTasks();
    schemas: {}
    id: ACTR01kd298z8kq4yd67m5pddd9cyp
    position:
      x: 0
      'y': 0
    edges: {}
```
