---
name: release-please-commits
description: Use when writing commits or commit messages inside borgiq-skills. This repo publishes `@borgiq/skills` to npm and the Claude Code plugin marketplace via release-please, which parses conventional commits on `main` to decide version bumps and CHANGELOG entries. A wrongly-typed or vague commit silently produces a wrong version or omits the change from the changelog.
---

# Writing commits in borgiq-skills

> **The format lives in [CONTRIBUTING.md](../../../CONTRIBUTING.md) ("Commit / PR title format") and [AGENTS.md](../../../AGENTS.md) ("Versioning and releases").** Read those first for the type table and bump rules. This skill only covers commit-specific guidance on top of them.

## What actually ends up on `main`

The repo is configured to **squash-merge** PRs with "Pull request title and description" as the default commit message. That means:

- The **only commit release-please sees** is the squashed commit on `main`.
- Its **subject = the PR title**.
- Its **body = the PR description**.
- Every intermediate commit you make on the feature branch is **discarded** by the squash.

Practical implication: **feature-branch commits don't need to be perfect.** Use them as save points. `wip`, `fix typo`, `address review` — all fine. Don't waste effort polishing them.

What you *do* need to get right is **the PR title** (and the PR description, if it carries `BREAKING CHANGE:` or `Refs:` footers). For PR-creation guidance see the sibling `release-please-prs` skill.

## Type quick reference (skills-specific)

- `feat:` — new spoke, new slash command, new auto-loaded skill (minor bump).
- `fix:` — bug or correctness fix in an existing skill's content (patch bump).
- `feat!:` / `BREAKING CHANGE:` footer — skill or command **renames or removals** (major bump — these break installed users).
- `docs:` / `chore:` / `ci:` / `test:` — no bump, hidden from CHANGELOG. Note: most reference-doc edits that change what an agent will *do* are `fix:` (they alter skill behavior), not `docs:` — reserve `docs:` for README/CONTRIBUTING-style repo docs.
- Scope from the skill or area touched: `feat(form-builder): …`, `fix(borgiq-builder): …`, `chore(installer): …`.

## When to use a conventional commit message anyway

The *only* commit message that matters for release-please is the one GitHub generates from your PR title + description at squash time. Never commit directly to `main` (only release-please's own PRs do that).

## Helping the PR title later

If you're committing on a feature branch, a useful habit:

- Make the **first commit's subject** read like the PR title you intend (e.g. `feat(form-builder): document conditional field groups`). When you later open the PR, `gh pr create` will pre-fill the title from that commit subject.
- Put the *why* in that commit's body — same content you'd want in the PR description.

This is purely ergonomic; release-please doesn't care.

## Don't

- Don't bump version fields by hand — release-please owns **all three** version locations (`package.json`, `plugins/borgiq-builder/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`) plus `.release-please-manifest.json`, kept in lockstep via `extra-files`.
- Don't include `BREAKING CHANGE:` footers in feature-branch commits expecting them to survive the squash — put the footer in the **PR description** instead, where it's authoritative.
- Don't run `git commit --amend` on commits already pushed to a shared branch.

## See also

- [CONTRIBUTING.md](../../../CONTRIBUTING.md) — release process for humans (staged publish + 2FA approval)
- `.claude/skills/release-please-prs/SKILL.md` — sibling skill for PR creation
