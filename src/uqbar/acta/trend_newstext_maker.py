# SPDX-License-Identifier: MIT
# uqbar/acta/newstext_maker.py
"""
Acta Diurna | Newstext Maker
===========================

Overview
--------
Placeholder.

Additional Info
---------------
micromamba install -c conda-forge openai
export OPENROUTER_API_KEY="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"
meta-llama/llama-3.1-405b-instruct:free

Metadata
--------
- Project: Acta diurna
- License: MIT
"""

# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from __future__ import annotations

import re
from collections import deque
from collections.abc import Iterable, Mapping, Sequence
from time import sleep
from typing import Any, Literal

from openai import OpenAI
from openai.types.chat import ChatCompletion

from uqbar.acta.trends import Trend, TrendList
from uqbar.utils.stats import get_random
from uqbar.utils.utils import PassError, dtnow

# -------------------------------------------------------------------------------------
# Constants
# -------------------------------------------------------------------------------------
DEFAULT_OPENROUTER_API_KEY: str = (
    "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"
)

DEFAULT_MODEL_ID: str = "allenai/olmo-3.1-32b-think:free"

DEFAULT_ROLE: ROLEType = "user"

DEFAULT_BASE_URL:str = "https://openrouter.ai/api/v1"

DEFAULT_API_KEY_LOC:str = "env"

DEFAULT_HEADERS: dict[str, str] = {
    "HTTP-Referer": "https://www.gusmaolab.org",
    "X-Title": "Acta Diurna",
}

DEFAULT_EXTRA_BODY: dict[str, str] = {"user": "acta-local-test"}

DEFAULT_MAX_RETRIES_MODEL: int = 3

SLEEP_MIN_BASE: float = 2.6


_TRIPLE_BACKTICK_RE = re.compile(
    r"```(?:[^\n`]*)\n?([\s\S]*?)```",  # optional language label, optional newline,
)                                       # then capture lazily


# Model Dictionary -> key: [name, id, tokens, context]
MODEL_PARAMETER_DICT: dict[str, list[str | int]] = {
  "allenai_31": [
    "AllenAI: Olmo 3.1 32B Think", "allenai/olmo-3.1-32b-think:free",
    38_000_000_000, 66_000], # TOP 1
  "mistral_small_24b": [
    "Mistral: Mistral Small 3.1 24B", "mistralai/mistral-small-3.1-24b-instruct:free",
    242_000_000, 128_000], # TOP 2
  "meta_llama_70b": [
    "Meta: Llama 3.3 70B Instruct", "meta-llama/llama-3.3-70b-instruct:free",
    25_000_000_000, 131_000], # TOP 3
  "google_gemma_27b": [
    "Google: Gemma 3 27B", "google/gemma-3-27b-it:free",
    27_000_000_000, 131_000], # TOP 4
  "deepseek_r1": [
    "DeepSeek: R1 0528", "deepseek/deepseek-r1-0528:free",
    19_000_000_000, 164_000], # TOP 5
  "arcee_ai": [
    "Arcee AI: Trinity Mini", "arcee-ai/trinity-mini:free",
    366_000_000, 131_000], # TOP 6
  "tng": [
    "TNG: R1T Chimera", "tngtech/tng-r1t-chimera:free",
    128_000_000_000, 164_000],
  "allenai_3": [
    "AllenAI: Olmo 3 32B Think", "allenai/olmo-3-32b-think:free",
    12_000_000_000, 66_000],
  "openai_oss_120b": [
    "OpenAI: gpt-oss-120b", "openai/gpt-oss-120b:free",
    745_000_000, 131_000],
  "openai_oss_20b": [
    "OpenAI: gpt-oss-20b", "openai/gpt-oss-20b:free",
    38_000_000_000, 131_000],
  "z_ai": [
    "Z.AI: GLM 4.5 Air", "z-ai/glm-4.5-air:free",
    176_000_000_000, 131_000],
  "moonshotaI": [
    "MoonshotAI: Kimi K2 0711", "moonshotai/kimi-k2:free",
    699_000_000, 33_000],
  "google_gemma_3n_2b": [
    "Google: Gemma 3n 2B", "google/gemma-3n-e2b-it:free",
    292_000_000, 8_000],
  "tng_deepseek_r1t2": [
    "TNG: DeepSeek R1T2 Chimera", "tngtech/deepseek-r1t2-chimera:free",
    949_000_000_000, 164_000],
  "google_gemma_3n_4b": [
    "Google: Gemma 3n 4B", "google/gemma-3n-e4b-it:free",
    415_000_000, 8_000],
  "qwen_4b": [
    "Qwen: Qwen3 4B", "qwen/qwen3-4b:free",
    574_000_000, 41_000],
  "google_gemma_4b": [
    "Google: Gemma 3 4B", "google/gemma-3-4b-it:free",
    231_000_000, 33_000],
  "google_gemma_12b": [
    "Google: Gemma 3 12B", "google/gemma-3-12b-it:free",
    424_000_000, 33_000],
  "meta_llama_3b": [
    "Meta: Llama 3.2 3B Instruct", "meta-llama/llama-3.2-3b-instruct:free",
    803_000_000, 131_000],
  "qwen_7b": [
    "Qwen: Qwen2.5-VL 7B Instruct", "qwen/qwen-2.5-vl-7b-instruct:free",
    75_000_000, 33_000],
  "meta_llama_405b": [
    "Meta: Llama 3.1 405B Instruct", "meta-llama/llama-3.1-405b-instruct:free",
    165_000_000, 131_000],
  "mistral_7b": [
    "Mistral: Mistral 7B Instruct", "mistralai/mistral-7b-instruct:free",
    574_000_000, 33_000],
  # "kwaipilot": [
  #   "Kwaipilot: KAT-Coder-Pro V1", "kwaipilot/kat-coder-pro:free",
  #   987_000_000_000, 256_000], # X
  # "nvidia_nemo_12b": [
  #   "NVIDIA: Nemotron Nano 12B 2 VL", "nvidia/nemotron-nano-12b-v2-vl:free",
  #   332_000_000_000, 128_000], # X
  # "tongyi": [
  #   "Tongyi: DeepResearch 30B A3B", "alibaba/tongyi-deepresearch-30b-a3b:free",
  #   15_000_000_000, 131_000], # X
  # "nvidia_nemo_9b": [
  #   "NVIDIA: Nemotron Nano 9B V2", "nvidia/nemotron-nano-9b-v2:free",
  #   374_000_000, 128_000], # X
  # "xiaomi": [
  #   "Xiaomi: MiMo-V2-Flash", "xiaomi/mimo-v2-flash:free",
  #   133_000_000_000, 262_000], # X
  # "financenvidia": [
  #   "FinanceNVIDIA: Nemotron 3 Nano 30B A3B", "nvidia/nemotron-3-nano-30b-a3b:free",
  #   174_000_000_000, 256_000], # X
  # "mistral_devstral": [
  #   "Mistral: Devstral 2 2512", "mistralai/devstral-2512:free",
  #   115_000_000_000, 262_000], # X
  # "nex_agi": [
  #   "Nex AGI: DeepSeek V3.1 Nex N1", "nex-agi/deepseek-v3.1-nex-n1:free",
  #   415_000_000_000, 131_000], # X
  # "qwen_coder_480b": [
  #   "Qwen: Qwen3 Coder 480B A35B", "qwen/qwen3-coder:free",
  #   35_000_000_000, 262_000], # X
  # "venice": [ # Venice: Uncensored
  #   "Venice", "cognitivecomputations/dolphin-mistral-24b-venice-edition:free",
  #   672_000_000, 33_000], # X
  # "tng_deepseek_r1t": [
  #   "TNG: DeepSeek R1T Chimera", "tngtech/deepseek-r1t-chimera:free",
  #   208_000_000_000, 164_000], # X
  # "google_gemini": [
  #   "Google: Gemini 2.0 Flash Experimental", "google/gemini-2.0-flash-exp:free",
  #   12_000_000_000, 105_000_000], # X
  # "nous_hermes_405b": [
  #   "Nous: Hermes 3 405B Instruct", "nousresearch/hermes-3-llama-3.1-405b:free",
  #   350_000_000, 131_000], # X
}


MODEL_NAME_LIST: list[str] = [
    "allenai_31", # TOP 1
    "mistral_small_24b", # TOP 2
    "meta_llama_70b", # TOP 3
    "google_gemma_27b", # TOP 4
    "deepseek_r1", # TOP 5
    "arcee_ai", # TOP 6
    "tng",
    "allenai_3",
    "openai_oss_120b",
    "openai_oss_20b",
    "z_ai",
    "moonshotaI",
    "google_gemma_3n_2b",
    "tng_deepseek_r1t2",
    "google_gemma_3n_4b",
    "qwen_4b",
    "google_gemma_4b",
    "google_gemma_12b",
    "meta_llama_3b",
    "qwen_7b",
    "meta_llama_405b",
    "mistral_7b",
    # "kwaipilot", # X
    # "nvidia_nemo_12b", # X
    # "tongyi", # X
    # "nvidia_nemo_9b", # X
    # "xiaomi", # X
    # "financenvidia", # X
    # "mistral_devstral", # X
    # "nex_agi", # X
    # "qwen_coder_480b", # X
    # "venice", # X
    # "tng_deepseek_r1t", # X
    # "google_gemini", # X
    # "nous_hermes_405b", # X
]


MODEL_KEY_DICT: dict[str, list[str]] = {
    "allenai_31": [
        "allenai/olmo-3.1-32b-think:free",
        "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",
        "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",
        "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",
    ], # TOP 1
    "mistral_small_24b": [
        "mistralai/mistral-small-3.1-24b-instruct:free",
        "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",
        "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",
        "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",
    ], # TOP 2
    "meta_llama_70b": [
        "meta-llama/llama-3.3-70b-instruct:free",
        "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",
        "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",
        "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",
    ], # TOP 3
    "google_gemma_27b": [
        "google/gemma-3-27b-it:free",
        "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",
        "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",
        "xxxxxxxxx",
    ], # TOP 4
    "deepseek_r1": [
        "deepseek/deepseek-r1-0528:free"
        "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",
        "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",
        "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",
    ], # TOP 5
    "arcee_ai": [
        "arcee-ai/trinity-mini:free",
        "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",
        "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",
        "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",
    ], # TOP 6
    "tng": [
        "tngtech/tng-r1t-chimera:free",
        "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",
        "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",
        "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",
    ],
    "allenai_3": [
        "allenai/olmo-3-32b-think:free",
        "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",
        "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",
        "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",
    ],
    "openai_oss_120b": [
        "openai/gpt-oss-120b:free",
        "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",
        "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",
        "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",
    ],
    "openai_oss_20b": [
        "openai/gpt-oss-20b:free",
        "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",
        "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",
        "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",
    ],
    "z_ai": [
        "z-ai/glm-4.5-air:free",
        "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",
        "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",
        "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",
    ],
    "moonshotaI": [
        "moonshotai/kimi-k2:free",
        "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",
        "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",
        "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",
    ],
    "google_gemma_3n_2b": [
        "google/gemma-3n-e2b-it:free",
        "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",
        "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",
        "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",
    ],
    "tng_deepseek_r1t2": [
        "tngtech/deepseek-r1t2-chimera:free",
        "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",
        "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",
        "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",
    ],
    "google_gemma_3n_4b": [
        "google/gemma-3n-e4b-it:free",
        "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",
        "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",
        "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",
    ],
    "qwen_4b": [
        "qwen/qwen3-4b:free",
        "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",
        "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",
        "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",
    ],
    "google_gemma_4b": [
        "google/gemma-3-4b-it:free",
        "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",
        "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",
        "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",
    ],
    "google_gemma_12b": [
        "google/gemma-3-12b-it:free",
        "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",
        "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",
        "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",
    ],
    "meta_llama_3b": [
        "meta-llama/llama-3.2-3b-instruct:free",
        "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",
        "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",
        "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",
    ],
    "qwen_7b": [
        "qwen/qwen-2.5-vl-7b-instruct:free",
        "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",
        "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",
        "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",
    ],
    "meta_llama_405b": [
        "meta-llama/llama-3.1-405b-instruct:free",
        "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",
        "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",
        "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",
    ],
    "mistral_7b": [
        "mistralai/mistral-7b-instruct:free",
        "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",
        "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",
        "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",
    ],
    # "kwaipilot": [
    #     "kwaipilot/kat-coder-pro:free",
    #     "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",
    #     "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",
    #     "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",
    # ], # X
    # "nvidia_nemo_12b": [
    #     "nvidia/nemotron-nano-12b-v2-vl:free",
    #     "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",
    #     "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",
    #     "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",
    # ], # X
    # "tongyi": [
    #     "alibaba/tongyi-deepresearch-30b-a3b:free",
    #     "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",
    #     "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",
    #     "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",
    # ], # X
    # "nvidia_nemo_9b": [
    #     "nvidia/nemotron-nano-9b-v2:free",
    #     "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",
    #     "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",
    #     "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",
    # ], # X
    # "xiaomi": [
    #     "xiaomi/mimo-v2-flash:free",
    #     "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",
    #     "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",
    #     "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",
    # ], # X
    # "financenvidia": [
    #     "nvidia/nemotron-3-nano-30b-a3b:free",
    #     "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",
    #     "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",
    #     "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",
    # ], # X
    # "mistral_devstral": [
    #     "mistralai/devstral-2512:free",
    #     "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",
    #     "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",
    #     "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",
    # ], # X
    # "nex_agi": [
    #     "nex-agi/deepseek-v3.1-nex-n1:free"
    #     "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"
    #     "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"
    #     "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"
    # ], # X
    # "qwen_coder_480b": [
    #     "qwen/qwen3-coder:free",
    #     "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",
    #     "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",
    #     "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",
    # ], # X
    # "venice": [
    #     "cognitivecomputations/dolphin-mistral-24b-venice-edition:free",
    #     "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",
    #     "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",
    #     "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",
    # ], # X
    # "tng_deepseek_r1t": [
    #     "tngtech/deepseek-r1t-chimera:free",
    #     "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",
    #     "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",
    #     "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",
    # ], # X
    # "google_gemini": [
    #     "google/gemini-2.0-flash-exp:free",
    #     "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",
    #     "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",
    #     "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",
    # ], # X
    # "nous_hermes_405b": [
    #     "nousresearch/hermes-3-llama-3.1-405b:free",
    #     "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",
    #     "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",
    #     "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",
    # ], # X
}


ROLEType = Literal["system", "user", "assistant", "developer"]


# --------------------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------------------
def _get_model_name_and_key(
    user_counter: int,
    model_counter: int,
    model_name_list: list[str],
    model_key_dict: dict[str, list[str]],
) -> tuple[str, str]:
    """
    Returns the model and key IDs based on the calculation of the current counters
    and the constant model and key structures.

    Returns
    -------
    api_model_id, api_key_id : tuple[str, str]
        A tuple containing the model and key IDs
    """
    api_model_id, api_key_id = DEFAULT_MODEL_ID, DEFAULT_OPENROUTER_API_KEY

    try:
        model_idx = 0

        user_idx = (user_counter%3) + 1
        model_key_idx = model_counter%len(model_name_list)

        model_key = model_name_list[model_key_idx]
        api_model_id = model_key_dict[model_key][model_idx]
        api_key_id = model_key_dict[model_key][user_idx]

        if not api_model_id or not api_key_id:
            raise PassError("pass")
        if ":free" not in api_model_id:
            raise PassError("pass")
        if "sk-or-v1" not in api_key_id:
            raise PassError("pass")

    except Exception:
        return DEFAULT_MODEL_ID, DEFAULT_OPENROUTER_API_KEY

    return api_model_id, api_key_id


def _chunk_prompt_result(prompt_result: str) -> list[list[str]] | None:
    """
    Extracts the first triple-backtick block from a prompt result and
    chunks its contents into paragraphs and lines.

    Returns
    -------
    list[list[str]] | None
        A list of paragraph chunks (each a list of lines),
        or None if parsing fails.
    """
    try:

        # Chunking logic
        result: list[list[str]] = []
        curr: list[str] = []

        lines = prompt_result.splitlines(keepends=True)

        for line in lines:
            # Blank line (paragraph break)
            if line.strip() == "":
                if curr:
                    result.append(curr)
                    curr = []
                continue

            # Normal line
            curr.append(line.rstrip("\n"))

        # Append last chunk if needed
        if curr:
            result.append(curr)

        return result

    except Exception:
        return None


def _merge_headers(*headers: Mapping[str, str] | None) -> dict[str, str]:
    merged: dict[str, str] = {}
    for h in headers:
        if not h:
            continue
        for k, v in h.items():
            if v is None:
                continue
            merged[str(k)] = str(v)
    return merged


def _perform_query_trend(
    query: str,
    model: str,
    role: ROLEType,
    base_url: str,
    apkey: str,
    default_headers: dict[str, str] | None = None,
    extra_body: dict[str, Any] | None = None,
    *,
    # OpenRouter attribution (optional, but good practice)
    app_url: str | None = None,
    app_title: str | None = None,

    # Model behavior
    temperature: float | None = None,
    top_p: float | None = None,
    max_tokens: int | None = None,
    seed: int | None = None,

    # Request shaping
    stop: str | Sequence[str] | None = None,
    response_format: dict[str, Any] | None = None,
    logit_bias: dict[str, int] | None = None,

    # Reliability / hygiene
    timeout_s: float | None = 120.0,
    max_retries: int = 3,

    # Advanced: pass richer messages if you ever need it
    system_prompt: str | None = None,
) -> ChatCompletion | None:
    """
    Perform a single chat completion request and return the raw ChatCompletion.

    This is designed as a reusable, copy/paste-friendly "cookiecutter" for clean API calls.

    Parameters you likely customize often:
      - model, temperature/top_p, max_tokens
      - app_url/app_title (attribution)
      - system_prompt (policy/instructions for your assistant persona)
      - extra_body (provider-specific knobs; kept as-is and forwarded)

    Notes:
      - `default_headers` is merged with optional attribution headers.
      - Retries are handled by the OpenAI Python SDK where supported; keep max_retries modest.
      - This function does *not* attempt to circumvent policies or limits; it’s built for
        good client behavior (reasonable retries, timeouts, attribution).
    """
    if not isinstance(query, str) or not query.strip():
        raise ValueError("query must be a non-empty string.")
    if role not in {"system", "user", "assistant", "developer"}:
        raise ValueError(f"Invalid role: {role!r}")

    # --- Headers (OpenRouter attribution is optional, but recommended) ---
    attribution_headers: dict[str, str] = {}
    if app_url:
        attribution_headers["HTTP-Referer"] = app_url
    if app_title:
        attribution_headers["X-Title"] = app_title

    headers = _merge_headers(default_headers, attribution_headers)

    # --- Client ---
    client = OpenAI(
        base_url=base_url,
        api_key=apkey,
        default_headers=headers,
    )

    # Apply per-request options (not all SDK versions support all options; fail softly).
    # `with_options` is the most ergonomic place to set retry/timeout knobs.
    try:
        client = client.with_options(max_retries=max_retries, timeout=timeout_s)
    except TypeError:
        try:
            client = client.with_options(max_retries=max_retries)
        except TypeError:
            pass  # older client; rely on defaults

    # --- Messages ---
    messages: list[dict[str, str]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": role, "content": query})

    # --- Payload ---
    payload: dict[str, Any] = {
        "model": model,
        "messages": messages,
    }

    # Optional common knobs
    if temperature is not None:
        payload["temperature"] = float(temperature)
    if top_p is not None:
        payload["top_p"] = float(top_p)
    if max_tokens is not None:
        payload["max_tokens"] = int(max_tokens)
    if seed is not None:
        payload["seed"] = int(seed)
    if stop is not None:
        payload["stop"] = stop
    if response_format is not None:
        payload["response_format"] = response_format
    if logit_bias is not None:
        payload["logit_bias"] = logit_bias

    # OpenRouter/provider-specific options (forwarded verbatim)
    if extra_body:
        payload.update(extra_body)

    # --- Call ---
    try:
        response: ChatCompletion = client.chat.completions.create(**payload)
    except Exception:
        print(f"Could not execute model: {model} with api-key = {apkey[-6:]}")
        print(f"Query = {query}")
        print(f"Will try a new model.{'-'*50}\n")
        return None
    return response


def _clean_output(
    prompt_result: str,
    split_words: bool = False,
) -> list[str] | None:
    """
    Extracts all text inside any number of triple-backtick codeboxes.

    - If no triple-backtick blocks exist -> None
    - If 1 block -> list with 1 element
    - If N blocks -> list with N elements

    Each extracted block is .strip()'d before returning.
    If split_words=True, each block becomes " ".join(block.split()).split(" ") behavior,
    i.e. split on spaces after stripping.
    """
    matches = _TRIPLE_BACKTICK_RE.findall(prompt_result)
    if not matches:
        return None

    chunks: list[str] = []
    for chunk in matches:
        cleaned = chunk.strip()
        if split_words:
            chunks.extend(cleaned.split(" ") if cleaned else [])
        else:
            chunks.append(cleaned)

    return chunks


def _has_only_str_and_at_least_one(lst: Any, fmt: type) -> bool:
    seen = False
    stop = False
    while not stop:
        if isinstance(lst, Iterable):
            for item in lst:
                _has_only_str_and_at_least_one(item, fmt)
        elif isinstance(lst, fmt):
            stop = True
            seen = True
        else:
            return seen
    return seen


# --------------------------------------------------------------------------------------
# Functions
# --------------------------------------------------------------------------------------
def query_models(
    trend_list: TrendList,
    user_counter: int,
    model_counter: int,
    *,
    model_name_list: list[str] = MODEL_NAME_LIST,
    model_key_dict: dict[str, list[str]] = MODEL_KEY_DICT,
    role: ROLEType = DEFAULT_ROLE,
    base_url: str = DEFAULT_BASE_URL,
    default_headers: dict[str, str] = DEFAULT_HEADERS,
    default_extra_body: dict[str, str] = DEFAULT_EXTRA_BODY,
    sleep_min_base: float = SLEEP_MIN_BASE,
    max_retries: int = DEFAULT_MAX_RETRIES_MODEL,
) -> None:
    """
    Query models for each Trend in `trend_list`, retrying failures up to `max_retries`
    per trend, with sleeps between attempts. Never raises (best-effort logging).
    """

    # Initialize trend trend_stack
    trend_stack: deque[Trend] = deque(trend_list)

    # Per-trend retry counters
    retries_left: dict[int, int] = {id(t): max_retries for t in trend_stack}

    # Create result list
    counter = -1

    # Main Trend while loop
    while trend_stack:

        # Initialize trend loop
        counter += 1
        trend = trend_stack.pop()

        # ---------------------------
        # Validate input
        # ---------------------------
        query = trend.tts_prompt_query
        if not isinstance(query, str) or not query.strip():
            print(f"{dtnow()} ERROR: trend.tts_prompt_query is not a non-empty string")
            sleep(get_random() + sleep_min_base)
            continue

        # ---------------------------
        # Pick model and key
        # ---------------------------
        api_model_id, api_key_id = _get_model_name_and_key(
            user_counter + counter,
            model_counter + counter,
            model_name_list,
            model_key_dict,
        )

        # ---------------------------
        # Check API key
        # ---------------------------
        if not api_key_id:
            print(f"{dtnow()} ERROR:")
            print(
                f"{dtnow()} You need to give an OpenRouter Key. Check"
                f" https://openrouter.ai/docs/guides/overview/auth/oauth"
            )
            continue

        # ---------------------------
        # Check model
        # ---------------------------
        if not api_model_id:
            print(f"{dtnow()} ERROR:")
            print(f"{dtnow()} Model ID invalid. Try: 'allenai_31'")
            continue

        # -------------------------------
        # Call provider (may return None)
        # -------------------------------
        if not isinstance(
            response := _perform_query_trend(
                query=query,
                model=api_model_id,
                role=role,
                base_url=base_url,
                apkey=api_key_id,
                extra_body=default_extra_body,
                app_url=default_headers.get("HTTP-Referer", None),
                app_title=default_headers.get("X-Title", None),
            ),
            ChatCompletion,
        ):
            print(f"{dtnow()} ERROR:")
            print(f"{dtnow()} Prompt could not be formed correctly")
            sleep(get_random() + sleep_min_base)
            continue

        # If call failed or returned an unusable response, requeue if possible.
        if not response or not getattr(response, "choices", None):
            left = retries_left.get(id(trend), 0) - 1
            retries_left[id(trend)] = left
            if left > 0:
                trend_stack.appendleft(trend)  # retry later (round-robin-ish)
            else:
                print(f"{dtnow()} ERROR: exhausted retries for trend={trend.title!r}")
            sleep(get_random() + sleep_min_base)
            continue

        # ---------------------------
        # Initialize output structures
        # ---------------------------
        trend.tts_presult_full_text = []
        trend.tts_presult_summary_text = []
        trend.image_presult_keywords = []
        trend.mood_presult_keyword = []


        # Track whether at least one choice succeeded for this trend
        any_success = False

        # ---------------------------
        # Process choices (avoid tortuous stacks / idx dict-of-lists)
        # ---------------------------
        for idx, choice in enumerate(response.choices):
            try:
                content: str | None = choice.message.content if choice and choice.message else None
                if not isinstance(content, str) or not content.strip():
                    raise ValueError("missing message.content")

                results_raw = _clean_output(prompt_result=content, split_words=False)
                if not isinstance(results_raw, list) or not results_raw:
                    raise ValueError("cleaned output is not a non-empty list")

                results_str: list[str] = [x for x in results_raw if isinstance(x, str) and x]
                if not results_str:
                    raise ValueError("cleaned output contains no strings")

                main_raw: str = results_str[0]
                summary_raw: str = results_str[1]
                keywords_raw: str = results_str[2]
                mood_word: str = results_str[3]

                main_chunked: list[list[str]] | None = _chunk_prompt_result(main_raw)
                if not isinstance(main_chunked, list) or not _has_only_str_and_at_least_one(main_chunked, str):
                    raise ValueError("chunked main text invalid (expected list[list[str]] with >=1 str)")

                if not isinstance(summary_raw, str):
                    raise ValueError("summary is not a string")

                keywords_list: list[str] = keywords_raw.split(";")
                if not isinstance(keywords_list, list) or not _has_only_str_and_at_least_one(keywords_list, str):
                    raise ValueError("keywords_list is invalid")

                if not isinstance(mood_word, str):
                    raise ValueError("summary is not a string")

                trend.tts_presult_full_text.append(main_chunked)
                trend.tts_presult_summary_text.append(summary_raw)
                trend.image_presult_keywords.append(keywords_list)
                trend.mood_presult_keyword.append(mood_word)
                any_success = True

            except Exception as e:
                # Never break; log and keep going to other choices
                print(f"..{dtnow()} ERROR: failed processing choice[{idx}] for trend={trend.title!r}")
                print(f"..{type(e).__name__}: {e}")
                continue

        # ---------------------------
        # Decide whether to retry this trend
        # ---------------------------
        if not any_success:
            left = retries_left.get(id(trend), 0) - 1
            retries_left[id(trend)] = left
            if left > 0:
                trend_stack.appendleft(trend)
                print(f"{dtnow()} WARN: no valid choices; requeued trend={trend.title!r} (retries_left={left})")
            else:
                print(f"{dtnow()} ERROR: no valid choices; exhausted retries for trend={trend.title!r}")

        else:
            # Reset retries on success (optional but typically desired)
            retries_left[id(trend)] = max_retries

        sleep(get_random() + sleep_min_base)

    return None


# --------------------------------------------------------------------------------------
# Exports
# --------------------------------------------------------------------------------------
__all__: list[str] = [
    "query_models",
]


# -------------------------------------------------------------------------------------
# Test | python -m uqbar.acta.trend_newstext_maker > out.txt 2>&1
# -------------------------------------------------------------------------------------
# if __name__ == "__main__":
