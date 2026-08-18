#!/usr/bin/env python3
"""
Skill Installer - Copies all skills into detected AI agent skill directories.

Supported targets:
    - Claude Code: ~/.claude/skills
    - OpenAI Codex CLI: ~/.codex/skills
    - opencode.ai: ~/.config/opencode/skills
    - Pi (pi.dev): ~/.pi/agent/skills

The installer detects which agents are present on the machine (by checking for
the parent ~/.claude, ~/.codex, ~/.config/opencode, ~/.pi directories) and
installs into each one found. If multiple are present, skills go to all of them.

For non-Claude targets, SKILL.md files are transformed at install time:
    1. Claude-specific frontmatter (disable-model-invocation, allowed-tools,
       argument-hint) is stripped — other agents don't honor those fields.
    2. The Claude `${CLAUDE_SKILL_DIR}` variable in bash blocks is replaced
       with the absolute install path so commands still run.
    3. Claude's inline-execution `!`<cmd>`` and ```!`` block markers are
       reduced to plain code spans / bash fences — other agents read these
       as code blocks the AI can choose to run.
    4. The 5 lifecycle skills (validate, new-actor, deploy, test, debug-flow)
       get a defensive prologue. `deploy` and `test` get a stronger warning
       since they have platform side effects.

Usage:
    install_skills.py [--dry-run] [--target claude|codex|opencode|pi|all]
    install_skills.py [--all]

Options:
    --dry-run         Show what would be copied without actually copying
    --target TARGET   Force install to a specific target (or 'all').
                      Default: auto-detect based on which directories exist.
    --all             Shorthand for --target all.

Examples:
    install_skills.py                    # Auto-detect and install to all found
    install_skills.py --dry-run          # Preview
    install_skills.py --target codex     # Force install to Codex only
    install_skills.py --all              # Install everywhere even if undetected

Requires pyyaml: pip install pyyaml
"""

import re
import shutil
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("❌ This installer needs pyyaml. Install with: pip install pyyaml")
    sys.exit(1)


# ---- Configuration ---------------------------------------------------------

TARGETS = {
    "claude": {
        "path": Path.home() / ".claude" / "skills",
        "detect_parent": Path.home() / ".claude",
        "transform": False,
    },
    "codex": {
        "path": Path.home() / ".codex" / "skills",
        "detect_parent": Path.home() / ".codex",
        "transform": True,
    },
    "opencode": {
        "path": Path.home() / ".config" / "opencode" / "skills",
        "detect_parent": Path.home() / ".config" / "opencode",
        "transform": True,
    },
    "pi": {
        "path": Path.home() / ".pi" / "agent" / "skills",
        "detect_parent": Path.home() / ".pi",
        "transform": True,
    },
}

# Frontmatter fields that mean something to Claude Code but not to other agents.
CLAUDE_ONLY_FRONTMATTER_FIELDS = (
    "disable-model-invocation",
    "allowed-tools",
    "argument-hint",
)

# Defensive prologues. Inserted into the body of any skill that originally had
# `disable-model-invocation: true` when installing to a non-Claude target.
PROLOGUE_STRONG = (
    "> ⚠️ **Side-effecting workflow.** Only execute this skill when the user "
    "explicitly asks to {action}. Confirm the target workspace and the action "
    "with the user before running any `borgiq` command in this skill.\n"
)

PROLOGUE_LIGHT = (
    "> ℹ️ **Manual workflow.** Only run when the user explicitly invokes it "
    "(e.g., {examples}).\n"
)

PROLOGUE_MAP = {
    "deploy":     ("strong", {"action": "deploy a workflow"}),
    "test":       ("strong", {"action": "test a flow"}),
    "validate":   ("light",  {"examples": '"validate this YAML", "check my workflow"'}),
    "new-actor":  ("light",  {"examples": '"scaffold an HTTP actor", "show me a starter YAML"'}),
    "debug-flow": ("strong", {"action": "debug a flowrun and apply fixes to a deployed canvas"}),
}

# Frontmatter block at the top of SKILL.md. Group 1 = YAML, group 2 = body.
FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n(.*)\Z", re.DOTALL)

# Claude's per-skill directory variable.
CLAUDE_SKILL_DIR_RE = re.compile(r"\$\{CLAUDE_SKILL_DIR\}")

# Claude's inline `!`<cmd>`` and ```!`` fenced block markers. We strip the
# leading `!` so other agents see plain code spans / bash fences.
INLINE_BANG_RE = re.compile(r"(^|(?<=\s))!`([^`]+)`")
BLOCK_BANG_RE = re.compile(r"^```!\s*$", re.MULTILINE)


# ---- Source dir ------------------------------------------------------------

def get_skills_source_dir():
    """Resolve the skills source directory relative to this script.

    Prefers the marketplace-era layout
    (plugins/borgiq-builder/skills/) and falls back to the legacy
    top-level skills/ path so older branches/forks still work.
    """
    script_dir = Path(__file__).parent.resolve()
    new_layout = script_dir.parent / "plugins" / "borgiq-builder" / "skills"
    if new_layout.is_dir():
        return new_layout
    return script_dir.parent / "skills"


# ---- Transformations -------------------------------------------------------

def transform_skill_md(src_path: Path, dst_path: Path, target_skill_dir: Path) -> None:
    """Apply the non-Claude transformations and write the result to dst_path.

    See module docstring for the 4 transformations.

    Args:
        src_path: source SKILL.md
        dst_path: destination SKILL.md (will be overwritten)
        target_skill_dir: absolute path of the destination skill dir,
            used to rewrite ${CLAUDE_SKILL_DIR} bash refs.
    """
    content = src_path.read_text()
    match = FRONTMATTER_RE.match(content)

    if not match:
        # No frontmatter — just strip bash markers and rewrite the var.
        new_text = _strip_bang(_rewrite_skill_dir(content, target_skill_dir))
        dst_path.write_text(new_text)
        return

    frontmatter_yaml, body = match.groups()
    fm = yaml.safe_load(frontmatter_yaml) or {}

    had_disable_invocation = fm.get("disable-model-invocation") is True
    skill_name = fm.get("name") or src_path.parent.name

    # A. Strip Claude-only fields.
    for field in CLAUDE_ONLY_FRONTMATTER_FIELDS:
        fm.pop(field, None)
    new_fm = yaml.safe_dump(
        fm,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
        width=10_000,  # don't fold long description lines
    ).rstrip()

    # B. Rewrite the per-skill directory variable.
    body = _rewrite_skill_dir(body, target_skill_dir)

    # C. Strip Claude's inline-execution `!` markers.
    body = _strip_bang(body)

    # D. Inject a defensive prologue for the 5 lifecycle commands.
    if had_disable_invocation and skill_name in PROLOGUE_MAP:
        tier, fmt_args = PROLOGUE_MAP[skill_name]
        template = PROLOGUE_STRONG if tier == "strong" else PROLOGUE_LIGHT
        body = _insert_prologue(body, template.format(**fmt_args))

    dst_path.write_text(f"---\n{new_fm}\n---\n{body}")


def _rewrite_skill_dir(text: str, target_skill_dir: Path) -> str:
    return CLAUDE_SKILL_DIR_RE.sub(str(target_skill_dir), text)


def _strip_bang(text: str) -> str:
    """Strip Claude's `!`<cmd>`` inline + ```!`` block markers."""
    text = INLINE_BANG_RE.sub(r"\1`\2`", text)
    text = BLOCK_BANG_RE.sub("```bash", text)
    return text


def _insert_prologue(body: str, prologue: str) -> str:
    """Insert prologue after the first H1 if present, else at the top.

    The body coming out of the frontmatter regex starts with a newline,
    so we lstrip that, find the H1 (if any), and insert the prologue
    between the H1 and the rest of the body.
    """
    body = body.lstrip("\n")
    lines = body.split("\n", 1)
    first = lines[0]
    rest = lines[1] if len(lines) > 1 else ""
    if first.startswith("# "):
        rest = rest.lstrip("\n")
        return f"\n{first}\n\n{prologue}\n{rest}"
    return f"\n{prologue}\n{body}"


# ---- Detection + install ---------------------------------------------------

def detect_targets(forced=None):
    """Return list of (name, config) for targets to install into."""
    if forced == "all":
        return list(TARGETS.items())
    if forced in TARGETS:
        return [(forced, TARGETS[forced])]
    detected = []
    for name, cfg in TARGETS.items():
        if cfg["detect_parent"].exists():
            detected.append((name, cfg))
    return detected


def install_one_skill(skill_src: Path, target_skill_dir: Path, transform: bool, dry_run: bool) -> str:
    """Install one skill into one target dir. Returns 'new' or 'replaced'."""
    state = "replaced" if (target_skill_dir.exists() or target_skill_dir.is_symlink()) else "new"

    if dry_run:
        return state

    if target_skill_dir.is_symlink():
        target_skill_dir.unlink()
    elif target_skill_dir.exists():
        shutil.rmtree(target_skill_dir)

    shutil.copytree(skill_src, target_skill_dir)

    if transform:
        skill_md = target_skill_dir / "SKILL.md"
        if skill_md.exists():
            transform_skill_md(skill_src / "SKILL.md", skill_md, target_skill_dir)

    return state


def install_to_target(name: str, target_cfg: dict, skills: list, dry_run: bool) -> int:
    """Install every skill into one target. Returns count installed."""
    target_dir = target_cfg["path"]
    transform_note = " (transformed for non-Claude)" if target_cfg["transform"] else ""
    print(f"📁 Target: {name} → {target_dir}{transform_note}")

    if not dry_run:
        target_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    for skill_dir in sorted(skills):
        skill_name = skill_dir.name
        target_skill_dir = target_dir / skill_name
        state = install_one_skill(skill_dir, target_skill_dir, target_cfg["transform"], dry_run)
        if state == "replaced":
            marker, suffix = "🔄", " (would overwrite existing)" if dry_run else " (replaced existing)"
        else:
            marker, suffix = "✅", ""
        print(f"  {marker} {skill_name}{suffix}")
        count += 1

    print()
    return count


def install_skills(dry_run=False, forced_target=None) -> int:
    """Copy all skills from source dir into every detected (or forced) target."""
    source_dir = get_skills_source_dir()

    if not source_dir.exists():
        print(f"❌ Error: Skills source directory not found: {source_dir}")
        return -1

    skills = [
        item for item in source_dir.iterdir()
        if item.is_dir() and (item / "SKILL.md").exists()
    ]

    if not skills:
        print(f"❌ No skills found in {source_dir}")
        return 0

    targets = detect_targets(forced_target)
    if not targets:
        print("❌ No supported agent directories found.")
        print(f"   Looked for: {', '.join(str(cfg['detect_parent']) for cfg in TARGETS.values())}")
        print("   Install Claude Code, Codex, opencode, or Pi first, or pass --target to force.")
        return -1

    print(f"📦 Found {len(skills)} skill(s) in {source_dir}")
    print(f"🎯 Installing to {len(targets)} target(s): {', '.join(name for name, _ in targets)}")
    print()

    if dry_run:
        print("🔍 DRY RUN - No files will be copied\n")

    total = 0
    for name, cfg in targets:
        total += install_to_target(name, cfg, skills, dry_run)

    verb = "Would perform" if dry_run else "Successfully performed"
    marker = "🔍" if dry_run else "✅"
    print(f"{marker} {verb} {total} install(s) across {len(targets)} target(s)")

    return total


# ---- CLI -------------------------------------------------------------------

def parse_target_arg(argv):
    """Pull `--target X` or `--target=X` (or `--all`) out of argv."""
    for i, arg in enumerate(argv):
        if arg == "--target" and i + 1 < len(argv):
            return argv[i + 1]
        if arg.startswith("--target="):
            return arg.split("=", 1)[1]
    if "--all" in argv:
        return "all"
    return None


def main():
    if "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__)
        sys.exit(0)

    dry_run = "--dry-run" in sys.argv or "-n" in sys.argv
    forced_target = parse_target_arg(sys.argv)

    valid_targets = set(TARGETS.keys()) | {"all"}
    if forced_target is not None and forced_target not in valid_targets:
        print(f"❌ Unknown --target value: {forced_target}")
        print(f"   Valid values: {', '.join(sorted(TARGETS))}, all")
        sys.exit(1)

    print("🚀 BorgIQ Skills Installer")
    print("=" * 40)
    print()

    result = install_skills(dry_run=dry_run, forced_target=forced_target)
    sys.exit(1 if result < 0 else 0)


if __name__ == "__main__":
    main()
