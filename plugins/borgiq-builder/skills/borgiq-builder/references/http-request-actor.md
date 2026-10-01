# HTTP Request Actor Reference

HttpRequestActor makes one REST call to an external service. Read it when you hand-build an HTTP actor: its options,
result, error block, authentication and common request patterns.

**Search templates first.** Most integrations (Gmail, Slack, GitHub, Google, Notion, …) ship as vetted templates; adapt
one before hand-writing `options`, `sourcePorts` and schemas: `borgiq templates apps --search "<vendor>"` →
`templates list --app-id TAPP…` → `templates get ATMP…` ([borgiq-cli.md](borgiq-cli.md)). Several dependent calls
belong in one DenoActor or PythonActor, not a chain of HTTP actors.

## Contents

- [Configuration Structure](#configuration-structure)
- [Options Reference](#options-reference)
- [Results Object](#results-object)
- [Error Handling](#error-handling)
- [Authentication](#authentication)
- [Using Variables (vars)](#using-variables-vars)
- [Output Transformation](#output-transformation)
- [Common Patterns](#common-patterns)
- [Input Schemas](#input-schemas)

## Configuration Structure

As a bundle `actor.yaml` (edges and position live in `canvas.yaml`):

```yaml
id: ACTR01kx4b00000000000000000021
version: 1
type: HttpRequestActor
name: Fetch Data from API
msgVar: fetch_data_from_api
description: Fetches data from the external API.
isActive: true
continueOnError: false
enableLTM: false
enableSTM: false
sourcePorts:
  - id: SPRTdefault
configuration:
  inputs:
    endpoint: ${{ msg.webhook_trigger.body.endpoint }}
  options:
    url: https://api.example.com/${{ inputs.endpoint }}
    method: GET
    headers:
      content-type: application/json; charset=utf-8
    auth: ${{ connection.auth }}
  connection:
    key: api-connection         # the workspace connection's key
    # type: <registered type>   # optional: one registry name, or a non-empty list
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
```

## Options Reference

Exact schema: [httpRequest/index.md](typescript/actorSchemas/task/httpRequest/index.md).

| Option | Type | Default | Meaning |
|---|---|---|---|
| `url` | string | required | Endpoint URL; interpolate path parameters into it |
| `method` | string | required | `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `HEAD`, `OPTIONS`, `PURGE`, `LINK`, `UNLINK` (any case) |
| `headers` | object | — | Header values are strings, numbers or booleans |
| `queryParams` | object | — | URL query parameters |
| `body` | any | — | Request body |
| `auth` | `{ type, values }` | — | Usually `${{ connection.auth }}` ([auth-types.md](auth-types.md)) |
| `contentType` | string | — | Body encoding: `json`, `xml`, `text`, `buffer` (raw binary), or any Content-Type such as `image/png` |
| `responseType` | string | `json` | `json` (parse), `text`, `arraybuffer` (binary file), `blob`, `document` (HTML/XML), `stream` |
| `multiPartFormFiles` | object | — | Field name → BIQFile or list of BIQFiles, sent as a multipart form |
| `emitRequest` | boolean | `false` | Add the sent request to the result as `request` |
| `emitBodyAsFile` | boolean | `false` | Return the response body as a file |
| `options` | object | — | Advanced: `maxContentLength` (response), `maxBodyLength` (request), `basicAuth` (`{ username, password }` for the proxy) |

```yaml
options:
  url: https://api.example.com/upload
  method: POST
  multiPartFormFiles:
    file: ${{ assets.uploadFile }}
    files:
      - ${{ assets.file1 }}
      - ${{ assets.file2 }}
  options:
    maxContentLength: 10485760   # 10 MB
```

## Results Object

`results` (and the emitted message, unless `outputs` reshapes it) is `{ body, statusCode, headers }`, plus `request`
(`url`, `method`, `headers`, `body`, `queryParams`) when `emitRequest: true`.

## Error Handling

Declare HTTP failures in the `error` block, as in the skeleton: `if` marks a non-2xx status as a failure, `retryIf`
retries rate limits and server errors, `includeResult` attaches the response as `metadata.results`, and `message`
sets the error text. Fields, the `err.<msgVar>` shape and `continueOnError`: [error-handling.md](error-handling.md).

## Authentication

Authenticate through a workspace connection: `auth: ${{ connection.auth }}` with `connection.key`. Other auth types and
hand-written `auth`: [auth-types.md](auth-types.md).

### Typed Connections

`connection.type` restricts which workspace connections the user can pick: one type name, or a non-empty list when
several are acceptable:

```yaml
connection:
  key: github-connection
  type:
    - github-oauth2
    - github-pat
```

Each value must **exactly match** a connection type registered in the platform (e.g. `gmail`, `google-calendar`,
`github-oauth2`, `github-pat`, `slack-oauth2`, `slack-bearer`, `stripe-bearer`, `jira-oauth2`, `openai-bearer`). A
made-up type (`github`, `slack`) matches nothing, and the user cannot select a connection. Omit `type` to allow any
connection.

The context exposes exactly what the connection type's `result:` block renders: always `connection.auth`, usually
`connection.baseUrl` (use it for account-specific hosts such as Zendesk, Shopify, Salesforce or Twilio), and occasional
extras (`connection.cloudId` for `jira-oauth2`, `connection.accountSid` for twilio). Check the connection YAML before
using any other `connection.*` field; `connection.subdomain` and `connection.region` do not exist.

## Using Variables (vars)

`vars` are scratch values computed in order, each able to read the ones before it. Example: a Gmail draft, whose raw
message is the header lines (optional ones dropped), a blank line and the body, base64-encoded:

```yaml
configuration:
  vars:
    - headerContent:
        - 'From: ${{ inputs.from }}'
        - 'To: ${{ inputs.to }}'
        - '${{ inputs.cc ? `Cc: ${inputs.cc}` : undefined }}'
        - 'Subject: ${{ inputs.subject }}'
    - header: ${{ Q.lo.compact(vars.headerContent) }}
    - base64Message: ${{ Q.toBase64([...vars.header, '', inputs.body].join('\r\n')) }}
  options:
    url: https://gmail.googleapis.com/gmail/v1/users/me/drafts
    method: POST
    auth: ${{ connection.auth }}
    body:
      message:
        raw: ${{ vars.base64Message }}
  connection:
    key: my-gmail
    type: gmail
```

## Output Transformation

Leave `outputs` out unless the user asks for a reshaped result; the one routine use is dropping `headers` with
`outputs: ${{ results.body }}`. When asked:

```yaml
outputs: ${{ results.body.labels.find(label => label.name === inputs.labelName).id }}
```

## Common Patterns

Omit an optional field by making it `undefined` (quote the value when it contains `: `):

```yaml
queryParams:
  q: ${{ inputs.query }}
  limit: ${{ inputs.limit || 100 }}
  pageToken: ${{ inputs.pageToken }}
body:
  required_field: ${{ inputs.required }}
  optional_field: "${{ inputs.optional?.length > 0 ? inputs.optional : undefined }}"
```

### URL Path Parameters

```yaml
options:
  url: https://api.example.com/users/${{ inputs.userId }}/messages/${{ inputs.messageId }}
  method: GET
```

## Input Schemas

Define input schemas for validation and UI generation:

`schemas.inputs` is a JSON schema whose properties take `type` (`string`, `integer`, `number`, `boolean`, `array`,
`object`, or `any` for a free-form value), `title`, `description`, `enum` and `default`. Schema design: the
`borgiq-json-schema-builder` skill.
