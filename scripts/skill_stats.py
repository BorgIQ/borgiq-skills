#!/usr/bin/env python3
"""
Measure the shipped skill pack and enforce its size budgets.

Usage:
    skill_stats.py                      per-skill summary and totals
    skill_stats.py --files              one row per shipped file
    skill_stats.py --tasks              load cost of each common task
    skill_stats.py --json OUT.json      write per-file and per-task numbers
    skill_stats.py --compare OUT.json   markdown before/after tables against
                                        an earlier --json (for PR bodies)
    skill_stats.py --check              enforce scripts/skill-budgets.json;
                                        exit 1 on any violation

Measures:
    words   whitespace-separated words
    lines   newline count
    tokens  characters / 4 (an estimate; use it for ratios, not absolutes)

A task's load cost is the SKILL.md files that trigger for it plus the
references its instructions route the agent to, counted as whole files
(scripts/task-paths.json). Whole files is conservative: an agent that greps
for a section loads less.

Budgets (scripts/skill-budgets.json) are a ratchet: each starts at the size a
file has today, and a change that shrinks a file lowers its budget in the same
PR, so nothing quietly regrows.
"""

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS = REPO / "plugins" / "borgiq-builder" / "skills"
BUDGETS = REPO / "scripts" / "skill-budgets.json"
TASKS = REPO / "scripts" / "task-paths.json"

HUB_REFS = "borgiq-builder/references/"
GENERATED = ("borgiq-builder/references/typescript/",
             "borgiq-builder/references/ai-agent-api-guide.md")

# Agent Skills spec limits for a SKILL.md body
SPEC_MAX_LINES = 500
SPEC_MAX_TOKENS = 5000


def measure(text):
    return {"words": len(text.split()), "lines": text.count("\n"), "tokens": len(text) // 4}


def shipped_files():
    rows = {}
    for path in sorted(SKILLS.rglob("*")):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        rows[path.relative_to(SKILLS).as_posix()] = measure(text)
    return rows


def group(rel):
    if rel.startswith(GENERATED):
        return "references (generated)"
    if rel.startswith(HUB_REFS):
        return "references (hand-written)"
    if rel.endswith("/SKILL.md"):
        return "SKILL.md"
    return "other"


def load_tasks():
    if not TASKS.exists():
        return []
    return json.loads(TASKS.read_text())["tasks"]


def task_costs(rows):
    out = []
    for task in load_tasks():
        missing = [f for f in task["files"] if f not in rows]
        tokens = sum(rows[f]["tokens"] for f in task["files"] if f in rows)
        out.append({"task": task["task"], "tokens": tokens, "files": task["files"], "missing": missing})
    return out


def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    return m.group(1) if m else ""


def description_length(text):
    try:
        import yaml
    except ImportError:  # pragma: no cover - CI installs pyyaml
        return None
    data = yaml.safe_load(frontmatter(text)) or {}
    desc = data.get("description", "")
    return len(desc.strip()) if isinstance(desc, str) else None


FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})\s*([\w+-]*)")


def arguments_in_shell_blocks(text):
    """Line numbers where $ARGUMENTS appears inside a bash/sh fenced block.

    Harnesses that do not substitute $ARGUMENTS would run it literally.
    """
    hits, fence, lang = [], None, ""
    for i, line in enumerate(text.split("\n"), 1):
        m = FENCE.match(line)
        if fence is None:
            if m:
                fence, lang = m.group(1), m.group(2).lower()
            continue
        if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence) and not m.group(2):
            fence = None
            continue
        if lang in ("bash", "sh", "shell", "zsh", "") and "$ARGUMENTS" in line:
            hits.append(i)
    return hits


def check(rows):
    budgets = json.loads(BUDGETS.read_text())
    errors = []

    for skill, b in budgets["skills"].items():
        rel = f"{skill}/SKILL.md"
        if rel not in rows:
            errors.append(f"{rel}: listed in skill-budgets.json but not found")
            continue
        r = rows[rel]
        for key in ("words", "lines"):
            if r[key] > b[key]:
                errors.append(f"{rel}: {r[key]} {key}, budget {b[key]}")
        desc = description_length((SKILLS / rel).read_text())
        if desc is not None and desc > b["description"]:
            errors.append(f"{rel}: description {desc} characters, budget {b['description']}")
        if skill not in budgets.get("spec_exempt", []):
            if r["lines"] > SPEC_MAX_LINES:
                errors.append(f"{rel}: {r['lines']} lines, spec maximum {SPEC_MAX_LINES}")
            if r["tokens"] > SPEC_MAX_TOKENS:
                errors.append(f"{rel}: ~{r['tokens']} tokens, spec maximum {SPEC_MAX_TOKENS}")

    for rel in rows:
        if rel.endswith("/SKILL.md") and rel.split("/")[0] not in budgets["skills"]:
            errors.append(f"{rel}: no entry in skill-budgets.json")

    cap = budgets["reference_words_cap"]
    exceptions = budgets.get("reference_exceptions", {})
    for rel, r in rows.items():
        if group(rel) != "references (hand-written)" or not rel.endswith(".md"):
            continue
        name = rel[len(HUB_REFS):]
        limit = exceptions.get(name, cap)
        if r["words"] > limit:
            errors.append(f"{rel}: {r['words']} words, limit {limit}"
                          + ("" if name in exceptions else f" (reference cap {cap})"))
    for name, limit in exceptions.items():
        rel = HUB_REFS + name
        if rel not in rows:
            errors.append(f"skill-budgets.json: reference exception {name} names a file that does not exist")
        elif rows[rel]["words"] <= cap:
            errors.append(f"skill-budgets.json: {name} is now {rows[rel]['words']} words, under the cap; "
                          "remove its exception")

    allowed = set(budgets.get("arguments_in_shell_allowed", []))
    for rel in rows:
        if not rel.endswith("/SKILL.md"):
            continue
        hits = arguments_in_shell_blocks((SKILLS / rel).read_text())
        if hits and rel not in allowed:
            errors.append(f"{rel}: $ARGUMENTS inside a shell block (line {', '.join(map(str, hits))}); "
                          "describe the argument in prose and use a placeholder in the command")
        if not hits and rel in allowed:
            errors.append(f"skill-budgets.json: {rel} no longer has $ARGUMENTS in a shell block; "
                          "remove it from arguments_in_shell_allowed")

    for t in task_costs(rows):
        for f in t["missing"]:
            errors.append(f"task-paths.json: '{t['task']}' lists {f}, which does not exist")

    return errors


def summary(rows):
    groups = {}
    for rel, r in rows.items():
        g = groups.setdefault(group(rel), {"files": 0, "words": 0, "tokens": 0})
        g["files"] += 1
        g["words"] += r["words"]
        g["tokens"] += r["tokens"]
    print(f"{'part':28s} {'files':>5s} {'words':>8s} {'~tokens':>8s}")
    for name, g in sorted(groups.items()):
        print(f"{name:28s} {g['files']:5d} {g['words']:8d} {g['tokens']:8d}")
    print(f"{'total':28s} {len(rows):5d} {sum(r['words'] for r in rows.values()):8d} "
          f"{sum(r['tokens'] for r in rows.values()):8d}")
    print()
    print(f"{'SKILL.md':34s} {'words':>6s} {'lines':>6s} {'~tokens':>8s}")
    for rel, r in rows.items():
        if rel.endswith("/SKILL.md"):
            print(f"{rel:34s} {r['words']:6d} {r['lines']:6d} {r['tokens']:8d}")


def compare(rows, before_path):
    before = json.loads(Path(before_path).read_text())
    old = before["files"]
    changed = sorted(k for k in set(old) | set(rows) if old.get(k) != rows.get(k))
    zero = {"words": 0, "tokens": 0}
    print("| File | Words before | Words after | ~Tokens before | ~Tokens after |")
    print("|---|---:|---:|---:|---:|")
    tw = [0, 0, 0, 0]
    for k in changed:
        a, b = old.get(k, zero), rows.get(k, zero)
        tw = [tw[0] + a["words"], tw[1] + b["words"], tw[2] + a["tokens"], tw[3] + b["tokens"]]
        print(f"| `{k}` | {a['words']:,} | {b['words']:,} | {a['tokens']:,} | {b['tokens']:,} |")
    print(f"| **Changed files** | **{tw[0]:,}** | **{tw[1]:,}** | **{tw[2]:,}** | **{tw[3]:,}** |")
    all_old = sum(r["words"] for r in old.values())
    all_new = sum(r["words"] for r in rows.values())
    print(f"| **Whole pack** | **{all_old:,}** | **{all_new:,}** | "
          f"**{sum(r['tokens'] for r in old.values()):,}** | **{sum(r['tokens'] for r in rows.values()):,}** |")
    old_tasks = {t["task"]: t["tokens"] for t in before.get("tasks", [])}
    new_tasks = task_costs(rows)
    moved = [t for t in new_tasks if old_tasks.get(t["task"]) != t["tokens"]]
    if moved:
        print()
        print("| Task | ~Tokens before | ~Tokens after |")
        print("|---|---:|---:|")
        for t in moved:
            print(f"| {t['task']} | {old_tasks.get(t['task'], 0):,} | {t['tokens']:,} |")


def main(argv):
    rows = shipped_files()
    if "--json" in argv:
        out = Path(argv[argv.index("--json") + 1])
        out.write_text(json.dumps({"files": rows, "tasks": task_costs(rows)}, indent=1) + "\n")
        print(f"wrote {out}")
        return 0
    if "--compare" in argv:
        compare(rows, argv[argv.index("--compare") + 1])
        return 0
    if "--files" in argv:
        print(f"{'file':72s} {'words':>6s} {'lines':>6s} {'~tokens':>8s}")
        for rel, r in rows.items():
            print(f"{rel:72s} {r['words']:6d} {r['lines']:6d} {r['tokens']:8d}")
        return 0
    if "--tasks" in argv:
        for t in task_costs(rows):
            print(f"{t['tokens'] / 1000:6.1f}k  {t['task']}")
        return 0
    if "--check" in argv:
        errors = check(rows)
        for e in errors:
            print(f"✗ {e}")
        if errors:
            print(f"\n{len(errors)} budget violation(s). Shrink the file, or lower/raise the budget in "
                  "scripts/skill-budgets.json with a reason in the PR.")
            return 1
        print("✓ skill budgets, reference caps and task paths OK")
        return 0
    summary(rows)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
