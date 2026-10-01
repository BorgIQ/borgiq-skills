# Context Variables Reference

What each variable a `${{ }}` expression can read holds, and where in an actor's configuration it is in scope. Read it when writing expressions. Code actors read the same data from `req`; that side is covered in [code-actor-runtime.md](code-actor-runtime.md#runtime-context).

## Contents

- [Scope and interpolation order](#scope-and-interpolation-order)
- [msg](#msg)
- [err](#err)
- [ctx](#ctx)
- [trigger](#trigger)
- [inputs](#inputs)
- [vars](#vars)
- [credentials](#credentials)
- [connection](#connection)
- [assets](#assets)
- [results](#results)
- [Expression idioms](#expression-idioms)

## Scope and interpolation order

An actor's configuration is interpolated in this order; each step sees what the earlier ones produced:

1. **inputs**: `msg`, `err`, `ctx`
2. **vars**: `inputs`, earlier `vars`, `msg`, `err`, `ctx`
3. **options**: `inputs`, `vars`, `msg`, `err`, `ctx`
4. the actor runs and produces `results`
5. **error**: `results`, `inputs`, `vars`, `msg`, `err`, `ctx`
6. **outputs**: the same as error; only when there is no error

Every step also sees `credentials`, `connection`, `assets`, the `Q` helpers ([q-lib.md](q-lib.md); `Q.lo` is lodash, `Q.dateFns` date-fns), and `trigger` in a trigger actor's own configuration. Code actors (DenoActor, PythonActor, UniversalTriggerActor) skip steps 2 and 6: their `vars` and `outputs` are never interpolated.

## msg

Outputs of upstream actors, keyed by `msgVar`: `${{ msg.fetch_user.body }}`, `${{ msg.webhook_trigger.body.id }}`. `${{ msg[ctx.sourceActor.msgVar] }}` reads the actor that sent this message without naming it, for reusable actors.

## err

Errors of upstream actors that failed with `continueOnError: true`, keyed by `msgVar` like `msg`. A failed actor's `msg.<msgVar>` is undefined and `err.<msgVar>` holds `{ name, message, stack, location, retry, canEmit, metadata? }`:

```yaml
inputs:
  previousError: ${{ err.fetch_user?.message || 'No error' }}
```

## ctx

The run's context. Exact schema: [typescript/schemas/ctx.md](typescript/schemas/ctx.md).

| Field | Holds |
|---|---|
| `org` | `{ id, name }` |
| `workspace` | `{ id, slug, name }` |
| `canvas` | `{ id, slug, name }` plus `webhookTriggers`, `interfaceTriggers`, `appTriggers`, `universalTriggers` (webhook source enabled): maps keyed by the trigger's msgVar, each entry `{ id, type, name, msgVar, description, url }` |
| `actor` | The running actor: `{ id, type, name, msgVar, description, upstreamActorCount, tools? }` (`tools` on agent actors) |
| `triggerActor` | The actor that started the run (in a sub-flow, its CallableTriggerActor): `{ id, type, name, msgVar, description }` |
| `sourceActor` | The actor that sent this message, same shape. Absent when a trigger fires. |
| `sourceMsgId` | Id of that message (`FMSG…`), unique per message: an idempotency key for downstream systems. Absent when a trigger fires. |
| `flowrun` | `{ id, createdAt }` |
| `parentFlowrun` | Only in a sub-flow: `{ workspace, canvas: { id, slug, name }, flowrunId, actorId, flowrunJobId }` |

- Read a trigger's URL from the canvas maps, e.g. `${{ ctx.canvas.webhookTriggers.<msgVar>.url }}`, rather than building it.
- **`ctx.actor.upstreamActorCount`** counts the distinct actors with an edge into this one: several edges from one actor count once, disabled actors don't count, a trigger's count is `0`. Use it as a `forkJoin`'s `size` (the editor's default) so a join after N parallel actors waits for all N; the size cannot exceed it ([message-processor-actor.md](message-processor-actor.md#forkjoin)).

## trigger

The event that fired the run, a union keyed by `trigger.type`. It exists only in a **trigger actor's own configuration** (every trigger type); in task actors it is `undefined`, and downstream actors read the trigger's payload from `msg.<triggerMsgVar>`. It is not `ctx.triggerActor`, which is static metadata about the trigger actor. There is no top-level `request` variable: write `trigger.request`.

| `trigger.type` | Extra fields (full schema: [typescript/schemas/trigger.md](typescript/schemas/trigger.md)) |
|---|---|
| `webhook` | `request`: the parsed request, shaped like the webhook trigger's [emitted message](webhook-trigger-actor.md#emitted-message); `user?` `{ id, name?, email, appSessionId? }`, the caller identified by an app token or API key (also `request.meta.user`) |
| `schedule` | `triggeredAt` (this fire, ISO timestamp), `lastTriggeredAt?` (previous fire, if tracked) |
| `interface` | `user?` `{ id, name?, email }`; `submission?` `{ interfaceId, body }`, present on a form post and absent on the first render |
| `app` | `user?` `{ id, name?, email }` |
| `reactAppBuild` | `user?`: a ReactAppTriggerActor build; serving the app never reaches the runtime |
| `lifecycle` | `event`: `'on-delete'` (with `scope`, `subject` `{ id }`, and `manual: true` on a test fire run by hand), or the reserved `'canvas-enabled'` / `'canvas-disabled'`. See [universal-trigger-actor.md → Cleaning Up on Delete](universal-trigger-actor.md#cleaning-up-on-delete). |
| `callable`, `email`, `button`, `mcpServer`, `manual` | none |

**Where to read an inbound HTTP payload:**

| Where you are | Read |
|---|---|
| Inside the trigger's own `options.webhook` config (e.g. `response.body` with `respondImmediately: true`) | `${{ trigger.request.body }}`, `.headers`, `.queryParams` |
| In any downstream actor (HttpRequest, Deno, Router, WebhookResponse, …) | `${{ msg.<triggerMsgVar>.body }}`, `.headers`, … |

The response is built before the trigger emits, so `msg.<thisActor>` does not exist there yet. Example: the Slack `url_verification` answer in [webhook-trigger-actor.md → Patterns](webhook-trigger-actor.md#patterns).

`trigger.request` exists only on webhook firings: guard a trigger that fires more than one way (a UniversalTriggerActor with several sources) with `${{ trigger.type === 'webhook' }}` or `${{ trigger?.request?.body?.x }}`.

## inputs

The actor's `configuration.inputs`, interpolated first: the wire that maps upstream data into the actor (`userId: ${{ msg.fetch_user.body.id }}`). Options read them as `${{ inputs.userId }}`, e.g. `url: https://api.example.com/users/${{ inputs.userId }}`; use optional chaining for a value that may be missing, `${{ inputs?.pageToken }}`.

## vars

Local scratch computed after `inputs`: a list evaluated in order, so a later entry can read an earlier one. Code actors never interpolate `vars`. Example, building a raw email:

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

## credentials

An actor has **one** `connection` but any number of credentials. `configuration.credentials` maps a local name to a workspace secret or connection; read it as `${{ credentials.<name> }}`.

```yaml
configuration:
  connection:
    key: my-gmail-connection        # the primary auth: ${{ connection.auth }}
  credentials:
    signingKey:
      workspaceKey: my-webhook-signing-key   # a secret (source: secret is the default)
    slack:
      workspaceKey: my-slack-connection      # another connection
      source: connection                     # ${{ credentials.slack.auth }}
```

- A secret arrives as its string value; a `source: connection` credential arrives with the same shape as `connection`.
- Use `connection` for the primary auth and credentials for the rest, e.g. a key to verify request signatures. Never put secrets in `inputs`; never log them.
- In code actors, read them from `req.credentials` / `req.connection`: [code-actor-runtime.md → Credentials and connections](code-actor-runtime.md#credentials-and-connections).

**Exposure modes.** Every secret and connection has one, set in the UI's *Exposure mode* field or with `--exposure-mode` on `borgiq secrets create` / `borgiq connections create`:

| UI label | `exposureMode` | What an expression gets |
|---|---|---|
| **Server-side** (the default, recommended) | `httpOnly` | A placeholder such as `BORGIQ_CREDENTIAL_<KEY>_<hash>` (connection fields: `BORGIQ_CONNECTION_…`), never the real value |
| **Sent to runtime** | `exposed` | The decrypted value |

A Server-side placeholder works only where it lands verbatim in an outbound **HTTPS** request (URL, header, text body): the BorgIQ egress proxy swaps in the real value there. It is not substituted over plain `http://` or in a binary body, and an expression that transforms it (hashing, `Q.jwtSign`, base64) works on the placeholder string: use Sent to runtime for those. A Server-side credential can also be limited to a list of URLs (`allowedUrls`); the proxy refuses it anywhere else. HttpRequestActor request signing (AWS SigV4, OAuth1) works with Server-side credentials: see [auth-types.md](auth-types.md).

## connection

The actor's single connection, mapped by `configuration.connection.key`. The optional `type` names the allowed connection type: a string, or a list when several fit (`[github-oauth2, github-pat]`). An HttpRequestActor passes `auth: ${{ connection.auth }}` and builds the auth headers or parameters from it ([http-request-actor.md](http-request-actor.md), [auth-types.md](auth-types.md)).

## assets

Workspace assets, by key: `${{ assets.company_logo }}` or `${{ assets['my-key'] }}`. A plain-text asset is a string, a YAML or JSON asset is the parsed object, and a file asset is a BIQFile (only once its upload succeeded). Only assets named literally in an expression are loaded, so write the key out rather than computing it.

## results

The actor's own result, in `error` and `outputs`: an HttpRequestActor's `{ statusCode, headers, body }`, or what a code actor returns. E.g. `outputs: ${{ results.body.data }}`, and in the error block `if: ${{ !Q.isHTTPStatusInRange(results.statusCode, ["200-299"]) }}`, `retryIf: ${{ Q.isHTTPStatusInRange(results.statusCode, ["429", "500-599"]) }}`, `message: ${{ Q.toJSON(results) }}` (see [error-handling.md](error-handling.md)).

## Expression idioms

```yaml
status: "${{ inputs.active ? 'Active' : 'Inactive' }}"   # quoted: a plain YAML value cannot contain ': '
email: ${{ msg.user?.profile?.email || 'unknown' }}
weekAgo: ${{ Q.dateFns.subDays(Q.now(), 7).toISOString() }}
token: "${{ Q.jwtSign({ userId: inputs.userId }, credentials.jwtSecret, { expiresIn: '1h' }) }}"   # jwtSecret must be Sent to runtime
```

For longer logic, use an immediately invoked function:

```yaml
${{(() => {
    const people = msg.upstream_actor.data;
    return Q.lo.chain(people).filter(p => p.birthYear > inputs.minYear).groupBy('country').value();
  })()}}
```

All functions (`Q.lo.get`, hashing, ids, CSV, HTML, markdown, base64): [q-lib.md](q-lib.md).
