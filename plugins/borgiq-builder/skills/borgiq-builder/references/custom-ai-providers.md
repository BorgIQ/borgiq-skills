# Custom AI Providers

A **custom provider** is any AI provider, gateway/router, or self-hosted server that is
**OpenAI-compatible** or uses the **OpenAI chat completions schema**. A workspace can add as many as
it needs — Fireworks, Groq, Together, DeepInfra, DeepSeek, Moonshot (Kimi), Z.ai (GLM), Mistral,
OpenRouter, Hugging Face Inference Providers, LiteLLM, LLMGateway, Portkey, Azure OpenAI's
`/openai/v1` surface, Ollama, vLLM, LM Studio, llama.cpp, SGLang, TGI — each under its own name.

The AI actor, AI Agent actor and AI Router actor can all run a custom provider's models. Built-in
providers (`openai`, `anthropic`, `google`, `xai`) are unchanged; custom providers are added next
to them.

## How a custom provider is identified

Each custom provider has a **slug** — a short kebab-case name such as `fireworks`, `openrouter` or
`my-vllm`: lowercase letters, digits and dashes, starting with a letter or digit, at most 40
characters, and never a built-in provider id (`openai`, `anthropic`, `google`, `xai`, `custom`,
`claude-code`, `codex`, …). The slug is the first segment of the provider's model references:

```
<slug>/<model-id>
fireworks/accounts/fireworks/models/llama-v3p1-70b-instruct
openrouter/moonshotai/kimi-k2
groq/llama-3.3-70b-versatile
my-vllm/qwen2.5-coder:7b
```

Only the **first** `/` splits the slug from the model id, so nested ids (Fireworks' `accounts/…`,
OpenRouter's `vendor/model`) pass through untouched. The same model id may exist under two slugs —
`fireworks/llama` and `groq/llama` are two different models with their own pricing.

## Model reference rules (all AI actors)

The `model` option accepts exactly three forms:

| Form | Example | Resolves to |
|------|---------|-------------|
| Known model id | `claude-sonnet-5`, `gpt-4o-mini` | The built-in provider's credential |
| `<built-in provider>/<model-id>` | `openai/gpt-6` | That built-in provider, for a model the platform does not list yet |
| `<slug>/<model-id>` | `fireworks/accounts/fireworks/models/llama-v3p1-70b-instruct` | The workspace custom provider with that slug |

A bare id that is not a known model (`llama3.1:8b`) is **rejected** at validation time. A slug that
does not exist in the workspace is **not** a validation error — the editor's model field and
`borgiq canvases validate` only warn — but the actor fails at run time with:

```
Model "<ref>" does not exist: no custom provider named "<slug>" in this workspace. Add it under Custom providers, or fix the model reference.
```

The AI Agent actor is stricter about known ids: a known model id must be one of its curated agent
models (`openai/gpt-4o-mini` names the known model too, so the same rule applies). A built-in
provider's unlisted model (`<provider>/<model-id>`) and `<slug>/<model-id>` are not restricted by that
list; a custom catalog entry with `agent: false` is refused when the agent runs (see the catalog's
`agent` field).

A built-in model id served through a gateway is referenced explicitly — `openrouter/gpt-4o-mini` —
and keeps GPT-4o mini's label, pricing and limits (a catalog entry can override them). A bare
`gpt-4o-mini` always goes to the workspace's OpenAI credential.

## Setting one up

### 1. Connection (the key) and base URL

A custom provider takes its key from a connection and its base URL from the first of:

1. **its own override** — set on the provider (`--base-url`, or the Base URL field in the web app);
2. **the connection's base URL** — the connection's optional `baseUrl` input, when filled in
   (for a `custom-provider-apikey` connection this input is required and *is* the endpoint);
3. **the connection type's vendor default** — vendor connection types carry it.

Any of these connection types works:

| Connection type | Vendor default base URL | Note |
|-----------------|-------------------------|------|
| `groq-bearer` | `https://api.groq.com/openai/v1` | |
| `fireworks-bearer` | `https://api.fireworks.ai/inference/v1` | Model ids are `accounts/fireworks/models/<name>` |
| `together-bearer` | `https://api.together.ai/v1` | |
| `openrouter-bearer` | `https://openrouter.ai/api/v1` | Optional `extraHeaders` for `HTTP-Referer` / `X-OpenRouter-Title` |
| `mistral-bearer` | `https://api.mistral.ai/v1` | |
| `deepseek-bearer` | `https://api.deepseek.com` | No `/v1` |
| `cerebras-bearer` | `https://api.cerebras.ai/v1` | |
| `deepinfra-bearer` | `https://api.deepinfra.com/v1/openai` | |
| `perplexity-bearer` | `https://api.perplexity.ai` | No `/v1`; Sonar chat completions are being superseded by Perplexity's Agent API (support announced until 2026-09-27) |
| `cohere-bearer` | `https://api.cohere.ai/compatibility/v1` | Cohere's OpenAI-compatible Compatibility API |
| `huggingface-bearer` | `https://router.huggingface.co/v1` | Ids are `org/model`, optionally `:provider` |
| `openai-bearer`, `xai-bearer` | `https://api.openai.com/v1`, `https://api.x.ai/v1` | The built-in providers' own types; usable behind a custom provider too (e.g. with an overriding gateway base URL) |
| `custom-provider-apikey` | — (its required `baseUrl` input is the endpoint) | Any other OpenAI-compatible endpoint; optional key (keyless self-hosted servers, at a public address); optional non-secret `extraHeaders` |
| `generic-bearer-token`, `generic-api-key` | — (set `--base-url`) | A generic API-key connection sends the key in the header it names (e.g. `x-api-key`) instead of `Authorization: Bearer` |

Other connection types (OAuth, custom auth, ...) are refused with a 400.

A generic API-key connection must send its key **in a header**: one with "Add to Header" switched
off (the key as a query parameter) is refused when the provider is saved, and at run time.

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

The connection's `extraHeaders` input is for **non-secret** headers only (OpenRouter's
`HTTP-Referer` / `X-OpenRouter-Title`); never put a credential there. A vendor that authenticates
with a named header (Azure's `api-key`) uses a `generic-api-key` connection instead.

#### The base URL must be publicly reachable

Every LLM call to a custom provider goes out from BorgIQ's cloud, so its base URL is checked
against server-side request forgery — when the provider is saved (the `--base-url` override) and
again on the effective base URL at every run:

- it must use `https://`;
- a host that is, or resolves through DNS to, a private (`10.x`, `172.16–31.x`, `192.168.x`),
  link-local, CGNAT or cloud-metadata (`169.254.169.254`) address is refused, so is an internal DNS
  name that resolves to one;
- a hostname that fails to resolve is refused;
- `localhost` / loopback (and `http://`) are accepted only in local development.

A refused override is a 400 at save: `Base URL "<url>" is not allowed: <reason>`. A self-hosted
server (Ollama, vLLM, LM Studio, llama.cpp, SGLang, TGI) therefore needs a public address — for
example behind an HTTPS reverse proxy. Private-network endpoints are not supported yet.

### 2. Custom provider (slug + connection + catalog)

In the web app: **Workspace settings → AI settings → Custom providers → Add custom provider**, or
with the CLI (`@borgiq/cli` >= 0.12.0):

```bash
# On a vendor connection the base URL is filled in from the connection type
borgiq ai-providers create --provider custom --name groq --connection groq --models llama-3.3-70b-versatile

# On a generic bearer / API-key connection, give the base URL (a public https:// address)
borgiq ai-providers create --provider custom --name my-vllm --connection my-vllm-key \
  --base-url https://vllm.example.com/v1 --models qwen2.5-coder:7b

borgiq ai-providers create --provider custom --name fireworks --connection fireworks \
  --models accounts/fireworks/models/llama-v3p1-70b-instruct,accounts/fireworks/models/qwen2p5-coder-32b-instruct

# Later
borgiq ai-providers edit fireworks --add-model accounts/fireworks/models/deepseek-v3
borgiq ai-providers edit fireworks --base-url https://gateway.example/fireworks/v1   # route through a gateway
borgiq ai-providers edit fireworks --no-base-url                                     # back to the connection's / vendor default
borgiq ai-providers list                 # shows the effective base URL of each custom provider
borgiq ai-providers models --custom      # every <slug>/<model-id> reference ready to paste
borgiq ai-providers delete fireworks -y
```

`--name` is required for a custom provider (its slug has no default). Renaming or deleting a custom
provider does **not** rewrite the `<slug>/<model-id>` references in canvases, and is not blocked by
them: the web app and the CLI (`edit --name`, `delete`) warn with the canvases that reference the
provider, then proceed. Those actors fail at run time until their `model` is fixed.

In the web app, picking a vendor connection prefills the provider's name (`groq-bearer` → `groq`)
and shows the base URL it will use; type one only to override it.

### 3. Model catalog

The catalog lists the models the endpoint serves. Only `id` is required; the other fields refine
pricing, limits and behaviour:

| Field | Default | Meaning |
|-------|---------|---------|
| `id` | — | The model id sent to the endpoint |
| `label` | the id | Label in the model dropdown |
| `contextWindow` | 128000 | Context window in tokens (pi's compaction budget for the AI Agent) |
| `maxTokens` | 8192 | Maximum output tokens |
| `reasoning` | false | The model supports extended thinking — required for `thinkingLevel` on the AI Agent to have an effect |
| `supportsImages` | false | Accepts image input |
| `structuredOutputs` | true | The endpoint accepts `response_format: json_schema`; set `false` for servers that only do prompt-based JSON (the AI actor then falls back to text + repair) |
| `agent` | true (omitted) | Whether the AI Agent actor may run the model. `agent: false` hides it from the AI Agent's model suggestions (and shows `false` in `borgiq ai-providers models`' `AGENT` column), and the AI Agent refuses it at run time; the AI actor and AI Router still use it |
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

A model that is not in the catalog still runs (`groq/some-new-model`) with default limits and zero
cost; the catalog is what makes it show up in the dropdown, priced and labelled.

## Using the models in actors

```yaml
type: AiActor
configuration:
  options: |
    model: fireworks/accounts/fireworks/models/llama-v3p1-70b-instruct
    prompt: ${{ inputs.text }}
```

```yaml
type: AiAgentActor
configuration:
  options: |
    model: openrouter/moonshotai/kimi-k2
    thinkingLevel: off      # unless the catalog entry says reasoning: true
    prompt: ${{ inputs.task }}
```

Both actors call the endpoint from BorgIQ's cloud, so a server on your own machine or private
network needs a public address (see [the base URL rules](#the-base-url-must-be-publicly-reachable)).

A custom provider needs an effective base URL: an AI Agent segment on a provider with none is
refused before it is dispatched (`Custom provider "<slug>" has no base URL: set one on the provider,
on its connection, or re-import the connection type.`).

> **Implementation note.** On the AI Agent's Lambda, pi registers a custom provider under the id
> `custom:<slug>` (so a workspace slug can never collide with one of pi's built-in provider ids).
> The id appears only in Lambda logs; canvases always reference `<slug>/<model-id>`.

## Vendor notes

| Vendor | Connection type | Base URL | Notes |
|--------|-----------------|----------|-------|
| Fireworks | `fireworks-bearer` | `https://api.fireworks.ai/inference/v1` | Model ids are `accounts/fireworks/models/<name>`; your own deployments are `accounts/<account>/models/<name>` |
| Groq | `groq-bearer` | `https://api.groq.com/openai/v1` | Fast open models; tool calling and JSON schema supported |
| Together | `together-bearer` | `https://api.together.ai/v1` | `thinkingFormat: "together"` for reasoning models on the AI Agent; `api.together.xyz` is the legacy host |
| OpenRouter | `openrouter-bearer` | `https://openrouter.ai/api/v1` | Model ids are `vendor/model`; `HTTP-Referer`/`X-OpenRouter-Title` as extra headers; `compat: { thinkingFormat: "openrouter" }` for reasoning |
| Mistral | `mistral-bearer` | `https://api.mistral.ai/v1` | |
| DeepSeek | `deepseek-bearer` | `https://api.deepseek.com` | No `/v1`; reasoning models: `reasoning: true`, `compat: { thinkingFormat: "deepseek" }` |
| Cerebras | `cerebras-bearer` | `https://api.cerebras.ai/v1` | Do not combine `tools` with `response_format` |
| DeepInfra | `deepinfra-bearer` | `https://api.deepinfra.com/v1/openai` | |
| Perplexity | `perplexity-bearer` | `https://api.perplexity.ai` | No `/v1`; Sonar chat completions superseded by the Agent API (support announced until 2026-09-27) |
| Cohere | `cohere-bearer` | `https://api.cohere.ai/compatibility/v1` | The Compatibility API; ids like `command-a-03-2025` |
| Hugging Face | `huggingface-bearer` | `https://router.huggingface.co/v1` | HF token with the Inference Providers permission; ids are `org/model`, optionally `:provider` |
| Moonshot / Kimi | `custom-provider-apikey` | `https://api.moonshot.ai/v1` | Thinking variants: `reasoning: true` |
| Z.ai / GLM | `custom-provider-apikey` | `https://api.z.ai/api/paas/v4` | `reasoning: true`, `compat: { thinkingFormat: "zai" }` |
| LiteLLM / LLMGateway / Portkey | `custom-provider-apikey` | the gateway's `/v1` | One slug fronts many upstreams |
| Azure OpenAI | `custom-provider-apikey` or `generic-api-key` | `https://<resource>.openai.azure.com/openai/v1` | Bearer key, or the `api-key` header via a generic API-key connection (never in `extraHeaders`) |
| Ollama / vLLM / LM Studio / llama.cpp | `custom-provider-apikey` | the server's `/v1` (default ports 11434, 8000, 1234, 8080) at a public `https://` address | Keyless servers work, but must be reachable at a public address (e.g. behind an HTTPS reverse proxy); private-network endpoints are not supported yet |

## Troubleshooting

| Symptom | Cause / fix |
|---------|-------------|
| `Unknown model "…"` on save | A bare id that is not a known model. Reference it as `<slug>/<model-id>` |
| `Model "x/y" does not exist: no custom provider named "x" in this workspace. Add it under Custom providers, or fix the model reference.` at run time | No custom provider with slug `x` (it was renamed, deleted, or never added). `borgiq ai-providers list`; the editor and `borgiq canvases validate` only warn (`Model "x/y" references custom provider "x", which does not exist in this workspace`) |
| `Use a short kebab-case name for a custom provider` | Slugs are lowercase letters, digits and dashes, start with a letter or digit, are at most 40 characters, and cannot be a built-in provider id (`openai`, `anthropic`, …, `custom`) |
| `Base URL "<url>" is not allowed: <reason>` on save | The override is not `https://`, points at `localhost`, resolves to a private / link-local / CGNAT / metadata address, or does not resolve. Use a public `https://` address; private-network endpoints are not supported yet |
| `Custom provider "x": its base URL is not allowed: …` at run time | The same check on the effective base URL (the connection's or vendor default included) |
| `A custom provider needs the API key in a header; this connection sends it as a query parameter.` on save, or `Custom provider "x": its connection sends the API key as a query parameter; …` at run time | The generic API-key connection has "Add to Header" off. Switch it on, or use a bearer connection |
| `Custom provider "x" has no base URL: …` (AI Agent), or `Custom provider "x": it has no base URL — …` | Nothing supplies one: set `--base-url`, fill the connection's base URL, or use a vendor connection type. `borgiq ai-providers list` shows the effective base URL |
| `Model "x/y" is not enabled for the AI Agent actor (agent: false in provider "x" catalog)` | The catalog entry says `agent: false`. Use another model on the AI Agent, or remove the flag |
| `Model "<id>" is not one of the AI Agent actor's <provider> models (…)` | A known model id (bare or as `<provider>/<id>`) that is not in the AI Agent's curated list. Pick a listed one (`borgiq ai-providers models` shows `agent: true`) |
| `Custom provider "x": its connection no longer exists — pick another connection in the workspace AI settings` | The linked connection was deleted (`borgiq ai-providers list` shows `connectionMissing: true`). `borgiq ai-providers edit x --connection <key>` |
| `An AI setting named "x" already exists` | Slugs are unique per workspace |
| The AI actor returns malformed JSON with `outputSchema` | The endpoint does not honour `response_format: json_schema`; set `structuredOutputs: false` on the catalog entry |
| `thinkingLevel` has no effect on the AI Agent | The catalog entry needs `reasoning: true` (and often a `compat.thinkingFormat`) |
| Usage log shows $0 | Add `costPerMTokens` to the catalog entry |
| `A custom provider cannot use a "<type>" connection` | Only AI vendor types, `custom-provider-apikey` and generic bearer / API-key connections are accepted |
| AI Agent refuses: `http:// base URL together with an API key` | Only reachable in local development (elsewhere `http://` is refused outright). The secret proxy only injects the key into https:// requests; use https://, or a keyless endpoint |
| A generic API-key connection (`x-api-key`) also sends `Authorization: Bearer` on the AI Agent | Expected: pi's client always adds it; both headers carry the same key over TLS and the endpoint reads the one it expects |
