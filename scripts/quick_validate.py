#!/usr/bin/env python3
"""
Quick validation script for skills - minimal version.

Usage:
    quick_validate.py <path>

Behavior depends on what <path> contains:
  - SKILL.md                                 → validate that one skill
  - .claude-plugin/plugin.json               → validate every SKILL.md under <path>/skills/
  - .claude-plugin/marketplace.json          → validate every plugin listed in the marketplace
  - otherwise                                → walk for SKILL.md files and validate each
"""

import json
import sys
import os
import re
import yaml
from pathlib import Path


def find_plugin_root(skill_path):
    """Walk up from a skill dir to find the enclosing plugin root.

    The plugin root is the directory containing `.claude-plugin/plugin.json`.
    Returns None if no plugin root is found before the filesystem root.
    """
    p = Path(skill_path).resolve()
    for candidate in [p, *p.parents]:
        if (candidate / ".claude-plugin" / "plugin.json").is_file():
            return candidate
    return None


FENCE_OPEN = re.compile(r'^ {0,3}(`{3,}|~{3,})')


def strip_fenced_blocks(content):
    """Return content with fenced code blocks blanked out, line by line.

    A fence opens with 3+ backticks or tildes (up to 3 spaces of indent) and
    closes with a line of the same character, at least as long. Blanking the
    lines keeps line numbers stable for callers that report them.
    """
    out = []
    fence = None
    for line in content.split('\n'):
        m = FENCE_OPEN.match(line)
        if fence is None:
            if m:
                fence = m.group(1)
                out.append('')
                continue
            out.append(line)
        else:
            if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence) \
                    and not line.strip()[len(m.group(1)):].strip():
                fence = None
            out.append('')
    return '\n'.join(out)


def strip_inline_code(text):
    """Remove inline code spans (`x`, ``x``) so links shown as code are ignored."""
    return re.sub(r'(`+)(?:(?!\1).)+?\1', '', text)


def find_markdown_links(content):
    """Extract all markdown links from content.

    Returns list of (link_text, link_path) tuples.
    Handles both [text](path) and [text](path#anchor) formats.
    Skips links inside fenced code blocks and inline code spans.
    """
    content_no_code = strip_inline_code(strip_fenced_blocks(content))
    # Match markdown links: [text](path) or [text](path#anchor)
    # Excludes image links which start with !
    pattern = r'(?<!!)\[([^\]]*)\]\(([^)\s]+)(?:\s+"[^"]*")?\)'
    matches = re.findall(pattern, content_no_code)
    return matches


def github_slug(heading):
    """Anchor GitHub generates for a heading (github-slugger rules).

    Lowercase; drop everything but letters, digits, underscores, hyphens and
    spaces; each space becomes a hyphen. "A — B" therefore slugs to "a--b".
    """
    text = heading.strip().lower()
    text = re.sub(r'!?\[([^\]]*)\]\([^)]*\)', r'\1', text)   # links/images -> text
    text = re.sub(r'<[^>]+>', '', text)                        # inline HTML
    text = re.sub(r'[^\w\- ]', '', text)
    return text.replace(' ', '-')


def heading_anchors(content):
    """Return the set of anchors a markdown file defines.

    Covers ATX headings outside fenced blocks (with GitHub's -1, -2 suffixes
    for repeats) and explicit HTML anchors (<a id="x"> / <a name="x">).
    """
    anchors = set()
    seen = {}
    for line in strip_fenced_blocks(content).split('\n'):
        m = re.match(r'^ {0,3}#{1,6}\s+(.*?)\s*#*\s*$', line)
        if m:
            slug = github_slug(m.group(1))
            if slug in seen:
                seen[slug] += 1
                anchors.add(f"{slug}-{seen[slug]}")
            else:
                seen[slug] = 0
                anchors.add(slug)
    for m in re.finditer(r'<a\s+(?:id|name)="([^"]+)"', content):
        anchors.add(m.group(1))
    return anchors


def is_external_link(path):
    """Check if a link is external (URL, mailto, etc.)."""
    external_prefixes = (
        'http://', 'https://', 'mailto:', 'tel:', 'ftp://',
        'javascript:', 'data:',
    )
    return path.lower().startswith(external_prefixes)


def should_skip_path(path):
    """Check if a path should be skipped during validation."""
    skip_dirs = {'node_modules', '.git', '__pycache__', '.venv', 'venv', 'dist', 'build'}
    parts = path.parts
    return any(part in skip_dirs for part in parts)


def check_dangling_references(skill_path, checked_files=None):
    """Check for dangling references in all markdown files.

    Cross-skill references inside the same plugin (resolved by walking up to the
    plugin root via `.claude-plugin/plugin.json`) are allowed — these are how
    spoke skills reach the hub's `references/` directory. A reference that
    escapes the plugin root entirely is reported as out-of-root.

    Anchors (`file.md#section`, `#section`) must match a heading in the
    target file, slugged the way GitHub renders it.

    Returns (dangling, out_of_root, bad_anchors) where each entry is
    (source_file, link_path, link_text).
    """
    if checked_files is None:
        checked_files = set()

    skill_path = Path(skill_path).resolve()
    plugin_root = find_plugin_root(skill_path) or skill_path
    dangling = []
    out_of_root = []
    bad_anchors = []
    anchor_cache = {}

    # Find all markdown files in the skill directory, excluding ignored dirs
    md_files = [f for f in skill_path.rglob('*.md') if not should_skip_path(f.relative_to(skill_path))]

    for md_file in md_files:
        if md_file in checked_files:
            continue
        checked_files.add(md_file)

        try:
            content = md_file.read_text()
        except Exception:
            continue

        links = find_markdown_links(content)

        for link_text, link_path in links:
            # Skip external links
            if is_external_link(link_path):
                continue

            # Split the anchor off for the file existence check
            file_path, _, anchor = link_path.partition('#')

            # Resolve relative to the markdown file's directory; an
            # anchor-only link points into the file itself
            resolved_path = (md_file.parent / file_path).resolve() if file_path else md_file

            # Get relative path from skill root for cleaner output
            try:
                source_rel = md_file.relative_to(skill_path)
            except ValueError:
                source_rel = md_file

            # Check if the reference escapes the plugin root.
            # Cross-skill references inside the plugin are fine.
            try:
                resolved_path.relative_to(plugin_root)
            except ValueError:
                out_of_root.append((str(source_rel), link_path, link_text))
                continue

            # Check if file or directory exists
            if not resolved_path.exists():
                dangling.append((str(source_rel), link_path, link_text))
                continue

            # Check the anchor against the target's headings
            if anchor and resolved_path.suffix == '.md' and resolved_path.is_file():
                if resolved_path not in anchor_cache:
                    anchor_cache[resolved_path] = heading_anchors(resolved_path.read_text())
                if anchor not in anchor_cache[resolved_path]:
                    bad_anchors.append((str(source_rel), link_path, link_text))

    return dangling, out_of_root, bad_anchors


def validate_skill(skill_path):
    """Basic validation of a skill"""
    skill_path = Path(skill_path)

    # Check SKILL.md exists
    skill_md = skill_path / 'SKILL.md'
    if not skill_md.exists():
        return False, "SKILL.md not found"

    # Read and validate frontmatter
    content = skill_md.read_text()
    if not content.startswith('---'):
        return False, "No YAML frontmatter found"

    # Extract frontmatter
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return False, "Invalid frontmatter format"

    frontmatter_text = match.group(1)

    # Parse YAML frontmatter
    try:
        frontmatter = yaml.safe_load(frontmatter_text)
        if not isinstance(frontmatter, dict):
            return False, "Frontmatter must be a YAML dictionary"
    except yaml.YAMLError as e:
        return False, f"Invalid YAML in frontmatter: {e}"

    # Allowed Claude Code skill frontmatter fields. See
    # https://code.claude.com/docs/en/skills for the canonical list. Includes
    # legacy `license` and `metadata` which the BorgIQ team has used historically,
    # and the Agent Skills spec's `compatibility` (environment requirements).
    ALLOWED_PROPERTIES = {
        'name', 'description', 'when_to_use', 'argument-hint', 'arguments',
        'disable-model-invocation', 'user-invocable', 'allowed-tools', 'model',
        'effort', 'context', 'agent', 'hooks', 'paths', 'shell',
        'license', 'metadata', 'compatibility',
    }

    # Check for unexpected properties (excluding nested keys under metadata)
    unexpected_keys = set(frontmatter.keys()) - ALLOWED_PROPERTIES
    if unexpected_keys:
        return False, (
            f"Unexpected key(s) in SKILL.md frontmatter: {', '.join(sorted(unexpected_keys))}. "
            f"Allowed properties are: {', '.join(sorted(ALLOWED_PROPERTIES))}"
        )

    # Check required fields
    if 'name' not in frontmatter:
        return False, "Missing 'name' in frontmatter"
    if 'description' not in frontmatter:
        return False, "Missing 'description' in frontmatter"

    # Extract name for validation
    name = frontmatter.get('name', '')
    if not isinstance(name, str):
        return False, f"Name must be a string, got {type(name).__name__}"
    name = name.strip()
    if name:
        # Check naming convention (hyphen-case: lowercase with hyphens)
        if not re.match(r'^[a-z0-9-]+$', name):
            return False, f"Name '{name}' should be hyphen-case (lowercase letters, digits, and hyphens only)"
        if name.startswith('-') or name.endswith('-') or '--' in name:
            return False, f"Name '{name}' cannot start/end with hyphen or contain consecutive hyphens"
        # Check name length (max 64 characters per spec)
        if len(name) > 64:
            return False, f"Name is too long ({len(name)} characters). Maximum is 64 characters."

    # Extract and validate description
    description = frontmatter.get('description', '')
    if not isinstance(description, str):
        return False, f"Description must be a string, got {type(description).__name__}"
    description = description.strip()
    if description:
        # Check for angle brackets
        if '<' in description or '>' in description:
            return False, "Description cannot contain angle brackets (< or >)"
        # Check description length (max 1024 characters per spec)
        if len(description) > 1024:
            return False, f"Description is too long ({len(description)} characters). Maximum is 1024 characters."

    # compatibility is optional; the spec caps it at 500 characters
    compatibility = frontmatter.get('compatibility')
    if compatibility is not None:
        if not isinstance(compatibility, str):
            return False, f"compatibility must be a string, got {type(compatibility).__name__}"
        if len(compatibility.strip()) > 500:
            return False, f"compatibility is too long ({len(compatibility.strip())} characters). Maximum is 500 characters."

    # Check for dangling / out-of-root references in all markdown files
    dangling, out_of_root, bad_anchors = check_dangling_references(skill_path)
    error_lines = []
    if out_of_root:
        error_lines.append("References outside skill root found:")
        for source_file, link_path, link_text in out_of_root:
            error_lines.append(f"  {source_file}: [{link_text}]({link_path})")
    if dangling:
        if error_lines:
            error_lines.append("")
        error_lines.append("Dangling references found:")
        for source_file, link_path, link_text in dangling:
            error_lines.append(f"  {source_file}: [{link_text}]({link_path})")
    if bad_anchors:
        if error_lines:
            error_lines.append("")
        error_lines.append("Anchors with no matching heading:")
        for source_file, link_path, link_text in bad_anchors:
            error_lines.append(f"  {source_file}: [{link_text}]({link_path})")
    if error_lines:
        return False, "\n".join(error_lines)

    return True, "Skill is valid!"

def validate_plugin_json(plugin_root):
    """Minimal plugin.json shape check. Returns (ok, message)."""
    plugin_json = Path(plugin_root) / ".claude-plugin" / "plugin.json"
    try:
        data = json.loads(plugin_json.read_text())
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return False, f"plugin.json invalid: {e}"
    if not isinstance(data, dict):
        return False, "plugin.json must be a JSON object"
    if not data.get("name"):
        return False, "plugin.json missing required 'name'"
    if not data.get("version"):
        return False, "plugin.json missing required 'version'"
    return True, f"plugin.json OK (name={data['name']}, version={data['version']})"


def validate_marketplace_json(marketplace_root):
    """Minimal marketplace.json shape check. Returns (ok, message)."""
    market_json = Path(marketplace_root) / ".claude-plugin" / "marketplace.json"
    try:
        data = json.loads(market_json.read_text())
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return False, f"marketplace.json invalid: {e}"
    if not isinstance(data, dict):
        return False, "marketplace.json must be a JSON object"
    for required in ("name", "owner", "plugins"):
        if required not in data:
            return False, f"marketplace.json missing required '{required}'"
    if not isinstance(data["plugins"], list) or not data["plugins"]:
        return False, "marketplace.json 'plugins' must be a non-empty array"
    return True, (
        f"marketplace.json OK (name={data['name']}, "
        f"{len(data['plugins'])} plugin(s))"
    )


def find_skill_dirs(root):
    """Return every directory under `root` that contains a SKILL.md."""
    root = Path(root)
    return sorted(p.parent for p in root.rglob("SKILL.md") if not should_skip_path(p.relative_to(root)))


def validate_target(target):
    """Dispatch based on what `target` contains.

    Returns (ok, [(label, ok, message), ...]) — one result per validated artifact.
    """
    target = Path(target).resolve()
    results = []

    is_skill = (target / "SKILL.md").is_file()
    is_plugin = (target / ".claude-plugin" / "plugin.json").is_file()
    is_market = (target / ".claude-plugin" / "marketplace.json").is_file()

    if is_market:
        ok, msg = validate_marketplace_json(target)
        results.append(("marketplace.json", ok, msg))
        # Recurse into each plugin listed in the marketplace. Claude Code resolves
        # a plugin's `source` relative to the marketplace/repo root (NOT any
        # `metadata.pluginRoot`), so resolve it the same way here.
        try:
            data = json.loads((target / ".claude-plugin" / "marketplace.json").read_text())
            for plugin_entry in data.get("plugins", []):
                source = plugin_entry.get("source", "")
                if isinstance(source, str) and source.startswith("./"):
                    plugin_dir = (target / source[2:]).resolve()
                    sub_ok, sub_results = validate_target(plugin_dir)
                    results.extend(sub_results)
        except Exception as e:
            results.append(("marketplace recursion", False, str(e)))

    if is_plugin:
        ok, msg = validate_plugin_json(target)
        results.append((f"{target.name}/plugin.json", ok, msg))
        for skill_dir in find_skill_dirs(target / "skills"):
            ok, msg = validate_skill(skill_dir)
            label = f"{target.name}/{skill_dir.relative_to(target / 'skills')}"
            results.append((label, ok, msg))

    if is_skill and not is_plugin:
        ok, msg = validate_skill(target)
        results.append((target.name, ok, msg))

    if not (is_skill or is_plugin or is_market):
        # Treat as a directory tree to walk for SKILL.md
        skill_dirs = find_skill_dirs(target)
        if not skill_dirs:
            results.append((str(target), False, "no SKILL.md or plugin/marketplace manifest found"))
        else:
            for skill_dir in skill_dirs:
                ok, msg = validate_skill(skill_dir)
                results.append((str(skill_dir.relative_to(target)), ok, msg))

    overall_ok = all(ok for _, ok, _ in results)
    return overall_ok, results


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python quick_validate.py <path>")
        print("  <path> can be a skill dir, a plugin dir, a marketplace repo, or any parent dir containing SKILL.md files.")
        sys.exit(1)

    ok, results = validate_target(sys.argv[1])
    pad = max((len(label) for label, _, _ in results), default=0)
    for label, sub_ok, msg in results:
        marker = "✓" if sub_ok else "✗"
        print(f"{marker} {label:<{pad}}  {msg}")
    sys.exit(0 if ok else 1)
    