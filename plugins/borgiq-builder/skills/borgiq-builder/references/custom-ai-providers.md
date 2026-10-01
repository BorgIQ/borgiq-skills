# Custom AI Providers

A **custom provider** is any AI provider, gateway/router, or self-hosted server that is **OpenAI-compatible** or uses
the **OpenAI chat completions schema** (the [vendor table](#1-connection-the-key-and-base-url) lists the common ones,
Azure OpenAI's `/openai/v1` surface included), added to a workspace under its own slug; a workspace can add as many as
it needs. Read it to set one up and to debug its errors. The AI actor, AI Agent actor and AI Router actor run its models as `<slug>/<model-id>`; the
reference forms and per-actor rules are in [ai-models.md](ai-models.md).

## Contents

- [How a custom provider is identified](#how-a-custom-provider-is-identified)
- [Setting one up](#setting-one-up)
- [Using the models in actors](#using-the-models-in-actors)
- [Troubleshooting](#troubleshooting)

## How a custom provider is identified

Each custom provider has a **slug**: a short kebab-case name such as `fireworks`, `openrouter` or `my-vllm`, of
lowercase letters, digits and dashes, starting with a letter or digit, at most 40 characters, and never a built-in
provider id (`openai`, `anthropic`, `google`, `xai`, `custom`, `claude-code`, `codex`, …). The slug is the first segment
of the provider's model references:

```
<slug>/<model-id>
fireworks/accounts/fireworks/models/llama-v3p1-70b-instruct
openrouter/moonshotai/kimi-k2
groq/llama-3.3-70b-versatile
my-vllm/qwen2.5-coder:7b
```

Only the **first** `/` splits the slug from the model id, so nested ids (Fireworks' `accounts/…`, OpenRouter's
`vendor/model`) pass through untouched. The same model id may exist under two slugs: `fireworks/llama` and
`groq/llama` are two different models with their own pricing. A built-in model id served through a gateway is
referenced explicitly (`openrouter/gpt-4o-mini`) and keeps GPT-4o mini's label, pricing and limits (a catalog entry can
override them); a bare `gpt-4o-mini` always goes to the workspace's OpenAI credential.

## Setting one up

### 1. Connection (the key) and base URL

A custom provider takes its key from a connection and its base URL from the first of:

1. **its own override**, set on the provider (`--base-url`, or the Base URL field in the web app);
2. **the connection's base URL**, the connection's optional `baseUrl` input when filled in (for a
   `custom-provider-apikey` connection this input is required and *is* the endpoint);
3. **the connection type's vendor default**.

| Vendor | Connection type | Base URL (vendor default) | Notes |
|--------|-----------------|---------------------------|-------|
| Groq | `groq-bearer` | `https://api.groq.com/openai/v1` | Tool calling and JSON schema supported |
| Fireworks | `fireworks-bearer` | `https://api.fireworks.ai/inference/v1` | Model ids are `accounts/fireworks/models/<name>`; your own deployments are `accounts/<account>/models/<name>` |
| Together | `together-bearer` | `https://api.together.ai/v1` | `thinkingFormat: "together"` for reasoning models on the AI Agent; `api.together.xyz` is the legacy host |
| OpenRouter | `openrouter-bearer` | `https://openrouter.ai/api/v1` | Model ids are `vendor/model`; optional `extraHeaders` for `HTTP-Referer` / `X-OpenRouter-Title`; `compat: { thinkingFormat: "openrouter" }` for reasoning |
| Mistral | `mistral-bearer` | `https://api.mistral.ai/v1` | |
| DeepSeek | `deepseek-bearer` | `https://api.deepseek.com` | No `/v1`; reasoning models: `reasoning: true`, `compat: { thinkingFormat: "deepseek" }` |
| Cerebras | `cerebras-bearer` | `https://api.cerebras.ai/v1` | Do not combine `tools` with `response_format` |
| DeepInfra | `deepinfra-bearer` | `https://api.deepinfra.com/v1/openai` | |
| Perplexity | `perplexity-bearer` | `https://api.perplexity.ai` | No `/v1`; Sonar chat completions are superseded by Perplexity's Agent API |
| Cohere | `cohere-bearer` | `https://api.cohere.ai/compatibility/v1` | Cohere's OpenAI-compatible Compatibility API; ids like `command-a-03-2025` |
| Hugging Face | `huggingface-bearer` | `https://router.huggingface.co/v1` | HF token with the Inference Providers permission; ids are `org/model`, optionally `:provider` |
| OpenAI, xAI | `openai-bearer`, `xai-bearer` | `https://api.openai.com/v1`, `https://api.x.ai/v1` | The built-in providers' types, usable behind a custom provider (e.g. with a gateway base URL) |
| Moonshot / Kimi | `custom-provider-apikey` | `https://api.moonshot.ai/v1` | Thinking variants: `reasoning: true` |
| Z.ai / GLM | `custom-provider-apikey` | `https://api.z.ai/api/paas/v4` | `reasoning: true`, `compat: { thinkingFormat: "zai" }` |
| LiteLLM / LLMGateway / Portkey | `custom-provider-apikey` | the gateway's `/v1` | One slug fronts many upstreams |
| Azure OpenAI | `custom-provider-apikey` or `generic-api-key` | `https://<resource>.openai.azure.com/openai/v1` | Bearer key, or the `api-key` header via a generic API-key connection (never in `extraHeaders`) |
| Ollama / vLLM / LM Studio / llama.cpp | `custom-provider-apikey` | the server's `/v1` (default ports 11434, 8000, 1234, 8080) at a public `https://` address | Keyless servers work, but only at a public address |
| Any other OpenAI-compatible endpoint | `custom-provider-apikey` | its required `baseUrl` input | Optional key (keyless self-hosted servers, at a public address); optional non-secret `extraHeaders` |
| Any | `generic-bearer-token`, `generic-api-key` | none: set `--base-url` | A generic API-key connection sends the key in the header it names (e.g. `x-api-key`) instead of `Authorization: Bearer` |

Other connection types (OAuth, custom auth, …) are refused with a 400. A generic API-key connection must send its key
**in a header**: one with "Add to Header" switched off (the key as a query parameter) is refused when the provider is
saved, and at run time. The `extraHeaders` input is for **non-secret** headers only (OpenRouter's `HTTP-Referer` /
`X-OpenRouter-Title`); never put a credential there. A vendor that authenticates with a named header (Azure's `api-key`)
uses a `generic-api-key` connection instead.

```bash
# A vendor connection: only the key is needed
cat > secret.json <<'JSON'
{ "apiKey": "gsk_..." }
JSON
borgiq connections create --key groq --type groq-bearer --secret-inputs-file secret.json

# A custom-provider connection for anything else: base URL + optional key
cat > inputs.json <<'JSON'
{ "baseUrl": "https://llm.example.com/v1" }
JSON
borgiq connections create --key my-vllm --type custom-provider-apikey --inputs-file inputs.json --secret-inputs-file secret.json
```

#### The base URL must be publicly reachable

Every LLM call to a custom provider goes out from BorgIQ's cloud, so its base URL is checked against server-side
request forgery, when the provider is saved (the `--base-url` override) and again on the effective base URL at every
run:

- it must use `https://`;
- a host that is, or resolves through DNS to, a private (`10.x`, `172.16–31.x`, `192.168.x`), link-local, CGNAT or
  cloud-metadata (`169.254.169.254`) address is refused, and so is an internal DNS name that resolves to one;
- a hostname that fails to resolve is refused;
- `localhost` / loopback (and `http://`) are accepted only in local development.

A refused override is a 400 at save: `Base URL "<url>" is not allowed: <reason>`. A self-hosted server (Ollama, vLLM,
LM Studio, llama.cpp, SGLang, TGI) therefore needs a public address, for example behind an HTTPS reverse proxy.
Private-network endpoints are not supported.

### 2. Custom provider (slug + connection + catalog)

In the web app: **Workspace settings → AI settings → Custom providers → Add custom provider**, or with the CLI
(`@borgiq/cli` >= 0.12.0):

```bash
# On a vendor connection the base URL is filled in from the connection type
borgiq ai-providers create --provider custom --name groq --connection groq --models llama-3.3-70b-versatile

# On a generic bearer / API-key connection, give the base URL (a public https:// address)
borgiq ai-providers create --provider custom --name my-vllm --connection my-vllm-key \
  --base-url https://vllm.example.com/v1 --models qwen2.5-coder:7b

# Later
borgiq ai-providers edit groq --add-model llama-3.1-8b-instant
borgiq ai-providers edit groq --base-url https://gateway.example/groq/v1   # route through a gateway
borgiq ai-providers edit groq --no-base-url                                # back to the connection's / vendor default
borgiq ai-providers list                 # shows the effective base URL of each custom provider
borgiq ai-providers models --custom      # every <slug>/<model-id> reference ready to paste
borgiq ai-providers delete groq -y
```

`--models` takes a comma-separated list of model ids. `--name` is required for a custom provider (its slug has no default). Renaming or deleting a custom provider does
**not** rewrite the `<slug>/<model-id>` references in canvases, and is not blocked by them: the web app and the CLI
(`edit --name`, `delete`) warn with the canvases that reference the provider, then proceed. Those actors fail at run
time until their `model` is fixed. In the web app, picking a vendor connection prefills the provider's name
(`groq-bearer` → `groq`) and shows the base URL it will use; type one only to override it.

### 3. Model catalog

The catalog lists the models the endpoint serves. Only `id` is required; the other fields refine pricing, limits and
behaviour:

| Field | Default | Meaning |
|-------|---------|---------|
| `id` | — | The model id sent to the endpoint |
| `label` | the id | Label in the model dropdown |
| `contextWindow` | 128000 | Context window in tokens (pi's compaction budget for the AI Agent) |
| `maxTokens` | 8192 | Maximum output tokens |
| `reasoning` | false | The model supports extended thinking; required for `thinkingLevel` on the AI Agent to have an effect |
| `supportsImages` | false | Accepts image input |
| `structuredOutputs` | true | The endpoint accepts `response_format: json_schema`; set `false` for servers that only do prompt-based JSON (the AI actor then falls back to text + repair) |
| `agent` | true (omitted) | `false` hides the model from the AI Agent's suggestions (`false` in the `AGENT` column of `borgiq ai-providers models`) and the AI Agent refuses it at run time; the AI actor and AI Router still use it |
| `costPerMTokens` | `{ input: 0, output: 0 }` | USD per million tokens, for the AI usage log |
| `compat` | — | pi OpenAI-completions compatibility overrides for the AI Agent (`supportsDeveloperRole`, `maxTokensField`, `thinkingFormat`, …) |

```json
[
  { "id": "llama-3.3-70b-versatile", "label": "Llama 3.3 70B", "maxTokens": 32768,
    "costPerMTokens": { "input": 0.59, "output": 0.79 } },
  { "id": "deepseek-r1-distill-llama-70b", "reasoning": true,
    "compat": { "thinkingFormat": "deepseek" } },
  { "id": "llama-3.1-8b-instant", "agent": false }
]
```

```bash
borgiq ai-providers create --provider custom --name groq --connection groq --models-file groq-models.json
```

A model that is not in the catalog still runs (`groq/some-new-model`) with default limits and zero cost; the catalog is
what makes it show up in the dropdown, priced and labelled.

## Using the models in actors

```yaml
type: AiActor
configuration:
  options:
    model: fireworks/accounts/fireworks/models/llama-v3p1-70b-instruct
    prompt: ${{ inputs.text }}
```

```yaml
type: AiAgentActor
configuration:
  options:
    model: openrouter/moonshotai/kimi-k2
    thinkingLevel: off      # unless the catalog entry says reasoning: true
    prompt: ${{ inputs.task }}
```

Both actors call the endpoint from BorgIQ's cloud, so a server on your own machine or private network needs a public
address (see [the base URL rules](#the-base-url-must-be-publicly-reachable)). A custom provider needs an effective base
URL: an AI Agent segment on a provider with none is refused before it is dispatched. The AI Agent's runtime logs name
the provider `custom:<slug>`; canvases always reference `<slug>/<model-id>`.

## CLI output and errors

Flags: `borgiq ai-providers <command> --help`. What the output means:

- `list [--provider <id>] --json`: an array of settings, built-in provider credential links (`name` is the provider)
  and custom providers (`provider: custom`, `name` is the slug), with `id`, `connectionId`, `connectionMissing` and
  `modelCount` (entries in `data.models`; the table's `MODELS`). `connectionMissing: true` means the linked connection
  was deleted, so the models cannot resolve until `ai-providers edit <name> --connection <key>`. A custom row also has
  `effectiveBaseUrl` (the setting's `data.baseURL` override, else `derivedBaseUrl`: the connection's own base URL, else
  the connection type's vendor default; absent when nothing supplies one; the table's `BASE URL`) and `baseUrlSource`
  (`setting`, `connection` or `connectionType`).
- `models [--custom] [--provider <id-or-slug>] --json`: a top-level array of `{ ref, label, provider, group, custom,
  agent }`, the known models and then each custom catalog as `<slug>/<model-id>`. A built-in provider's unlisted
  `<provider>/<model-id>` works in actors but is not listed. `agent` (the `AGENT` column) says whether the model may
  drive an AI Agent actor: a known model when the AI Agent's curated list has it, a catalog model unless its entry says
  `agent: false`.
- `create --provider openai --connection <key>` links a built-in provider's connection (the name defaults to the
  provider id). A custom provider created with no models gets a warning: actors cannot use it until its catalog is
  filled.
- `edit` sends a full replacement, resending unchanged parts; with no flags it prints `Nothing to update.` and sends
  nothing. `--data-file` replaces the whole non-secret `data` object and warns when that replaces a catalog.
- `delete <name> -y` (or `--force`).

| Situation | Result |
|---|---|
| A custom-only flag (`--base-url`, `--no-base-url`, `--models`, `--models-file`, `--add-model`, `--remove-model`) on a built-in provider | Usage error, exit 2: `<flag> applies to custom providers only …` |
| `--provider custom` without `--name`, not interactive | Usage error, exit 2: `--name is required for a custom provider.` |
| `--base-url` with `--no-base-url`, `--connection` with `--no-connection`, or `--models` with `--models-file` | Usage error, exit 2: `Use either … not both.` |
| `--connection` names a key that does not exist | Usage error, exit 2: `Connection '<x>' not found. …` |
| `models --provider <x>` matches nothing | `No provider named '<x>'. …` on stderr |
| `edit` / `delete` names no provider | Not found, exit 5: `AI provider '<x>' not found in workspace. …` |
| `edit --name` or `delete` of a provider canvases reference | Proceeds after a stderr warning naming them: `Warning: <n> canvas(es) reference this provider (<names>) — their "<slug>/<model-id>" models will stop resolving after the rename` (or `delete`) |

## Troubleshooting

| Symptom | Cause / fix |
|---------|-------------|
| `Unknown model "…"` on save | A bare id that is not a known model: use `<slug>/<model-id>` |
| `Model "x/y" does not exist: no custom provider named "x" …` at run time | No provider with slug `x` (renamed, deleted, or never added); check `borgiq ai-providers list`. The editor and `borgiq canvases validate` only warn: `Model "x/y" references custom provider "x", which does not exist in this workspace` |
| `Use a short kebab-case name for a custom provider` | The slug breaks the [slug rules](#how-a-custom-provider-is-identified) |
| `Base URL "<url>" is not allowed: <reason>` on save | The override breaks the [base URL rules](#the-base-url-must-be-publicly-reachable): use a public `https://` address |
| `Custom provider "x": its base URL is not allowed: …` at run time | The same check on the effective base URL (the connection's or vendor default included) |
| `A custom provider needs the API key in a header; this connection sends it as a query parameter.` on save, or `Custom provider "x": its connection sends the API key as a query parameter; …` at run time | The generic API-key connection has "Add to Header" off. Switch it on, or use a bearer connection |
| `Custom provider "x" has no base URL: set one on the provider, on its connection, or re-import the connection type.` (AI Agent), or `Custom provider "x": it has no base URL — …` | Set `--base-url`, fill the connection's base URL, or use a vendor connection type; `borgiq ai-providers list` shows the effective base URL |
| `Model "x/y" is not enabled for the AI Agent actor (agent: false in provider "x" catalog)` | Use another model on the AI Agent, or remove the flag |
| `Model "<id>" is not one of the AI Agent actor's <provider> models (…)` | A known id outside the AI Agent's list ([ai-models.md](ai-models.md)); `borgiq ai-providers models` shows `agent: true` for the listed ones |
| `Custom provider "x": its connection no longer exists — pick another connection in the workspace AI settings` | The linked connection was deleted (`borgiq ai-providers list` shows `connectionMissing: true`). `borgiq ai-providers edit x --connection <key>` |
| `An AI setting named "x" already exists` | Slugs are unique per workspace |
| The AI actor returns malformed JSON with `outputSchema` | Set `structuredOutputs: false` on the catalog entry |
| `thinkingLevel` has no effect on the AI Agent | Set `reasoning: true` (and often a `compat.thinkingFormat`) on the catalog entry |
| Usage log shows $0 | Add `costPerMTokens` to the catalog entry |
| `A custom provider cannot use a "<type>" connection` | Use a connection type from the vendor table |
| AI Agent refuses: `http:// base URL together with an API key` | Only reachable in local development (elsewhere `http://` is refused outright). The secret proxy only injects the key into https:// requests; use https://, or a keyless endpoint |
| A generic API-key connection (`x-api-key`) also sends `Authorization: Bearer` on the AI Agent | Expected: pi's client always adds it; both headers carry the same key over TLS and the endpoint reads the one it expects |
