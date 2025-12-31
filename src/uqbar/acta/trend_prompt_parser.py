# SPDX-License-Identifier: MIT
# uqbar/acta/prompt_maker.py
"""
Acta Diurna | Prompt Maker
==========================

Overview
--------
Placeholder.

Metadata
--------
- Project: Acta diurna
- License: MIT
"""

# -------------------------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------------------------
from __future__ import annotations

from datetime import datetime
import numpy as np
from numpy.typing import NDArray
import os
from pathlib import Path
import re
from sortedcontainers import SortedList

from uqbar.acta.utils import Trend, TrendList, GO_EMOTIONS_LABELS


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
    last_ruler: str = f"\n"
    if is_last:
        first_ruler: str = f"{'-'*big_ruler_len}\n\n"
        last_ruler: str = f""

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
    last_ruler: str = f"\n"
    if is_last:
        first_ruler: str = f"{'-'*big_ruler_len}\n\n"
        last_ruler: str = f""

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
def create_trend_tts_prompt(
    trend_list: TrendList,
    *,
    prompt_file_path: Path = DEFAULT_PROMPT_TTS_PATH,
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
    total_size: int = len(trend_list)

    # Iterate through trends
    for counter, trend in enumerate(trend_list, start=1):

        # Get news_url_list
        news_url_list: list[str] = [
            trend.news_item_url_1,
            trend.news_item_url_2,
            trend.news_item_url_3,
        ]

        tts_prompt_query, file_prompt_query = _get_prompt_string(
            is_last=counter == total_size,
            news_url_list=news_url_list,
            current_count=counter,
            total_count=total_size,
        )

        trend.tts_prompt_query = tts_prompt_query
        trend.tts_file_prompt_query = file_prompt_query

    # Check whether to write in a file
    if not write_file:
        return prompt_file_path

    # Write Output to file and return Path
    with open(prompt_file_path, "w") as file:
        for trend in trend_list:
            file.write(trend.file_prompt_query)

    return prompt_file_path


def create_trend_image_mood_prompt(
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
    total_size: int = len(trend_list)

    # Iterate through trends
    for counter, trend in enumerate(trend_list, start=1):

        # Get news_url_list
        news_piece_summary: list[str] = trend.tts_presult_summary_text

        mood_prompt_query, file_prompt_query = _get_prompt_string_image_mood_query(
            is_last=counter == total_size,
            news_url_list=news_piece_summary,
            current_count=counter,
            total_count=total_size,
        )

        trend.image_mood_prompt_query: str = mood_prompt_query
        trend.image_mood_file_prompt_query: str = file_prompt_query

    # Check whether to write in a file
    if not write_file:
        return prompt_file_path

    # Write Output to file and return Path
    with open(prompt_file_path, "w") as file:
        for trend in trend_list:
            file.write(trend.image_mood_file_prompt_query)

    return prompt_file_path


def read_trend_prompt(
    *,
    prompt_file_path: Path = PROMPT_FILE_PATH,
) -> list[list[str]]:
    """
    Placeholder.
    """

    prev_id: str | None = None
    curr_id: str | None = None

    curr_result: list[str] = []
    prompt_result_list: list[list[str]] = []

    inside_prompt: bool = False
    inside_result: bool = False
    inside_result_idx: int = 0

    # Reading file
    file_lines: list[str] = []
    with open(prompt_file_path, "r", encoding="utf-8") as file:

        for line in file:

            file_lines.append(line)

    for counter, line in enumerate(file_lines, start=1):

        sline = line.strip()

        # Try to match
        big_ruler_match = BIG_RULER_RE.match(line)

        # Start of prompt
        if big_ruler_match:
            inside_prompt: bool = True
            inside_result: bool = False

        # Inside Results
        if inside_result:

            if inside_result_idx == 0:
                inside_result_idx += 1
                continue

            elif inside_result_idx >= 1:

                # Newline, end of prompt, end of file
                if len(sline) == 0:

                    # End of file
                    try:
                        tline: str = file_lines[counter]
                    except Exception as e:
                        break

                    # End of prompt
                    if "-----" in file_lines[counter]:
                        inside_result: bool = False
                        inside_prompt: bool = False
                        inside_result_idx: int = 0
                        continue

                    # Just newline
                    curr_result.append(line)
                    inside_result_idx += 1
                    continue

                # Regular line with result
                curr_result.append(sline)
                inside_result_idx += 1
                continue

        # Inside prompt - wait for small ruler or header
        if inside_prompt:

            # Check header
            prompt_header_match = PROMPT_HEADER_RE.match(sline)
            if prompt_header_match:

                prompt_number: int = int(prompt_header_match.group("prompt_number"))
                prompt_total: int = int(prompt_header_match.group("prompt_total"))
                curr_id: int = prompt_number

                cond_id: bool = False
                if prev_id is not None:
                    cond_id: bool = curr_id != prev_id

                if cond_id:
                    prompt_results = _flush_prompt(prev_id, curr_result)
                    prompt_result_list.append(prompt_results)
                    curr_result: list[str] = []

                prev_id: int = curr_id
                prompt_header_match: bool = False

            # If still in big ruler, small ruller will match also
            # To prevent that, stop early if in big ruller line
            if big_ruler_match:
                big_ruler_match: bool = False
                continue

            # Try to match end of prompt
            small_ruler_match = SMALL_RULER_RE.match(sline)

            # End of prompt
            if small_ruler_match:
                inside_prompt: bool = False
                inside_result: bool = True
                small_ruler_match: bool = False
                inside_result_idx: int = 0

    if curr_result:
        prompt_results = _flush_prompt(prev_id, curr_result)
        prompt_result_list.append(prompt_results)

    # Return the prompt result list chunked
    return prompt_result_list


# --------------------------------------------------------------------------------------
# Exports
# --------------------------------------------------------------------------------------
__all__: list[str] = [
    "create_trend_tts_prompt",
    "create_trend_image_mood_prompt",
]


# -------------------------------------------------------------------------------------
# Test | python -m uqbar.acta.trend_prompt_parser > out.txt 2>&1
# -------------------------------------------------------------------------------------
# if __name__ == "__main__":
