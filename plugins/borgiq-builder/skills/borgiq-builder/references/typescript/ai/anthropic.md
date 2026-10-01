# ai/anthropic

Generated from the platform's runtime types. Do not edit.

Anthropic model ids, the agent model list, and per-model information including prices.

See also: [ai/lib](lib.md).

## ai/anthropic

**Source:** `ai/anthropic.ts`

```typescript
import { AiModelInformation, AiProvider, convertCostPerMTokensToCostPer1kTokens } from './lib.js';

export const PROVIDER_LABEL = 'Anthropic';

export enum AnthropicModels {
  /** Every Claude 3.x id is retired and requests to it fail: Claude 3 Sonnet on 2025-07-21,
   * 3.5 Sonnet 2025-10-28, 3 Opus 2026-01-05, 3.5 Haiku and 3.7 Sonnet 2026-02-19, 3 Haiku
   * 2026-04-20. `claude-3-sonnet-latest` and `claude-3-haiku-latest` never existed. The values
   * stay because saved actors reference them. */
  CLAUDE_3_7_SONNET = 'claude-3-7-sonnet-latest',
  CLAUDE_3_7_SONNET_2025_02_19 = 'claude-3-7-sonnet-20250219',
  
  CLAUDE_3_5_SONNET = 'claude-3-5-sonnet-latest',
  CLAUDE_3_5_SONNET_2024_10_22 = 'claude-3-5-sonnet-20241022',
  CLAUDE_3_5_SONNET_2024_06_20 = 'claude-3-5-sonnet-20240620',

  CLAUDE_3_5_HAIKU = 'claude-3-5-haiku-latest',
  CLAUDE_3_5_HAIKU_2024_10_22 = 'claude-3-5-haiku-20241022',
  
  CLAUDE_3_OPUS = 'claude-3-opus-latest',
  CLAUDE_3_OPUS_2024_02_29 = 'claude-3-opus-20240229',
  CLAUDE_3_SONNET = 'claude-3-sonnet-latest',
  CLAUDE_3_SONNET_2024_02_29 = 'claude-3-sonnet-20240229',
  CLAUDE_3_HAIKU = 'claude-3-haiku-latest',
  CLAUDE_3_HAIKU_2024_03_07 = 'claude-3-haiku-20240307',

  /** Retired, requests fail: Opus 4 and Sonnet 4 on 2026-06-15, Opus 4.1 on 2026-08-05. */
  CLAUDE_4_OPUS = 'claude-opus-4-0',
  CLAUDE_4_OPUS_2025_05_14 = 'claude-opus-4-20250514',
  CLAUDE_4_1_OPUS = 'claude-opus-4-1',
  CLAUDE_4_1_OPUS_2025_08_05 = 'claude-opus-4-1-20250805',
  CLAUDE_4_SONNET = 'claude-sonnet-4-0',
  CLAUDE_4_SONNET_2025_05_14 = 'claude-sonnet-4-20250514',
  CLAUDE_4_5_SONNET = 'claude-sonnet-4-5',
  CLAUDE_4_5_SONNET_2025_09_29 = 'claude-sonnet-4-5-20250929',
  CLAUDE_4_5_OPUS = 'claude-opus-4-5',
  CLAUDE_4_5_OPUS_2025_11_01 = 'claude-opus-4-5-20251101',
  CLAUDE_4_5_HAIKU = 'claude-haiku-4-5',
  CLAUDE_4_5_HAIKU_2025_10_01 = 'claude-haiku-4-5-20251001',

  /** From the 4.6 generation on, the dateless id is itself the pinned snapshot: the two dated
   * 4.6 values below were never valid API ids. */
  CLAUDE_4_6_OPUS = 'claude-opus-4-6',
  CLAUDE_4_6_OPUS_2026_02_05 = 'claude-opus-4-6-20260205',
  CLAUDE_4_6_SONNET = 'claude-sonnet-4-6',
  CLAUDE_4_6_SONNET_2026_02_17 = 'claude-sonnet-4-6-20260217',

  CLAUDE_4_7_OPUS = 'claude-opus-4-7',

  CLAUDE_4_8_OPUS = 'claude-opus-4-8',

  CLAUDE_5_SONNET = 'claude-sonnet-5',
  CLAUDE_5_OPUS = 'claude-opus-5',
  CLAUDE_5_5_OPUS = 'claude-opus-5-5',

  /** Mythos-class tier. Claude Mythos 5 / 5.1 are the same underlying models with
   * safeguards lifted, but are restricted to Anthropic's trusted-access program and
   * are deliberately not listed here. */
  CLAUDE_5_FABLE = 'claude-fable-5',
  CLAUDE_5_1_FABLE = 'claude-fable-5-1',
}

/** Anthropic models proficient enough to drive agentic workflows (flagship + fast variants).
 * The first entry seeds the cross-provider agent default, so keep a balanced Sonnet first. */
export const AnthropicAgentModels = [
  AnthropicModels.CLAUDE_5_SONNET,
  AnthropicModels.CLAUDE_5_5_OPUS,
  AnthropicModels.CLAUDE_5_1_FABLE,
  AnthropicModels.CLAUDE_5_OPUS,
  AnthropicModels.CLAUDE_5_FABLE,
  AnthropicModels.CLAUDE_4_8_OPUS,
  AnthropicModels.CLAUDE_4_7_OPUS,
  AnthropicModels.CLAUDE_4_6_SONNET,
  AnthropicModels.CLAUDE_4_6_OPUS,
  AnthropicModels.CLAUDE_4_5_SONNET,
  AnthropicModels.CLAUDE_4_5_HAIKU,
  AnthropicModels.CLAUDE_4_5_OPUS,
] as const;

export const AnthropicModelInformationMap: Record<AnthropicModels, AiModelInformation> = {
  [AnthropicModels.CLAUDE_3_7_SONNET]: {
    provider: AiProvider.Anthropic,
    label: 'Claude 3.7 Sonnet',
    providerLabel: PROVIDER_LABEL,
    date: '2025-02-19',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(3),
      output: convertCostPerMTokensToCostPer1kTokens(15),
    },
    maxTokens: 64000,
  },
  [AnthropicModels.CLAUDE_3_7_SONNET_2025_02_19]: {
    provider: AiProvider.Anthropic,
    label: 'Claude 3.7 Sonnet 2025-02-19',
    providerLabel: PROVIDER_LABEL,
    date: '2025-02-19',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(3),
      output: convertCostPerMTokensToCostPer1kTokens(15),
    },
    maxTokens: 64000,
  },

  [AnthropicModels.CLAUDE_3_5_SONNET]: {
    provider: AiProvider.Anthropic,
    label: 'Claude 3.5 Sonnet',
    providerLabel: PROVIDER_LABEL,
    date: '2024-10-22',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(3),
      output: convertCostPerMTokensToCostPer1kTokens(15),
    },
    maxTokens: 8192,
  },
  [AnthropicModels.CLAUDE_3_5_SONNET_2024_10_22]: {
    provider: AiProvider.Anthropic,
    label: 'Claude 3.5 Sonnet 2024-10-22',
    providerLabel: PROVIDER_LABEL,
    date: '2024-10-22',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(3),
      output: convertCostPerMTokensToCostPer1kTokens(15),
    },
    maxTokens: 8192,
  },
  [AnthropicModels.CLAUDE_3_5_SONNET_2024_06_20]: {
    provider: AiProvider.Anthropic,
    label: 'Claude 3.5 Sonnet 2024-06-20',
    providerLabel: 'Anthropic',
    date: '2024-06-20',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(3),
      output: convertCostPerMTokensToCostPer1kTokens(15),
    },
    maxTokens: 8192,
  },

  [AnthropicModels.CLAUDE_3_5_HAIKU]: {
    provider: AiProvider.Anthropic,
    label: 'Claude 3.5 Haiku',
    providerLabel: 'Anthropic',
    date: '2024-10-22',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(0.8),
      output: convertCostPerMTokensToCostPer1kTokens(4),
    },
    maxTokens: 8192,
  },
  [AnthropicModels.CLAUDE_3_5_HAIKU_2024_10_22]: {
    provider: AiProvider.Anthropic,
    label: 'Claude 3.5 Haiku 2024-10-22',
    providerLabel: 'Anthropic',
    date: '2024-10-22',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(0.8),
      output: convertCostPerMTokensToCostPer1kTokens(4),
    },
    maxTokens: 8192,
  },


  [AnthropicModels.CLAUDE_3_OPUS]: {
    provider: AiProvider.Anthropic,
    label: 'Claude 3 Opus',
    providerLabel: 'Anthropic',
    date: '2024-02-29',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(15),
      output: convertCostPerMTokensToCostPer1kTokens(75),
    },
    maxTokens: 4096,
  },
  [AnthropicModels.CLAUDE_3_OPUS_2024_02_29]: {
    provider: AiProvider.Anthropic,
    label: 'Claude 3 Opus 2024-02-29',
    providerLabel: 'Anthropic',
    date: '2024-02-29',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(15),
      output: convertCostPerMTokensToCostPer1kTokens(75),
    },
    maxTokens: 4096,
  },
  [AnthropicModels.CLAUDE_3_SONNET]: {
    provider: AiProvider.Anthropic,
    label: 'Claude 3 Sonnet',
    providerLabel: 'Anthropic',
    date: '2024-02-29',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(3),
      output: convertCostPerMTokensToCostPer1kTokens(15),
    },
    maxTokens: 4096,
  },
  [AnthropicModels.CLAUDE_3_SONNET_2024_02_29]: {
    provider: AiProvider.Anthropic,
    label: 'Claude 3 Sonnet 2024-02-29',
    providerLabel: 'Anthropic',
    date: '2024-02-29',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(3),
      output: convertCostPerMTokensToCostPer1kTokens(15),
    },
    maxTokens: 4096,
  },
  [AnthropicModels.CLAUDE_3_HAIKU]: {
    provider: AiProvider.Anthropic,
    label: 'Claude 3 Haiku',
    providerLabel: 'Anthropic',
    date: '2024-03-07',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(0.25),
      output: convertCostPerMTokensToCostPer1kTokens(1.25),
    },
    maxTokens: 4096,
  },
  [AnthropicModels.CLAUDE_3_HAIKU_2024_03_07]: {
    provider: AiProvider.Anthropic,
    label: 'Claude 3 Haiku 2024-03-07',
    providerLabel: 'Anthropic',
    date: '2024-03-07',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(0.25),
      output: convertCostPerMTokensToCostPer1kTokens(1.25),
    },
    maxTokens: 4096,
  },

  [AnthropicModels.CLAUDE_4_OPUS]: {
    provider: AiProvider.Anthropic,
    label: 'Claude 4 Opus',
    providerLabel: 'Anthropic',
    date: '2025-05-14',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(15),
      output: convertCostPerMTokensToCostPer1kTokens(75),
    },
    maxTokens: 32000,
  },
  [AnthropicModels.CLAUDE_4_OPUS_2025_05_14]: {
    provider: AiProvider.Anthropic,
    label: 'Claude 4 Opus 2025-05-14',
    providerLabel: 'Anthropic',
    date: '2025-05-14',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(15),
      output: convertCostPerMTokensToCostPer1kTokens(75),
    },
    maxTokens: 32000,
  },
  [AnthropicModels.CLAUDE_4_SONNET]: {
    provider: AiProvider.Anthropic,
    label: 'Claude 4 Sonnet',
    providerLabel: 'Anthropic',
    date: '2025-05-14',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(3),
      output: convertCostPerMTokensToCostPer1kTokens(15),
    },
    maxTokens: 64000,
  },
  [AnthropicModels.CLAUDE_4_SONNET_2025_05_14]: {
    provider: AiProvider.Anthropic,
    label: 'Claude 4 Sonnet 2025-05-14',
    providerLabel: 'Anthropic',
    date: '2025-05-14',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(3),
      output: convertCostPerMTokensToCostPer1kTokens(15),
    },
    maxTokens: 64000,
  },
  [AnthropicModels.CLAUDE_4_1_OPUS]: {
    provider: AiProvider.Anthropic,
    label: 'Claude 4.1 Opus',
    providerLabel: 'Anthropic',
    date: '2025-08-05',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(15),
      output: convertCostPerMTokensToCostPer1kTokens(75),
    },
    maxTokens: 32000,
  },
  [AnthropicModels.CLAUDE_4_1_OPUS_2025_08_05]: {
    provider: AiProvider.Anthropic,
    label: 'Claude 4.1 Opus 2025-08-05',
    providerLabel: 'Anthropic',
    date: '2025-08-05',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(15),
      output: convertCostPerMTokensToCostPer1kTokens(75),
    },
    maxTokens: 32000,
  },
  [AnthropicModels.CLAUDE_4_5_SONNET]: {
    provider: AiProvider.Anthropic,
    label: 'Claude 4.5 Sonnet',
    providerLabel: 'Anthropic',
    date: '2025-09-29',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(3),
      output: convertCostPerMTokensToCostPer1kTokens(15),
    },
    maxTokens: 64000,
  },
  [AnthropicModels.CLAUDE_4_5_SONNET_2025_09_29]: {
    provider: AiProvider.Anthropic,
    label: 'Claude 4.5 Sonnet 2025-09-29',
    providerLabel: 'Anthropic',
    date: '2025-09-29',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(3),
      output: convertCostPerMTokensToCostPer1kTokens(15),
    },
    maxTokens: 64000,
  },
  [AnthropicModels.CLAUDE_4_5_OPUS]: {
    provider: AiProvider.Anthropic,
    label: 'Claude 4.5 Opus',
    providerLabel: 'Anthropic',
    date: '2025-11-24',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(5),
      output: convertCostPerMTokensToCostPer1kTokens(25),
    },
    maxTokens: 64000,
  },
  [AnthropicModels.CLAUDE_4_5_OPUS_2025_11_01]: {
    provider: AiProvider.Anthropic,
    label: 'Claude 4.5 Opus 2025-11-01',
    providerLabel: 'Anthropic',
    date: '2025-11-24',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(5),
      output: convertCostPerMTokensToCostPer1kTokens(25),
    },
    maxTokens: 64000,
  },
  [AnthropicModels.CLAUDE_4_5_HAIKU]: {
    provider: AiProvider.Anthropic,
    label: 'Claude 4.5 Haiku',
    providerLabel: 'Anthropic',
    date: '2025-10-15',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(1),
      output: convertCostPerMTokensToCostPer1kTokens(5),
    },
    maxTokens: 64000,
  },
  [AnthropicModels.CLAUDE_4_5_HAIKU_2025_10_01]: {
    provider: AiProvider.Anthropic,
    label: 'Claude 4.5 Haiku 2025-10-01',
    providerLabel: 'Anthropic',
    date: '2025-10-15',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(1),
      output: convertCostPerMTokensToCostPer1kTokens(5),
    },
    maxTokens: 64000,
  },

  [AnthropicModels.CLAUDE_4_6_OPUS]: {
    provider: AiProvider.Anthropic,
    label: 'Claude 4.6 Opus',
    providerLabel: PROVIDER_LABEL,
    date: '2026-02-05',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(5),
      output: convertCostPerMTokensToCostPer1kTokens(25),
    },
    maxTokens: 128000,
  },
  [AnthropicModels.CLAUDE_4_6_OPUS_2026_02_05]: {
    provider: AiProvider.Anthropic,
    label: 'Claude 4.6 Opus 2026-02-05',
    providerLabel: PROVIDER_LABEL,
    date: '2026-02-05',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(5),
      output: convertCostPerMTokensToCostPer1kTokens(25),
    },
    maxTokens: 128000,
  },
  [AnthropicModels.CLAUDE_4_6_SONNET]: {
    provider: AiProvider.Anthropic,
    label: 'Claude 4.6 Sonnet',
    providerLabel: PROVIDER_LABEL,
    date: '2026-02-17',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(3),
      output: convertCostPerMTokensToCostPer1kTokens(15),
    },
    maxTokens: 128000,
  },
  [AnthropicModels.CLAUDE_4_6_SONNET_2026_02_17]: {
    provider: AiProvider.Anthropic,
    label: 'Claude 4.6 Sonnet 2026-02-17',
    providerLabel: PROVIDER_LABEL,
    date: '2026-02-17',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(3),
      output: convertCostPerMTokensToCostPer1kTokens(15),
    },
    maxTokens: 128000,
  },

  [AnthropicModels.CLAUDE_4_7_OPUS]: {
    provider: AiProvider.Anthropic,
    label: 'Claude 4.7 Opus',
    providerLabel: PROVIDER_LABEL,
    date: '2026-04-16',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(5),
      output: convertCostPerMTokensToCostPer1kTokens(25),
    },
    maxTokens: 128000,
  },
  [AnthropicModels.CLAUDE_4_8_OPUS]: {
    provider: AiProvider.Anthropic,
    label: 'Claude 4.8 Opus',
    providerLabel: PROVIDER_LABEL,
    date: '2026-05-28',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(5),
      output: convertCostPerMTokensToCostPer1kTokens(25),
    },
    maxTokens: 128000,
  },

  [AnthropicModels.CLAUDE_5_SONNET]: {
    provider: AiProvider.Anthropic,
    label: 'Claude Sonnet 5',
    providerLabel: PROVIDER_LABEL,
    date: '2026-06-30',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(2),
      output: convertCostPerMTokensToCostPer1kTokens(10),
    },
    maxTokens: 128000,
  },
  [AnthropicModels.CLAUDE_5_OPUS]: {
    provider: AiProvider.Anthropic,
    label: 'Claude Opus 5',
    providerLabel: PROVIDER_LABEL,
    date: '2026-07-24',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(5),
      output: convertCostPerMTokensToCostPer1kTokens(25),
    },
    maxTokens: 128000,
  },
  [AnthropicModels.CLAUDE_5_5_OPUS]: {
    provider: AiProvider.Anthropic,
    label: 'Claude Opus 5.5',
    providerLabel: PROVIDER_LABEL,
    date: '2026-09-22',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(4),
      output: convertCostPerMTokensToCostPer1kTokens(20),
    },
    maxTokens: 128000,
  },

  [AnthropicModels.CLAUDE_5_FABLE]: {
    provider: AiProvider.Anthropic,
    label: 'Claude Fable 5',
    providerLabel: PROVIDER_LABEL,
    date: '2026-06-09',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(10),
      output: convertCostPerMTokensToCostPer1kTokens(50),
    },
    maxTokens: 128000,
  },
  [AnthropicModels.CLAUDE_5_1_FABLE]: {
    provider: AiProvider.Anthropic,
    label: 'Claude Fable 5.1',
    providerLabel: PROVIDER_LABEL,
    date: '2026-09-01',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(10),
      output: convertCostPerMTokensToCostPer1kTokens(50),
    },
    maxTokens: 128000,
  },
} as const;
```
