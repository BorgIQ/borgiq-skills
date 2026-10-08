# ai/openAi

Generated from the platform's runtime types. Do not edit.

OpenAI model ids, the agent model list, and per-model information including prices.

See also: [ai/lib](lib.md).

## ai/openAi

**Source:** `ai/openAi.ts`

```typescript
import { AiModelInformation, AiProvider, convertCostPerMTokensToCostPer1kTokens } from './lib.js';

const PROVIDER_LABEL = 'OpenAI';

export enum OpenAiModels {
  GPT_4O = 'gpt-4o',
  GPT_4O_2024_11_20 = 'gpt-4o-2024-11-20',
  GPT_4O_2024_08_06 = 'gpt-4o-2024-08-06',
  /** Shuts down 2026-10-23 (OpenAI's substitute: gpt-5.6-sol). */
  GPT_4O_2024_05_13 = 'gpt-4o-2024-05-13',

  GPT_4O_MINI = 'gpt-4o-mini',
  GPT_4O_MINI_2024_07_18 = 'gpt-4o-mini-2024-07-18',

  /** o1 and o1-pro shut down 2026-10-23 (OpenAI's substitute: gpt-5.6-sol). */
  OPENAI_O1 = 'o1',
  OPENAI_O1_2024_12_17 = 'o1-2024-12-17',

  OPENAI_O1_PRO = 'o1-pro',
  OPENAI_O1_PRO_2025_03_19 = 'o1-pro-2025-03-19',

  /** Shut down 2025-10-27. */
  OPENAI_O1_MINI = 'o1-mini',
  OPENAI_O1_MINI_2024_09_12 = 'o1-mini-2024-09-12',

  /** The dated o3 and o3-pro snapshots shut down 2026-12-11 (OpenAI's substitute: gpt-5.6-sol). */
  OPENAI_O3 = 'o3',
  OPENAI_O3_2025_04_16 = 'o3-2025-04-16',

  /** Shuts down 2026-10-23 (OpenAI's substitute: gpt-5.6-sol). */
  OPENAI_O3_MINI = 'o3-mini',
  OPENAI_O3_MINI_2025_01_31 = 'o3-mini-2025-01-31',

  OPENAI_O3_PRO = 'o3-pro',
  OPENAI_O3_PRO_2025_06_10 = 'o3-pro-2025-06-10',

  /** Shuts down 2026-10-23 (OpenAI's substitute: gpt-5.6-terra). */
  OPENAI_O4_MINI = 'o4-mini',
  OPENAI_O4_MINI_2025_04_16 = 'o4-mini-2025-04-16',

  GPT_4_1 = 'gpt-4.1',
  GPT_4_1_2025_04_14 = 'gpt-4.1-2025-04-14',

  GPT_4_1_MINI = 'gpt-4.1-mini',
  GPT_4_1_MINI_2025_04_14 = 'gpt-4.1-mini-2025-04-14',

  /** Shuts down 2026-10-23 (OpenAI's substitute: gpt-5.6-luna). */
  GPT_4_1_NANO = 'gpt-4.1-nano',
  GPT_4_1_NANO_2025_04_14 = 'gpt-4.1-nano-2025-04-14',

  /** The dated gpt-5, gpt-5-mini and gpt-5-nano snapshots shut down 2026-12-11 (OpenAI's
   * substitutes: gpt-5.6-sol, gpt-5.6-terra, gpt-5.6-luna). */
  GPT_5 = 'gpt-5',
  GPT_5_2025_08_07 = 'gpt-5-2025-08-07',

  GPT_5_MINI = 'gpt-5-mini',
  GPT_5_MINI_2025_08_07 = 'gpt-5-mini-2025-08-07',

  GPT_5_NANO = 'gpt-5-nano',
  GPT_5_NANO_2025_08_07 = 'gpt-5-nano-2025-08-07',

  /** Every chat-latest id is shut down: gpt-5 and gpt-5.1 on 2026-07-23, gpt-5.2 on 2026-08-10. */
  GPT_5_CHAT_LATEST = 'gpt-5-chat-latest',
  GPT_5_CHAT_LATEST_2025_08_07 = 'gpt-5-chat-latest-2025-08-07',

  GPT_5_1_CHAT_LATEST = 'gpt-5.1-chat-latest',
  GPT_5_1 = 'gpt-5.1',
  GPT_5_1_2025_11_13 = 'gpt-5.1-2025-11-13',

  GPT_5_2 = 'gpt-5.2',
  /** Never a real snapshot id; OpenAI's is gpt-5.2-2025-12-11. Same for the dated Pro, 5.4 and
   * 5.4 Pro values ending 12-09 / 03-17 below. */
  GPT_5_2_2025_12_09 = 'gpt-5.2-2025-12-09',
  GPT_5_2_2025_12_11 = 'gpt-5.2-2025-12-11',

  GPT_5_2_CHAT_LATEST = 'gpt-5.2-chat-latest',
  GPT_5_2_CHAT_LATEST_2025_12_09 = 'gpt-5.2-chat-latest-2025-12-09',

  GPT_5_2_PRO = 'gpt-5.2-pro',
  GPT_5_2_PRO_2025_12_09 = 'gpt-5.2-pro-2025-12-09',
  GPT_5_2_PRO_2025_12_11 = 'gpt-5.2-pro-2025-12-11',

  GPT_5_4 = 'gpt-5.4',
  GPT_5_4_2026_03_17 = 'gpt-5.4-2026-03-17',
  GPT_5_4_2026_03_05 = 'gpt-5.4-2026-03-05',

  GPT_5_4_MINI = 'gpt-5.4-mini',
  GPT_5_4_MINI_2026_03_17 = 'gpt-5.4-mini-2026-03-17',

  GPT_5_4_NANO = 'gpt-5.4-nano',
  GPT_5_4_NANO_2026_03_17 = 'gpt-5.4-nano-2026-03-17',

  GPT_5_4_PRO = 'gpt-5.4-pro',
  GPT_5_4_PRO_2026_03_17 = 'gpt-5.4-pro-2026-03-17',
  GPT_5_4_PRO_2026_03_05 = 'gpt-5.4-pro-2026-03-05',

  GPT_5_5 = 'gpt-5.5',
  GPT_5_5_2026_04_23 = 'gpt-5.5-2026-04-23',

  GPT_5_5_PRO = 'gpt-5.5-pro',
  GPT_5_5_PRO_2026_04_23 = 'gpt-5.5-pro-2026-04-23',

  GPT_5_6 = 'gpt-5.6',
  GPT_5_6_SOL = 'gpt-5.6-sol',
  GPT_5_6_TERRA = 'gpt-5.6-terra',
  GPT_5_6_LUNA = 'gpt-5.6-luna',

  GPT_6_ASTRA = 'gpt-6-astra',
  GPT_6_SOL = 'gpt-6-sol',
  GPT_6_LUNA = 'gpt-6-luna',

  /** No dated snapshot: OpenAI lists the alias as its own only snapshot. */
  GPT_6_1_SOL = 'gpt-6.1-sol',
}

/** OpenAI models proficient enough to drive agentic workflows (flagship + mid + budget tiers).
 * The first entry is the Codex harness default, so it is the balanced GPT-6.1 Sol rather than the
 * pricier GPT-6 Astra. */
export const OpenAiAgentModels = [
  OpenAiModels.GPT_6_1_SOL,
  OpenAiModels.GPT_6_SOL,
  OpenAiModels.GPT_6_ASTRA,
  OpenAiModels.GPT_6_LUNA,
  OpenAiModels.GPT_5_6,
  OpenAiModels.GPT_5_6_TERRA,
  OpenAiModels.GPT_5_6_LUNA,
  OpenAiModels.GPT_5_5,
  OpenAiModels.GPT_5_4,
  OpenAiModels.GPT_5_4_MINI,
  OpenAiModels.GPT_5_2,
  OpenAiModels.GPT_5_1,
  OpenAiModels.GPT_5,
  OpenAiModels.GPT_5_MINI,
] as const;

export const OpenAiModelInformationMap: Record<OpenAiModels, AiModelInformation> = {
  [OpenAiModels.GPT_4O]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 4o',
    providerLabel: PROVIDER_LABEL,
    date: '2024-08-06',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(2.5),
      output: convertCostPerMTokensToCostPer1kTokens(10),
    },
    maxTokens: 16384,
  },
  [OpenAiModels.GPT_4O_2024_08_06]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 4o 2024-08-06',
    providerLabel: PROVIDER_LABEL,
    date: '2024-08-06',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(2.5),
      output: convertCostPerMTokensToCostPer1kTokens(10),
    },
    maxTokens: 16384,
  },
  [OpenAiModels.GPT_4O_2024_11_20]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 4o 2024-11-20',
    providerLabel: PROVIDER_LABEL,
    date: '2024-11-20',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(2.5),
      output: convertCostPerMTokensToCostPer1kTokens(10),
    },
    maxTokens: 16384,
  },
  [OpenAiModels.GPT_4O_2024_05_13]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 4o 2024-05-13',
    providerLabel: PROVIDER_LABEL,
    date: '2024-05-13',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(5),
      output: convertCostPerMTokensToCostPer1kTokens(15),
    },
    maxTokens: 16384,
  },

  [OpenAiModels.GPT_4O_MINI]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 4o Mini',
    providerLabel: PROVIDER_LABEL,
    date: '2024-07-18',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(0.150),
      output: convertCostPerMTokensToCostPer1kTokens(0.600),
    },
    maxTokens: 16384,
  },

  [OpenAiModels.GPT_4O_MINI_2024_07_18]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 4o Mini 2024-07-18',
    providerLabel: PROVIDER_LABEL,
    date: '2024-07-18',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(0.150),
      output: convertCostPerMTokensToCostPer1kTokens(0.600),
    },
    maxTokens: 16384,
  },

  [OpenAiModels.OPENAI_O1]: {
    provider: AiProvider.OpenAI,
    label: 'o1',
    providerLabel: PROVIDER_LABEL,
    date: '2024-12-17',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(15),
      output: convertCostPerMTokensToCostPer1kTokens(60),
    },
    maxTokens: 100000,
  },

  [OpenAiModels.OPENAI_O1_2024_12_17]: {
    provider: AiProvider.OpenAI,
    label: 'o1 2024-12-17',
    providerLabel: PROVIDER_LABEL,
    date: '2024-12-17',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(15),
      output: convertCostPerMTokensToCostPer1kTokens(60),
    },
    maxTokens: 100000,
  },

  [OpenAiModels.OPENAI_O1_PRO]: {
    provider: AiProvider.OpenAI,
    label: 'o1 Pro',
    providerLabel: PROVIDER_LABEL,
    date: '2025-03-19',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(150),
      output: convertCostPerMTokensToCostPer1kTokens(600),
    },
    maxTokens: 100000,
  },
  [OpenAiModels.OPENAI_O1_PRO_2025_03_19]: {
    provider: AiProvider.OpenAI,
    label: 'o1 Pro 2025-03-19',
    providerLabel: PROVIDER_LABEL,
    date: '2025-03-19',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(150),
      output: convertCostPerMTokensToCostPer1kTokens(600),
    },
    maxTokens: 100000,
  },

  [OpenAiModels.OPENAI_O1_MINI]: {
    provider: AiProvider.OpenAI,
    label: 'o1 Mini',
    providerLabel: PROVIDER_LABEL,
    date: '2024-09-12',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(1.1),
      output: convertCostPerMTokensToCostPer1kTokens(4.4),
    },
    maxTokens: 65536,
  },
  [OpenAiModels.OPENAI_O1_MINI_2024_09_12]: {
    provider: AiProvider.OpenAI,
    label: 'o1 Mini 2024-09-12',
    providerLabel: PROVIDER_LABEL,
    date: '2024-09-12',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(1.1),
      output: convertCostPerMTokensToCostPer1kTokens(4.4),
    },
    maxTokens: 65536,
  },

  [OpenAiModels.OPENAI_O3]: {
    provider: AiProvider.OpenAI,
    label: 'o3',
    providerLabel: PROVIDER_LABEL,
    date: '2025-04-16',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(2),
      output: convertCostPerMTokensToCostPer1kTokens(8),
    },
    maxTokens: 100000,
  },
  [OpenAiModels.OPENAI_O3_2025_04_16]: {
    provider: AiProvider.OpenAI,
    label: 'o3 2025-04-16',
    providerLabel: PROVIDER_LABEL,
    date: '2025-04-16',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(2),
      output: convertCostPerMTokensToCostPer1kTokens(8),
    },
    maxTokens: 100000,
  },

  [OpenAiModels.OPENAI_O3_MINI]: {
    provider: AiProvider.OpenAI,
    label: 'o3 Mini',
    providerLabel: PROVIDER_LABEL,
    date: '2025-01-31',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(1.1),
      output: convertCostPerMTokensToCostPer1kTokens(4.4),
    },
    maxTokens: 100000,
  },
  [OpenAiModels.OPENAI_O3_MINI_2025_01_31]: {
    provider: AiProvider.OpenAI,
    label: 'o3 Mini 2025-01-31',
    providerLabel: PROVIDER_LABEL,
    date: '2025-01-31',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(1.1),
      output: convertCostPerMTokensToCostPer1kTokens(4.4),
    },
    maxTokens: 100000,
  },

  [OpenAiModels.OPENAI_O3_PRO]: {
    provider: AiProvider.OpenAI,
    label: 'o3 Pro',
    providerLabel: PROVIDER_LABEL,
    date: '2025-06-10',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(20),
      output: convertCostPerMTokensToCostPer1kTokens(80),
    },
    maxTokens: 100000,
  },
  [OpenAiModels.OPENAI_O3_PRO_2025_06_10]: {
    provider: AiProvider.OpenAI,
    label: 'o3 Pro 2025-06-10',
    providerLabel: PROVIDER_LABEL,
    date: '2025-06-10',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(20),
      output: convertCostPerMTokensToCostPer1kTokens(80),
    },
    maxTokens: 100000,
  },

  [OpenAiModels.OPENAI_O4_MINI]: {
    provider: AiProvider.OpenAI,
    label: 'o4 Mini',
    providerLabel: PROVIDER_LABEL,
    date: '2025-04-16',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(1.1),
      output: convertCostPerMTokensToCostPer1kTokens(4.4),
    },
    maxTokens: 100000,
  },
  [OpenAiModels.OPENAI_O4_MINI_2025_04_16]: {
    provider: AiProvider.OpenAI,
    label: 'o4 Mini 2025-04-16',
    providerLabel: PROVIDER_LABEL,
    date: '2025-04-16',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(1.1),
      output: convertCostPerMTokensToCostPer1kTokens(4.4),
    },
    maxTokens: 100000,
  },

  [OpenAiModels.GPT_4_1]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 4.1',
    providerLabel: PROVIDER_LABEL,
    date: '2025-04-14',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(2),
      output: convertCostPerMTokensToCostPer1kTokens(8),
    },
    maxTokens: 32768,
  },
  [OpenAiModels.GPT_4_1_2025_04_14]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 4.1 2025-04-14',
    providerLabel: PROVIDER_LABEL,
    date: '2025-04-14',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(2),
      output: convertCostPerMTokensToCostPer1kTokens(8),
    },
    maxTokens: 32768,
  },

  [OpenAiModels.GPT_4_1_MINI]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 4.1 Mini',
    providerLabel: PROVIDER_LABEL,
    date: '2025-04-14',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(0.4),
      output: convertCostPerMTokensToCostPer1kTokens(1.6),
    },
    maxTokens: 32768,
  },
  [OpenAiModels.GPT_4_1_MINI_2025_04_14]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 4.1 Mini 2025-04-14',
    providerLabel: PROVIDER_LABEL,
    date: '2025-04-14',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(0.4),
      output: convertCostPerMTokensToCostPer1kTokens(1.6),
    },
    maxTokens: 32768,
  },

  [OpenAiModels.GPT_4_1_NANO]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 4.1 Nano',
    providerLabel: PROVIDER_LABEL,
    date: '2025-04-14',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(0.1),
      output: convertCostPerMTokensToCostPer1kTokens(0.4),
    },
    maxTokens: 32768,
  },
  [OpenAiModels.GPT_4_1_NANO_2025_04_14]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 4.1 Nano 2025-04-14',
    providerLabel: PROVIDER_LABEL,
    date: '2025-04-14',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(0.1),
      output: convertCostPerMTokensToCostPer1kTokens(0.4),
    },
    maxTokens: 32768,
  },

  [OpenAiModels.GPT_5]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5',
    providerLabel: PROVIDER_LABEL,
    date: '2025-08-07',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(1.25),
      output: convertCostPerMTokensToCostPer1kTokens(10),
    },
    maxTokens: 128000,
  },
  [OpenAiModels.GPT_5_2025_08_07]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5 2025-08-07',
    providerLabel: PROVIDER_LABEL,
    date: '2025-08-07',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(1.25),
      output: convertCostPerMTokensToCostPer1kTokens(10),
    },
    maxTokens: 128000,
  },

  [OpenAiModels.GPT_5_MINI]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5 Mini',
    providerLabel: PROVIDER_LABEL,
    date: '2025-08-07',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(0.25),
      output: convertCostPerMTokensToCostPer1kTokens(2),
    },
    maxTokens: 128000,
  },
  [OpenAiModels.GPT_5_MINI_2025_08_07]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5 Mini 2025-08-07',
    providerLabel: PROVIDER_LABEL,
    date: '2025-08-07',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(0.25),
      output: convertCostPerMTokensToCostPer1kTokens(2),
    },
    maxTokens: 128000,
  },

  [OpenAiModels.GPT_5_NANO]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5 Nano',
    providerLabel: PROVIDER_LABEL,
    date: '2025-08-07',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(0.05),
      output: convertCostPerMTokensToCostPer1kTokens(0.4),
    },
    maxTokens: 128000,
  },
  [OpenAiModels.GPT_5_NANO_2025_08_07]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5 Nano 2025-08-07',
    providerLabel: PROVIDER_LABEL,
    date: '2025-08-07',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(0.05),
      output: convertCostPerMTokensToCostPer1kTokens(0.4),
    },
    maxTokens: 128000,
  },

  [OpenAiModels.GPT_5_CHAT_LATEST]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5 Chat Latest',
    providerLabel: PROVIDER_LABEL,
    date: '2025-08-07',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(1.25),
      output: convertCostPerMTokensToCostPer1kTokens(10),
    },
    maxTokens: 128000,
  },
  [OpenAiModels.GPT_5_CHAT_LATEST_2025_08_07]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5 Chat Latest 2025-08-07',
    providerLabel: PROVIDER_LABEL,
    date: '2025-08-07',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(1.25),
      output: convertCostPerMTokensToCostPer1kTokens(10),
    },
    maxTokens: 128000,
  },

  [OpenAiModels.GPT_5_1_CHAT_LATEST]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5.1 Chat Latest',
    providerLabel: PROVIDER_LABEL,
    date: '2025-11-13',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(1.25),
      output: convertCostPerMTokensToCostPer1kTokens(10),
    },
    maxTokens: 128000,
  },
  [OpenAiModels.GPT_5_1]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5.1',
    providerLabel: PROVIDER_LABEL,
    date: '2025-11-13',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(1.25),
      output: convertCostPerMTokensToCostPer1kTokens(10),
    },
    maxTokens: 128000,
  },
  [OpenAiModels.GPT_5_1_2025_11_13]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5.1 2025-11-13',
    providerLabel: PROVIDER_LABEL,
    date: '2025-11-13',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(1.25),
      output: convertCostPerMTokensToCostPer1kTokens(10),
    },
    maxTokens: 128000,
  },

  [OpenAiModels.GPT_5_2]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5.2',
    providerLabel: PROVIDER_LABEL,
    date: '2025-12-11',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(1.75),
      output: convertCostPerMTokensToCostPer1kTokens(14),
    },
    maxTokens: 128000,
  },
  [OpenAiModels.GPT_5_2_2025_12_09]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5.2 2025-12-09',
    providerLabel: PROVIDER_LABEL,
    date: '2025-12-11',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(1.75),
      output: convertCostPerMTokensToCostPer1kTokens(14),
    },
    maxTokens: 128000,
  },
  [OpenAiModels.GPT_5_2_2025_12_11]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5.2 2025-12-11',
    providerLabel: PROVIDER_LABEL,
    date: '2025-12-11',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(1.75),
      output: convertCostPerMTokensToCostPer1kTokens(14),
    },
    maxTokens: 128000,
  },

  [OpenAiModels.GPT_5_2_CHAT_LATEST]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5.2 Chat Latest',
    providerLabel: PROVIDER_LABEL,
    date: '2025-12-09',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(1.75),
      output: convertCostPerMTokensToCostPer1kTokens(14),
    },
    maxTokens: 128000,
  },
  [OpenAiModels.GPT_5_2_CHAT_LATEST_2025_12_09]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5.2 Chat Latest 2025-12-09',
    providerLabel: PROVIDER_LABEL,
    date: '2025-12-09',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(1.75),
      output: convertCostPerMTokensToCostPer1kTokens(14),
    },
    maxTokens: 128000,
  },

  [OpenAiModels.GPT_5_2_PRO]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5.2 Pro',
    providerLabel: PROVIDER_LABEL,
    date: '2025-12-11',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(21),
      output: convertCostPerMTokensToCostPer1kTokens(168),
    },
    maxTokens: 128000,
  },
  [OpenAiModels.GPT_5_2_PRO_2025_12_09]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5.2 Pro 2025-12-09',
    providerLabel: PROVIDER_LABEL,
    date: '2025-12-11',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(21),
      output: convertCostPerMTokensToCostPer1kTokens(168),
    },
    maxTokens: 128000,
  },
  [OpenAiModels.GPT_5_2_PRO_2025_12_11]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5.2 Pro 2025-12-11',
    providerLabel: PROVIDER_LABEL,
    date: '2025-12-11',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(21),
      output: convertCostPerMTokensToCostPer1kTokens(168),
    },
    maxTokens: 128000,
  },

  /** From GPT-5.4 on, a prompt over 272K input tokens bills the whole request at 2x input and
   * 1.5x output (mini and nano excepted). */
  [OpenAiModels.GPT_5_4]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5.4',
    providerLabel: PROVIDER_LABEL,
    date: '2026-03-05',
    costPer1kTokens: {
      272000: {
        input: convertCostPerMTokensToCostPer1kTokens(2.5),
        output: convertCostPerMTokensToCostPer1kTokens(15),
      },
      default: {
        input: convertCostPerMTokensToCostPer1kTokens(5),
        output: convertCostPerMTokensToCostPer1kTokens(22.5),
      },
    },
    maxTokens: 128000,
  },
  [OpenAiModels.GPT_5_4_2026_03_17]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5.4 2026-03-17',
    providerLabel: PROVIDER_LABEL,
    date: '2026-03-05',
    costPer1kTokens: {
      272000: {
        input: convertCostPerMTokensToCostPer1kTokens(2.5),
        output: convertCostPerMTokensToCostPer1kTokens(15),
      },
      default: {
        input: convertCostPerMTokensToCostPer1kTokens(5),
        output: convertCostPerMTokensToCostPer1kTokens(22.5),
      },
    },
    maxTokens: 128000,
  },
  [OpenAiModels.GPT_5_4_2026_03_05]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5.4 2026-03-05',
    providerLabel: PROVIDER_LABEL,
    date: '2026-03-05',
    costPer1kTokens: {
      272000: {
        input: convertCostPerMTokensToCostPer1kTokens(2.5),
        output: convertCostPerMTokensToCostPer1kTokens(15),
      },
      default: {
        input: convertCostPerMTokensToCostPer1kTokens(5),
        output: convertCostPerMTokensToCostPer1kTokens(22.5),
      },
    },
    maxTokens: 128000,
  },

  [OpenAiModels.GPT_5_4_MINI]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5.4 Mini',
    providerLabel: PROVIDER_LABEL,
    date: '2026-03-17',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(0.75),
      output: convertCostPerMTokensToCostPer1kTokens(4.5),
    },
    maxTokens: 128000,
  },
  [OpenAiModels.GPT_5_4_MINI_2026_03_17]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5.4 Mini 2026-03-17',
    providerLabel: PROVIDER_LABEL,
    date: '2026-03-17',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(0.75),
      output: convertCostPerMTokensToCostPer1kTokens(4.5),
    },
    maxTokens: 128000,
  },

  [OpenAiModels.GPT_5_4_NANO]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5.4 Nano',
    providerLabel: PROVIDER_LABEL,
    date: '2026-03-17',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(0.2),
      output: convertCostPerMTokensToCostPer1kTokens(1.25),
    },
    maxTokens: 128000,
  },
  [OpenAiModels.GPT_5_4_NANO_2026_03_17]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5.4 Nano 2026-03-17',
    providerLabel: PROVIDER_LABEL,
    date: '2026-03-17',
    costPer1kTokens: {
      input: convertCostPerMTokensToCostPer1kTokens(0.2),
      output: convertCostPerMTokensToCostPer1kTokens(1.25),
    },
    maxTokens: 128000,
  },

  [OpenAiModels.GPT_5_4_PRO]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5.4 Pro',
    providerLabel: PROVIDER_LABEL,
    date: '2026-03-05',
    costPer1kTokens: {
      272000: {
        input: convertCostPerMTokensToCostPer1kTokens(30),
        output: convertCostPerMTokensToCostPer1kTokens(180),
      },
      default: {
        input: convertCostPerMTokensToCostPer1kTokens(60),
        output: convertCostPerMTokensToCostPer1kTokens(270),
      },
    },
    maxTokens: 128000,
  },
  [OpenAiModels.GPT_5_4_PRO_2026_03_17]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5.4 Pro 2026-03-17',
    providerLabel: PROVIDER_LABEL,
    date: '2026-03-05',
    costPer1kTokens: {
      272000: {
        input: convertCostPerMTokensToCostPer1kTokens(30),
        output: convertCostPerMTokensToCostPer1kTokens(180),
      },
      default: {
        input: convertCostPerMTokensToCostPer1kTokens(60),
        output: convertCostPerMTokensToCostPer1kTokens(270),
      },
    },
    maxTokens: 128000,
  },
  [OpenAiModels.GPT_5_4_PRO_2026_03_05]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5.4 Pro 2026-03-05',
    providerLabel: PROVIDER_LABEL,
    date: '2026-03-05',
    costPer1kTokens: {
      272000: {
        input: convertCostPerMTokensToCostPer1kTokens(30),
        output: convertCostPerMTokensToCostPer1kTokens(180),
      },
      default: {
        input: convertCostPerMTokensToCostPer1kTokens(60),
        output: convertCostPerMTokensToCostPer1kTokens(270),
      },
    },
    maxTokens: 128000,
  },

  [OpenAiModels.GPT_5_5]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5.5',
    providerLabel: PROVIDER_LABEL,
    date: '2026-04-24',
    costPer1kTokens: {
      272000: {
        input: convertCostPerMTokensToCostPer1kTokens(5),
        output: convertCostPerMTokensToCostPer1kTokens(30),
      },
      default: {
        input: convertCostPerMTokensToCostPer1kTokens(10),
        output: convertCostPerMTokensToCostPer1kTokens(45),
      },
    },
    maxTokens: 128000,
  },
  [OpenAiModels.GPT_5_5_2026_04_23]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5.5 2026-04-23',
    providerLabel: PROVIDER_LABEL,
    date: '2026-04-24',
    costPer1kTokens: {
      272000: {
        input: convertCostPerMTokensToCostPer1kTokens(5),
        output: convertCostPerMTokensToCostPer1kTokens(30),
      },
      default: {
        input: convertCostPerMTokensToCostPer1kTokens(10),
        output: convertCostPerMTokensToCostPer1kTokens(45),
      },
    },
    maxTokens: 128000,
  },

  [OpenAiModels.GPT_5_5_PRO]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5.5 Pro',
    providerLabel: PROVIDER_LABEL,
    date: '2026-04-24',
    costPer1kTokens: {
      272000: {
        input: convertCostPerMTokensToCostPer1kTokens(30),
        output: convertCostPerMTokensToCostPer1kTokens(180),
      },
      default: {
        input: convertCostPerMTokensToCostPer1kTokens(60),
        output: convertCostPerMTokensToCostPer1kTokens(270),
      },
    },
    maxTokens: 128000,
  },
  [OpenAiModels.GPT_5_5_PRO_2026_04_23]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5.5 Pro 2026-04-23',
    providerLabel: PROVIDER_LABEL,
    date: '2026-04-24',
    costPer1kTokens: {
      272000: {
        input: convertCostPerMTokensToCostPer1kTokens(30),
        output: convertCostPerMTokensToCostPer1kTokens(180),
      },
      default: {
        input: convertCostPerMTokensToCostPer1kTokens(60),
        output: convertCostPerMTokensToCostPer1kTokens(270),
      },
    },
    maxTokens: 128000,
  },

  /** Sol's $4/$20 is OpenAI's 2026-08-21 promotional rate, "available at least through
   * November 21, 2026"; its list rate is $5/$30. Revisit these two entries after that date. */
  [OpenAiModels.GPT_5_6]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5.6',
    providerLabel: PROVIDER_LABEL,
    date: '2026-07-09',
    costPer1kTokens: {
      272000: {
        input: convertCostPerMTokensToCostPer1kTokens(4),
        output: convertCostPerMTokensToCostPer1kTokens(20),
      },
      default: {
        input: convertCostPerMTokensToCostPer1kTokens(8),
        output: convertCostPerMTokensToCostPer1kTokens(30),
      },
    },
    maxTokens: 128000,
  },
  [OpenAiModels.GPT_5_6_SOL]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5.6 Sol',
    providerLabel: PROVIDER_LABEL,
    date: '2026-07-09',
    costPer1kTokens: {
      272000: {
        input: convertCostPerMTokensToCostPer1kTokens(4),
        output: convertCostPerMTokensToCostPer1kTokens(20),
      },
      default: {
        input: convertCostPerMTokensToCostPer1kTokens(8),
        output: convertCostPerMTokensToCostPer1kTokens(30),
      },
    },
    maxTokens: 128000,
  },
  /** Repriced 2026-07-30: Terra -20%, Luna -80%. */
  [OpenAiModels.GPT_5_6_TERRA]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5.6 Terra',
    providerLabel: PROVIDER_LABEL,
    date: '2026-07-09',
    costPer1kTokens: {
      272000: {
        input: convertCostPerMTokensToCostPer1kTokens(2),
        output: convertCostPerMTokensToCostPer1kTokens(12),
      },
      default: {
        input: convertCostPerMTokensToCostPer1kTokens(4),
        output: convertCostPerMTokensToCostPer1kTokens(18),
      },
    },
    maxTokens: 128000,
  },
  [OpenAiModels.GPT_5_6_LUNA]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 5.6 Luna',
    providerLabel: PROVIDER_LABEL,
    date: '2026-07-09',
    costPer1kTokens: {
      272000: {
        input: convertCostPerMTokensToCostPer1kTokens(0.2),
        output: convertCostPerMTokensToCostPer1kTokens(1.2),
      },
      default: {
        input: convertCostPerMTokensToCostPer1kTokens(0.4),
        output: convertCostPerMTokensToCostPer1kTokens(1.8),
      },
    },
    maxTokens: 128000,
  },

  [OpenAiModels.GPT_6_ASTRA]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 6 Astra',
    providerLabel: PROVIDER_LABEL,
    date: '2026-09-03',
    costPer1kTokens: {
      272000: {
        input: convertCostPerMTokensToCostPer1kTokens(10),
        output: convertCostPerMTokensToCostPer1kTokens(50),
      },
      default: {
        input: convertCostPerMTokensToCostPer1kTokens(20),
        output: convertCostPerMTokensToCostPer1kTokens(75),
      },
    },
    maxTokens: 128000,
  },
  [OpenAiModels.GPT_6_SOL]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 6 Sol',
    providerLabel: PROVIDER_LABEL,
    date: '2026-09-22',
    costPer1kTokens: {
      272000: {
        input: convertCostPerMTokensToCostPer1kTokens(2),
        output: convertCostPerMTokensToCostPer1kTokens(10),
      },
      default: {
        input: convertCostPerMTokensToCostPer1kTokens(4),
        output: convertCostPerMTokensToCostPer1kTokens(15),
      },
    },
    maxTokens: 128000,
  },
  [OpenAiModels.GPT_6_LUNA]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 6 Luna',
    providerLabel: PROVIDER_LABEL,
    date: '2026-09-22',
    costPer1kTokens: {
      272000: {
        input: convertCostPerMTokensToCostPer1kTokens(0.1),
        output: convertCostPerMTokensToCostPer1kTokens(0.5),
      },
      default: {
        input: convertCostPerMTokensToCostPer1kTokens(0.2),
        output: convertCostPerMTokensToCostPer1kTokens(0.75),
      },
    },
    maxTokens: 128000,
  },

  /** Same input and output rates as GPT-6 Sol; only its cached-input rate is lower, which this
   * map does not model. */
  [OpenAiModels.GPT_6_1_SOL]: {
    provider: AiProvider.OpenAI,
    label: 'GPT 6.1 Sol',
    providerLabel: PROVIDER_LABEL,
    date: '2026-09-29',
    costPer1kTokens: {
      272000: {
        input: convertCostPerMTokensToCostPer1kTokens(2),
        output: convertCostPerMTokensToCostPer1kTokens(10),
      },
      default: {
        input: convertCostPerMTokensToCostPer1kTokens(4),
        output: convertCostPerMTokensToCostPer1kTokens(15),
      },
    },
    maxTokens: 128000,
  },
} as const;
```
