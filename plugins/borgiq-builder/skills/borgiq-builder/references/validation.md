# Actor ID Generation and Validation

This document covers generating actor IDs, msgVars, and validating/post-processing workflow YAML.

## Table of Contents

- [Actor ID and msgVar Generation](#actor-id-and-msgvar-generation)
- [Validation](#validation)
- [Post-Processing](#post-processing)
- [Complete Workflow](#complete-workflow)

## Actor ID and msgVar Generation

Generate a unique actor ID and msgVar before building the actor.

ID and msgVar generation ship as `borgiq generate` in the `@borgiq/cli`. These are **offline** commands — they need no API token and no dependency install. If `borgiq` is missing, install it with `npm install -g @borgiq/cli`.

**Generate IDs and msgVar:**
```bash
# Generate actor ID (30-character ULID)
borgiq generate id actor
# Output: ACTR01kcsnjnkqa69w50qr60dcd06e

# Generate edge ID (30-character ULID)
borgiq generate id edge
# Output: EDGE01kd6gqx5k7tvzs86y40w8etms

# Generate source port ID (11-character: SPRT + 7 random chars)
borgiq generate id sourceport
# Output: SPRT5d5gj2s

# Generate webhook trigger key (26-character ULID, required for WebhookTriggerActor)
borgiq generate id webhooktriggerkey
# Output: 01KD298E3VRBDAZN9X5ETV4R6G

# Generate msgVar from actor name
borgiq generate msgvar "Fetch user profile from Gmail"
# Output: fetch_user_profile_from_gmail
```

**When to generate source port IDs:**
- RouterActor and AiRouterActor require custom source ports for conditional routing
- Use `SPRTdefault` for the fallback/default port (no generation needed)
- Generate a new source port ID for each named condition (e.g., Success, Error, Create, Update)

**Workflow:**
1. Decide on the actor name (e.g., "Extract structured data from URLs via Firecrawl")
2. Generate the actor ID using `borgiq generate id actor`
3. Generate the msgVar using `borgiq generate msgvar` with the actor name
4. For RouterActor/AiRouterActor: generate source port IDs using `borgiq generate id sourceport`
5. For WebhookTriggerActor: generate a webhook trigger key using `borgiq generate id webhooktriggerkey`
6. Generate edge IDs using `borgiq generate id edge` for each connection
7. Build the actor YAML with the generated IDs

## Validation

**IMPORTANT:** Always validate and post-process generated or edited YAML before presenting it to the user.

```bash
# From file
borgiq validate actor.yaml

# From stdin
cat actor.yaml | borgiq validate

# Skip TypeScript validation for DenoActor code (faster)
borgiq validate actor.yaml --skip-typecheck
```

Code typechecking (DenoActor/PythonActor) runs only when `deno` / `python3` are installed; otherwise it is skipped with a warning. Exit code is non-zero when the workflow is invalid.

**Validation checks:**
- YAML syntax and structure
- Required fields (type, name, msgVar, configuration)
- Actor ID format (`ACTR` + 26 lowercase alphanumeric chars)
- Edge ID format (`EDGE` + 26 lowercase alphanumeric chars)
- Source port ID format (`SPRT` + 7 lowercase alphanumeric chars or `SPRTdefault`)
- Actor-specific options (HttpRequestActor, DenoActor, MessageProcessorActor, etc.)
- TypeScript/JavaScript syntax for DenoActor code
- Memory requirements (enableLTM/enableSTM for specific actions)
- Edge consistency (source/target actor IDs, port IDs)

## Post-Processing

After validation, run the post-processing command to clean up unnecessary fields:

```bash
# Post-process and output to stdout
borgiq validate actor.yaml --post-process

# Post-process and modify file in place
borgiq validate actor.yaml --post-process --in-place
borgiq validate actor.yaml --post-process -i

# From stdin
cat actor.yaml | borgiq validate --post-process
```

**Post-processing transformations:**
- Removes `label` from edges for non-router actors (only AiRouterActor and RouterActor use edge labels)
- Ensures consistent YAML formatting

## Complete Workflow

1. Generate or edit the YAML
2. Write to a file
3. Run `borgiq validate <file>` - fix any errors
4. Run `borgiq validate <file> --post-process -i` - clean up the file
5. Present the validated and cleaned YAML to the user
