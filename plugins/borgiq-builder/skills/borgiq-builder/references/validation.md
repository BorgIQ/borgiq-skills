# IDs and validation

What valid BorgIQ IDs look like and how to mint them, what to do with no shell, and which validator checks what.
Validate every generated or edited canvas before you present or push it.

## ID formats

With a shell, mint every ID with `borgiq generate` (offline, no token; `--json` prints `{ id }`); never invent one.

| Entity | Format | Mint with |
|---|---|---|
| Actor | `ACTR` + 26 lowercase ULID characters (`[0123456789abcdefghjkmnpqrstvwxyz]`: no `i`, `l`, `o`, `u`) | `borgiq generate id actor` → `ACTR01kcsnjnkqa69w50qr60dcd06e` |
| Edge | `EDGE` + the same 26 characters | `borgiq generate id edge` |
| Source port | `SPRT` + 7 lowercase letters or digits, or the fixed `SPRTdefault`, `SPRTdone000`, `SPRTevent00` | `borgiq generate id sourceport` → `SPRT5d5gj2s` |
| Webhook trigger key | a 26-character uppercase ULID | `borgiq generate id webhooktriggerkey` → `01KD298E3VRBDAZN9X5ETV4R6G` |
| msgVar | the name lowercased, all but letters, digits, `_` and `$` dropped, spaces as `_`, `_` before a leading digit | `borgiq generate msgvar "Fetch user profile from Gmail"` → `fetch_user_profile_from_gmail` |

A canvas ID is `CANV` + the same 26 characters, assigned by the platform. Mint one source port per named route of a
RouterActor or AiRouterActor (`SPRTdefault` is the fallback, never minted); other actors' ports are fixed
([ports per type](edges-and-positioning.md#port-ids)). A WebhookTriggerActor needs a trigger key. msgVars are unique
in a canvas; regenerate one when you rename its actor ([editing-workflows.md](editing-workflows.md)).

## No shell

There is no CLI and no validator. Write one `metadata` + `actors` document, compose every ID and msgVar exactly by the
table (each unique in the canvas), and tell the user the document is unvalidated: `canvases validate` or the web
editor checks it once deployed.

## Validators per mode

| Mode | Command | Checks |
|---|---|---|
| Bundle | `borgiq bundle validate <dir> --strict` | Offline: files, index, graph, ports and code trees, each finding against its file ([canvas-bundles.md](cli/canvas-bundles.md#troubleshooting)) |
| Document (`metadata` + `actors`) | `borgiq validate <file>` (or stdin) | Offline: YAML structure, required fields (`type`, `name`, `msgVar`, `configuration`), ID formats, each type's options, the `enableLTM`/`enableSTM` an action needs, edge consistency, text checks on Deno and Python code (e.g. a `receive` handler). Non-zero exit when invalid. Not for a bundle's `actor.yaml` |
| One actor's options | `borgiq canvas-actors verify <canvas>` | Against the type's schema ([body](cli/cli-data-formats.md#verify-bodies)) |
| A deployed canvas | `borgiq canvases validate <canvas> --json` | `{ valid, errors, warnings }`. Errors: ID formats, each type's source ports, duplicate msgVars or edge IDs, edges to missing actors or undeclared ports, code entrypoints, webhook trigger keys, missing AI agent tools or connections. Warnings: no trigger actor, an actor without incoming edges, an unknown custom model provider. Fix, push, validate again |

Code is never typechecked or syntax-checked locally (`--skip-typecheck` is accepted and ignored); the API is the
authority on code. `borgiq validate <file> --post-process` (`-i` rewrites the file) is optional cleanup after
validation passes, and validates nothing: it adds `schemas: {}` where missing, removes edge `label`s (only routers use
them), leaves RouterActor and AiRouterActor untouched, and reformats only when it changed something.
