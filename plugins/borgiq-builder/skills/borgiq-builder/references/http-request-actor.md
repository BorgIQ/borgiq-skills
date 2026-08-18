# HTTP Request Actor Reference

The HttpRequestActor makes REST API calls to external services within BorgIQ workflows.

> **Before you build: check the template catalog.** Most third-party integrations (Gmail, Slack, GitHub, Google, Notion, …) already ship as vetted BorgIQ templates. Prefer adapting a template over hand-writing an HttpRequestActor — it avoids malformed `options`, wrong `sourcePorts`, and incorrect config encoding (the most common cause of broken actors). Search → convert:
> `borgiq templates apps --search "<vendor>"` → `borgiq templates list --app-id TAPP...` → `borgiq templates get ATMP... --json | borgiq scaffold actor-from-template`. Only hand-build (below) when no template fits. See the hub skill's "Deploying and Testing with the CLI" for the full flow.

## Table of Contents

- [Configuration Structure](#configuration-structure)
- [Options Reference](#options-reference)
- [TypeScript Schema Definition](#typescript-schema-definition)
- [Results Object](#results-object)
- [Error Handling](#error-handling)
- [Authentication](#authentication)
- [Using Variables (vars)](#using-variables-vars)
- [Output Transformation](#output-transformation)
- [Common Patterns](#common-patterns)
- [Input Schemas](#input-schemas)
- [Examples](#examples)

## Configuration Structure

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  ACTR01xxxxx:
    type: HttpRequestActor
    version: 1
    name: Actor Name Here
    msgVar: actor_name_here
    description: What this actor does
    isActive: true
    continueOnError: false
    enableLTM: false
    enableSTM: false
    sourcePorts:
      - id: SPRTdefault
    configuration:
      inputs:
        key: value
      vars:
        - varName: ${{ expression }}
      options:
        url: https://api.example.com/endpoint
        method: GET
        headers:
          content-type: application/json; charset=utf-8
        queryParams:
          param: value
        body:
          field: value
        auth: ${{ connection.auth }}
        emitRequest: false
      outputs: ${{ results.body }}
      connection:
        key: connection-key-from-workspace
        type: optional-type   # one registry name, or a non-empty array of acceptable names
      error:
        if: ${{ !Q.isHTTPStatusInRange(results.statusCode, ["200-299"]) }}
        retryIf: ${{ Q.isHTTPStatusInRange(results.statusCode, ["429", "500-599"]) }}
        includeResult: true
        message: ${{ Q.toJSON(results) }}
    schemas:
      inputs:
        type: object
        properties:
          fieldName:
            type: string
            title: Field Title
            description: Field description
        required:
          - fieldName
    id: ACTR01xxxxx
    position:
      x: 0
      'y': 0
    edges: {}
```

## Options Reference

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `url` | string | Yes | The endpoint URL. Supports interpolation. |
| `method` | string | Yes | HTTP method: GET, POST, PUT, PATCH, DELETE, etc. |
| `headers` | object | No | Request headers |
| `queryParams` | object | No | URL query parameters |
| `body` | any | No | Request body (for POST/PUT/PATCH) |
| `auth` | expression | No | Authentication object from connection |
| `contentType` | string | No | Body content type: json, xml, text, buffer, or valid HTTP Content-Type |
| `responseType` | string | No | Expected response type: arraybuffer, document, json, text, stream |
| `multiPartFormFiles` | object | No | Form file uploads as multipart form |
| `emitRequest` | boolean | No | Include request details in output (default: false) |
| `emitBodyAsFile` | boolean | No | Return response body as a file (default: false) |
| `options` | object | No | Advanced options: basicAuth, maxContentLength, maxBodyLength |

## TypeScript Schema Definition

The complete TypeScript schema for HttpRequestActor options:

```typescript
import { z } from 'zod';

/** Request options for advanced use cases */
const IRequestOptionsSchema = z.object({
  basicAuth: z.object({
    username: z.string(),
    password: z.string(),
  }).nullish()
    .describe('The basic auth to access the proxy'),
  maxContentLength: z.number().nullish()
    .describe('The maximum content length of the response'),
  maxBodyLength: z.number().nullish()
    .describe('The maximum body length of the request'),
});

/** The options for the HttpRequestActor */
/** See auth-types.md for AuthDataSchema definition */
const HttpRequestActorOptionsSchema = z.object({
  auth: AuthDataSchema.nullish()
    .describe('The authentication data for the request. See auth-types.md for details.'),
  method: z.enum([
    'get', 'GET',
    'delete', 'DELETE',
    'head', 'HEAD',
    'options', 'OPTIONS',
    'post', 'POST',
    'put', 'PUT',
    'patch', 'PATCH',
    'purge', 'PURGE',
    'link', 'LINK',
    'unlink', 'UNLINK'
  ])
    .describe('The method of the http request (case insensitive)'),
  url: z.url()
    .describe('The url to send the request to'),
  headers: z.record(z.string(), z.union([z.string(), z.number(), z.boolean()])).nullish()
    .describe('The headers to send with the request'),
  queryParams: z.record(z.string(), z.unknown()).nullish()
    .describe('The query parameters to send with the request'),
  body: z.any().nullish()
    .describe('The body to send with the request'),
  multiPartFormFiles: z.record(z.string(), z.union([BIQFileSchema, z.array(BIQFileSchema)])).nullish()
    .describe('The form file upload as a multipart form'),
  contentType: z.string().nullish()
    .describe('The content type of the body: json, xml, text, buffer, or valid HTTP Content-Type'),
  responseType: z.enum(['arraybuffer', 'blob', 'document', 'json', 'text', 'stream']).nullish()
    .describe('The expected type of the response'),
  options: IRequestOptionsSchema.nullish()
    .describe('Advanced request options: basicAuth, maxContentLength, maxBodyLength'),
  emitRequest: z.boolean().nullish()
    .describe('If the actor should emit the request object in the emitted message'),
  emitBodyAsFile: z.boolean().nullish()
    .describe('If the actor should return the response as a file'),
});

/** The emitted message schema for the HttpRequestActor */
const HttpRequestActorResultSchema = z.object({
  body: z.any()
    .describe('The body of the response'),
  statusCode: z.number()
    .describe('The status code of the response'),
  headers: z.unknown()
    .describe('The headers of the response'),
  request: z.object({
    url: z.string(),
    method: z.string(),
    headers: z.record(z.string(), z.unknown()),
    body: z.union([z.string(), z.record(z.string(), z.unknown())]).nullish(),
    queryParams: z.record(z.string(), z.unknown()).nullish(),
  }).nullish()
    .describe('The HTTP request object sent. Only defined if emitRequest was set to true'),
});
```

### Content Types

| Value | Description |
|-------|-------------|
| `json` | JSON (application/json) |
| `xml` | XML (application/xml) |
| `text` | Plain text (text/plain) |
| `buffer` | Raw binary file |
| Any valid Content-Type | e.g., `image/png`, `application/pdf` |

### Response Types

| Value | Description |
|-------|-------------|
| `json` | Parse response as JSON (default) |
| `text` | Return response as text |
| `arraybuffer` | Return as binary file |
| `document` | Parse as HTML/XML document |
| `stream` | Return as stream |

### Multipart Form Files

Upload files using `multiPartFormFiles`:

```yaml
options:
  url: https://api.example.com/upload
  method: POST
  multiPartFormFiles:
    file: ${{ assets.uploadFile }}
    # Or multiple files
    files:
      - ${{ assets.file1 }}
      - ${{ assets.file2 }}
```

### Advanced Options

```yaml
options:
  url: https://api.example.com
  method: GET
  options:
    maxContentLength: 10485760  # 10MB
    maxBodyLength: 10485760
```

## Results Object

After the HTTP request executes, the `results` object contains:

```json
{
  "body": { ... },
  "statusCode": 200,
  "headers": {
    "content-type": "application/json",
    "cache-control": "max-age=3600"
  }
}
```

## Error Handling

Configure error handling in the `error` section:

```yaml
error:
  if: ${{ !Q.isHTTPStatusInRange(results.statusCode, ["200-299"]) }}
  retryIf: ${{ Q.isHTTPStatusInRange(results.statusCode, ["429", "500-599"]) }}
  includeResult: true
  message: ${{ Q.toJSON(results) }}
```

| Field | Description |
|-------|-------------|
| `if` | Condition that determines if this is an error |
| `retryIf` | Condition for automatic retry (rate limits, server errors) |
| `includeResult` | Include full response in error message |
| `message` | Custom error message |

## Authentication

See [auth-types.md](auth-types.md) for complete authentication type definitions and examples.

### Using Connections

The preferred way to authenticate HTTP requests is via workspace connections:

```yaml
configuration:
  options:
    url: https://api.example.com
    method: GET
    auth: ${{ connection.auth }}
  connection:
    key: my-api-connection
```

### Typed Connections

Use `type` to restrict which workspace connections the user can select. A single string allows one connection type:

```yaml
connection:
  key: john-gmail
  type: gmail
```

Use a non-empty array when several connection types are acceptable:

```yaml
connection:
  key: github-connection
  type:
    - github-oauth2
    - github-pat
```

### Connection Types

Each connection `type` value is an **exact match** against a connection-type name registered in the platform (e.g. `gmail`, `google-calendar`, `github-oauth2`, `github-pat`, `slack-oauth2`, `slack-bearer`, `stripe-bearer`, `jira-oauth2`, `openai-bearer`). A made-up type (e.g. `github` or `slack`) matches nothing and the user cannot select a connection. Omit `type` to allow any connection.

The interpolation context exposes exactly what the connection type's `result:` block renders — always `connection.auth`, usually `connection.baseUrl` (use it for account-specific hosts like Zendesk/Shopify/Salesforce/Twilio), plus occasional extras (e.g. `connection.cloudId` for jira-oauth2, `connection.accountSid` for twilio). Check the connection YAML before referencing any other `connection.*` field — fields like `connection.subdomain` or `connection.region` do not exist.

## Using Variables (vars)

Variables provide a temporary computation space for building complex values:

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

## Output Transformation

Use `outputs` to transform the response for downstream actors:

```yaml
# Extract specific field
outputs: ${{ results.body }}

# Find item in array
outputs: ${{ results.body.labels.find(label => label.name === inputs.labelName).id }}

# Return multiple fields
outputs:
  id: ${{ results.body.id }}
  name: ${{ results.body.name }}
```

Don't overuse `outputs`. Unless asked by the user, don't use `outputs` to transform the response. Only use it to remove `headers` from the response.

```yaml
outputs: ${{ results.body }}
```

## Common Patterns

### GET with Query Parameters

```yaml
options:
  url: https://api.example.com/search
  method: GET
  queryParams:
    q: ${{ inputs.query }}
    limit: ${{ inputs.limit || 100 }}
    pageToken: ${{ inputs.pageToken }}
```

### POST with JSON Body

```yaml
options:
  url: https://api.example.com/items
  method: POST
  headers:
    content-type: application/json
  body:
    name: ${{ inputs.name }}
    data: ${{ inputs.data }}
```

### Conditional Fields

Use conditional expressions to omit fields when undefined:

```yaml
body:
  required_field: ${{ inputs.required }}
  optional_field: ${{ inputs.optional?.length > 0 ? inputs.optional : undefined }}
```

### URL Path Parameters

```yaml
options:
  url: https://api.example.com/users/${{ inputs.userId }}/messages/${{ inputs.messageId }}
  method: GET
```

## Input Schemas

Define input schemas for validation and UI generation:

```yaml
schemas:
  inputs:
    type: object
    properties:
      userId:
        type: string
        title: User ID
        description: The user's email or 'me' for authenticated user
        default: me
      format:
        type: string
        title: Format
        enum:
          - minimal
          - full
          - raw
        default: full
      maxResults:
        type: integer
        title: Max Results
        description: Maximum number of results to return
    required:
      - userId
```

### Schema Types

| Type | Description |
|------|-------------|
| `string` | Text value |
| `integer` | Whole number |
| `number` | Decimal number |
| `boolean` | True/false |
| `array` | List of items |
| `object` | Nested object |
| `any` | Flexible type (use for dynamic objects) |

## Examples

See [http-request-actor-examples.md](http-request-actor-examples.md) for complete examples including:
- Basic GET request with query params
- Gmail: Fetch label ID by name
- Gmail: Create a draft
- Gmail: Get email by ID (with input schema)
- Airtable: Append data to table
- Gmail: Search email (typed connection)
- Firecrawl: Scrape (complex body handling)

## Quick Example

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  ACTR01example:
    type: HttpRequestActor
    version: 1
    name: Fetch Data from API
    msgVar: fetch_data_from_api
    description: Fetch data from external API
    isActive: true
    continueOnError: false
    enableLTM: false
    enableSTM: false
    sourcePorts:
      - id: SPRTdefault
    configuration:
      inputs:
        endpoint: ''
      options:
        url: https://api.example.com/${{ inputs.endpoint }}
        method: GET
        headers:
          content-type: application/json; charset=utf-8
        auth: ${{ connection.auth }}
      connection:
        key: api-connection
      error:
        if: ${{ !Q.isHTTPStatusInRange(results.statusCode, ["200-299"]) }}
        retryIf: ${{ Q.isHTTPStatusInRange(results.statusCode, ["429", "500-599"]) }}
        includeResult: true
        message: ${{ Q.toJSON(results) }}
    schemas:
      inputs:
        type: object
        properties:
          endpoint:
            type: string
            title: Endpoint
            description: API endpoint path
        required:
          - endpoint
    id: ACTR01example
    position:
      x: 0
      'y': 0
    edges: {}
```
