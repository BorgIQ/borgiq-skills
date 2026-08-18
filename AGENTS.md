# AGENTS.md

This is the **development repository** for `borgiq-skills` — the public, multi-agent distribution of BorgIQ skills. The same SKILL.md content reaches **Claude Code**, **OpenAI Codex CLI**, **opencode.ai**, **Pi (pi.dev)**, and 14+ other agents (Cursor, Copilot, Cline, Gemini, …) via [skills.sh](https://www.skills.sh/). Channels documented below.

## Repository layout

```
borgiq-skills/
├── .claude-plugin/
│   └── marketplace.json                 # marketplace catalog
└── plugins/
    └── borgiq-builder/
        ├── .claude-plugin/
        │   └── plugin.json              # plugin manifest (version source of truth)
        └── skills/
            ├── borgiq-builder/    # HUB — actor wiring, expressions, triggers
            │   ├── SKILL.md
            │   └── references/          # 53+ reference docs (shared across all skills)
            │                            #   (ID gen / validation / scaffolding now ship in @borgiq/cli)
            ├── borgiq-form-builder/     # SPOKE — interface pages + forms
            ├── borgiq-react-app-builder/  # SPOKE — React app UIs in ReactAppTriggerActor
            ├── borgiq-agent-builder/    # SPOKE — AI agents, agent-harness, MCP
            ├── borgiq-json-schema-builder/  # SPOKE — JSON schema design
            ├── validate/                # COMMAND — disable-model-invocation: true
            ├── new-actor/               # COMMAND
            ├── deploy/                  # COMMAND
            ├── test/                    # COMMAND
            └── debug-flow/              # COMMAND
```

The hub and spokes auto-invoke based on the user's prompt; the five slash commands are user-only and are invoked as `/borgiq-builder:<name>`. Spokes reference the hub's `references/` directory via relative paths (`../borgiq-builder/references/...`); resolution stays inside the plugin cache.

## Output directory

Generated workflow YAML files and other skill outputs are written to `outputs/` at the repo root.

## BorgIQ CLI

The `borgiq` CLI (`@borgiq/cli`) provides programmatic access to the BorgIQ API. Install and authenticate before invoking the slash commands:

```bash
npm install -g @borgiq/cli
borgiq auth login
```

If `borgiq` commands fail with `401`, run `borgiq auth login` again. The five lifecycle slash commands (`/validate`, `/new-actor`, `/deploy`, `/test`, `/debug-flow`) wrap this CLI. See [borgiq-cli.md](plugins/borgiq-builder/skills/borgiq-builder/references/borgiq-cli.md) for the full reference.

**Offline helpers (no auth, no script install).** ID generation, workflow validation, and JSON scaffolding are provided by the CLI itself — `borgiq generate`, `borgiq validate`, and `borgiq scaffold`. These replaced the local `skills/borgiq-builder/scripts/` TypeScript validators/generators that the skill used to run via `npx tsx`; the skill now shells out to the verified CLI instead. This requires **`@borgiq/cli` >= 0.8.0**; older CLIs lack these commands. The `scaffold-*.sh` helpers under `references/cli/scripts/` are retained and now mint IDs via `borgiq generate`.

**Canvas bundles.** `borgiq bundle init/pull/push/pack/unpack/validate` require **`@borgiq/cli` >= 0.8.0**. If `borgiq bundle` is unavailable, upgrade (`npm install -g @borgiq/cli`); agents must fall back to the direct document/batch workflow when the command is unavailable.

## Scripts

The `scripts/` directory contains developer tooling for working on this repo (these are NOT shipped to plugin users):

- `quick_validate.py` — validate a SKILL.md, a plugin, or the whole marketplace
- `init_skill.py` — initialize a new skill from template
- `package_skill.py` — *(legacy)* package a skill as a `.skill` zip for Claude API users
- `install_skills.py` — *(legacy)* install a `.skill` zip into `~/.claude/skills/`

The `package_skill.py` workflow is retained for Claude API customers who can't use marketplace install yet. `install_skills.py` is now used both for legacy `.skill` install AND as the file-copy installer for Codex / opencode / Pi from a git clone.

### quick_validate.py

Walks any of these and reports per-artifact pass/fail:

```bash
python3 scripts/quick_validate.py .                                    # whole marketplace
python3 scripts/quick_validate.py plugins/borgiq-builder         # one plugin
python3 scripts/quick_validate.py plugins/borgiq-builder/skills/borgiq-form-builder  # one skill
```

Cross-skill references inside the same plugin (the spoke → hub `references/` pattern) are allowed. References that escape the plugin root or fail to resolve are reported.

### init_skill.py

Two usage forms:

```bash
# Add a new spoke or command to the existing plugin:
python3 scripts/init_skill.py my-new-spoke --plugin borgiq-builder

# Or specify an explicit path:
python3 scripts/init_skill.py custom-skill --path /custom/location
```

## Distribution channels

| Agent | Channel | Native install command |
|---|---|---|
| Claude Code | Plugin marketplace (this repo's `.claude-plugin/marketplace.json`) | `/plugin marketplace add BorgIQ/borgiq-skills`, then `/plugin install borgiq-builder@borgiq-skills` |
| Pi (pi.dev) | npm package `@borgiq/skills` (published from this repo) | `pi install npm:@borgiq/skills` |
| OpenAI Codex CLI | File copy via `scripts/install_skills.py` | `python3 scripts/install_skills.py --target codex` |
| opencode.ai | File copy via `scripts/install_skills.py`; also reads `~/.claude/skills/` | `python3 scripts/install_skills.py --target opencode` |
| Cursor / Copilot / Cline / Gemini / 14+ others | [skills.sh](https://www.skills.sh/) via Vercel's `skills` CLI | `npx skills add BorgIQ/borgiq-skills` |

**`install_skills.py` transforms SKILL.md for non-Claude targets.** Other agents don't honor Claude's `disable-model-invocation: true`, `allowed-tools`, or `argument-hint` frontmatter, and they don't have an equivalent of `${CLAUDE_SKILL_DIR}`. On non-Claude installs the script:

1. Strips Claude-only frontmatter fields
2. Rewrites `${CLAUDE_SKILL_DIR}` to the absolute install path (so bash blocks work)
3. Strips Claude's `!`<cmd>`` / ```!`` execution markers (other agents read these as code spans / bash fences instead of auto-executing them)
4. Injects a defensive prologue into the 5 lifecycle workflows — strong tier for `deploy`, `test`, and `debug-flow` (have platform side effects; debug-flow can `bundle push` fixes), light tier for `validate` / `new-actor`

**The Pi-via-npm channel and the skills.sh CLI both ship the source SKILL.md byte-for-byte** (no transforms — they copy/clone what's in the repo). Claude-specific frontmatter fields (`disable-model-invocation`, `allowed-tools`, `argument-hint`) are ignored by other agents — so `disable-model-invocation: true` doesn't actually block model invocation outside of Claude Code. The 5 lifecycle commands could become auto-invocable on Cursor / Copilot / Cline / Gemini / Pi-via-npm. Mitigations:

- **For deploy, test, and debug-flow** — the `borgiq` CLI itself prompts for confirmation on destructive operations (workspace selection, auth scope), so a runaway agent still has a hard checkpoint.
- **For full safety** — Pi users can fall back to `pi install git:github.com/BorgIQ/borgiq-skills` or `install_skills.py --target pi`, both of which run the transform pipeline and inject defensive prologues. Cursor / Copilot / Cline / Gemini users who want the same defenses can clone the repo and run `install_skills.py --all` instead of `npx skills add`.

The skills.sh manifest at [skills.sh.json](skills.sh.json) groups the 10 skills into two categories ("Build BorgIQ workflows", "Lifecycle workflows") for display on the [skills.sh](https://www.skills.sh/) leaderboard.

**Cross-agent freebie:** both opencode and Pi explicitly read Claude's locations (`~/.claude/skills/`, `.claude/skills/`). If a customer is using Claude Code + the marketplace plugin, those two agents see the borgiq skills with zero extra steps.

## Versioning and releases

Releases are **automated by release-please**. The `release` GitHub Action watches `main` for conventional commits and opens a release PR that bumps:

- `plugins/borgiq-builder/.claude-plugin/plugin.json` → `$.version` (Claude Code)
- `.claude-plugin/marketplace.json` → `$.plugins[0].version` (Claude Code marketplace)
- `package.json` → `$.version` (npm / Pi)
- `.release-please-manifest.json`
- `CHANGELOG.md`

All three version locations are kept in lockstep via `extra-files` in [release-please-config.json](release-please-config.json). When the release PR is merged, release-please creates a git tag (`vX.Y.Z`) and a GitHub release. Two downstream things happen automatically:

1. The `publish-npm` job in [.github/workflows/release.yml](.github/workflows/release.yml) runs `npm stage publish --provenance --access public` for `@borgiq/skills` — the version is **staged, not live**. A maintainer approves it with `npm stage approve <id>` (2FA) to make it public; CI's OIDC token is staging-only and structurally cannot publish live. See [CONTRIBUTING.md](CONTRIBUTING.md). Do not run `npm publish` locally.
2. Claude Code's marketplace auto-update picks up the new tag on the next `/plugin marketplace update` (or auto-update window) — this path is independent of npm approval.

**Commit conventions** (parsed by release-please on `main`):

- `feat:` — minor bump. New spoke, new slash command, new auto-loaded skill.
- `fix:` — patch bump. Bug or correctness fix in an existing skill.
- `perf:` / `refactor:` — patch bump.
- `docs:` / `chore:` / `test:` / `build:` / `ci:` — no version bump, hidden from CHANGELOG.
- `feat!:` (or `BREAKING CHANGE:` footer) — major bump. Use for skill/command renames or removals — these break installed users.

Do not bump version fields by hand. release-please owns them.

When committing or opening PRs in this repo, use the in-repo `release-please-commits` and `release-please-prs` skills (`.claude/skills/`) — the PR title becomes the squashed commit release-please parses, so it must be a conventional commit by itself.
