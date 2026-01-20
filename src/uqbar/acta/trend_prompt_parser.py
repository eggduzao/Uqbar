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

import re
from collections.abc import Iterable
from datetime import datetime
from pathlib import Path

from uqbar.acta.trends import Trend, TrendList

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
    total_word_image_count: int = TOTAL_WORD_IMAGE_COUNT,
    small_ruler_len: int = SMALL_RULER_LEN,
    big_ruler_len: int = BIG_RULER_LEN,
) -> tuple[str, str]:

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
        f"6. Please return each in a separate triple-backtick codebox:\n"
        f"    6.1. The full text.\n"
        f"    6.2. A ~{SUMMARY_WORD_COUNT}-words (±20%) summary of the full text in another\n"
        f"         triple-backtick code block.\n"
        f"    6.3. A semicolon-separated list of the TOP ~{total_word_image_count} most \n"
        f"         representative keywords (±5 words), optimised for a google-like search.\n"
        f"    6.4. A single word, most representative of the mood that an average person \n"
        f"         would feel when seeing such news story.\n"
        f"\n"
        f"7. Do return only the four triple-backtick codeboxes above, stacked on after  \n"
        f"the other; and NOTHING more other than their content.\n"
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


def _flush_prompt(
    prev_id: int,
    curr_result: list[str] | None,
) -> list[str] | None:
    """Returns chunked prompt results"""

    if curr_result is None:
        print(f"Error at flush_prompt(): prev_id = {prev_id}")
        print("Table does not exist or is empty. Go get more data please.")
        return None

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
            e for e in [
                trend.news_item_url_1,
                trend.news_item_url_2,
                trend.news_item_url_3,
            ] if e
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
            if isinstance(trend, Trend) and isinstance(trend.tts_file_prompt_query, str):
                file.write(trend.tts_file_prompt_query)

    return prompt_file_path


def read_trend_prompt(
    *,
    prompt_file_path: Path = DEFAULT_PROMPT_TTS_PATH,
) -> list[list[str]]:
    """
    Placeholder.
    """

    prev_id: int = 0

    curr_result: list[str] = []
    prompt_result_list: list[list[str]] = []

    inside_prompt: bool = False
    inside_result: bool = False
    inside_result_idx: int = 0

    # Reading file
    file_lines: list[str] = []
    with open(prompt_file_path, encoding="utf-8") as file:

        for line in file:

            file_lines.append(line)

    for counter, line in enumerate(file_lines, start=1):

        sline = line.strip()

        # Try to match
        big_ruler_match: bool = BIG_RULER_RE.match(line) is not None

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
                        file_lines[counter]
                    except Exception:
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
            pmatch = PROMPT_HEADER_RE.match(sline)
            prompt_header_match: bool = pmatch is not None
            if prompt_header_match and pmatch is not None:

                prompt_number: int = int(pmatch.group("prompt_number"))
                int(pmatch.group("prompt_total"))
                curr_id: int = prompt_number

                cond_id: bool = False
                if prev_id is not None:
                    cond_id: bool = curr_id != prev_id

                if cond_id:
                    prompt_results = _flush_prompt(prev_id, curr_result)
                    if prompt_results is not None:
                        prompt_result_list.append([e for e in prompt_results if e])
                    curr_result: list[str] = []

                prev_id: int = curr_id
                prompt_header_match: bool = False

            # If still in big ruler, small ruller will match also
            # To prevent that, stop early if in big ruller line
            if big_ruler_match:
                big_ruler_match: bool = False
                continue

            # Try to match end of prompt
            small_ruler_match: bool = SMALL_RULER_RE.match(sline) is not None

            # End of prompt
            if small_ruler_match:
                inside_prompt: bool = False
                inside_result: bool = True
                small_ruler_match: bool = False
                inside_result_idx: int = 0

    if curr_result:
        prompt_results = _flush_prompt(prev_id, curr_result)
        if isinstance(prompt_results, Iterable):
            prompt_result_list.append([e for e in prompt_results if e])

    # Return the prompt result list chunked
    return prompt_result_list


# --------------------------------------------------------------------------------------
# Exports
# --------------------------------------------------------------------------------------
__all__: list[str] = [
    "create_trend_tts_prompt",
    "read_trend_prompt",
]


# -------------------------------------------------------------------------------------
# Test | python -m uqbar.acta.trend_prompt_parser > out.txt 2>&1
# -------------------------------------------------------------------------------------
# if __name__ == "__main__":
