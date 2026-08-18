# BorgIQ CLI Troubleshooting Guide

Common errors encountered when using the BorgIQ CLI (`@borgiq/cli`), with causes and fixes.

---

## 1. Authentication Errors

### Error: 401 Unauthorized

```
Error: Request failed with status 401: Unauthorized
```

**Cause:** The API token is missing, expired, or has been revoked. The CLI reads the token from `~/.config/borgiq/config.json`.

**Fix:**

```bash
borgiq auth login
```

This re-authenticates and stores a fresh token. Verify the token format matches `biq_<40 hex chars>`.

### Error: Not logged in

```
Error: Not logged in. Run `borgiq auth login` first.
```

**Cause:** No token exists in `~/.config/borgiq/config.json`. The CLI has never been authenticated on this machine, or the config file was deleted.

**Fix:**

```bash
borgiq auth login
```

---

## 2. JSON Parse Errors

### Error: Invalid JSON in file

```
Error: Invalid JSON in file: <path>
```

**Cause:** The file passed to `--file` is not valid JSON. Common reasons:

- The file is YAML (`.yaml` / `.yml`) -- the CLI only accepts JSON via `JSON.parse()`
- The JSON has syntax errors (trailing commas, unquoted keys, comments)
- The file is empty

**Fix:** Validate the file with `jq` before passing it:

```bash
jq . my-file.json
# If this fails, fix the syntax errors

# If you have YAML, convert it first:
# npx js-yaml my-file.yaml > my-file.json

borgiq canvas-actors create --file my-file.json
```

### Error: Invalid JSON from stdin

```
Error: Invalid JSON from stdin
```

**Cause:** Data piped into the CLI is not valid JSON. This can happen when piping output from a command that includes non-JSON text (log lines, headers, etc.).

**Fix:** Ensure the piped output is pure JSON:

```bash
# Verify the output is valid JSON first
cat data.json | jq . | borgiq canvas-actors create --canvas <id>
```

---

## 3. Schema Validation Errors (400)

### Error: 400 Bad Request — validation failed

```
Error: Request failed with status 400: Validation failed
  - config.options: expected string, got object
```

**Cause:** The JSON payload does not match the expected schema. The two most common schemas differ in how `config` fields are represented:

- **ExportedCanvasData** uses JSON objects for config values
- **CanvasActor** uses YAML strings for config values

Passing the wrong format causes validation failures.

**Example — wrong format for `canvas-actors create`:**

```json
{
  "config": {
    "options": { "method": "GET", "url": "https://example.com" }
  }
}
```

The `canvas-actors create` endpoint expects CanvasActor schema, where config values are YAML strings:

```json
{
  "config": {
    "options": "method: GET\nurl: https://example.com"
  }
}
```

**Fix:** Check which schema the command expects and convert config fields accordingly. Also ensure all required fields are present in the payload.

---

## 4. ID Format Errors

### Error: Invalid actor ID

```
Error: Invalid actor ID: "ACTR123"
```

**Cause:** Actor IDs must be exactly 30 characters: the prefix `ACTR` followed by 26 characters from the ULID charset (excludes `i`, `l`, `o`, `u`).

Valid regex:

```
ACTR[0123456789abcdefghjkmnpqrstvwxyz]{26}
```

### Error: Invalid edge ID

```
Error: Invalid edge ID: "<value>"
```

**Cause:** Edge IDs follow the same pattern as actor IDs but with the `EDGE` prefix:

```
EDGE[0123456789abcdefghjkmnpqrstvwxyz]{26}
```

### Error: Invalid source port ID

```
Error: Invalid source port ID: "<value>"
```

**Cause:** Source port IDs are either:

- A well-known value: `SPRTdefault`, `SPRTdone000`, `SPRTevent00`
- A generated value: `SPRT` + 7 alphanumeric characters (11 characters total)

**Fix:** Double-check the ID by reading it from the canvas data. Do not hand-craft IDs -- copy them from API responses.

---

## 5. Version Conflict Errors (409)

### Error: 409 Conflict — editVersion mismatch

```
Error: Request failed with status 409: Conflict
  - editVersion mismatch: expected 5, got 3
```

**Cause:** The canvas was modified by another user or process between the time you read it and the time you submitted your update. The `editVersion` in your request no longer matches the current version on the server.

**Fix:**

1. Re-read the canvas to get the current `editVersion`
2. Reapply your changes to the fresh data
3. Retry the update with the current `editVersion`

```bash
# Re-read the canvas
borgiq canvases get --canvas <id> --output json > canvas.json

# Extract current editVersion, apply your changes, then retry
borgiq canvas-actors update --canvas <id> --actor-id <actor-id> --file updated.json
```

---

## 6. Server Validation Errors

### Error: Canvas validation failed

```bash
borgiq canvases validate --canvas <id>
```

```
Validation errors:
  - DenoActor "my-actor" is missing required "code" field
  - Duplicate msgVar "response" in actors: ACTR..., ACTR...
  - Edge EDGE... references non-existent actor ACTR...
  - Actor ACTR... has no incoming connections
```

**Cause:** The canvas structure has logical errors:

- A DenoActor is missing its `code` field
- Two actors use the same `msgVar` name, causing variable collisions
- An edge references an actor ID that does not exist on the canvas
- An actor has no connections (orphaned)

**Fix:** Patch the actor to resolve each error, then re-validate:

```bash
borgiq canvas-actors update --canvas <id> --actor-id <actor-id> --file fix.json
borgiq canvases validate --canvas <id>
```

---

## 7. Permission Errors (403)

### Error: 403 Forbidden

```
Error: Request failed with status 403: Forbidden
  - Token missing required scope: canvas:write
```

**Cause:** The API token does not have the scopes needed for the operation. Common required scopes:

- `org:access` -- access the organization
- `workspace:access` -- access workspaces
- `canvas:read` -- read canvas data
- `canvas:write` -- create, update, or delete canvas resources

This error also occurs when the authenticated user is not a member of the target org or workspace.

**Fix:** Create a new API token with the correct scopes and re-authenticate:

```bash
# Generate a new token in the BorgIQ UI with the required scopes, then:
borgiq auth login
```

---

## 8. Rate Limiting (429)

### Error: 429 Too Many Requests

```
Error: Request failed with status 429: Too Many Requests
  - Rate limit exceeded. Retry after 12 seconds.
```

**Cause:** The API is rate limited to 120 requests per minute per token. Automated scripts or batch operations can easily exceed this limit.

**Fix:**

- Check the `RateLimit-Remaining` response header to see how many requests you have left
- Respect the `Retry-After` response header before retrying
- Add delays between requests in scripts:

```bash
# Example: add a delay between batch operations
for id in $ACTOR_IDS; do
  borgiq canvas-actors get --canvas <canvas-id> --actor-id "$id"
  sleep 1
done
```

---

## 9. Command Not Found

### Error: borgiq: command not found

```
zsh: command not found: borgiq
```

**Cause:** The CLI is not installed, or the npm global bin directory is not in your `PATH`.

**Fix:**

```bash
npm install -g @borgiq/cli

# If already installed but not found, check your PATH:
npm bin -g
# Add the output directory to your PATH if needed
```

---

## 10. Pipe/Stdin Issues

### Error: unexpected input or hang when piping

```
Error: Invalid JSON from stdin
# or the CLI hangs waiting for input
```

**Cause:**

- Binary data (not JSON text) was piped into the CLI
- stdin was not closed (e.g., running in an interactive terminal without piping anything -- the CLI waits for input indefinitely)
- The piped output contains extra text before or after the JSON

**Fix:** Use `--file` instead of piping when in doubt:

```bash
# Instead of piping:
#   some-command | borgiq canvas-actors create --canvas <id>

# Use --file:
some-command > payload.json
jq . payload.json  # validate it's clean JSON
borgiq canvas-actors create --canvas <id> --file payload.json
```

If you must pipe, ensure the source emits only valid JSON to stdout, with no extra log lines or binary content.
