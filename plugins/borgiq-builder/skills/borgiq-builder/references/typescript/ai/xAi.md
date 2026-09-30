# ai/xAi

Generated from the platform's runtime types. Do not edit.

xAI Grok model ids, the agent model list, and per-model information including prices.

See also: [ai/lib](lib.md).

## ai/xAi

**Source:** `ai/xAi.ts`

```typescript
import { AiModelInformation, AiProvider, convertCostPerMTokensToCostPer1kTokens } from './lib.js';

export const PROVIDER_LABEL = 'xAI Grok';

export enum xAiModels {
  /** grok-4-0709, both grok-4-fast ids and grok-code-fast-1 were retired 2026-05-15: requests
   * redirect to grok-4.3 (grok-code-fast-1 to grok-build-0.1) and bill at grok-4.3's rates, which
   * is what their entries carry. xAI no longer lists the bare grok-4 id. */
  GROK_4 = 'grok-4',
  GROK_4_0709 = 'grok-4-0709',

  GROK_4_FAST_REASONING = 'grok-4-fast-reasoning',
  GROK_4_FAST_NON_REASONING = 'grok-4-fast-non-reasoning',

  GROK_CODE_FAST_1 = 'grok-code-fast-1',

  GROK_4_3 = 'grok-4.3',

  GROK_4_5 = 'grok-4.5',

  GROK_4_6 = 'grok-4.6',

  GROK_4_7 = 'grok-4.7',

  GROK_4_20_REASONING = 'grok-4.20-0309-reasoning',
  GROK_4_20_NON_REASONING = 'grok-4.20-0309-non-reasoning',
  GROK_4_20_MULTI_AGENT = 'grok-4.20-multi-agent-0309',

  GROK_BUILD_0_1 = 'grok-build-0.1',
}

/** xAI models proficient enough to drive agentic workflows (flagship + fast/code). */
export const xAiAgentModels = [
  xAiModels.GROK_4_7,
  xAiModels.GROK_4_6,
  xAiModels.GROK_4_5,
  xAiModels.GROK_4_20_REASONING,
  xAiModels.GROK_4_20_MULTI_AGENT,
  xAiModels.GROK_BUILD_0_1,
  xAiModels.GROK_4_3,
  xAiModels.GROK_4_FAST_REASONING,
  xAiModels.GROK_CODE_FAST_1,
] as const;

export const xAiModelInformationMap: Record<xAiModels, AiModelInformation> = {
  [xAiModels.GROK_4]: {
    provider: AiProvider.xAi,
    label: 'Grok 4',
    providerLabel: PROVIDER_LABEL,
    date: '2025-07-09',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(3),
      output: convertCostPerMTokensToCostPer1kTokens(15),
    },
    maxTokens: 256000,
  },
  [xAiModels.GROK_4_0709]: {
    provider: AiProvider.xAi,
    label: 'Grok 4 (2025-07-09)',
    providerLabel: PROVIDER_LABEL,
    date: '2025-07-09',
    costPer1kTokens: {
      200000: {
        input: convertCostPerMTokensToCostPer1kTokens(1.25),
        output: convertCostPerMTokensToCostPer1kTokens(2.5),
      },
      default: {
        input: convertCostPerMTokensToCostPer1kTokens(2.5),
        output: convertCostPerMTokensToCostPer1kTokens(5),
      },
    },
    maxTokens: 1000000,
  },
  [xAiModels.GROK_4_FAST_REASONING]: {
    provider: AiProvider.xAi,
    label: 'Grok 4 Fast (Reasoning)',
    providerLabel: PROVIDER_LABEL,
    date: '2025-09-20',
    costPer1kTokens: {
      200000: {
        input: convertCostPerMTokensToCostPer1kTokens(1.25),
        output: convertCostPerMTokensToCostPer1kTokens(2.5),
      },
      default: {
        input: convertCostPerMTokensToCostPer1kTokens(2.5),
        output: convertCostPerMTokensToCostPer1kTokens(5),
      },
    },
    maxTokens: 1000000,
  },
  [xAiModels.GROK_4_FAST_NON_REASONING]: {
    provider: AiProvider.xAi,
    label: 'Grok 4 Fast (Non-Reasoning)',
    providerLabel: PROVIDER_LABEL,
    date: '2025-09-20',
    costPer1kTokens: {
      200000: {
        input: convertCostPerMTokensToCostPer1kTokens(1.25),
        output: convertCostPerMTokensToCostPer1kTokens(2.5),
      },
      default: {
        input: convertCostPerMTokensToCostPer1kTokens(2.5),
        output: convertCostPerMTokensToCostPer1kTokens(5),
      },
    },
    maxTokens: 1000000,
  },
  [xAiModels.GROK_CODE_FAST_1]: {
    provider: AiProvider.xAi,
    label: 'Grok Code Fast 1',
    providerLabel: PROVIDER_LABEL,
    date: '2025-08-01',
    costPer1kTokens: {
      200000: {
        input: convertCostPerMTokensToCostPer1kTokens(1.25),
        output: convertCostPerMTokensToCostPer1kTokens(2.5),
      },
      default: {
        input: convertCostPerMTokensToCostPer1kTokens(2.5),
        output: convertCostPerMTokensToCostPer1kTokens(5),
      },
    },
    maxTokens: 256000,
  },
  /** From Grok 4.3 onwards xAI prices in two tiers: prompts at or below 200k input
   * tokens bill at the base rate, anything larger bills the whole request at double. */
  [xAiModels.GROK_4_3]: {
    provider: AiProvider.xAi,
    label: 'Grok 4.3',
    providerLabel: PROVIDER_LABEL,
    date: '2026-04-30',
    costPer1kTokens: {
      200000: {
        input: convertCostPerMTokensToCostPer1kTokens(1.25),
        output: convertCostPerMTokensToCostPer1kTokens(2.5),
      },
      default: {
        input: convertCostPerMTokensToCostPer1kTokens(2.5),
        output: convertCostPerMTokensToCostPer1kTokens(5),
      },
    },
    maxTokens: 1000000,
  },
  [xAiModels.GROK_4_5]: {
    provider: AiProvider.xAi,
    label: 'Grok 4.5',
    providerLabel: PROVIDER_LABEL,
    date: '2026-07-16',
    costPer1kTokens: {
      200000: {
        input: convertCostPerMTokensToCostPer1kTokens(2),
        output: convertCostPerMTokensToCostPer1kTokens(6),
      },
      default: {
        input: convertCostPerMTokensToCostPer1kTokens(4),
        output: convertCostPerMTokensToCostPer1kTokens(12),
      },
    },
    maxTokens: 500000,
  },
  [xAiModels.GROK_4_6]: {
    provider: AiProvider.xAi,
    label: 'Grok 4.6',
    providerLabel: PROVIDER_LABEL,
    date: '2026-08-12',
    costPer1kTokens: {
      200000: {
        input: convertCostPerMTokensToCostPer1kTokens(2),
        output: convertCostPerMTokensToCostPer1kTokens(6),
      },
      default: {
        input: convertCostPerMTokensToCostPer1kTokens(4),
        output: convertCostPerMTokensToCostPer1kTokens(12),
      },
    },
    maxTokens: 500000,
  },
  [xAiModels.GROK_4_7]: {
    provider: AiProvider.xAi,
    label: 'Grok 4.7',
    providerLabel: PROVIDER_LABEL,
    date: '2026-09-21',
    costPer1kTokens: {
      200000: {
        input: convertCostPerMTokensToCostPer1kTokens(2),
        output: convertCostPerMTokensToCostPer1kTokens(6),
      },
      default: {
        input: convertCostPerMTokensToCostPer1kTokens(4),
        output: convertCostPerMTokensToCostPer1kTokens(12),
      },
    },
    maxTokens: 500000,
  },

  [xAiModels.GROK_4_20_REASONING]: {
    provider: AiProvider.xAi,
    label: 'Grok 4.20 (Reasoning)',
    providerLabel: PROVIDER_LABEL,
    date: '2026-03-09',
    costPer1kTokens: {
      200000: {
        input: convertCostPerMTokensToCostPer1kTokens(1.25),
        output: convertCostPerMTokensToCostPer1kTokens(2.5),
      },
      default: {
        input: convertCostPerMTokensToCostPer1kTokens(2.5),
        output: convertCostPerMTokensToCostPer1kTokens(5),
      },
    },
    maxTokens: 1000000,
  },
  [xAiModels.GROK_4_20_NON_REASONING]: {
    provider: AiProvider.xAi,
    label: 'Grok 4.20 (Non-Reasoning)',
    providerLabel: PROVIDER_LABEL,
    date: '2026-03-09',
    costPer1kTokens: {
      200000: {
        input: convertCostPerMTokensToCostPer1kTokens(1.25),
        output: convertCostPerMTokensToCostPer1kTokens(2.5),
      },
      default: {
        input: convertCostPerMTokensToCostPer1kTokens(2.5),
        output: convertCostPerMTokensToCostPer1kTokens(5),
      },
    },
    maxTokens: 1000000,
  },
  [xAiModels.GROK_4_20_MULTI_AGENT]: {
    provider: AiProvider.xAi,
    label: 'Grok 4.20 (Multi-Agent)',
    providerLabel: PROVIDER_LABEL,
    date: '2026-03-09',
    costPer1kTokens: {
      200000: {
        input: convertCostPerMTokensToCostPer1kTokens(1.25),
        output: convertCostPerMTokensToCostPer1kTokens(2.5),
      },
      default: {
        input: convertCostPerMTokensToCostPer1kTokens(2.5),
        output: convertCostPerMTokensToCostPer1kTokens(5),
      },
    },
    maxTokens: 1000000,
  },

  [xAiModels.GROK_BUILD_0_1]: {
    provider: AiProvider.xAi,
    label: 'Grok Build 0.1',
    providerLabel: PROVIDER_LABEL,
    date: '2026-05-29',
    costPer1kTokens: {
      200000: {
        input: convertCostPerMTokensToCostPer1kTokens(1),
        output: convertCostPerMTokensToCostPer1kTokens(2),
      },
      default: {
        input: convertCostPerMTokensToCostPer1kTokens(2),
        output: convertCostPerMTokensToCostPer1kTokens(4),
      },
    },
    maxTokens: 256000,
  },
} as const;
```
