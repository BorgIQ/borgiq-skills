# Python Actor Reference

The PythonActor executes custom Python code in a sandboxed Python runtime within BorgIQ workflows.

> **API model (important):** A Python Actor is a **pure function** — `receive(req: Request) -> Response`. There is **no `actor` object**. Read everything you need from `req` (`req.inputs`, `req.ctx`, `req.connection`, `req.credentials`, `req.memory`) and return a `Response`. Memory is **value-in / value-out**: read it from `req.memory`, and **return `memory` in the `Response` to persist it**. Emitted messages go under `Response.results`. Signals are returned via `Response.signal` (built with `signal.*`), not set imperatively. Everything — the `Request`/`Response` types, the `signal` constructors, `RetryableError`, and the `biq_api`/`mount_file`/`stash_file` helpers — is imported from the single `borgiq` package.

## Table of Contents

- [Execution Environment](#execution-environment)
- [Configuration Structure](#configuration-structure)
- [Input Schemas](#input-schemas)
- [Options Reference](#options-reference)
- [TypeScript Schema Definition](#typescript-schema-definition)
- [Code Files](#code-files)
- [Code Template](#code-template)
- [Logging](#logging)
- [Request and Response](#request-and-response)
- [Memory Types](#memory-types)
- [Installing Dependencies](#installing-dependencies)
- [File Operations](#file-operations)
- [BIQ Runtime API](#biq-runtime-api)
- [Error Handling](#error-handling)
- [Credentials and Connections](#credentials-and-connections)
- [Signals](#signals)
- [Runtime Context](#runtime-context)
- [Return Values](#return-values)
- [Examples](#examples)
- [Checkpointing for Resumable Operations](#checkpointing-for-resumable-operations)
- [Best Practices](#best-practices)

## Execution Environment

Python Actors run inside **AWS Lambda** with the following constraints:

| Constraint | Value | Notes |
|------------|-------|-------|
| Maximum timeout | 15 minutes | Absolute limit, cannot be exceeded |
| Configurable timeout | Varies | Set per workspace via `pythonActorTimeoutInSeconds` |
| Memory | Configurable | Set in Lambda configuration |
| Ephemeral storage | Temp directory | Limited, cleared between invocations |
| Python version | 3.11+ | Managed by UV package manager |

**Critical Implication:** All long-running operations must be designed as **pausable and resumable**. Never assume an operation will complete in a single invocation.

### Design for Interruption

Since Lambda can timeout at any point, your code must:

1. **Track progress** - Know where you stopped
2. **Save state** - Persist progress before timeout (return it in `Response.memory`)
3. **Resume gracefully** - Pick up where you left off (read it from `req.memory`)
4. **Set safe time limits** - Stop processing before Lambda kills the function

### Temporary File Storage

Use Python's `tempfile` module for temporary directories. **Never hardcode paths like `/tmp`.**

```python
import tempfile
import os

# Correct - use tempfile module
with tempfile.TemporaryDirectory(prefix="myactor_") as temp_dir:
    temp_file = os.path.join(temp_dir, "output.json")
    with open(temp_file, "w") as f:
        f.write(json.dumps(data))
    # Process file...
# Directory is automatically cleaned up

# Wrong - never hardcode paths
bad_path = "/tmp/myfile.json"  # Don't do this
```

**Important:**
- Temp files are cleared between Lambda invocations
- Do not rely on temp storage for persistence—use LTM (returned in `Response.memory`) or external storage
- Always clean up temp files when done to avoid storage limits
- Use context managers (`with` statements) for automatic cleanup

## Configuration Structure

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  ACTR01xxxxx:
    type: PythonActor
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
      options:
        emitArrayAsSingleMessage: true
        dependencies:
          - pandas==2.2.3
          - numpy==2.1.3
        env:
          - name: ENV_VAR
            value: some_value
      # Source is a list of files, sibling of `options`, never interpolated.
      # Exactly one entry must have path `main.py` — it is the entrypoint.
      codeDir:
        - path: main.py
          content: |
            from typing import Any
            from borgiq import Request, Response, biq_api, mount_file, stash_file, RetryableError

            from utils import shape

            def receive(req: Request) -> Response:
                return Response(results=shape("success"))
        - path: utils.py
          content: |
            def shape(result: str) -> dict:
                return {"result": result}
    schemas:
      inputs:
        type: object
        properties:
          key:
            type: string
            title: Key
            description: Description of the key input
        required:
          - key
    id: ACTR01xxxxx
    position:
      x: 0
      'y': 0
    edges: {}
```

## Input Schemas

**Important:** If your code accesses `req.inputs` properties, you MUST configure both:
1. `configuration.inputs` - The actual input values (can reference `msg`, `ctx`, `secrets`)
2. `schemas.inputs` - A JSON Schema defining the input structure for validation and UI generation

### Schema Format

Input schemas use JSON Schema with BorgIQ UI extensions:

```yaml
schemas:
  inputs:
    type: object
    properties:
      apiKey:
        type: string
        title: API Key
        description: The API key for authentication
        ui:
          order: 0
          component: password
      timeout:
        type: number
        title: Timeout (seconds)
        description: Request timeout in seconds
        default: 30
        ui:
          order: 1
      debugMode:
        type: boolean
        title: Debug Mode
        description: Enable verbose logging
        default: false
        ui:
          order: 2
    required:
      - apiKey
```

### UI Extensions

The `ui` property provides hints for form rendering:

| Property | Description |
|----------|-------------|
| `order` | Display order in forms (0 = first) |
| `component` | Override default component (`password`, `textarea`, `code`, etc.) |

### Complete Example

```yaml
actors:
  ACTR01example:
    type: PythonActor
    version: 1
    name: Process Data
    msgVar: process_data
    configuration:
      inputs:
        apiKey: ${{ credentials.API_KEY }}
        timeout: 30
        data: ${{ msg.upstream_actor.body }}
      options:
        dependencies:
          - requests==2.32.3
      codeDir:
        - path: main.py
          content: |
            from typing import Any
            import requests
            from borgiq import Request, Response, RetryableError

            def receive(req: Request) -> Response:
                api_key = req.inputs.get('apiKey')
                timeout = req.inputs.get('timeout', 30)
                data = req.inputs.get('data')

                response = requests.post(
                    'https://api.example.com/process',
                    headers={
                        'Authorization': f'Bearer {api_key}',
                        'Content-Type': 'application/json',
                    },
                    json=data,
                    timeout=timeout,
                )
                response.raise_for_status()

                return Response(results=response.json())
    schemas:
      inputs:
        type: object
        properties:
          apiKey:
            type: string
            title: API Key
            description: API key for the external service
            ui:
              order: 0
              component: password
          timeout:
            type: number
            title: Timeout
            description: Request timeout in seconds
            default: 30
            ui:
              order: 1
          data:
            type: object
            title: Data
            description: Data to process
            ui:
              order: 2
        required:
          - apiKey
          - data
```

## Options Reference

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `emitArrayAsSingleMessage` | boolean | true | Emit array as single message instead of multiple messages |
| `dependencies` | string[] | [] | Python packages to install (e.g., `["pandas>=2.0.0", "numpy>=1.24.0"]`) |
| `env` | object[] | [] | Environment variables for the runtime |

## TypeScript Schema Definition

The complete TypeScript schema for PythonActor options:

```typescript
import { z } from 'zod';

/** One source file of the actor's project tree. */
export const CodeFileSchema = z.object({
  /** path relative to the project root; '/' separates nested folders, e.g. 'lib/util.py' */
  path: z.string().min(1).max(255),
  /** raw file content, UTF-8 text */
  content: z.string(),
});

/**
 * The PythonActor's `configuration.codeDir`: at most 200 files and 1 MiB of content in total,
 * exactly one of them at `main.py`, none of them using a filename the runtime reserves.
 */
export const PythonActorCodeDirSchema = makeCodeDirSchema({
  requiredEntrypoint: 'main.py',
  reservedPaths: PYTHON_RESERVED_PATHS,
});

/** The options for the PythonActor */
export const PythonActorOptionsSchema = z.object({
  emitArrayAsSingleMessage: z.boolean().nullish()
    .describe('Emit the array as a single message instead of an array of messages, defaults to true')
    .default(true),
  dependencies: z.array(z.string()).nullish()
    .describe('List of Python package dependencies (e.g., ["pandas>=2.0.0", "numpy>=1.24.0"]). These will be installed using UV')
    .default([]),
  env: z.array(z.object({
    name: z.string()
      .regex(/^[A-Z0-9_]+$/, 'Environment variable name must contain only uppercase letters, numbers and underscores')
      .regex(/^(?!TMPDIR$)/, 'Environment variable name cannot be TMPDIR')
      .regex(/^(?!HOME$)/, 'Environment variable name cannot be HOME')
      .regex(/^(?!PYTHONUNBUFFERED$)/, 'Environment variable name cannot be PYTHONUNBUFFERED')
      .regex(/^(?!UV_CACHE_DIR$)/, 'Environment variable name cannot be UV_CACHE_DIR')
      .regex(/^(?!UV_PROJECT_ENVIRONMENT$)/, 'Environment variable name cannot be UV_PROJECT_ENVIRONMENT')
      .regex(/^(?!PYTHONUSERBASE$)/, 'Environment variable name cannot be PYTHONUSERBASE')
      .describe('Environment variable name (must contain only uppercase letters, numbers and underscores)'),
    value: z.string().nullish()
      .describe('Environment variable value')
  })).nullish().default([])
    .describe('List of environment variables to pass to the Python runtime'),
});

/** The response schema for the PythonActor */
export const PythonActorResultSchema = z.any();
```

### Environment Variables

Environment variable names must:
- Contain only uppercase letters, numbers, and underscores (`[A-Z0-9_]+`)
- Not be reserved names: `TMPDIR`, `HOME`, `PYTHONUNBUFFERED`, `UV_CACHE_DIR`, `UV_PROJECT_ENVIRONMENT`, `PYTHONUSERBASE`

```yaml
options:
  env:
    - name: API_KEY
      value: ${{ credentials.apiKey }}
    - name: DEBUG_MODE
      value: "true"
```

## Code Files

A Python Actor's source is a small project, held in `configuration.codeDir` as a list of `{path, content}` files:

```yaml
configuration:
  codeDir:
    - path: main.py            # required entrypoint — defines receive()
      content: |
        from borgiq import Request, Response

        from utils import normalize
        from lib.report import summarize

        def receive(req: Request) -> Response:
            return Response(results=summarize(normalize(req.inputs)))
    - path: utils.py           # a sibling module: import it by name
      content: |
        def normalize(inputs: dict) -> dict:
            return {k: v for k, v in inputs.items() if v is not None}
    - path: lib/__init__.py    # a package needs its __init__.py
      content: ""
    - path: lib/report.py
      content: |
        def summarize(data: dict) -> dict:
            return {"count": len(data), "data": data}
```

Rules:

- **`main.py` is required** and must be at the root of the tree — exactly one entry may have that path. The runtime imports it; a tree without it is rejected on save.
- **The tree root is on `sys.path`**, so a root-level `utils.py` is `import utils`, and a folder is a package once it contains `__init__.py` (`from lib.report import summarize`, nested packages included). Declared dependencies are importable from any of your modules, not just the entrypoint.
- **`codeDir` is never interpolated.** `${{ }}` in your source is literal text, not an expression — pass runtime values through `configuration.inputs` and read them from `req.inputs`. A `${{ credentials.* }}` written into source is therefore never resolved, and source that happens to look like an expression survives verbatim.
- **Removing an entry removes the file.** The runtime rebuilds the actor's directory from the list on every code change, so a deleted module stops being importable immediately.
- **Reserved filenames** — the runtime puts its own modules in the same directory, and the tree root wins on `sys.path`, so a file of your own with one of these names would shadow it. Rejected on save: `server.py`, `handler.py`, `borgiq.py`, `pyproject.toml`, `.python-version`, `uv.lock`, and anything under `.borgiq/`, `.venv/` or `borgiq/`. Comparison is case-insensitive. Dependencies stay in `options.dependencies`, which is why a `pyproject.toml` of your own is reserved rather than merged.
- **Shadowing a third-party package is your call, not an error.** A root `requests.py` wins over the installed `requests` — normal Python behavior, and only runtime-critical names are reserved. Name modules distinctly to avoid surprising yourself.
- **Limits:** UTF-8 text only, at most 200 files, 1 MiB of content across the whole tree. Paths are relative, `/`-separated, and may not contain `.` or `..` segments.

Editing surfaces:

- **Bundle:** real files under the actor folder's `code/` directory — see [Canvas Bundles → Code actor project trees](cli/canvas-bundles.md#code-actor-project-trees).
- **Direct document / batch payload:** the `configuration.codeDir` list itself, as shown above. It is a structured array in both formats, not a YAML string.
- **Web editor:** the actor's Code page shows a file tree beside the editor; the right-hand panel on the canvas edits the entrypoint inline. The **AI code assist works on the selected file only** — it cannot see sibling files, so prompt it per file and wire the pieces together yourself.

An actor written before multi-file support carries a single `configuration.code` string. It keeps running, and saving it from the editor (or pushing it from a bundle) converts it to a one-entry `codeDir`. Never set both fields.

## Code Template

The entrypoint file, `main.py`:

```python
from typing import Any, Dict, List, Optional, Union, BinaryIO
from borgiq import Request, Response, signal, biq_api, mount_file, stash_file, RetryableError

def receive(req: Request) -> Response:
    # req.inputs                       — interpolated inputs for this invocation
    # req.ctx                          — RuntimeContext (org / workspace / canvas / flowrun / actor)
    # req.connection                   — the single connection's resolved config (read-only)
    # req.credentials['XXXX']          — resolved secret values (read-only)
    # req.memory['stm'] / req.memory['ltm']  — short / long term memory (value-in)
    # biq_api(path, **kwargs)          — request wrapper for the BIQ Runtime API
    # mount_file(file) / stash_file(file, filename=None, mime_type=None)
    # raise RetryableError() to be re-invoked with the same message; other exceptions are permanent.

    # Console output is captured and stored with the flowrun
    print('Processing started')

    return Response(
        # `results` is emitted as msg.ActorName downstream (list => one message per item).
        results={'result': 'data'},
        # Return memory to persist it; omit to leave it unchanged.
        memory=req.memory,
        # Any actor may respond to a pending request in the flow. Allowed signals:
        # signal.webhook_respond | signal.callable_response | signal.delay_until
        # signal=signal.webhook_respond(status_code=200, body={"ok": True}),
    )
```

**Return-value notes:**
- `results=None` (or omitting `results`) emits **no** message downstream.
- `results=[a, b]` emits one message per item (unless `emitArrayAsSingleMessage: true`).
- `raise RetryableError()` re-invokes the actor with the same message; all other exceptions are permanent.

## Logging

Console output is captured and stored with the flowrun for debugging:

```python
print('Processing item:', item['id'])
print(f'Rate limit approaching: {rate_remaining}')
print(f'ERROR: Failed to process: {error}')
```

**Note:** Logs are visible in the flowrun details in the BorgIQ UI.

## Request and Response

User code is the pure function `receive(req: Request) -> Response`. There is no `actor` object — read everything from `req`, and return a `Response`.

```python
class Request:
    inputs: Dict[str, Any]          # interpolated inputs for this invocation (read-only)
    ctx: RuntimeContext             # org / workspace / canvas / flowrun / actor metadata
    connection: Dict[str, Any]      # the single connection's resolved config (read-only)
    credentials: Dict[str, str]     # resolved secret values, keyed by name (read-only)
    memory: Dict[str, Any]          # {"stm": {...}, "ltm": {...}} (value-in)

class Response:
    results: Any                    # emitted as msg.ActorName (list => one message per item)
    memory: Optional[Dict[str, Any]]  # {"stm": ..., "ltm": ...} to persist; omit to leave unchanged
    signal: Optional[Any]           # one of signal.webhook_respond / callable_response / delay_until
    error: Optional[Dict[str, Any]]  # {"message": str, "retryable": bool} to fail explicitly
```

**Migration note (from the old `actor` object):**

| Old (removed) | New |
|---------------|-----|
| `receive(inputs={}, actor=None)` | `receive(req: Request)` |
| `inputs.get('x')` | `req.inputs.get('x')` |
| `actor.ctx['...']` | `req.ctx['...']` |
| `actor.connection` | `req.connection` |
| `actor.credentials` | `req.credentials` |
| `actor.stm` / `actor.ltm` (mutated in place) | `req.memory['stm']` / `req.memory['ltm']` (read), returned in `Response.memory` (write) |
| `actor.set_signal({...})` | `return Response(signal=signal.<type>(...))` |
| `actor.assets` | Removed — manage assets via the `/assets` `biq_api` endpoints |
| `return {data}` | `return Response(results={data})` |
| `from borgiq.actor import ...` / `from borgiq.errors import ...` | `from borgiq import Request, Response, signal, biq_api, mount_file, stash_file, RetryableError` |

## Memory Types

Memory is **value-in / value-out**. Read the incoming state from `req.memory`, and **return `memory` in your `Response` to persist it**. If you omit `memory` from the response, the stored memory is left unchanged.

### Short-Term Memory (STM)

Persists within a single flowrun. Useful for state within one workflow execution.

```python
def receive(req: Request) -> Response:
    # Read value
    count = req.memory['stm'].get('counter', 0) + 1

    # Update memory and return it to persist
    req.memory['stm']['counter'] = count
    return Response(results={'count': count}, memory=req.memory)
```

### Long-Term Memory (LTM)

Persists across flowruns. Useful for tracking state between workflow executions.

```python
import time

def receive(req: Request) -> Response:
    # Read last processed timestamp from incoming memory
    last_checked_at = req.memory['ltm'].get('lastInvokedAt', 0)

    # Update and persist via Response.memory
    req.memory['ltm']['lastInvokedAt'] = int(time.time() * 1000)
    return Response(results={'lastCheckedAt': last_checked_at}, memory=req.memory)
```

**Important:** When using LTM, enable it in actor configuration:
```yaml
enableLTM: true
```

## Installing Dependencies

Python dependencies are installed using the **UV package manager** for fast cold starts. Specify dependencies in the `options.dependencies` array.

> **Security rule — pin exact versions.** Always pin each dependency to an
> exact version with `==`. Dependencies are resolved and installed at deploy /
> cold-start time and there is **no committed lockfile** for an actor's
> `dependencies`, so a bare name or a floating range (`>=`, `~=`, `*`) installs
> whatever is **latest** at that moment — a supply-chain risk (a malicious or
> breaking release is pulled automatically) and a source of non-deterministic
> deploys. Exact pins are immune to both.

```yaml
options:
  dependencies:
    - pandas==2.2.3
    - numpy==2.1.3
    - requests==2.32.3
    - beautifulsoup4==4.12.3
```

**Dependency Format:**
- Exact version (**required for security**): `pandas==2.2.3`
- Avoid — bare name (`pandas`), open range (`pandas>=2.0.0`), or bounded range (`pandas>=2.0.0,<3.0.0`): all resolve non-deterministically.

**Note:** UV provides significantly faster dependency installation compared to pip, reducing cold start times.

## File Operations

BorgIQ provides utilities for working with files in Python actors.

### mount_file

Mounts a BIQFile to the local filesystem and returns the path. Use this to access files passed as inputs.

```python
from borgiq import Request, Response, mount_file

def receive(req: Request) -> Response:
    # Mount the input file to local filesystem
    file_path = mount_file(req.inputs.get('uploadedFile'))

    # Now you can read it with standard Python
    with open(file_path, 'r') as f:
        content = f.read()

    return Response(results={'content': content})
```

### stash_file

Uploads a file to BorgIQ storage and returns a BIQFile object that can be passed to downstream actors.

```python
from borgiq import Request, Response, stash_file

def receive(req: Request) -> Response:
    # Create some content
    csv_content = "name,age\nAlice,30\nBob,25"

    # Upload to BorgIQ storage (accepts str, bytes, bytearray, memoryview, or file-like object)
    biq_file = stash_file(csv_content.encode('utf-8'), filename='output.csv', mime_type='text/csv')

    # Return the file reference for downstream actors
    return Response(results={'file': biq_file})
```

**Signature:** `stash_file(file: str | bytes | bytearray | memoryview | BinaryIO, filename: str = None, mime_type: str = None) -> dict`

**File parameter accepts:**
- `str` - Path to a local file
- `bytes`, `bytearray`, `memoryview` - Binary data
- File-like object - Any object with a `read()` method

### File Processing Example

```python
import tempfile
import os
from borgiq import Request, Response, mount_file, stash_file

def receive(req: Request) -> Response:
    # Mount input file
    input_path = mount_file(req.inputs.get('inputFile'))

    # Process the file
    with open(input_path, 'r') as f:
        content = f.read()
    processed = content.upper()

    # Create temp directory for output
    with tempfile.TemporaryDirectory(prefix="process_") as temp_dir:
        output_path = os.path.join(temp_dir, "processed.txt")
        with open(output_path, 'w') as f:
            f.write(processed)

        # Stash the output file
        output_file = stash_file(output_path, filename='processed.txt', mime_type='text/plain')

    return Response(results={'outputFile': output_file})
```

## BIQ Runtime API

Use `biq_api` to make authenticated calls to the BorgIQ Runtime API from within your actor.

```python
from borgiq import Request, Response, biq_api

def receive(req: Request) -> Response:
    # Make an API call to BorgIQ Runtime
    response = biq_api(
        '/api/some-endpoint',
        method='POST',
        json={'data': 'value'}
    )

    if not response.ok:
        raise Exception(f'BIQ API error: {response.status_code}')

    return Response(results=response.json())
```

**Note:** `biq_api` uses the requests library interface. Common parameters: `method`, `json`, `data`, `headers`, `params`.

### Available API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/collections` | POST | All Collection API operations (action in request body) |
| `/issueCallbackToken` | POST | Issue a callback token for async workflows |
| `/files/{fileId}/downloadUrl` | GET | Get a signed download URL for a file (supports `?expiresInMinutes=N&downloadAsAttachment=true`) |
| `/files/upload` | POST | Upload multiple files (multipart) |
| `/files/upload` | PUT | Stream a single file directly to S3 |
| `/files/download` | GET | Stream file content from S3 |
| `/files/updateUploads` | POST | Update file status after presigned URL upload |

> **File operations:** Prefer `mount_file` and `stash_file` from `borgiq` instead of calling the `/files/*` endpoints directly. These helpers handle download, upload, temp file management, and cleanup automatically. The raw endpoints above are what `mount_file`/`stash_file` use under the hood — only call them directly if you need advanced control (e.g., custom expiration, presigned URL workflows).

| `/assets` | GET | List workspace assets |
| `/assets` | POST | Create a new asset |
| `/assets/{key}` | PUT | Update an asset |
| `/assets/{key}` | DELETE | Delete an asset |
| `/secrets` | GET | Get decrypted secrets |
| `/connections/{key}` | GET | Get decrypted connection credentials |
| `/publicKey` | GET | Get workspace public key (for encrypting sensitive data) |
| `/sendEmail` | POST | Send an email |
| `/interfaces/status` | PUT | Update interface status display |
| `/toolkit/chatCompletion` | POST | AI chat completion (internal) |
| `/dataStore/*` | Various | Legacy data store operations (deprecated — use `/collections` instead) |

> **Assets:** the old `actor.assets` field no longer exists in the `Request`. To read or manage workspace assets from actor code, use the `/assets` `biq_api` endpoints above.

### Collection API

The Collection API provides structured, persistent storage organized into named collections, backed by DynamoDB. All operations use `POST /collections` with an `action` field.

**For full documentation** of all 13 actions, parameters, conditions, concurrent update patterns, DynamoDB behavior, and error codes, see [collection-api.md](collection-api.md).

**Quick reference:**

```python
from borgiq import Request, Response, biq_api

def receive(req: Request) -> Response:
    # putItem — full replace
    biq_api('/collections', method='POST', json={
        'action': 'putItem', 'collection': 'my-col', 'key': 'k1',
        'value': {'name': 'Alice'}
    })

    # getItem — eventually consistent read (returns None if missing)
    item = biq_api('/collections', method='POST', json={
        'action': 'getItem', 'collection': 'my-col', 'key': 'k1'
    }).json()

    # updateItem — shallow field merge (only listed fields change)
    biq_api('/collections', method='POST', json={
        'action': 'updateItem', 'collection': 'my-col', 'key': 'k1',
        'value': {'email': 'new@email.com'}
    })

    # updateItem with atomic counter
    biq_api('/collections', method='POST', json={
        'action': 'updateItem', 'collection': 'my-col', 'key': 'k1',
        'atomicCounters': {'visits': 1}
    })

    # query — prefix search
    results = biq_api('/collections', method='POST', json={
        'action': 'query', 'collection': 'my-col', 'key': 'user:*'
    }).json()

    return Response(results=results.get('value', {}))
```

See [collection-api.md](collection-api.md) for `batchGetItem`, `batchWriteItem`, `transactWrite`, `transactGet`, conditions, concurrent update patterns, and DynamoDB mapping details.

## Error Handling

You can fail an actor in two ways: raise, or return an `error` on the `Response`.

### Retryable Errors

Raise `RetryableError` for transient failures that should be retried:

```python
from borgiq import RetryableError

if response.status_code == 401:
    raise RetryableError('Authentication failed, token might need refresh')

if response.status_code == 429:
    raise RetryableError('Rate limit reached, will retry')
```

### Permanent Errors

Regular exceptions are treated as permanent failures:

```python
if not req.inputs.get('required_field'):
    raise ValueError('Required field is missing')
```

### Explicit Error via Response

You may also return an explicit error instead of raising:

```python
return Response(error={'message': 'Upstream service unavailable', 'retryable': True})
```

## Credentials and Connections

**Key rule:** An actor can have **only ONE connection**, but **multiple secrets (credentials)**. Use `req.connection` for the single app/auth source; use `req.credentials` for individual secret values.

- `req.connection` — the single connection's resolved config (e.g. OAuth tokens at `req.connection['auth']['values']['token']`).
- `req.credentials` — a map of secret name → resolved string value (`req.credentials['MY_SECRET']`).

### Accessing Connection Auth

For OAuth and other connection-based auth (single connection):

```python
token = req.connection.get('auth', {}).get('values', {}).get('token')

response = requests.get(
    url,
    headers={'Authorization': f'Bearer {token}'}
)
```

### Accessing Credentials (Secrets)

Credentials are resolved secret values, keyed by name:

```python
api_key = req.credentials.get('OPENAI_API_KEY')
mongo_user = req.credentials.get('MONGO_USERNAME')
mongo_pass = req.credentials.get('MONGO_PASSWORD')
```

Reference them in the actor configuration with `${{ credentials.NAME }}`:

```yaml
configuration:
  inputs:
    apiKey: ${{ credentials.OPENAI_API_KEY }}
```

## Signals

Signals communicate with the Orchestrator for special operations. In the new model, a signal is a **value** returned on the `Response` and built with a `signal.*` constructor — there is no `actor.set_signal()`.

### User-Settable Signals

An actor returns at most one signal via `Response.signal`. The constructors available to actor code are:

| Constructor | Purpose | Arguments |
|-------------|---------|-----------|
| `signal.webhook_respond(...)` | Respond to a pending webhook request | `status_code: int, headers: dict = None, body: Any = None` |
| `signal.callable_response(...)` | Respond to a pending callable/subflow request | `payload: dict, throw_error: bool = None` |
| `signal.delay_until(...)` | Delay message emission until a time | `delay_until: str` (ISO 8601) |

> Other orchestrator signal types (`callFlow`, `waitForCallbackToken`, `notifyCallbackToken`, the `interface*` family, `ai`, `aiAgent`) are driven by their dedicated actors / the MessageProcessorActor, not set from Python code.

### Using Signals

```python
from datetime import datetime, timedelta
from borgiq import Request, Response, signal

def receive(req: Request) -> Response:
    # Delay emitting the message until a specific time
    delay_until = (datetime.now() + timedelta(minutes=1)).isoformat()
    return Response(
        results={'queued': True},
        signal=signal.delay_until(delay_until=delay_until),
    )
```

### WebhookRespond Signal

Use the `webhook_respond` signal to return an HTTP response directly from a Python Actor instead of using a separate WebhookResponseActor. The actor's `results` still propagate downstream as normal.

```python
from borgiq import Request, Response, signal

def receive(req: Request) -> Response:
    result = {'success': True, 'data': req.inputs.get('payload')}
    return Response(
        results=result,
        signal=signal.webhook_respond(
            status_code=200,
            headers={'Content-Type': 'application/json'},
            body=result,
        ),
    )
```

## Runtime Context

Access runtime information via `req.ctx`:

```python
ctx = {
    'org': {'id': str, 'name': str},
    'workspace': {
        'id': str,
        'slug': str,
        'name': str,
        'pythonActorTimeoutInSeconds': int,
    },
    'canvas': {'id': str, 'slug': str, 'name': str},  # + webhookTriggers / interfaceTriggers / appTriggers
    'actor': {'id': str, 'type': str, 'name': str, 'msgVar': str},
    'flowrun': {'id': str, 'createdAt': str},
    'triggerActor': {'id': str, 'type': str, 'name': str, 'msgVar': str},
    'sourceActor': {'id': str, 'type': str, 'name': str, 'msgVar': str},  # Optional
    'sourceMsgId': str,  # Optional
}
```

Usage:
```python
print(f"Running in workspace: {req.ctx['workspace']['name']}")
print(f"Flowrun ID: {req.ctx['flowrun']['id']}")
```

## Return Values

The `results` field of the returned `Response` becomes available as `msg.actor_msgvar` in downstream actors, where `actor_msgvar` is the actor's `msgVar` property.

| Return | Behavior |
|--------|----------|
| `Response(results={'data': ...})` | Emit dict as message |
| `Response(results=[item1, item2])` | Emit multiple messages (one per item) |
| `Response(results=None)` or `Response()` | Do NOT emit any message |
| `Response(results=..., memory=...)` | Emit message AND persist memory |

### Emitting Arrays

By default, returning a list under `results` emits multiple messages. To emit as single message:

```yaml
options:
  emitArrayAsSingleMessage: true
```

## Examples

### Basic Example: Execute Shell Commands

```python
from typing import Any
import subprocess
import os
from borgiq import Request, Response

def receive(req: Request) -> Response:
    """Execute shell commands using system binaries."""

    cmd = req.inputs.get('cmd', '').strip()

    if not cmd:
        raise ValueError("No command provided in inputs.cmd")

    try:
        # Set up environment with proper PATH
        env = os.environ.copy()
        env['PATH'] = '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:' + env.get('PATH', '')

        # Execute the command
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300,
            env=env
        )

        output = result.stdout
        if result.stderr:
            output += "\n" + result.stderr if output else result.stderr

        return Response(results={
            "output": output.strip() if output else "",
            "command": cmd,
            "returnCode": result.returncode,
            "success": result.returncode == 0
        })

    except subprocess.TimeoutExpired:
        return Response(results={
            "output": "",
            "error": f"Command timed out after 300 seconds: {cmd}",
            "command": cmd,
            "returnCode": -1,
            "success": False
        })
```

### LTM Example: Track Last Invocation

```python
from typing import Any
import time
from borgiq import Request, Response

def receive(req: Request) -> Response:
    last_checked_at = req.memory['ltm'].get('lastInvokedAt', 0)
    current_timestamp = int(time.time() * 1000)

    req.memory['ltm']['lastInvokedAt'] = current_timestamp

    return Response(results={'lastCheckedAt': last_checked_at}, memory=req.memory)
```

### API Example: Google Calendar Events

```python
from typing import Any
import requests
from datetime import datetime, timedelta
from borgiq import Request, Response, RetryableError

MAX_PROCESSED_EVENTS = 300

def receive(req: Request) -> Response:
    token = req.connection.get('auth', {}).get('values', {}).get('token')

    if not token:
        raise ValueError('No OAuth2 token found in connection')

    calendar_id = req.inputs.get('calendarId')
    now = datetime.now()
    time_min = now - timedelta(minutes=15)
    time_max = now + timedelta(minutes=15)

    from urllib.parse import quote
    encoded_calendar_id = quote(calendar_id, safe='')

    response = requests.get(
        f'https://www.googleapis.com/calendar/v3/calendars/{encoded_calendar_id}/events',
        params={
            'timeMin': time_min.isoformat() + 'Z',
            'timeMax': time_max.isoformat() + 'Z',
            'singleEvents': 'true',
            'orderBy': 'startTime',
        },
        headers={
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json',
        }
    )

    if response.status_code == 401:
        raise RetryableError('Authentication failed')

    if not response.ok:
        raise Exception(f'Failed to fetch events: {response.text}')

    data = response.json()

    # Track processed events in LTM (read from req.memory['ltm'])
    processed_event_ids = req.memory['ltm'].get('processedEventIds', {})

    events_to_emit = []

    for event in data.get('items', []):
        if event['id'] in processed_event_ids:
            continue

        events_to_emit.append({
            'id': event['id'],
            'summary': event.get('summary'),
            'start': event.get('start'),
            'end': event.get('end'),
        })

        processed_event_ids[event['id']] = True

    # Trim and persist LTM via Response.memory
    if len(processed_event_ids) > MAX_PROCESSED_EVENTS:
        # Keep only the most recent entries
        entries = list(processed_event_ids.items())[-MAX_PROCESSED_EVENTS:]
        processed_event_ids = dict(entries)

    req.memory['ltm']['processedEventIds'] = processed_event_ids

    return Response(results=events_to_emit, memory=req.memory)
```

### Data Processing Example: Pandas DataFrame

```python
from typing import Any
import pandas as pd
import io
from borgiq import Request, Response, mount_file, stash_file

def receive(req: Request) -> Response:
    # Mount input CSV file
    csv_path = mount_file(req.inputs.get('csvFile'))

    # Read into DataFrame
    df = pd.read_csv(csv_path)

    # Process data
    df['processed_at'] = pd.Timestamp.now().isoformat()
    df = df.dropna()

    # Convert to JSON and stash
    json_output = df.to_json(orient='records')
    output_file = stash_file(
        json_output.encode('utf-8'),
        filename='processed.json',
        mime_type='application/json'
    )

    return Response(results={
        'rowCount': len(df),
        'columns': list(df.columns),
        'outputFile': output_file
    })
```

### Database Example: MongoDB Operations

```python
from typing import Any
from pymongo import MongoClient
from borgiq import Request, Response

client = None

def receive(req: Request) -> Response:
    global client

    # Initialize client once, reuse across invocations
    if client is None:
        user = req.credentials.get('MONGO_USERNAME')
        password = req.credentials.get('MONGO_PASSWORD')
        cluster = req.inputs.get('cluster')

        uri = f"mongodb+srv://{user}:{password}@{cluster}/?retryWrites=true&w=majority"
        client = MongoClient(uri)

    # Ping the database
    result = client.admin.command('ping')

    return Response(results=result)
```

## Checkpointing for Resumable Operations

Since Python Actors run in AWS Lambda (max 15 minutes), long-running operations must implement checkpointing. There are two approaches:

| Approach | How It Works | Best For |
|----------|--------------|----------|
| **LTM-based** | Actor stores checkpoint in `req.memory['ltm']` (returned in `Response.memory`) | Self-contained actors, simple flows |
| **Input-based** | Checkpoint passed via `req.inputs`, emitted in `Response.results` | Complex flows, external orchestration |

**Important:** When implementing checkpointing, ask the user which approach they prefer.

### Checkpointing Large Datasets with Stashed Files

When working with large datasets that cannot fit in LTM or would be expensive to serialize repeatedly, use `stash_file` to persist intermediate data between invocations:

1. Write the working dataset to a temporary file
2. Stash the file to BorgIQ storage
3. Include the BIQFile reference in your checkpoint/cursor
4. On resume, mount the file and continue processing

```python
from typing import Any
import json
import tempfile
import os
import time
from borgiq import Request, Response, mount_file, stash_file

def receive(req: Request) -> Response:
    checkpoint = req.memory['ltm'].get('checkpoint')
    working_data = []
    start_index = 0

    if checkpoint and checkpoint.get('dataFile'):
        # Resume: mount the stashed file and load data
        data_path = mount_file(checkpoint['dataFile'])
        with open(data_path, 'r') as f:
            working_data = json.load(f)
        start_index = checkpoint['lastProcessedIndex']
        print(f"Resuming from index {start_index}, loaded {len(working_data)} items")
    else:
        # First run: fetch initial dataset
        working_data = fetch_large_dataset()

    # Process items with time budget
    start_time = time.time()
    BUFFER_TIME = 30
    max_run_time = req.inputs.get('maxRunTimeMs', 240000) / 1000

    for i in range(start_index, len(working_data)):
        if (time.time() - start_time) > (max_run_time - BUFFER_TIME):
            # Running low on time - checkpoint and exit
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(working_data, f)
                temp_path = f.name

            stashed_file = stash_file(temp_path, filename='checkpoint-data.json', mime_type='application/json')
            os.unlink(temp_path)

            req.memory['ltm']['checkpoint'] = {
                'lastProcessedIndex': i,
                'dataFile': stashed_file,
            }

            return Response(results={'status': 'in_progress', 'processedSoFar': i}, memory=req.memory)

        process_item(working_data[i])

    # Complete - clear checkpoint
    req.memory['ltm'].pop('checkpoint', None)
    return Response(results={'status': 'complete', 'totalProcessed': len(working_data)}, memory=req.memory)
```

**Benefits:**
- Avoids LTM size limits for large datasets
- Reduces serialization overhead on each checkpoint
- Data persists reliably in BorgIQ storage
- Works with both LTM-based and input-based checkpointing

### Time Budget Management

Always reserve buffer time before Lambda timeout:

```python
import time

start_time = time.time()
max_run_time = req.inputs.get('maxRunTimeMs', 240000) / 1000  # 4 minutes default
BUFFER_TIME = 30  # 30 seconds buffer

def has_time_remaining():
    elapsed = time.time() - start_time
    return elapsed < (max_run_time - BUFFER_TIME)
```

### Approach 1: LTM-Based Checkpointing

The actor manages its own checkpoint state using Long-Term Memory — read from `req.memory['ltm']`, persist via `Response.memory`.

```python
from typing import Any
import time
from borgiq import Request, Response

def receive(req: Request) -> Response:
    start_time = time.time()
    max_run_time = req.inputs.get('maxRunTimeMs', 240000) / 1000
    BUFFER_TIME = 30

    # Resume from LTM checkpoint if exists
    checkpoint = req.memory['ltm'].get('checkpoint')
    last_processed_id = checkpoint.get('lastProcessedId') if checkpoint else None

    if checkpoint:
        print(f"Resuming from checkpoint: {checkpoint.get('processedCount')} items processed")

    results = {
        'processed': checkpoint.get('processedCount', 0) if checkpoint else 0,
        'hasMore': True,
    }

    while results['hasMore'] and (time.time() - start_time) < (max_run_time - BUFFER_TIME):
        batch = fetch_batch(last_processed_id, req.inputs.get('batchSize', 50))

        if not batch:
            results['hasMore'] = False
            break

        for item in batch:
            process_item(item)
            results['processed'] += 1
            last_processed_id = item['_id']

        # Save checkpoint after each batch
        req.memory['ltm']['checkpoint'] = {
            'lastProcessedId': last_processed_id,
            'processedCount': results['processed'],
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        }

    # Clear checkpoint on completion
    if not results['hasMore']:
        req.memory['ltm'].pop('checkpoint', None)
        print('Processing complete, checkpoint cleared')

    return Response(results=results, memory=req.memory)
```

### Approach 2: Input-Based Checkpointing

Checkpoint cursor is passed in via `req.inputs` and emitted in `Response.results` for external management.

```python
from typing import Any
import time
from borgiq import Request, Response

def receive(req: Request) -> Response:
    start_time = time.time()
    max_run_time = req.inputs.get('maxRunTimeMs', 240000) / 1000
    BUFFER_TIME = 30

    # Resume from cursor provided in inputs (if any)
    cursor = req.inputs.get('cursor')
    last_processed_id = cursor.get('lastProcessedId') if cursor else None

    if cursor:
        print(f"Resuming from cursor: {cursor.get('processedCount')} items previously processed")

    results = {
        'processed': cursor.get('processedCount', 0) if cursor else 0,
        'hasMore': True,
        'cursor': None,  # Emit cursor for next invocation
    }

    while results['hasMore'] and (time.time() - start_time) < (max_run_time - BUFFER_TIME):
        batch = fetch_batch(last_processed_id, req.inputs.get('batchSize', 50))

        if not batch:
            results['hasMore'] = False
            break

        for item in batch:
            process_item(item)
            results['processed'] += 1
            last_processed_id = item['_id']

    # Emit cursor if there's more to process
    if results['hasMore']:
        results['cursor'] = {
            'lastProcessedId': last_processed_id,
            'processedCount': results['processed'],
        }
        print('Emitting cursor for continuation')

    return Response(results=results)
```

**Usage:** The downstream flow or orchestrator receives `results['cursor']` and passes it back as `req.inputs['cursor']` on the next invocation.

### Hash-Based Change Detection

For idempotent operations, detect when source data has changed:

```python
import hashlib

def calculate_hash(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

# Skip unchanged items
content_hash = calculate_hash(item['content'])
if item.get('processedHash') == content_hash:
    results['skipped'] += 1
    continue
```

### Handling Rate Limits

Use `RetryableError` for transient failures:

```python
from borgiq import RetryableError

if response.status_code == 429:
    raise RetryableError('Rate limit reached, will retry')
```

## Best Practices

1. **Initialize clients once** - Store clients at module level, reuse across invocations
2. **Use LTM for state tracking** - Read from `req.memory['ltm']`, persist via `Response.memory`
3. **Handle timeouts gracefully** - Save state before timeout, resume on next invocation
4. **Use RetryableError** - For transient failures (rate limits, auth refresh)
5. **Log progress** - Use `print()` for debugging (captured in flowrun logs)
6. **Validate inputs early** - Check required fields, secrets, and connections at the start; fail fast with clear errors
7. **Keep actors focused** - Split complex logic into multiple actors
8. **Prefer native Python over CLI tools** - Use libraries like `zipfile`, `tarfile` instead of shelling out
9. **Use tempfile module** - Don't hardcode paths like `/tmp`
10. **Use context managers** - Ensure proper cleanup with `with` statements
11. **Pin dependency versions** - Always pin `options.dependencies` to exact versions with `==` (`pandas==2.2.3`), never a bare name or floating range — prevents supply-chain attacks and non-deterministic deploys. See [Installing Dependencies](#installing-dependencies)

### Validate Credentials and Connections

Always validate that required credentials and connections are present before using them. Raise descriptive errors if missing.

```python
from borgiq import Request, Response

def receive(req: Request) -> Response:
    # Validate credentials upfront
    if not req.credentials.get('OPENAI_API_KEY'):
        raise ValueError('Missing required credential: OPENAI_API_KEY. Configure it in workspace credentials.')

    if not req.credentials.get('MONGO_USERNAME') or not req.credentials.get('MONGO_PASSWORD'):
        raise ValueError('Missing required credentials: MONGO_USERNAME and MONGO_PASSWORD')

    # Validate connection auth
    token = req.connection.get('auth', {}).get('values', {}).get('token')
    if not token:
        raise ValueError('Missing OAuth token. Ensure connection is configured and authorized.')

    # Validate required inputs
    if not req.inputs.get('database') or not req.inputs.get('collection'):
        raise ValueError('Missing required inputs: database and collection')

    # Now safe to proceed...
    return Response(results={})
```

### Prefer Native Python Over CLI Tools

Prefer Python libraries over shelling out to CLI tools when a native equivalent exists. Native libraries provide better error handling, cross-platform consistency, and avoid subprocess overhead.

However, **some CLI tools are available on the Lambda image** and can be used via `subprocess.run()` when no suitable Python alternative exists:
- `git` - Git operations
- `aws` - AWS CLI
- `jq` - JSON processing (though `json` module is preferred)
- `convert`/`magick` - ImageMagick image processing
- `tar` - Archive operations (though `tarfile` module is preferred)

```python
# Preferred - use native libraries when available
import zipfile
import io

with zipfile.ZipFile('archive.zip', 'r') as zip_ref:
    zip_ref.extractall('output_dir')

# Acceptable - use CLI tools when no native alternative exists
import subprocess
result = subprocess.run(['git', 'clone', repo_url, '/tmp/repo'], capture_output=True, text=True, check=True)
```

**Common operations with native alternatives (prefer these):**

| Operation | Use This | Not This |
|-----------|----------|----------|
| Zip/Unzip | `zipfile`, `tarfile` | `unzip`, `zip` CLI |
| JSON processing | `json` module | `jq` CLI |
| HTTP requests | `requests`, `urllib` | `curl`, `wget` CLI |
| Base64 encoding | `base64` module | `base64` CLI |
| Hashing | `hashlib` module | `shasum`, `md5` CLI |
| File operations | `open()`, `os`, `shutil` | `cat`, `cp`, `mv` CLI |

**Operations where CLI tools are appropriate:**

| Operation | CLI Tool | Why |
|-----------|----------|-----|
| Git operations | `git` | No native Python git equivalent with full functionality |
| AWS service operations | `aws` CLI | Convenient for one-off AWS operations; `boto3` is preferred for complex usage |
| Image manipulation | `convert`/`magick` (ImageMagick) | Advanced image processing beyond Pillow capabilities |
