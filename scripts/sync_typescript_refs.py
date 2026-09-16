#!/usr/bin/env python3
"""
Sync the TypeScript reference mirrors from the BorgIQ platform's prompt type files.

Usage:
    sync_typescript_refs.py [--platform <path>] [--check]

The files under
  plugins/borgiq-builder/skills/borgiq-builder/references/typescript/*.md
mirror the platform's
  packages/core/src/prompts/typeFiles/runtime-types/src/<path>.txt
section by section. Each section is:

    ## <path without .ts>

    **Source:** `<path>.ts`

    ```typescript
    <contents of <path>.txt, trailing blank lines trimmed>
    ```

The section list is read from the existing `**Source:**` lines, so this script only refreshes
the fenced bodies: it never adds or drops a section. A section whose `.txt` no longer exists in
the platform (or whose heading does not match its source) is reported as an error; nothing is
written while any error remains.

The platform checkout defaults to $BORGIQ_PLATFORM_PATH, else a sibling `../borgiq-platform`
next to this repository. `--check` writes nothing and exits 1 when any section has drifted
(listing each one), 0 when every mirror is current.
"""

import argparse
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MIRROR_DIR = REPO_ROOT / "plugins" / "borgiq-builder" / "skills" / "borgiq-builder" / "references" / "typescript"
TYPE_FILES_SUBPATH = Path("packages") / "core" / "src" / "prompts" / "typeFiles" / "runtime-types" / "src"

SOURCE_LINE = re.compile(r"^\*\*Source:\*\* `([^`]+\.ts)`$", re.MULTILINE)
HEADING_LINE = re.compile(r"^## (.+)$", re.MULTILINE)
FENCE_OPEN = "```typescript\n"
FENCE_CLOSE = "\n```"


def default_platform_path():
    env = os.environ.get("BORGIQ_PLATFORM_PATH")
    if env:
        return Path(env)
    return REPO_ROOT.parent / "borgiq-platform"


def mirror_body(txt):
    """The fenced body for a type file: its contents with trailing blank lines trimmed."""
    return txt.rstrip("\n") + "\n"


def sync_file(md_path, type_files_root):
    """Rebuild one mirror file.

    Returns (new_content, drifted_sources, errors). `new_content` is None when there are errors.
    """
    content = md_path.read_text(encoding="utf-8")
    sources = list(SOURCE_LINE.finditer(content))
    drifted = []
    errors = []
    pieces = []
    cursor = 0

    for i, match in enumerate(sources):
        source = match.group(1)
        label = f"{md_path.name}: {source}"

        # The section's heading is the last `## ` line before its Source line.
        headings = list(HEADING_LINE.finditer(content, cursor if i == 0 else sources[i - 1].end(), match.start()))
        expected_heading = source[: -len(".ts")]
        if not headings or headings[-1].group(1).strip() != expected_heading:
            found = headings[-1].group(1).strip() if headings else "(none)"
            errors.append(f"{label}: heading '{found}' does not match the source (expected '## {expected_heading}')")

        # The section ends where the next section's heading starts (or at end of file).
        if i + 1 < len(sources):
            next_headings = list(HEADING_LINE.finditer(content, match.end(), sources[i + 1].start()))
            region_end = next_headings[-1].start() if next_headings else sources[i + 1].start()
        else:
            region_end = len(content)

        open_at = content.find(FENCE_OPEN, match.end(), region_end)
        close_at = content.rfind(FENCE_CLOSE, match.end(), region_end)
        if open_at == -1 or close_at == -1 or close_at < open_at + len(FENCE_OPEN) - 1:
            errors.append(f"{label}: no ```typescript block found in the section")
            continue
        body_start = open_at + len(FENCE_OPEN)
        body_end = close_at + 1  # keep the body's final newline inside the body

        txt_path = type_files_root / (expected_heading + ".txt")
        if not txt_path.is_file():
            errors.append(f"{label}: source no longer exists in the platform ({txt_path})")
            continue

        new_body = mirror_body(txt_path.read_text(encoding="utf-8"))
        if content[body_start:body_end] != new_body:
            drifted.append(source)
        pieces.append(content[cursor:body_start])
        pieces.append(new_body)
        cursor = body_end

    pieces.append(content[cursor:])
    if not sources:
        errors.append(f"{md_path.name}: no **Source:** sections found")
    return (None if errors else "".join(pieces)), drifted, errors


def main():
    parser = argparse.ArgumentParser(description="Sync references/typescript/*.md from the platform's prompt type files.")
    parser.add_argument(
        "--platform",
        type=Path,
        default=None,
        help="Path to a borgiq-platform checkout (default: $BORGIQ_PLATFORM_PATH, else ../borgiq-platform)",
    )
    parser.add_argument("--check", action="store_true", help="Report drifted sections and exit 1 without writing")
    args = parser.parse_args()

    platform = (args.platform or default_platform_path()).resolve()
    type_files_root = platform / TYPE_FILES_SUBPATH
    if not type_files_root.is_dir():
        print(f"❌ Platform type files not found: {type_files_root}", file=sys.stderr)
        print("   Pass --platform <path> or set BORGIQ_PLATFORM_PATH.", file=sys.stderr)
        sys.exit(2)

    md_files = sorted(p for p in MIRROR_DIR.glob("*.md") if p.name != "index.md")
    all_errors = []
    results = []
    section_count = 0
    for md_path in md_files:
        new_content, drifted, errors = sync_file(md_path, type_files_root)
        section_count += len(SOURCE_LINE.findall(md_path.read_text(encoding="utf-8")))
        all_errors.extend(errors)
        results.append((md_path, new_content, drifted))

    if all_errors:
        for error in all_errors:
            print(f"❌ {error}", file=sys.stderr)
        print(f"\n{len(all_errors)} error(s); nothing written.", file=sys.stderr)
        sys.exit(1)

    drifted_total = sum(len(d) for _, _, d in results)
    for md_path, new_content, drifted in results:
        for source in drifted:
            print(f"{'drifted' if args.check else 'updated'}: {md_path.name}: {source}")
        if drifted and not args.check:
            md_path.write_text(new_content, encoding="utf-8")

    if args.check:
        if drifted_total:
            print(f"\n❌ {drifted_total} of {section_count} section(s) out of date. Run scripts/sync_typescript_refs.py to update.")
            sys.exit(1)
        print(f"✅ All {section_count} sections match {type_files_root}")
        sys.exit(0)

    print(f"\n✅ {drifted_total} of {section_count} section(s) updated from {type_files_root}")
    sys.exit(0)


if __name__ == "__main__":
    main()
