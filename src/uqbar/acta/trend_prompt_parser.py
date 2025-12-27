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

from uqbar.acta.utils import Trend, TrendList


# -------------------------------------------------------------------------------------
# Constants
# -------------------------------------------------------------------------------------

# Get the current local date and time as a datetime object
NOW: str = str(datetime.now())

OUT: Path = Path("/Users/egg/Desktop")

PROMPT_FILE_PATH: Path = (
    OUT / "2025-12-18_13-01-55.txt"
)  # str("_".join(NOW.split(".")[0].split(" ")) + ".txt").replace(":", "-")


# Rulers
BIG_RULER_LEN: int = 170

SMALL_RULER_LEN: int = 25

# Word Count
TOTAL_WORD_COUNT: int = 12_000

TOTAL_PARAGRAPH_WORD_COUNT: int = 60

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
        f"6. Please return the text in a triple-backtick code block."
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


def _get_prompt_string_image_query(
    is_last: bool,
    news_piece: str,
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
        f"1. Goal: Give me the most representative ~{total_word_image_count} \n"
        f"words (±5 words), for a 'Google-like' Image Query; synthesizing \n"
        f"the following news piece: \n"
        f"```\n"
        f"{news_piece}\n"
        f"```\n"
        f"\n"
        f"2. Give me the words separated by spaces.\n"
        f"\n"
        f"3. Please return the words **only** in a triple-backtick code block.\n"
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


def _get_prompt_string_mood_query(
    is_last: bool,
    news_piece: str,
    current_count: int,
    total_count: int,
    *,
    total_paragraph_word_count: int = TOTAL_PARAGRAPH_WORD_COUNT,
    small_ruler_len: int = SMALL_RULER_LEN,
    big_ruler_len: int = BIG_RULER_LEN,
) -> str:

    first_ruler: str = f"{'-'*big_ruler_len}\n\n"
    last_ruler: str = f"\n"
    if is_last:
        first_ruler: str = f"{'-'*big_ruler_len}\n\n"
        last_ruler: str = f""

    regular_prompt: str = (
        f"1. Goal: Write a short paragraph with Continuous Prose as a Professional \n"
        f"Calm  News-Media Narrator, targeting a 'Mood Predictor'; based on the \n"
        f"following news piece: \n"
        f"```\n"
        f"{news_piece}\n"
        f"```\n"
        f"\n"
        f"2. Length of paragraph: ~{total_paragraph_word_count:,} words (±30%).\n"
        f"\n"
        f"3. Style & Strategy: Optimize the textual flow and key words for Deep \n"
        f"Neural Net-based Mood Predictor. Make sure to use key words to express \n"
        f"the mood of the news piece.\n"
        f"\n"
        f"4. Avoid wording that may counfounf the Deep Learning-Based Mood \n"
        f"Predictor, such as double negatives, etc. \n"
        f"\n"
        f"6. Please return the text **only** in a triple-backtick code block.\n"
    )

    special_prompt: str = (
        f"{first_ruler}"
        f"> MOOD PROMPTS [{current_count:02d} of {total_count:02d}]\n"
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
def create_trend_prompt(
    trend_list: TrendList,
    *,
    prompt_file_path: Path = PROMPT_FILE_PATH,
    overwrite_file: bool = False,
    write_file: bool = False,
) -> Path | None:
    """
    Create Trends Prompt for Chat GPT
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
        trend.file_prompt_query = file_prompt_query

    # Check whether to write in a file
    if not write_file:
        return prompt_file_path

    # Write Output to file and return Path
    with open(prompt_file_path, "w") as file:
        for trend in trend_list:
            file.write(trend.file_prompt_query)

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
    "create_trend_prompt",
    "read_trend_prompt",
]


# -------------------------------------------------------------------------------------
# Test | python -m uqbar.acta.trend_prompt_parser > out.txt 2>&1
# -------------------------------------------------------------------------------------
# if __name__ == "__main__":
