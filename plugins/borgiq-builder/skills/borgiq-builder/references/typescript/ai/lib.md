# ai/lib

Generated from the platform's runtime types. Do not edit.

AI providers, including custom OpenAI-compatible ones, and the per-model information shape.

## ai/lib

**Source:** `ai/lib.ts`

```typescript
export const convertCostPerMTokensToCostPer1kTokens = (costPerMTokens: number) => {
  // Convert cost per million tokens to cost per 1k tokens cost per million tokens * millicents per dollar * 1000 tokens / 1,000,000 tokens
  return costPerMTokens * 100_000 * 1000 / 1_000_000;
};

export enum AiProvider {
  OpenAI = 'openai',
  Anthropic = 'anthropic',
  Google = 'google',
  xAi = 'xai',
  ClaudeCode = 'claude-code',
  Codex = 'codex',
  /** A custom provider: any AI provider, gateway/router or self-hosted server that is
   * OpenAI-compatible or uses the OpenAI chat completions schema (Fireworks, Groq, Together,
   * DeepInfra, OpenRouter, LiteLLM, Ollama, vLLM, LM Studio, llama.cpp, Azure OpenAI's /openai/v1,
   * ...). A workspace may add several, each an AI setting whose `name` is the provider's slug, with
   * a connection for the key (a vendor connection type flagged `aiProvider`, a generic bearer /
   * API-key type, or `custom-provider-apikey`), a base URL (its own override, else the connection's,
   * else the connection type's vendor default — see ./providerBaseUrl.ts) and a model catalog;
   * models are referenced as `<slug>/<model-id>` (see ./modelRef.ts), not through a build-time enum. */
  Custom = 'custom',
}

/** The providers that serve models (every AiProvider except the agent-harness credential
 * providers `claude-code` and `codex`). A qualified model reference `<provider>/<model-id>` may
 * name one of the built-in ones; `custom` is reached through a custom provider's slug instead. */
export const AI_MODEL_PROVIDERS = [
  AiProvider.OpenAI,
  AiProvider.Anthropic,
  AiProvider.Google,
  AiProvider.xAi,
  AiProvider.Custom,
] as const satisfies readonly AiProvider[];

export type AiModelProvider = (typeof AI_MODEL_PROVIDERS)[number];

/** Human-readable provider names: the `providerLabel` of a built-in provider's model and the model
 * dropdown's group title for it. A custom provider's models group under "Custom Provider — <slug>"
 * (see ./modelRef.ts `getAiModelInformation`), so the `custom` label here is only its prefix. */
export const AiProviderLabels: Record<AiProvider, string> = {
  [AiProvider.OpenAI]: 'OpenAI',
  [AiProvider.Anthropic]: 'Anthropic',
  [AiProvider.Google]: 'Google',
  [AiProvider.xAi]: 'xAI Grok',
  [AiProvider.ClaudeCode]: 'Claude Code',
  [AiProvider.Codex]: 'Codex',
  [AiProvider.Custom]: 'Custom Provider',
};

type TokenWindow = number | 'default';

export interface  AiModelInformation {
  provider: AiProvider;
  label: string;
  providerLabel: string;
  date: string;
  costPer1kTokens: { input: number; output: number } | Record<TokenWindow, { input: number; output: number }>;
  maxTokens: number;
}
```
