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
`local-vllm` (letters, digits and dashes; never a built-in provider id). The slug is the first
segment of the provider's model references:

```
<slug>/<model-id>
fireworks/accounts/fireworks/models/llama-v3p1-70b-instruct
openrouter/moonshotai/kimi-k2
groq/llama-3.3-70b-versatile
local-vllm/qwen2.5-coder:7b
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
does not exist in the workspace fails at run time with `No custom provider named "<slug>"`.

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
| `custom-provider-apikey` | — (its required `baseUrl` input is the endpoint) | Any other OpenAI-compatible endpoint; optional key (keyless local servers); optional `extraHeaders` |
| `generic-bearer-token`, `generic-api-key` | — (set `--base-url`) | A generic API-key connection sends the key in the header it names (e.g. `x-api-key`) instead of `Authorization: Bearer` |

Other connection types (OAuth, custom auth, ...) are refused with a 400.

```bash
# A vendor connection: only the key is needed
cat > secret.json <<'JSON'
{ "apiKey": "gsk_..." }
JSON
borgiq connections create --key groq --type groq-bearer --secret-inputs-file secret.json

# A custom-provider connection for anything else: base URL + optional key
cat > inputs.json <<'JSON'
{ "baseUrl": "http://vllm.internal:8000/v1" }
JSON
borgiq connections create --key local-vllm --type custom-provider-apikey --inputs-file inputs.json --secret-inputs-file secret.json
```

### 2. Custom provider (slug + connection + catalog)

In the web app: **Workspace settings → AI settings → Custom providers → Add custom provider**, or
with the CLI (`@borgiq/cli` >= 0.12.0):

```bash
# On a vendor connection the base URL is filled in from the connection type
borgiq ai-providers create --provider custom --name groq --connection groq --models llama-3.3-70b-versatile

# On a generic bearer / API-key connection, give the base URL
borgiq ai-providers create --provider custom --name local-vllm --connection local-vllm-key \
  --base-url http://vllm.internal:8000/v1 --models qwen2.5-coder:7b

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
| `costPerMTokens` | `{ input: 0, output: 0 }` | USD per million tokens, for the AI usage log |
| `compat` | — | pi OpenAI-completions compatibility overrides for the AI Agent (`supportsDeveloperRole`, `maxTokensField`, `thinkingFormat`, …) |

```json
[
  { "id": "llama-3.3-70b-versatile", "label": "Llama 3.3 70B", "maxTokens": 32768,
    "costPerMTokens": { "input": 0.59, "output": 0.79 } },
  { "id": "deepseek-r1-distill-llama-70b", "reasoning": true,
    "compat": { "thinkingFormat": "deepseek" } }
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

The AI Agent actor runs in the cloud, so its custom provider must be reachable from there; a
server on your own machine works for the AI actor only when the platform can reach it.

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
| Azure OpenAI | `custom-provider-apikey` or `generic-api-key` | `https://<resource>.openai.azure.com/openai/v1` | Bearer key, or the `api-key` header via a generic API-key connection |
| Ollama / vLLM / LM Studio / llama.cpp | `custom-provider-apikey` | `http://<host>:11434/v1`, `:8000/v1`, `:1234/v1`, `:8080/v1` | Usually keyless; must be reachable by the platform |

## Troubleshooting

| Symptom | Cause / fix |
|---------|-------------|
| `Unknown model "…"` on save | A bare id that is not a known model. Reference it as `<slug>/<model-id>` |
| `No custom provider named "x"` at run time | No custom provider with slug `x` in this workspace. `borgiq ai-providers list` |
| `Use a short kebab-case name for a custom provider` | Slugs are lowercase letters, digits and dashes, and cannot be a built-in provider id (`openai`, `anthropic`, …, `custom`) |
| `An AI setting named "x" already exists` | Slugs are unique per workspace |
| The AI actor returns malformed JSON with `outputSchema` | The endpoint does not honour `response_format: json_schema`; set `structuredOutputs: false` on the catalog entry |
| `thinkingLevel` has no effect on the AI Agent | The catalog entry needs `reasoning: true` (and often a `compat.thinkingFormat`) |
| Usage log shows $0 | Add `costPerMTokens` to the catalog entry |
| `The custom provider "x" has no base URL` | Nothing supplies one: set `--base-url`, fill the connection's base URL, or use a vendor connection type. `borgiq ai-providers list` shows the effective base URL |
| `A custom provider cannot use a "<type>" connection` | Only AI vendor types, `custom-provider-apikey` and generic bearer / API-key connections are accepted |
| AI Agent refuses: `http:// base URL together with an API key` | The secret proxy only injects the key into https:// requests; use https://, or a keyless endpoint (the AI actor is unaffected) |
| A generic API-key connection (`x-api-key`) also sends `Authorization: Bearer` on the AI Agent | Expected: pi's client always adds it; both headers carry the same key over TLS and the endpoint reads the one it expects |
