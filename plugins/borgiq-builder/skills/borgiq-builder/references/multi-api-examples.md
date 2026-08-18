# Multi-API Call Examples

When a task requires multiple HTTP requests stitched together (e.g., fetch a label ID by name, then apply that label to an email), use a **DenoActor** or **PythonActor** with multiple API calls instead of chaining multiple HttpRequestActors. This keeps the logic self-contained and easier to maintain.

## Table of Contents

- [TypeScript/Deno Example](#typescriptdeno-example)
- [Python Example](#python-example)
- [When to Use This Pattern](#when-to-use-this-pattern)
- [Key Points](#key-points)
- [Multiple Connections](#multiple-connections)

## TypeScript/Deno Example

```typescript
// Example: Apply label to Gmail message (requires 2 API calls)
import type { Request, Response } from "@borgiq/actors";

export default async function receive(req: Request): Promise<Response> {
  const token = req.connection?.auth?.values?.token;
  if (!token) throw new Error('Missing OAuth token');

  const headers = { Authorization: `Bearer ${token}` };

  // Step 1: Fetch label ID by name
  const labelsRes = await fetch(
    `https://gmail.googleapis.com/gmail/v1/users/me/labels`,
    { headers }
  );
  const labels = await labelsRes.json();
  const label = labels.labels.find((l: any) => l.name === req.inputs.labelName);
  if (!label) throw new Error(`Label not found: ${req.inputs.labelName}`);

  // Step 2: Apply label to message
  const applyRes = await fetch(
    `https://gmail.googleapis.com/gmail/v1/users/me/messages/${req.inputs.messageId}/modify`,
    {
      method: 'POST',
      headers: { ...headers, 'Content-Type': 'application/json' },
      body: JSON.stringify({ addLabelIds: [label.id] }),
    }
  );

  return { results: await applyRes.json() };
}
```

## Python Example

```python
# Example: Apply label to Gmail message (requires 2 API calls)
import requests
from borgiq import Request, Response

def receive(req: Request) -> Response:
    token = req.connection.get('auth', {}).get('values', {}).get('token')
    if not token:
        raise ValueError('Missing OAuth token')

    headers = {'Authorization': f'Bearer {token}'}

    # Step 1: Fetch label ID by name
    labels_res = requests.get(
        'https://gmail.googleapis.com/gmail/v1/users/me/labels',
        headers=headers
    )
    labels = labels_res.json()
    label = next((l for l in labels.get('labels', []) if l['name'] == req.inputs.get('labelName')), None)
    if not label:
        raise ValueError(f"Label not found: {req.inputs.get('labelName')}")

    # Step 2: Apply label to message
    apply_res = requests.post(
        f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{req.inputs.get('messageId')}/modify",
        headers={**headers, 'Content-Type': 'application/json'},
        json={'addLabelIds': [label['id']]}
    )

    return Response(results=apply_res.json())
```

## When to Use This Pattern

| Scenario | Approach |
|----------|----------|
| Single API call | HttpRequestActor |
| Multiple sequential API calls that depend on each other | DenoActor or PythonActor |
| API call + data processing | DenoActor or PythonActor |
| Parallel API calls needing combined results | DenoActor/PythonActor or fork/forkJoin pattern |

## Key Points

1. **Access tokens via `req.connection`** - Never pass secrets through inputs
2. **Chain dependent calls** - Each step can use results from previous steps
3. **Error handling** - Throw errors early if required data is missing
4. **Return `results`** - The `Response.results` value becomes the actor's output downstream

## Multiple Connections

**Key rule:** An actor has **only ONE connection** (`req.connection`) plus any number of secrets (`req.credentials`). If a single actor genuinely needs to call different services with different OAuth connections, fetch the additional connection's decrypted credentials at runtime via the `/connections/{key}` BIQ Runtime API endpoint:

```typescript
import type { Request, Response } from "@borgiq/actors";
import { biqApi } from "@borgiq/actors";

export default async function receive(req: Request): Promise<Response> {
  // The actor's primary connection
  const gmailToken = req.connection.auth.values.token;

  // A second connection fetched by its workspace key
  const calendarRes = await biqApi('/connections/my-calendar-connection', { method: 'GET' });
  const calendarToken = (await calendarRes.json()).auth.values.token;

  // Use each token for its respective API
  const gmailResponse = await fetch(gmailUrl, {
    headers: { Authorization: `Bearer ${gmailToken}` }
  });
  const calendarResponse = await fetch(calendarUrl, {
    headers: { Authorization: `Bearer ${calendarToken}` }
  });

  return { results: { ok: true } };
}
```

> Prefer splitting work across actors (one connection each) where possible; reach for `/connections/{key}` only when the logic must live in a single actor.

See [flow-consolidation.md](flow-consolidation.md) for more details on handling multiple connections when consolidating flows.
