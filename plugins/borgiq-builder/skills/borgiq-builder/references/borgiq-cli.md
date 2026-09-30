# BorgIQ CLI

How to drive BorgIQ from a shell with the `borgiq` CLI (`@borgiq/cli`): which version a command needs, the conventions
every command shares, what each command group is for, starting from a template or a recipe, and what common errors
mean. Flags and examples for any command come from `borgiq <command> --help`.

## Contents

- [Before you start](#before-you-start)
- [CLI versions](#cli-versions)
- [Conventions](#conventions)
- [Command map](#command-map)
- [Workspace resources](#workspace-resources)
- [Start from a template](#start-from-a-template)
- [Start from a recipe](#start-from-a-recipe)
- [Errors](#errors)

## Before you start

- **No shell?** Skip the CLI. Write one `metadata` + `actors` document for the user to deploy in the BorgIQ web UI, and
  say it is unvalidated ([validation.md](validation.md#no-shell)).
- **Install:** `npm install -g @borgiq/cli`.
- **Auth is the user's job.** Run `borgiq auth status`. If it fails, ask the user to run `borgiq auth login`, which
  stores the token in `~/.config/borgiq/config.json` (owner-only). Never ask for a token, and never read that file or
  environment variables that hold tokens.
- **Build in a bundle** ([cli/canvas-bundles.md](cli/canvas-bundles.md)). Direct documents and batch payloads
  ([cli/cli-data-formats.md](cli/cli-data-formats.md)) are only for when a bundle is not possible.
- **Run, monitor, debug:** [flowrun-job-states.md](flowrun-job-states.md). **Deployed workspaces** run the last build,
  not the pushed code: [deployment.md](deployment.md).

## CLI versions

Check the version with `borgiq --version`, and one command with `borgiq help <command>`, which exits non-zero when
the command is missing (`borgiq <command> --help` exits 0 either way, so it is no check):

```bash
borgiq help bundle >/dev/null 2>&1 || echo "upgrade: npm install -g @borgiq/cli"
```

| Commands | Need `@borgiq/cli` |
|---|---|
| `generate`, `validate` | ≥ 0.6.0 |
| `bundle` (`init`, `pull`, `push`, `pack`, `unpack`, `validate`), `scaffold` | ≥ 0.8.0 |
| `bundle build` (react-app builds) | ≥ 0.9.0 |
| Multi-file `code/` trees with `main.ts` / `main.py` entrypoints | ≥ 0.10.0 |
| `workspaces deployment`, `canvases runtime-build`, `bundle push --runtime-build`, canvas builds in `bundle build` | ≥ 0.11.0 |
| `ai-providers`, `canvas-actors app-url` / `thumbnail`, the bundle's `README.md` and `thumbnail.<ext>` files | ≥ 0.12.0 |
| `recipes` | ≥ 0.13.0; npm may still serve 0.12.0, so always check with `borgiq help recipes` |

Upgrade with `npm install -g @borgiq/cli`. If that is not possible, fall back: no `bundle` → direct documents; no
`recipes` → templates.

## Conventions

- **Output.** A table on a terminal; JSON when piped or with `--json`. Pass `--json` whenever you parse output. It sets
  the output format only, never how input is read. In JSON mode an error goes to stderr as
  `{ "error": { code, status, details, … } }`.
- **Input.** `--file <path>` reads JSON, or YAML when the name ends in `.yaml`/`.yml`. `--file -` and a pipe read stdin
  as YAML (which includes JSON). With nothing piped on a terminal, the command fails at once instead of waiting.
- **Canvases.** A `<canvas>` argument and `--canvas` take the slug or the ULID, except in `triggers run` and
  `flowrun-jobs test-run`, which need the ULID (`metadata.id` from `borgiq canvases get <slug> --json`). `--canvas-id`
  is a deprecated alias of `--canvas`.
- **Org and workspace.** `--org` and `--workspace` (slug or ID) override the logged-in defaults.
- **Lists.** `--page`, `--page-size` (at most 100) and `--all` (every page). Never hand-roll a page loop.
- **IDs.** Mint every ID with `borgiq generate` (offline). Formats: [validation.md](validation.md).
- **Deletes** ask first; `-y`/`--yes` (alias `--force`) skips the prompt.
- **Exit codes.** 0 success · 1 other · 2 usage (bad flags or input, HTTP 400/422) · 3 auth (401) · 4 forbidden (403) ·
  5 not found (404) · 6 conflict (409) · 7 rate limited (429) · 8 server (5xx) · 9 network.

## Command map

| Group | Use it for |
|---|---|
| `auth` | `status` checks the login; `login` is the user's |
| `orgs list`, `workspaces list` | Slugs for `--org` / `--workspace` |
| `workspaces deployment`, `canvases runtime-build*` | Deployed workspaces and canvas builds ([deployment.md](deployment.md)) |
| `actors list`, `actors schema <Type> [--action <a>]` | Actor types; a type's options schema, default options and memory flags, source ports, connection support and `code` block (`language`, `entrypoint`, `multiFile`) |
| `templates`, `recipes` | [Start from a template](#start-from-a-template), [Start from a recipe](#start-from-a-recipe) |
| `bundle` | Build and sync a canvas as files ([cli/canvas-bundles.md](cli/canvas-bundles.md)) |
| `generate`, `validate` | IDs and msgVars; check a `metadata` + `actors` document ([validation.md](validation.md)) |
| `scaffold actor\|actor-from-template\|canvas\|batch` | Direct-path payloads: an actor from its type's schema (fetched from the API), a template as an actor, actors wrapped for `create-with-data` or `batch` ([cli/cli-data-formats.md](cli/cli-data-formats.md)) |
| `canvases` | `list`; `get` (`--include-data` adds the actors); `create`; `update` (metadata; `--readme-file` replaces the README, an empty file clears it); `delete`; `export`; `validate` (server-side, [validation.md](validation.md)); `layout` (auto-arranges the actors; `--source-actor-id` only what is downstream of them); `create-with-data`, `update-data`, `verify-import` ([cli/cli-data-formats.md](cli/cli-data-formats.md)) |
| `canvas-actors` | Without a bundle: `list` (`--actor-type`, `--is-active`, `--search`), `get`, `flow` (an actor plus everything downstream), `verify` (options against the type's schema, nothing saved), `create`, `update`, `delete`, `batch` |
| `canvas-actors app-url`, `canvas-actors thumbnail set\|get\|rm` | An App or React App actor's thumbnail. `app-url` prints only the served URL (`--json`: `{ actorId, src }`; needs `app:use`); `thumbnail set` returns the stored `{ fileId }`; `get` prints `{ actorId, fileId, mimeType, sizeInBytes }`, never the image. Capture and limits: the `borgiq-react-app-builder` skill, *App thumbnail* |
| `connections`, `secrets`, `assets` | [Workspace resources](#workspace-resources) |
| `ai-providers` | AI providers and usable model references ([custom-ai-providers.md](custom-ai-providers.md#cli-output-and-errors)) |
| `tokens` | Personal access tokens ([api-tokens.md](api-tokens.md)) |
| `triggers run`, `flowruns`, `flowrun-jobs`, `flowrun-results`, `flowrun-messages` | Run, monitor and debug ([flowrun-job-states.md](flowrun-job-states.md)) |

## Workspace resources

Actors name connections, secrets and assets by key. Check each key exists before you write or deploy it:

```bash
borgiq connections list --json    # key and type of each connection
borgiq connections types --json   # connection types the workspace offers (gmail, slack-oauth2, github-oauth2, …)
borgiq secrets list --json        # keys only, never values
borgiq assets list --json         # files, images and documents
```

A connection goes in `configuration.connection: { key, type }`, where `type` is one exact connection-type name or a
non-empty array of them ([Typed Connections](http-request-actor.md#typed-connections)); a secret in
`configuration.credentials.<name>.workspaceKey`. If one is missing, give the user the exact key to create under
**Workspace Settings > Connections > Add Connection** (e.g. Gmail OAuth2) or **Workspace Settings > Secrets > Add
Secret**.

## Start from a template

A template is a published single-actor configuration ("Send Slack message", "GitHub: open issue") from BorgIQ or your
org or workspace. Search before hand-building an integration actor. A template suits one integration step you want
to keep updatable: its actor keeps a `template` stamp.

```bash
borgiq templates apps --search slack --json                    # app ids (TAPP…)
borgiq templates list --search "send email" --type TASK --json # name/description/tags; --type TASK|TRIGGER, repeatable
borgiq templates list --app-id TAPP… --all --json
borgiq templates get ATMP… --json                              # adds `actor`, an ExportedCanvasActor (object shape)
```

`list` returns `{ total, data }`, metadata only, 25 per page by default. **In a bundle**, write `actor` as the new
`actor.yaml` with the [bundle fixups](cli/canvas-bundles.md#templates-and-the-starter-limitation). **On the direct
path**, `canvas-actors create` and `batch` want YAML-string configuration, so convert it:

```bash
ACTOR_ID=$(borgiq templates get ATMP… --json \
  | borgiq scaffold actor-from-template --name "Notify #ops on deploy" --output actor.json --print-id)
borgiq canvas-actors create "$CANVAS_ID" "$ACTOR_ID" --file actor.json --json
```

`scaffold actor-from-template` does what the web editor does when a template is dropped on a canvas: YAML strings for
the `configuration` and `schemas` fields, a fresh actor id, a msgVar from `--name` (default: the template's name), a
fresh top-level `webhookTriggerKey`, and the `template: { id, version, appName }` provenance. It never replaces
`configuration.webhook.triggerKey` (mint one with `borgiq generate id webhooktriggerkey`), never checks the msgVar
against the canvas, and wires no edges, credentials, secrets or `inputs` values: set those with `canvas-actors
update`. Flags: `--file` (default stdin), `--name`, `--output`, `--print-id` (prints only the id, on stdout). For a
batch, pipe its JSON (no `--output` or `--print-id`) into `borgiq scaffold batch --output ops.json`, then
`borgiq canvas-actors batch <canvas> --file ops.json`.

## Start from a recipe

Recipes need CLI ≥ 0.13.0:
`borgiq help recipes >/dev/null 2>&1 || echo "upgrade: npm install -g @borgiq/cli"`. Without them, build from
templates.

A **recipe** is a saved starting point BorgIQ publishes: one task actor (`TASK`, e.g. an AI agent with its tools
attached), one trigger (`TRIGGER`), a whole flow (`FLOW`, trigger → steps) or a trigger-less chain (`SEGMENT`). Use
one when the ask is a multi-actor pattern ("classify webhook requests and post to Slack", "summarize and notify", "an
agent with memory"). It is **not versioned and not linked back**: the added actors are ordinary canvas actors that
nothing updates (a step that came from a template keeps its own `template` stamp).

**Wiring.** The entry is the actor an incoming edge attaches to; the exit is the actor and port an outgoing edge
leaves from; either is `null` when absent. `FLOW` and `SEGMENT` have both. A `TASK` or `TRIGGER` has what its actor
has: a trigger never has an entry, a webhook trigger has an exit, an MCP server (a `TRIGGER` with its tools) has
neither. `--after` needs a `TASK` or `SEGMENT` with an entry, `--into-edge` one with an entry and an exit; a `FLOW` or
`TRIGGER` is always added unwired. The whole recipe always lands.

```bash
borgiq recipes list --kind TASK --has-entry --json   # --kind TASK|TRIGGER|FLOW|SEGMENT; --app-id, --has-exit, --search
borgiq recipes apps --json                           # apps that hold recipes (one with only recipes is not in templates apps)
borgiq recipes get RCPE… --json | jq '{name, kind, entry, exit, settings}'
borgiq recipes add RCPE… --canvas "$CANVAS_ID" --after ACTR… --settings settings.yaml --json   # --after ACTR…:SPRTdone000 names the port
borgiq recipes add RCPE… --canvas "$CANVAS_ID" --into-edge EDGE… --json
borgiq recipes add RCPE… --canvas "$CANVAS_ID" --x 0 --y 800 --json                           # unwired, at a position
```

`list` items are metadata: `id`, `kind`, `name`, `description`, `actorCount`, `apps` (a recipe can be in several),
`settingsCount`, `entry`, `exit` and tags; an unknown `--kind` is a `400`. `--x`/`--y` place the entry actor (or,
without one, the top-left actor); by default the recipe lands below everything on the canvas.

**Settings.** `recipes get` returns `data.actors` (an ExportedCanvasData actor map), `entry`, `exit` and `settings`:
`connections[]` (`{ type, label?, actorIds, groupKey }`), `credentials[]` (`{ key, type?, source, label?, actorIds,
groupKey }`) and `inputs[]` (`{ key, label, type, required?, default?, targets }`). The `actorIds` are recipe-local. The
`--settings` file (JSON or YAML; `-` reads stdin) keys groups by `groupKey` and inputs by `key`. A group takes one
workspace key, or `{ <recipe actor id>: <key> }` for chosen actors of that group:

```yaml
connections:
  slack-bearer|slack-oauth2: team-slack
credentials:
  apiKey||secret: { ACTR…: my-api-key }
inputs:
  channel: '#triage'
```

The API checks everything before adding anything: keys must exist in the workspace (`borgiq connections list`,
`borgiq secrets list`) and match the group's connection type; values must read as their input's type (`abc` is not a
number, `yes` is not a boolean, JSON must parse); an omitted input takes its default, and a required one without a
default must be given. Omitted groups stay unset: set them later with `canvas-actors update`. Errors: `400` with
`details` when a check fails, a group, input or actor id is not the recipe's, or the wiring target is missing or does
not fit; `403` for an actor type the organization may not use (e.g. `PythonActor` outside a privileged
organization); `404` for an unknown recipe or canvas; `409` when the actor it wires to changed meanwhile (nothing
was added; re-read and retry).

`add` returns `{ actorIds, entryActorId, exitActorId, edgeIds }` (`null` ids when there is no entry or exit). The API
mints the ids and rewrites references to them in code and configuration, mints webhook keys, suffixes colliding
msgVars and wires the recipe in. Never rebuild a recipe from `recipes get` + `canvas-actors batch`.

## Errors

| Message or status | Exit | Meaning and fix |
|---|---|---|
| `401`, or `auth status` fails | 3 | Token missing, expired or revoked: ask the user to run `borgiq auth login` |
| `403` | 4 | The token lacks a scope, or the user is not a member of that org or workspace. The user creates a token with the scope ([api-tokens.md](api-tokens.md#scopes)) and logs in again |
| `404` | 5 | Wrong slug or ID, or wrong org/workspace: list first, or pass `--org` / `--workspace` |
| `409` from `canvas-actors update`/`delete`/`batch` or `update-data --mode replace` | 6 | The canvas changed since you read it (`editVersion`): re-read, reapply, retry with the current `--edit-version`. Bundle conflicts: [canvas-bundles.md](cli/canvas-bundles.md#incremental-sync-and-conflicts) |
| `400` naming a field, e.g. an object where a YAML string belongs | 2 | Wrong payload shape for the command: [cli-data-formats.md](cli/cli-data-formats.md#common-mistakes) |
| `429` | 7 | Rate limited per token: wait for `Retry-After` and back off ([api-tokens.md](api-tokens.md#rate-limits-and-errors)) |
| `Invalid JSON in file: <path>`, `Invalid YAML in file: <path>` | 2 | The file does not parse as its extension says |
| `Invalid YAML/JSON from stdin.` | 2 | The pipe carried other text (log lines, binary): write the payload to a file and pass `--file` |
| `Provide input via the file flag or pipe YAML/JSON to stdin.` | 2 | Nothing was piped on a terminal |
| `unknown command '<name>'` | 1 | The CLI predates the command: [CLI versions](#cli-versions) |
| `command not found: borgiq` | — | Not installed, or npm's global bin directory is not on `PATH` |
