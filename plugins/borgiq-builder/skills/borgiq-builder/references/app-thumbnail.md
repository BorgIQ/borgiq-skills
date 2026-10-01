# App thumbnail

Capture and attach the image shown on an app's canvas node and the workspace apps page, for a ReactAppTriggerActor
or a legacy AppTriggerActor (`@borgiq/cli` ≥ 0.12.0). Give every app you build one (otherwise it shows a placeholder),
and refresh it after a visible UI change.

## Limits

PNG, JPEG, WebP or GIF, **≤ 2 MiB**, no SVG; about 1280 px wide is plenty. The API reads the type from the bytes, not
the extension, and stores the image sent inline (no upload step). The CLI never resizes: if a PNG is too large, capture
a smaller viewport or save it as `.jpg`.

## Capture

Screenshot the app's own page, not the editor around it:

```bash
SRC=$(borgiq canvas-actors app-url <canvas> <actorId>)    # stdout is only the URL
npx playwright screenshot --viewport-size=1280,800 --wait-for-timeout=3000 "$SRC" thumbnail.png
```

- The URL carries a content token that expires within minutes. Fetch it right before the screenshot, never log it, and
  treat it like a password until then.
- `--wait-for-timeout` lets the app load real data; raise it for slow backends. A loading spinner is a bad thumbnail.
- A React app must be built first: an unbuilt one answers `409`. On a deployed workspace the URL serves the active
  runtime build.
- `403` means the CLI token lacks the `app:use` scope. Mint one for the capture with
  `borgiq tokens create --name thumbnail --scopes org:access,workspace:access,canvas:read,canvas:write,app:use --json`,
  pass its `rawToken` as `BORGIQ_API_TOKEN` without echoing it, and revoke it afterwards
  (`borgiq tokens revoke <id> --yes`).
- Playwright needs its Chromium (`npx playwright install chromium` once). With no headless browser, do not fake a
  thumbnail: ask the user to upload one from the app editor's Settings, or give them
  `borgiq auth handoff-url --redirect /org/{org}/w/{wsp}/c/{canvas}/apps/{actorId}` for their own browser.

## Attach

```bash
borgiq canvas-actors thumbnail set <canvas> <actorId> thumbnail.png   # --edit-version <n> guards a concurrent edit
borgiq canvas-actors thumbnail get <canvas> <actorId> --out check.png  # prints type and size, never the base64
borgiq canvas-actors thumbnail rm  <canvas> <actorId>
```

In a canvas bundle, put the file beside the actor's `actor.yaml`, name it there, then push:

```text
actors/triggers/react-app/<actorId>/
  actor.yaml        # thumbnail: thumbnail.png
  thumbnail.png
```

- `bundle pull` writes an existing thumbnail the same way, as `thumbnail.<png|jpg|webp|gif>`.
- A `thumbnail.*` file that `actor.yaml` does not name is not pushed (`bundle validate` warns). A name without its file
  is a validate error.
- To remove it, delete both the file and the `thumbnail:` line, then push.
- Details: [canvas-bundles.md → App thumbnails](cli/canvas-bundles.md#app-thumbnails).

With a CLI older than 0.12.0, set it through the API: `PATCH …/canvases/{canvas}/actors/{actorId}` with
`{ "thumbnail": { "dataUrl": "data:image/png;base64,…" } }`, or `{ "thumbnail": null }` to remove it.
