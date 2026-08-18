---
name: release-please-prs
description: Use when opening, editing, or retitling pull requests in borgiq-skills (including `gh pr create`, `gh pr edit --title`, PR title suggestions, and PR description drafts). This repo squash-merges PRs, so the PR title becomes the commit subject release-please parses on `main` — a non-conventional title silently breaks the next release's version bump and CHANGELOG.
---

# Opening PRs in borgiq-skills

> **The format lives in [CONTRIBUTING.md](../../../CONTRIBUTING.md) ("Commit / PR title format") and [AGENTS.md](../../../AGENTS.md) ("Versioning and releases").** Read those first for the type table and bump rules. This skill only covers PR-specific guidance on top of them.

## Why PR titles matter so much in this repo

The repo squash-merges with "Pull request title and description" as the default commit message format. So when a PR merges:

- **PR title → squashed commit subject on `main`** (this is what release-please parses for `<type>(<scope>): <subject>`)
- **PR description → squashed commit body on `main`** (this is what release-please scans for `BREAKING CHANGE:` and `Refs:` footers)
- **Feature-branch commits → discarded** (release-please never sees them)

There is no fallback. If the PR title isn't a conventional commit, release-please ignores the change entirely — no version bump, no CHANGELOG entry, and installed users never get the update through npm.

## PR title

**The PR title must be a conventional commit by itself.** Quick reminders specific to PRs:

- Don't append `(#42)` — GitHub adds the PR number automatically to the squash commit subject; never bake it into the title yourself.
- Don't prefix with `Draft:` or `WIP:` — use GitHub's "Mark as draft" button instead. A `WIP:` prefix breaks conventional-commit parsing.
- If your PR genuinely contains two unrelated changes that need different types (e.g. one `feat:` and one `fix:`), **split it into two PRs**. The squash collapses them into a single commit with a single type.
- Renaming or removing a skill or command is a **breaking change** for installed users — title it `feat!:` or carry a `BREAKING CHANGE:` footer in the description.

## PR description (body)

The PR description ends up as the body of the squashed commit, which means release-please reads it for footers. Structure it like this:

```
## Summary
<1–3 bullets on what changed and why>

## Test plan
- [ ] python3 scripts/quick_validate.py .
- [ ] <anything else you validated>

<optional footers at the bottom>
BREAKING CHANGE: <description if applicable>
Refs: #123
```

Footers must be at the very end of the body, on their own lines, in the standard `Token: value` format. Don't bury them inside prose.

## This repo is public

Never reference private BorgIQ repositories, internal documentation, ticket identifiers, or internal hostnames in **anything public-visible**: files, commit messages, the PR title/body, or the **branch name**.

## `gh pr create` recipe

```bash
gh pr create \
  --title "feat(form-builder): document conditional field groups" \
  --body "$(cat <<'EOF'
## Summary
- Documents conditional visibility groups in the form-builder spoke …

## Test plan
- [ ] python3 scripts/quick_validate.py .

Refs: #42
EOF
)"
```

Use a heredoc for the body so newlines and bullet points are preserved.

## Retitling an existing PR

```bash
gh pr edit <PR#> --title "fix(borgiq-builder): correct webhook trigger config shape"
```

Do this *before* the squash-merge. After merge, the squashed commit on `main` is what release-please reads — fixing the PR title retroactively does nothing.

## Edge cases

- **The release-please PR itself** is titled `chore(main): release X.Y.Z`. Never rewrite it — release-please uses this title to find its own PR on subsequent runs. Merging it stages an npm publish that still needs a maintainer's 2FA approval (see [CONTRIBUTING.md](../../../CONTRIBUTING.md)).
- **PRs that introduce *and* fix something in one go**: use the higher-priority type. `feat:` outranks `fix:`. The fix-line goes in the body bullets.
- **Reverts**: GitHub auto-generates revert PR titles as `Revert "feat(…): …"`. Edit to a conventional `revert(…):` title (or `chore:` for silent reverts).
- **Dependabot PRs**: dependabot.yml is configured with `prefix: ci` for action bumps — already parseable.

## Don't

- Don't merge a PR with a non-conventional title — the change won't appear in the next release.
- Don't squash-merge by hand at the terminal (`gh pr merge --squash` is fine; `git merge --squash` locally and pushing main is not).
- Don't put `BREAKING CHANGE:` in the PR title alone hoping it gets picked up — put it as a footer in the description.

## See also

- [CONTRIBUTING.md](../../../CONTRIBUTING.md) — release process for humans (staged publish + 2FA approval)
- `.claude/skills/release-please-commits/SKILL.md` — sibling skill for commits
