# borgiq-skills

Skills for building **BorgIQ** workflows (Actors, Triggers, Flows) from your AI coding agent. One source of truth, distributed to **Claude Code**, **OpenAI Codex CLI**, **opencode.ai**, **Pi (pi.dev)**, **Cursor**, **GitHub Copilot**, **Cline**, **Gemini**, and 10+ more agents via [skills.sh](https://www.skills.sh/).

The plugin contains:
- 1 **hub** skill — `borgiq-builder` — actor wiring, edges, expressions, workflow composition
- 4 **spoke** skills that auto-load when their domain is in play: `borgiq-form-builder`, `borgiq-react-app-builder`, `borgiq-agent-builder`, `borgiq-json-schema-builder`
- 5 **lifecycle commands**: `/validate`, `/new-actor`, `/deploy`, `/test`, `/debug-flow`

---

## Installation

Pick your agent. The same SKILL.md content reaches all four; the install mechanism differs.

### Claude Code (recommended)

One-line install via the plugin marketplace. Adds auto-update, namespacing (`/borgiq-builder:validate`), version pinning, and lets `/plugin` show context cost + a "Will install" panel before confirming.

```text
/plugin marketplace add BorgIQ/borgiq-skills
/plugin install borgiq-builder@borgiq-skills
```

Team install via project `.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "borgiq-skills": { "source": { "source": "github", "repo": "BorgIQ/borgiq-skills" } }
  },
  "enabledPlugins": { "borgiq-builder@borgiq-skills": true }
}
```

### Any other agent — via [skills.sh](https://www.skills.sh/)

Vercel's open agent skills ecosystem auto-detects your AI agent and installs there:

```bash
npx skills add BorgIQ/borgiq-skills
```

Works with Cursor, GitHub Copilot, Cline, Gemini, Claude Code, Codex, opencode, and 11+ other agents the skills CLI knows about. The CLI clones the repo, discovers all 10 skills, and installs them into the right directory for your agent. Add `--skill <name>` to install just one, `--agent <name>` to target a specific agent, or `--all` for everything.

### Pi (pi.dev)

Native package install via npm:

```bash
pi install npm:@borgiq/skills
```

Or via git:

```bash
pi install git:github.com/BorgIQ/borgiq-skills
```

Pi reads the `pi.skills` glob in [package.json](package.json) and registers all 10 skills.

### OpenAI Codex CLI / opencode.ai

These don't have a marketplace yet, so install via the bundled script. Works from a fresh clone or a checkout you already have.

```bash
git clone https://github.com/BorgIQ/borgiq-skills
cd borgiq-skills
pip install pyyaml                       # one-time
python3 scripts/install_skills.py --target codex      # Codex
python3 scripts/install_skills.py --target opencode   # opencode
python3 scripts/install_skills.py --all               # everything detected (or forced)
```

`install_skills.py` auto-detects which agents are installed on the machine (by looking for `~/.claude`, `~/.codex`, `~/.config/opencode`, `~/.pi`) and installs to each one found. For non-Claude targets it strips Claude-only frontmatter (`disable-model-invocation`, `allowed-tools`, `argument-hint`), rewrites `${CLAUDE_SKILL_DIR}` to an absolute install path, and injects a defensive prologue into the lifecycle workflows so the agent doesn't auto-deploy or auto-test without explicit user intent.

### Claude API (legacy `.skill` zip)

For programmatic Claude API access (no marketplace support yet), upload via the Skills API:

```python
from anthropic import Anthropic
client = Anthropic()
with open("borgiq-builder.skill", "rb") as f:
    skill = client.beta.skills.create(display_title="BorgIQ Builder", files=f)
```

The `.skill` zip is built with `scripts/package_skill.py`.

### Claude.ai (Web)

Custom skills aren't supported in the web interface yet. Use Claude Code or the Claude API.

---

## Compatibility matrix

| Agent | Install path | Source of truth | Auto-update |
|---|---|---|---|
| Claude Code | `~/.claude/skills/` or `.claude/skills/` | Plugin marketplace | ✅ via `/plugin marketplace update` |
| OpenAI Codex CLI | `~/.codex/skills/` | `install_skills.py --target codex` or `npx skills add` | ❌ re-run installer |
| opencode.ai | `~/.config/opencode/skills/` (also reads `~/.claude/skills/`) | `install_skills.py --target opencode` or `npx skills add` | ❌ re-run installer |
| Pi (pi.dev) | `~/.pi/agent/skills/` (also reads `~/.claude/skills/`) | `pi install npm:@borgiq/skills` | ✅ via `pi update` |
| Cursor / Copilot / Cline / Gemini / 14+ others | Per-agent (auto-detected by skills CLI) | `npx skills add BorgIQ/borgiq-skills` | ❌ re-run installer |

**Cross-agent freebie:** opencode and Pi also read Claude's locations (`~/.claude/skills/`, `.claude/skills/`). If you've installed via the Claude Code marketplace already, those two agents pick up the borgiq skills automatically — no extra step.

---

## Developing skills

The repository is laid out as a Claude Code plugin marketplace under `plugins/`:

```
.claude-plugin/marketplace.json
plugins/borgiq-builder/
├── .claude-plugin/plugin.json
└── skills/
    ├── borgiq-builder/        # hub
    ├── borgiq-form-builder/
    ├── borgiq-react-app-builder/
    ├── borgiq-agent-builder/
    ├── borgiq-json-schema-builder/
    ├── validate/                    # lifecycle command
    ├── new-actor/
    ├── deploy/
    ├── test/
    └── debug-flow/
```

### Scaffold a new skill

```bash
python3 scripts/init_skill.py my-new-spoke --plugin borgiq-builder
```

### Validate

`quick_validate.py` walks a SKILL.md, a plugin, or the whole marketplace and checks frontmatter, plugin.json, marketplace.json, and cross-skill reference resolution.

```bash
python3 scripts/quick_validate.py .                                            # whole marketplace
python3 scripts/quick_validate.py plugins/borgiq-builder                 # one plugin
python3 scripts/quick_validate.py plugins/borgiq-builder/skills/borgiq-form-builder
```

### Test the multi-agent installer

Install into a temporary `HOME` and inspect the transforms:

```bash
HOME=$(mktemp -d) python3 scripts/install_skills.py --all --dry-run
```

---

## Versioning

Releases are automated by [release-please](.github/workflows/release.yml). Conventional commits on `main` produce a release PR that bumps:

- `plugins/borgiq-builder/.claude-plugin/plugin.json` → `$.version` (Claude Code marketplace)
- `.claude-plugin/marketplace.json` → `$.plugins[0].version` (Claude Code marketplace)
- `package.json` → `$.version` (Pi via npm)
- `.release-please-manifest.json`
- `CHANGELOG.md`

Merging the release PR creates a git tag (`vX.Y.Z`) and a GitHub release, and CI **stages** the npm package (`npm stage publish --provenance`) — a maintainer then approves the staged release with 2FA before it goes live. See [CONTRIBUTING.md](CONTRIBUTING.md) for the full flow. Claude Code marketplace auto-update picks up the new tag from git independently.

Conventional commits:
- `feat:` — new spoke, new command, new auto-loaded skill (minor bump)
- `fix:` — bug or correctness fix (patch bump)
- `feat!:` or `BREAKING CHANGE:` — skill/command renames or removals (major bump — breaks installed users)
- `docs:` / `chore:` / `ci:` / `test:` — no version bump, hidden from CHANGELOG

---

## License

[Apache-2.0](LICENSE)
