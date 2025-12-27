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

from openai import OpenAI

from pathlib import Path
import subprocess
import os


from uqbar.acta.utils import dtnow, Trend, TrendList
from uqbar.acta.trend_prompt_parser import (
    _get_prompt_string_image_query, 
    _get_prompt_string_mood_query,
) 


# -------------------------------------------------------------------------------------
# Constants
# -------------------------------------------------------------------------------------
DEFAULT_OPENROUTER_API_KEY: str = (
    "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"
)

DEFAULT_MODEL: str = "allenai_31"

DEFAULT_ROLE: str = "user"

DEFAULT_BASE_URL:str = "https://openrouter.ai/api/v1"

DEFAULT_API_KEY_LOC:str = "env"


DEFAULT_HEADERS: dict[str, str] = {"HTTP-Referer": "http://localhost:3000"}


# Model Dictionary -> key: [name, id, tokens, context]
MODEL: dict[str, list[str | int]] = {
    "allenai_31": ["AllenAI: Olmo 3.1 32B Think (free)", "allenai/olmo-3.1-32b-think:free", 38_000_000_000, 66_000], # TOP 1
    "xiaomi": ["Xiaomi: MiMo-V2-Flash (free)", "xiaomi/mimo-v2-flash:free", 133_000_000_000, 262_000], # X
    "financenvidia": ["FinanceNVIDIA: Nemotron 3 Nano 30B A3B (free)", "nvidia/nemotron-3-nano-30b-a3b:free", 174_000_000_000, 256_000], # X
    "mistral_devstral": ["Mistral: Devstral 2 2512 (free)", "mistralai/devstral-2512:free", 115_000_000_000, 262_000], # X
    "nex_agi": ["Nex AGI: DeepSeek V3.1 Nex N1 (free)", "nex-agi/deepseek-v3.1-nex-n1:free", 415_000_000_000, 131_000], # X
    "arcee_ai": ["Arcee AI: Trinity Mini (free)", "arcee-ai/trinity-mini:free", 366_000_000, 131_000], # TOP 6
    "tng": ["TNG: R1T Chimera (free)", "tngtech/tng-r1t-chimera:free", 128_000_000_000, 164_000],
    "allenai_3": ["AllenAI: Olmo 3 32B Think (free)", "allenai/olmo-3-32b-think:free", 12_000_000_000, 66_000],
    "kwaipilot": ["Kwaipilot: KAT-Coder-Pro V1 (free)", "kwaipilot/kat-coder-pro:free", 987_000_000_000, 256_000], # X
    "nvidia_nemo_12b": ["NVIDIA: Nemotron Nano 12B 2 VL (free)", "nvidia/nemotron-nano-12b-v2-vl:free", 332_000_000_000, 128_000], # X
    "tongyi": ["Tongyi: DeepResearch 30B A3B (free)", "alibaba/tongyi-deepresearch-30b-a3b:free", 15_000_000_000, 131_000], # X
    "nvidia_nemo_9b": ["NVIDIA: Nemotron Nano 9B V2 (free)", "nvidia/nemotron-nano-9b-v2:free", 374_000_000, 128_000], # X
    "openai_oss_120b": ["OpenAI: gpt-oss-120b (free)", "openai/gpt-oss-120b:free", 745_000_000, 131_000],
    "openai_oss_20b": ["OpenAI: gpt-oss-20b (free)", "openai/gpt-oss-20b:free", 38_000_000_000, 131_000],
    "z_ai": ["Z.AI: GLM 4.5 Air (free)", "z-ai/glm-4.5-air:free", 176_000_000_000, 131_000],
    "qwen_coder_480b": ["Qwen: Qwen3 Coder 480B A35B (free)", "qwen/qwen3-coder:free", 35_000_000_000, 262_000], # X
    "moonshotaI": ["MoonshotAI: Kimi K2 0711 (free)", "moonshotai/kimi-k2:free", 699_000_000, 33_000],
    "venice": ["Venice: Uncensored (free)", "cognitivecomputations/dolphin-mistral-24b-venice-edition:free", 672_000_000, 33_000], # X
    "google_gemma_3n_2b": ["Google: Gemma 3n 2B (free)", "google/gemma-3n-e2b-it:free", 292_000_000, 8_000],
    "tng_deepseek_r1t2": ["TNG: DeepSeek R1T2 Chimera (free)", "tngtech/deepseek-r1t2-chimera:free", 949_000_000_000, 164_000],
    "deepseek_r1": ["DeepSeek: R1 0528 (free)", "deepseek/deepseek-r1-0528:free", 19_000_000_000, 164_000], # TOP 5
    "google_gemma_3n_4b": ["Google: Gemma 3n 4B (free)", "google/gemma-3n-e4b-it:free", 415_000_000, 8_000],
    "qwen_4b": ["Qwen: Qwen3 4B (free)", "qwen/qwen3-4b:free", 574_000_000, 41_000],
    "tng_deepseek_r1t": ["TNG: DeepSeek R1T Chimera (free)", "tngtech/deepseek-r1t-chimera:free", 208_000_000_000, 164_000], # X
    "mistral_small_24b": ["Mistral: Mistral Small 3.1 24B (free)", "mistralai/mistral-small-3.1-24b-instruct:free", 242_000_000, 128_000], # TOP 2
    "google_gemma_4b": ["Google: Gemma 3 4B (free)", "google/gemma-3-4b-it:free", 231_000_000, 33_000],
    "google_gemma_12b": ["Google: Gemma 3 12B (free)", "google/gemma-3-12b-it:free", 424_000_000, 33_000],
    "google_gemma_27b": ["Google: Gemma 3 27B (free)", "google/gemma-3-27b-it:free", 27_000_000_000, 131_000], # TOP 4
    "google_gemini": ["Google: Gemini 2.0 Flash Experimental (free)", "google/gemini-2.0-flash-exp:free", 12_000_000_000, 105_000_000], # X
    "meta_llama_70b": ["Meta: Llama 3.3 70B Instruct (free)", "meta-llama/llama-3.3-70b-instruct:free", 25_000_000_000, 131_000], # TOP 3
    "meta_llama_3b": ["Meta: Llama 3.2 3B Instruct (free)", "meta-llama/llama-3.2-3b-instruct:free", 803_000_000, 131_000],
    "qwen_7b": ["Qwen: Qwen2.5-VL 7B Instruct (free)", "qwen/qwen-2.5-vl-7b-instruct:free", 75_000_000, 33_000],
    "nous_hermes_405b": ["Nous: Hermes 3 405B Instruct (free)", "nousresearch/hermes-3-llama-3.1-405b:free", 350_000_000, 131_000], # X
    "meta_llama_405b": ["Meta: Llama 3.1 405B Instruct (free)", "meta-llama/llama-3.1-405b-instruct:free", 165_000_000, 131_000],
    "mistral_7b": ["Mistral: Mistral 7B Instruct (free)", "mistralai/mistral-7b-instruct:free", 574_000_000, 33_000],
}

# --------------------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------------------
def _get_model_name(model_alias: str) -> str | None:

    try:
        model_list = MODEL.get(model_alias, None)
        return model_list[1] or None
    except Exception as e:
        return None


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
        # 1. Find opening triple backtick
        start = prompt_result.find("```")
        if start == -1:
            return None

        # Consume opening ``` and optional language label (up to first newline)
        start_line_end = prompt_result.find("\n", start)
        if start_line_end == -1:
            return None

        # 2. Find closing triple backtick
        end = prompt_result.find("```", start_line_end + 1)
        if end == -1:
            return None

        # Extract the content inside the backticks
        prompt_str = prompt_result[start_line_end + 1 : end]

        # 3. Chunking logic
        result: list[list[str]] = []
        curr: list[str] = []

        lines = prompt_str.splitlines(keepends=True)

        for line in lines:
            # Case 2: blank line (paragraph break)
            if line.strip() == "":
                if curr:
                    result.append(curr)
                    curr = []
                continue

            # Case 1: normal line
            curr.append(line.rstrip("\n"))

        # Append last chunk if needed
        if curr:
            result.append(curr)

        return result

    except Exception:
        return None


def _perform_query_trend(
    query: str,
    model: str,
    role: str,
    base_url: str,
    apkey: str,
    default_headers: dict[str, str],
) -> ChatCompletion:
    """
    Returns a ChatCompletion object from a query.

    The structure of a ChatCompletion is:
    ```json
    }
        response = {
        "id": "...",
        "model": "...",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "Here is the generated text..."
                },
                "finish_reason": "stop"
            }
            # potentially more choices here
        ],
        "usage": {
            "prompt_tokens": ...,
            "completion_tokens": ...
        }
    }
    ```
    """
    # Client automatically uses the OPENROUTER_API_KEY environment variable
    client = OpenAI(
        base_url=base_url,
        api_key=apkey,
        default_headers=default_headers, # Required by OpenRouter for logging
    )

    message_list = [
        {"role": role, "content": query}
    ]

    response = client.chat.completions.create(
        model=model,
        messages=message_list,
    )

    return response


def _clean_output(
    prompt_result: str,
    split_words: bool = False,
) -> list[str] | str:

    # 1. Find opening triple backtick
    start = prompt_result.find("```")
    if start == -1:
        return None

    # Consume opening ``` and optional language label (up to first newline)
    start_line_end = prompt_result.find("\n", start)
    if start_line_end == -1:
        return None

    # 2. Find closing triple backtick
    end = prompt_result.find("```", start_line_end + 1)
    if end == -1:
        return None

    # Extract the content inside the backticks
    prompt_str = prompt_result[start_line_end + 1 : end]

    # Split words or return entire chunk
    if split_words:
        return prompt_str.strip().split(" ")
    return prompt_str


# --------------------------------------------------------------------------------------
# Functions
# --------------------------------------------------------------------------------------
def query_models(
    trend_list: list[str],
    *,
    model: str = DEFAULT_MODEL,
    role: str = DEFAULT_ROLE,
    base_url: str = DEFAULT_BASE_URL,
    apkey: str = DEFAULT_API_KEY_LOC,
    default_headers: dict[str, str] = DEFAULT_HEADERS,
) -> None:

    # Check API key
    api_key = DEFAULT_OPENROUTER_API_KEY
    if apkey.lower() == "env":
        api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print(f"{dtnow()} ERROR:")
        print(
            f"{dtnow()} You need to give an OpenRouter Key. Check"
            f" https://openrouter.ai/docs/guides/overview/auth/oauth"
        )
        return

    # Check model
    model_name: str = _get_model_name(model)
    if model_name is None:
        print(f"{dtnow()} ERROR:")
        print(f"{dtnow()} Model ID invalid. Try: 'allenai_31'")
        return

    # Create result list
    for trend in trend_list:

        query: str = trend.tts_prompt_query

        response: ChatCompletion = _perform_query_trend(
            query = query,
            model=model_name,
            role=role,
            base_url=base_url,
            apkey=api_key,
            default_headers=default_headers,
        )

        response_content: list[list[str]] = _chunk_prompt_result(
            response.choices[0].message.content,
        )

        trend.tts_prompt_response = response_content

    return None


def query_image_and_mood(
    trend_list: list[str],
    *,
    model: str = DEFAULT_MODEL,
    role: str = DEFAULT_ROLE,
    base_url: str = DEFAULT_BASE_URL,
    apkey: str = DEFAULT_API_KEY_LOC,
    default_headers: dict[str, str] = DEFAULT_HEADERS,
) -> None:

    # Check API key
    api_key = DEFAULT_OPENROUTER_API_KEY
    if apkey.lower() == "env":
        api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print(f"{dtnow()} ERROR:")
        print(
            f"{dtnow()} You need to give an OpenRouter Key. Check"
            f" https://openrouter.ai/docs/guides/overview/auth/oauth"
        )
        return

    # Check model
    model_name: str = _get_model_name(model)
    if model_name is None:
        print(f"{dtnow()} ERROR:")
        print(f"{dtnow()} Model ID invalid. Try: 'allenai_31'")
        return

    # Create result list
    for trend in enumerate(trend_list, start=1):

        # News piece
        news_piece = trend.tts_prompt_response

        # Create image prompt
        prompt_image_keywords, file_image_keywords = _get_prompt_string_image_query(
            is_last=counter==total_size,
            news_piece=news_piece,
            current_count=counter,
            total_count=total_size,
        )

        response: ChatCompletion = _perform_query_trend(
            query = prompt_image_keywords,
            model=model_name,
            role=role,
            base_url=base_url,
            apkey=api_key,
            default_headers=default_headers,
        )

        response_content: list[str] = _clean_output(
            prompt_result=response.choices[0].message.content,
            split_words=False,
        )

        trend.image_prompt_response: list[str] = response_content

        # Create mood prompt
        prompt_mood_keywords, file_mood_keywords = _get_prompt_string_mood_query(
            is_last=counter==total_size,
            news_piece=news_piece,
            current_count=counter,
            total_count=total_size,
        )

        response: ChatCompletion = _perform_query_trend(
            query = query,
            model=model_name,
            role=role,
            base_url=base_url,
            apkey=api_key,
            default_headers=default_headers,
        )

        response_content: list[str] = _clean_output(
            prompt_result=response.choices[0].message.content,
            split_words=False,
        )

        trend.mood_prompt_response: str = response_content

# --------------------------------------------------------------------------------------
# Exports
# --------------------------------------------------------------------------------------
__all__: list[str] = [
    "query_models",
    "query_image_and_mood",
]


# -------------------------------------------------------------------------------------
# Test | python -m uqbar.acta.trend_newstext_maker > out.txt 2>&1
# -------------------------------------------------------------------------------------
# if __name__ == "__main__":
