# Python Actor Reference

The PythonActor runs Python code in a sandboxed Python 3.11 runtime with UV-managed dependencies. This file covers what
is Python-only: configuration, dependencies, modules, temporary files, CLI tools, the SDK and examples. The contract,
emit rules, errors, source files, credentials, memory, signals and the runtime API are shared with Deno: read
[code-actor-runtime.md](code-actor-runtime.md) with it.

## Contents

- [Configuration](#configuration)
- [Options and dependencies](#options-and-dependencies)
- [Modules and packages](#modules-and-packages)
- [Temporary files](#temporary-files)
- [CLI tools](#cli-tools)
- [Template and SDK](#template-and-sdk)
- [Examples](#examples)

## Configuration

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
            from borgiq import Request, Response

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

The `codeDir` rules and `schemas.inputs` are in [code-actor-runtime.md](code-actor-runtime.md#source-files-codedir).

## Options and dependencies

| Option | Type | Default | Meaning |
|---|---|---|---|
| `emitArrayAsSingleMessage` | boolean | `true` | A list under `results` is one message; `false` emits one message per item |
| `dependencies` | string[] | `[]` | Packages UV installs, each pinned with `==` (`pandas==2.2.3`) |
| `env` | `{ name, value }[]` | `[]` | Environment variables for the runtime. Names match `[A-Z0-9_]+`; `TMPDIR`, `HOME`, `PYTHONUNBUFFERED`, `UV_CACHE_DIR`, `UV_PROJECT_ENVIRONMENT` and `PYTHONUSERBASE` are reserved |

- The runtime is **exactly Python 3.11**: syntax or packages that need 3.12+ fail.
- **Pin every dependency with `==`.** A bare name (`pandas`), an open range (`pandas>=2.0.0`) or a bounded range
  (`pandas>=2.0.0,<3.0.0`) resolves non-deterministically. When dependencies are resolved, and why pinning matters on a
  deployed workspace: [code-actor-runtime.md](code-actor-runtime.md#dependencies-and-deployed-workspaces).
- **`requests` is always installed:** the runtime adds `requests>=2.31.0` to every PythonActor, so you need not list
  it; if you pin it yourself, pin 2.31.0 or later.
- UV installs dependencies much faster than pip, which shortens cold starts.

Exact schema: [typescript/actorSchemas/task/python.md](typescript/actorSchemas/task/python.md).

## Modules and packages

- **The tree root is on `sys.path`:** a root-level `utils.py` is `import utils`, and a folder is a package once it
  contains `__init__.py` (`from lib.report import summarize`, nested packages included).
- **Declared dependencies are importable from any of your modules**, not just the entrypoint.
- **Shadowing a third-party package is your call, not an error.** A root `requests.py` wins over the installed
  `requests` (normal Python behavior; only runtime-critical names are reserved). Name modules distinctly.

```yaml
codeDir:
  - path: main.py            # defines receive(); imports utils and lib.report
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

## Temporary files

`tempfile` writes to the actor's temporary directory ([how long files last](code-actor-runtime.md#temporary-files)).
Use it (with `with` blocks, which clean up automatically), never a hardcoded `/tmp/...` path:

```python
import os, tempfile

with tempfile.TemporaryDirectory(prefix="myactor_") as temp_dir:
    temp_file = os.path.join(temp_dir, "output.json")
    ...
# the directory is removed here
```

## CLI tools

Prefer a Python library when one exists: better error handling, consistent behavior, no subprocess overhead.

| Operation | Use | Not |
|---|---|---|
| Zip/unzip | `zipfile`, `tarfile` | `unzip`, `zip` |
| JSON processing | `json` | `jq` |
| HTTP requests | `requests`, `urllib` | `curl`, `wget` |
| Base64 | `base64` | `base64` CLI |
| Hashing | `hashlib` | `shasum`, `md5` |
| File operations | `open()`, `os`, `shutil` | `cat`, `cp`, `mv` |

The image does carry CLI tools for the cases no library covers: `git` (no Python equivalent with full functionality),
`aws` (one-off AWS operations; prefer `boto3` for complex use), ImageMagick `convert` / `magick` (beyond Pillow),
`jq`, `tar`, and also `wget`, GraphicsMagick `gm`, ghostscript `gs` and `gcloud`.

- **Pass an argument list, never `shell=True` on an input:** each input is then one argument and is never parsed as
  shell syntax. Put `--` before input values, so a value starting with `-` cannot become an option.
- **The process does not inherit the image's environment:** set `PATH` for the tools you call. When outbound HTTPS goes
  through the BorgIQ egress proxy, `SSL_CERT_FILE` is a CA bundle that trusts it; point tools such as git at it.
- **AWS credentials in the environment are dummies** (`AWS_REGION=disabled`): pass real ones in the subprocess `env`
  for `aws`.
- Work in a `tempfile` directory, not a hard-coded path.

```python
import os
import subprocess
import tempfile
from borgiq import Request, Response

def receive(req: Request) -> Response:
    """Shallow-clone a repository and list its top-level files."""
    repo_url = req.inputs.get('repoUrl', '').strip()
    if not repo_url.startswith('https://'):
        raise ValueError("inputs.repoUrl must be an https:// URL")

    env = os.environ.copy()
    env['PATH'] = '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:' + env.get('PATH', '')
    if env.get('SSL_CERT_FILE'):
        env['GIT_SSL_CAINFO'] = env['SSL_CERT_FILE']

    with tempfile.TemporaryDirectory(prefix='repo_') as work_dir:
        result = subprocess.run(
            ['git', 'clone', '--depth', '1', '--', repo_url, work_dir],
            capture_output=True, text=True, timeout=120, env=env,
        )
        if result.returncode != 0:
            raise RuntimeError(f"git clone failed: {result.stderr.strip()}")
        files = sorted(os.listdir(work_dir))

    return Response(results={'repoUrl': repo_url, 'files': files})
```

## Template and SDK

The entrypoint, `main.py`:

```python
from borgiq import Request, Response, signal, biq_api, mount_file, stash_file, RetryableError

def receive(req: Request) -> Response:
    # req.inputs                            — interpolated inputs for this invocation
    # req.ctx                               — RuntimeContext (org / workspace / canvas / flowrun / actor)
    # req.connection                        — the single connection's resolved config (read-only)
    # req.credentials['XXXX']               — secret values; placeholders when Server-side (read-only)
    # req.memory['stm'] / req.memory['ltm'] — short / long term memory (value-in)
    # raise RetryableError() to be re-invoked with the same message; other exceptions are permanent.

    print('Processing started')  # captured with the flowrun

    return Response(
        # `results` is emitted as msg.<msgVar> downstream (a list is ONE message unless
        # options.emitArrayAsSingleMessage is false; None emits a null message).
        results={'result': 'data'},
        # Return memory to persist it; omit to leave it unchanged.
        memory=req.memory,
    )
```

Everything is imported from the `borgiq` package:

| Name | Signature and behavior |
|---|---|
| `Request` | Dataclass: `inputs`, `ctx`, `connection`, `credentials` (dicts), `memory` (`{'stm': {...}, 'ltm': {...}}`) |
| `Response` | Dataclass: `results=None`, `memory=None`, `signal=None`, `error=None` (`{'message': str, 'retryable': bool}`) |
| `biq_api(path, **kwargs)` | A `requests` call to the runtime API ([endpoints](code-actor-runtime.md#runtime-api)); kwargs `method` (default `GET`), `json`, `data`, `headers`, `params`; returns a `requests.Response` |
| `mount_file(file)` | Downloads a BIQFile input; returns its local path |
| `stash_file(file, filename=None, mime_type=None)` | Uploads a path (`str`), `bytes`, `bytearray`, `memoryview` or a file-like object (anything with `read()`); returns the BIQFile dict |
| `signal.webhook_respond`, `signal.callable_response`, `signal.delay_until` | Build a signal, but the platform ignores signals from a PythonActor ([Signals](code-actor-runtime.md#signals)): respond with a WebhookResponseActor or CallableResponseActor downstream |
| `RetryableError` | Raise it to be re-invoked with the same message |

Collections and streams return `{ ok, value, error? }`:

```python
page = biq_api('/streams', method='POST', json={
    'action': 'readStream', 'stream': 'order-events',
    'from': req.inputs.get('cursor') or 'start', 'maxRecords': 500,
}).json()['value']
```

Every action: [collection-actor.md](collection-actor.md) (`putItem` is create-only), [stream-api.md](stream-api.md).

Memory is a dict per half: `count = req.memory['stm'].get('counter', 0) + 1`, then
`req.memory['stm']['counter'] = count` and `return Response(results={'count': count}, memory=req.memory)`. Set a key
to `None` to clear it ([the merge contract](code-actor-runtime.md#memory)).

## Examples

### Two dependent API calls

Looks up a Gmail label by name, then applies it to a message:

```python
import requests
from borgiq import Request, Response

def receive(req: Request) -> Response:
    token = req.connection.get('auth', {}).get('values', {}).get('token')
    if not token:
        raise ValueError('Missing OAuth token')
    headers = {'Authorization': f'Bearer {token}'}

    # Step 1: fetch the label id by name
    labels = requests.get('https://gmail.googleapis.com/gmail/v1/users/me/labels', headers=headers).json()
    label = next((l for l in labels.get('labels', []) if l['name'] == req.inputs.get('labelName')), None)
    if not label:
        raise ValueError(f"Label not found: {req.inputs.get('labelName')}")

    # Step 2: apply it to the message
    apply_res = requests.post(
        f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{req.inputs.get('messageId')}/modify",
        headers={**headers, 'Content-Type': 'application/json'},
        json={'addLabelIds': [label['id']]},
    )
    return Response(results=apply_res.json())
```

### pandas over a stashed file

```python
import pandas as pd
from borgiq import Request, Response, mount_file, stash_file

def receive(req: Request) -> Response:
    df = pd.read_csv(mount_file(req.inputs.get('csvFile')))   # a BIQFile input
    df['processed_at'] = pd.Timestamp.now().isoformat()
    df = df.dropna()

    output_file = stash_file(df.to_json(orient='records').encode('utf-8'),
                             filename='processed.json', mime_type='application/json')
    return Response(results={'rowCount': len(df), 'columns': list(df.columns), 'outputFile': output_file})
```

### Checkpoint a batch loop in LTM

Needs `enableLTM: true`; `maxRunTimeMs` is an input set below the runtime's timeout
([pattern](code-actor-runtime.md#long-running-work-and-checkpoints)).

```python
import time
from borgiq import Request, Response

def receive(req: Request) -> Response:
    start_time = time.time()
    max_run_time = req.inputs.get('maxRunTimeMs') / 1000
    BUFFER_TIME = 30

    checkpoint = req.memory['ltm'].get('checkpoint')   # None when there is none, or once cleared
    last_processed_id = checkpoint.get('lastProcessedId') if checkpoint else None
    results = {'processed': checkpoint.get('processedCount', 0) if checkpoint else 0, 'hasMore': True}
    if checkpoint:
        print(f"Resuming from checkpoint: {results['processed']} items processed")

    while results['hasMore'] and (time.time() - start_time) < (max_run_time - BUFFER_TIME):
        batch = fetch_batch(last_processed_id, req.inputs.get('batchSize', 50))
        if not batch:
            results['hasMore'] = False
            break
        for item in batch:
            process_item(item)
            results['processed'] += 1
            last_processed_id = item['_id']
        # save the checkpoint after each batch
        req.memory['ltm']['checkpoint'] = {
            'lastProcessedId': last_processed_id,
            'processedCount': results['processed'],
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        }

    # Complete: set the checkpoint to None; a popped key would survive the merge.
    if not results['hasMore']:
        req.memory['ltm']['checkpoint'] = None

    return Response(results=results, memory=req.memory)
```

### Checkpoint a large dataset in a stashed file

For a working set too large for memory: stash it, keep the BIQFile in the LTM checkpoint, mount it on resume. Needs
`enableLTM: true`.

```python
import json, os, tempfile, time
from borgiq import Request, Response, mount_file, stash_file

def receive(req: Request) -> Response:
    checkpoint = req.memory['ltm'].get('checkpoint')
    if checkpoint and checkpoint.get('dataFile'):
        with open(mount_file(checkpoint['dataFile'])) as f:   # resume: load the stashed data
            working_data = json.load(f)
        start_index = checkpoint['lastProcessedIndex']
    else:
        working_data, start_index = fetch_large_dataset(), 0  # first run

    start_time, BUFFER_TIME = time.time(), 30
    max_run_time = req.inputs.get('maxRunTimeMs') / 1000
    for i in range(start_index, len(working_data)):
        if time.time() - start_time > max_run_time - BUFFER_TIME:
            # running low on time: stash the data, checkpoint, and exit
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(working_data, f)
            data_file = stash_file(f.name, filename='checkpoint-data.json', mime_type='application/json')
            os.unlink(f.name)
            req.memory['ltm']['checkpoint'] = {'lastProcessedIndex': i, 'dataFile': data_file}
            return Response(results={'status': 'in_progress', 'processedSoFar': i}, memory=req.memory)
        process_item(working_data[i])

    req.memory['ltm']['checkpoint'] = None   # clear it: a popped key would survive the merge
    return Response(results={'status': 'complete', 'totalProcessed': len(working_data)}, memory=req.memory)
```
