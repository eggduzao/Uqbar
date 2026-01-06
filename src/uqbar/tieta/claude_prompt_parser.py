# SPDX-License-Identifier: MIT
# uqbar/acta/claude_prompt_parser.py
"""
Tieta | Claude Prompt Parser
============================

Overview
--------
Placeholder.

Metadata
--------
- Project: Tieta
- License: MIT
"""

# -------------------------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------------------------
from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

from uqbar.acta.utils import GO_EMOTIONS_LABELS, TrendList

# -------------------------------------------------------------------------------------
# Constants
# -------------------------------------------------------------------------------------

# Get the current local date and time as a datetime object
NOW: str = str(datetime.now())

OUT: Path = Path("/Users/egg/Desktop")


DEFAULT_PROMPT_TTS_PATH: Path = OUT / "tts.txt"

DEFAULT_PROMPT_IMG_MOOD_PATH: Path = OUT / "img_mood.txt"


# Rulers
BIG_RULER_LEN: int = 170

SMALL_RULER_LEN: int = 25

# Word Count
TOTAL_WORD_COUNT: int = 1_200

SUMMARY_WORD_COUNT: int = 100

TOTAL_WORD_IMAGE_COUNT: int = 10


# Regular expressions
BIG_RULER_RE = re.compile(rf"^-{{{BIG_RULER_LEN}}}")

SMALL_RULER_RE = re.compile(rf"^-{{{SMALL_RULER_LEN}}}")

PROMPT_HEADER_RE = re.compile(
    r"^> TREND PROMPTS \[(?P<prompt_number>\d+) of (?P<prompt_total>\d+)\]"
)


# --------------------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------------------
def _get_prompt_string(
    is_last: bool,
    news_url_list: list[str],
    current_count: int,
    total_count: int,
    *,
    total_word_count: int = TOTAL_WORD_COUNT,
    summary_word_count: int = SUMMARY_WORD_COUNT,
    small_ruler_len: int = SMALL_RULER_LEN,
    big_ruler_len: int = BIG_RULER_LEN,
) -> str:

    first_ruler: str = f"{'-'*big_ruler_len}\n\n"
    last_ruler: str = "\n"
    if is_last:
        first_ruler: str = f"{'-'*big_ruler_len}\n\n"
        last_ruler: str = ""

    regular_prompt: str = (
        f"1. Goal: Write a Continuous Prose as a Professional Calm News-Media Narrator,\n"
        f"targeting a General Audience; synthesizing these three news sources, which report\n"
        f"the same facts with minor framing differences:\n"
        f"    1.1. {news_url_list[0]}\n"
        f"    1.2. {news_url_list[1]}\n"
        f"    1.3. {news_url_list[2]}\n"
        f"\n"
        f"2. Length of text: ~{total_word_count:,} words (±20%).\n"
        f"\n"
        f"3. Style: Predominantly in a news-style impersonal voice, hook the reader with\n"
        f"mystery in the first 2–3 sentences. Develop the news arc while maintaining mystery.\n"
        f"Release the mystery once the reader’s full attention is secured. Fill the remainder\n"
        f"of the report with background and established facts.\n"
        f"\n"
        f"4. Optimize the textual flow for neural TTS. Minor trimming after generation is\n"
        f"acceptable. Keep sentences short to medium in length.\n"
        f"\n"
        f"5. Constraints:\n"
        f"    5.1. Create mystery and tension. Atmospheric or metaphorical language is allowed,\n"
        f"         but do not introduce false factual claims.\n"
        f"    5.2. Adopt a news-anchor storytelling tone. Avoid excessive LinkedIn-style\n"
        f"         seriousness or job-market structure.\n"
        f"    5.3. Avoid hyphens and other TTS-unfriendly characters.\n"
        f"\n"
        f"6. Please return:\n"
        f"    6.1. The full text in a triple-backtick code block.\n"
        f"    6.2. A ~{SUMMARY_WORD_COUNT} words (±20%) summary of the full text in another\n"
        f"         triple-backtick code block.\n"
    )

    special_prompt: str = (
        f"{first_ruler}"
        f"> TREND PROMPTS [{current_count:02d} of {total_count:02d}]\n"
        f"\n"
        f"Honeybun,\n"
        f"\n"
        f"{regular_prompt}\n"
        f"\n"
        f"{'-'*small_ruler_len}\n"
        f"\n"
        f"XXXXX\n"
        f"{last_ruler}"
    )

    return regular_prompt, special_prompt


def _get_prompt_string_image_mood_query(
    is_last: bool,
    news_piece_summary: str,
    current_count: int,
    total_count: int,
    *,
    total_word_image_count: int = TOTAL_WORD_IMAGE_COUNT,
    small_ruler_len: int = SMALL_RULER_LEN,
    big_ruler_len: int = BIG_RULER_LEN,
) -> str:

    first_ruler: str = f"{'-'*big_ruler_len}\n\n"
    last_ruler: str = "\n"
    if is_last:
        first_ruler: str = f"{'-'*big_ruler_len}\n\n"
        last_ruler: str = ""

    regular_prompt: str = (
        f"Background: Based on the following news paragraph:\n"
        f"```\n"
        f"{news_piece_summary}\n"
        f"```\n"
        f"\n"
        f"1. Goal 1: Give me the TOP ~{total_word_image_count} most \n"
        f"representative keywords (±5 words).\n"
        f"  1.1. This list of keywords should be optimised for a 'Google-like' \n"
        f"  Image Query;\n"
        f"  1.2. This list of keywords should be separated by spaces.\n"
        f"  1.3. This list of keywords should be returned in a triple-backtick \n"
        f"  code block.\n"
        f"\n"
        f"2. Goal 2: Select from the list of moods below, the one the best \n"
        f"describes the text.\n"
        f"```\n"
        f"{"\n".join(GO_EMOTIONS_LABELS)}\n"
        f"```\n"
        f"\n"
        f"3. Return:\n"
        f"  3.1 `Goal 1` as a space-separated list of words inside a \n"
        f"  triple-backtick codebox.\n"
        f"  3.2 `Goal 2` as a single word inside a triple-backtick codebox.\n"
    )

    special_prompt: str = (
        f"{first_ruler}"
        f"> IMAGE QUERY AND MOOD PROMPTS [{current_count:02d} of {total_count:02d}]\n"
        f"\n"
        f"Honeybun,\n"
        f"\n"
        f"{regular_prompt}\n"
        f"\n"
        f"{'-'*small_ruler_len}\n"
        f"\n"
        f"XXXXX\n"
        f"{last_ruler}"
    )

    return regular_prompt, special_prompt


def _flush_prompt(
    prev_id: int,
    curr_result: list[str],
) -> None:
    """Returns chunked prompt results"""

    if curr_result is None:
        print(f"Error at flush_prompt(): prev_id = {prev_id}")
        print("Table does not exist or is empty. Go get more data please.")
        return

    # Create Story Chunks
    curr_chunk: list[str] = []
    story_chunk_list: list[str] = []
    for cline in curr_result:

        curr_chunk.append(cline)
        if len(cline) <= 2:
            story_chunk_list.append("".join(curr_chunk))
            curr_chunk: list[str] = []

    # Update prompt result list
    return story_chunk_list


# --------------------------------------------------------------------------------------
# Functions
# --------------------------------------------------------------------------------------
def create_prompts(
    trend_list: TrendList,
    *,
    prompt_file_path: Path = DEFAULT_PROMPT_IMG_MOOD_PATH,
    overwrite_file: bool = False,
    write_file: bool = False,
) -> Path | None:
    """
    Create Trends Prompt for Chat GPT or OpenRouter models.
    """

    # Check file
    prompt_file_path.parent.mkdir(parents=True, exist_ok=True)
    if prompt_file_path.exists() and not overwrite_file:
        return prompt_file_path

    # Check length of multi-prompt
    len(trend_list)

    # Iterate through trends
    for _counter, trend in enumerate(trend_list, start=1):

        pass

    # Check whether to write in a file
    if not write_file:
        return prompt_file_path

    # Write Output to file and return Path
    with open(prompt_file_path, "w") as file:
        for trend in trend_list:
            file.write(trend.image_mood_file_prompt_query)

    return prompt_file_path


# --------------------------------------------------------------------------------------
# Exports 061260
# --------------------------------------------------------------------------------------
__all__: list[str] = [
    "create_prompts",
]
