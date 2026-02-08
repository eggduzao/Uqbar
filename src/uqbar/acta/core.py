# SPDX-License-Identifier: MIT
# uqbar/acta/core.py
"""
Acta Diurna | Core
==================

Overview
--------
Placeholder.

# Clear tabs on all files in src/:
# from repo root
python - <<'PY'
from pathlib import Path

root = Path("src")
for p in root.rglob("*.py"):
    s = p.read_text(encoding="utf-8")
    if "\t" in s:
        p.write_text(s.expandtabs(4), encoding="utf-8")
        print("fixed tabs:", p)
PY

# Black
black . --target-version py312

Usage
-----

1. OpenRouter Key

Make sure the OpenRouter's Key is in the environment:

```bash
export OPENROUTER_API_KEY="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"
```

Also, make sure you successdully installed the requirements. This can be done
using any of the methods below.

2. Requirements

2.1. No Docker and no Environment

```bash
pip install -r requirements.txt
pip install -r requirements-pip.txt
```

**2.2. Docker Image (recommended)**

```bash
docker build -t acta:trends .
docker run --rm acta:trends
```

2.3. Micromamba (or Conda/Miniconda/Mamba)

```bash
micromamba install -n trends -f environment.yml
micromamba activate trends
pip install -r requirements-pip.txt
```

Usage Details
-------------

1. xxx

2. xxx


3. Create prompt result

To create the prompt result we will use the model:
`allenai/olmo-3.1-32b-think:free`
as it has a very good context window and a superb resoning for sober news,



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
import sys
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from enum import Enum, IntEnum
from pathlib import Path
from typing import Any

from uqbar.acta.mood_predictor import predict_mood
from uqbar.acta.trend_download_scraper import get_trends
from uqbar.acta.trend_newstext_maker import query_models
from uqbar.acta.trend_prompt_parser import create_trend_prompt
from uqbar.acta.trends import TrendList, load_trendlist, save_trendlist
from uqbar.utils.stats import hyper_random
from uqbar.utils.utils import dtnow

# from uqbar.acta.image_scraper import
# from uqbar.acta.image_downloader import
# from uqbar.acta.image_processor import

# from uqbar.acta.audio_maker import
# from uqbar.acta.video_maker import

# -------------------------------------------------------------------------------------
# Constants
# -------------------------------------------------------------------------------------
class Subcommand(Enum):
    """Placeholder"""
    TODO = "todo"


@dataclass
class Args:
    ROOT_PATH: str = "root_path"
    THIS_DATE: str = "this_date"
    SEMAPHORE: str = "semaphore"


class SemaphoreKey(IntEnum):
    ZERO = 0
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    ELEVEN = 11
    TWELVE = 12
    THIRTEEN = 13


class Semaphore:
    def __init__(self, default: bool = False) -> None:
        self._values: dict[SemaphoreKey, bool] = {
            key: default for key in SemaphoreKey
        }

    # --- Accessors ---
    def get(self, key: SemaphoreKey | int) -> bool:
        return self._values[self._normalize(key)]

    def set(self, key: SemaphoreKey | int, value: bool) -> None:
        self._values[self._normalize(key)] = value

    # --- Bulk ops ---
    def set_all(self, value: bool) -> None:
        for k in self._values:
            self._values[k] = value

    def update_many(
        self,
        keys: Iterable[SemaphoreKey | int],
        value: bool,
    ) -> None:
        for k in keys:
            self.set(k, value)

    def there_is_higher(self, key: SemaphoreKey | int) -> bool:
        """
        Return True if any semaphore key with value >= `key` is True.

        Parameters
        ----------
        key : SemaphoreKey | int
            Starting key (inclusive).

        Returns
        -------
        bool
            True if any flag at or above `key` is enabled, else False.
        """
        start = self._normalize(key).value
        return any(self._values[SemaphoreKey(i)] for i in range(start, len(SemaphoreKey)))

    # --- Internal ---
    @staticmethod
    def _normalize(key: SemaphoreKey | int) -> SemaphoreKey:
        if isinstance(key, SemaphoreKey):
            return key
        try:
            return SemaphoreKey(key)
        except ValueError as e:
            raise KeyError(f"Invalid semaphore key: {key!r}") from e


# --------------------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------------------
def _resolve_semaphore(raw_string: str | None) -> Semaphore:
    """
    Resolve a semaphore selection string into a Semaphore instance.

    Semantics
    ---------
    - If `raw_string` is None or empty/whitespace: enable all steps.
    - Otherwise, parse integers from the string and enable only those steps.

    Accepted input examples
    -----------------------
    "1,2,3"
    "1 2 3"
    "1; 2; 3"
    "1, 2;3  4"
    "7-8,11-13"   # ranges supported

    Notes
    -----
    - Never raises; invalid tokens are ignored with a warning.
    """
    semaphore = Semaphore()

    if raw_string is None or not raw_string.strip():
        semaphore.set_all(True)
        return semaphore

    s = raw_string.strip()

    # Split on common separators: commas, semicolons, and any whitespace.
    tokens = [t for t in re.split(r"[,\s;]+", s) if t]
    ints: list[int] = []

    for tok in tokens:
        # Support simple ranges like "7-8" or "11-13"
        if "-" in tok:
            a_str, b_str = (p.strip() for p in tok.split("-", 1))
            if a_str.isdigit() and b_str.isdigit():
                a, b = int(a_str), int(b_str)
                lo, hi = (a, b) if a <= b else (b, a)
                ints.extend(range(lo, hi + 1))
            else:
                print(f"Invalid range token ignored: {tok!r}")
            continue

        if tok.isdigit():
            ints.append(int(tok))
        else:
            print(f"Invalid token ignored: {tok!r}")

    # Enable parsed steps
    if ints:
        semaphore.update_many(ints, True)
    else:
        print("No valid step indices found; enabling all steps.")
        semaphore.set_all(True)

    return semaphore


def _run_or_load(
    *,
    key: SemaphoreKey,
    finalphore: Semaphore,
    working_path: Path,
    filename: str,
    state: TrendList,
    run: Callable[[TrendList], TrendList],
) -> TrendList | None:
    """
    If `key` is enabled, run `run(state)` and save checkpoint (if state is TrendList).
    Otherwise, load checkpoint and return it.

    This is intentionally low-ceremony for "personal pipeline" code.
    """
    checkpoint_path: Path = working_path / filename

    if finalphore.get(key):
        new_state = run(state)
        if isinstance(new_state, TrendList):
            save_trendlist(new_state, checkpoint_path)
        return new_state

    elif not checkpoint_path.exists():
        if finalphore.there_is_higher(key):
            print(f"File {checkpoint_path} does not exist.")
        return state

    elif not isinstance(
        loaded := load_trendlist(checkpoint_path),
        TrendList,
    ):
        print(f"Invalid checkpoint: {checkpoint_path}")
        sys.exit(1)

    return loaded


# --------------------------------------------------------------------------------------
# Functions
# --------------------------------------------------------------------------------------
def acta_core(
    args: dict[str, Any],
) -> int:
    """
    Main `acta` pipeline.

    # Parameters
    # project_name: str,
    # time_each_pic: float,
    # total_duration: float,
    # transition_duration: float,
    # fps: int,
    # width: int,
    # height: int,
    # input_thumb_path: Path,
    # input_background_path: Path,
    # input_picture_path: Path,
    # input_mtrack_voice_path: Path,
    # input_mtrack_background_path: Path,
    # output_video_path: Path,

    Notes
    -----
    Placeholder

    Parameters
    ----------
    Placeholder : Placeholder
        Placeholder
    """
    return_code: int = 0

    # Parameters
    root_path: Path | None = args[Args.ROOT_PATH]
    this_date: str | None = args[Args.THIS_DATE]
    semaphore: str | None = args[Args.SEMAPHORE]

    if not root_path:
        return_code = 1
        return return_code

    if not this_date:
        from datetime import date
        now_date: date = date.today()
        datetime_utc: str = now_date.isoformat()
    else:
        datetime_utc: str = str(this_date)

    if not semaphore:
        finalphore: Semaphore = _resolve_semaphore(None)
    else:
        finalphore: Semaphore = _resolve_semaphore(semaphore)

    print("\n")
    print(f"root_path = {root_path}")
    print(f"this_date = {this_date}")
    print(f"semaphore = {semaphore}")

    # Options
    if not isinstance(
        hyper_random_for_openroute_user_tts := hyper_random(interval=[0, 47]),
        int
    ):
        raise ValueError("hyper_random function did not return an integer")
    if not isinstance(
        hyper_random_for_openroute_model_tts := hyper_random(interval=[0, 487]),
        int
    ):
        raise ValueError("hyper_random function did not return an integer")

    # Declarations
    working_path: Path | None = None
    rss_download_path: Path | None = None

    trend_list: TrendList | None = None

    # 0. Setup | Initialization
    if finalphore.get(SemaphoreKey.ZERO):
        working_path = root_path / datetime_utc
        try:
            working_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"An error occurred during path creation: {e}")
        rss_download_path = working_path / "rss_trend.html"

    if not working_path or not isinstance(working_path, Path):
        return 1

    print("\n")
    print(f"working_path = {working_path}")
    print(f"rss_download_path = {working_path}")
    print(f"trend_list = {working_path}")

    # 1) Get trends
    trend_list = _run_or_load(
        key=SemaphoreKey.ONE,
        finalphore=finalphore,
        working_path=working_path,
        filename="trends_1.json",
        state=trend_list if trend_list else TrendList(),
        run=lambda _prev: get_trends(
            rss_download_path=rss_download_path,
            working_path=working_path,
            delete_rss_xml_path=False,
        ),
    )
    if not isinstance(trend_list, TrendList):
        return 1

    # 2) Create prompts (in-place mutation; return state)
    trend_list = _run_or_load(
        key=SemaphoreKey.TWO,
        finalphore=finalphore,
        working_path=working_path,
        filename="trends_2.json",
        state=trend_list,
        run=lambda prev: (
            create_trend_prompt(
                trend_list=prev,
                overwrite_file=False,
                write_file=False,
            )
            or prev
        ),
    )
    if not isinstance(trend_list, TrendList):
        return 1

    # 3) Query models (in-place mutation; return state)
    trend_list = _run_or_load(
        key=SemaphoreKey.THREE,
        finalphore=finalphore,
        working_path=working_path,
        filename="trends_3.json",
        state=trend_list,
        run=lambda prev: (
            query_models(
                trend_list=prev,
                user_counter=hyper_random_for_openroute_user_tts,
                model_counter=hyper_random_for_openroute_model_tts,
            )
            or prev
        ),
    )
    if not isinstance(trend_list, TrendList):
        return 1

    # # 1. [MAIN PATH] Get trend xml file
    # if working_path and working_path.exists():
    #     output_log_path = working_path / "trends_1.json"
    # if finalphore.get(SemaphoreKey.ONE):
    #     if not isinstance(
    #         trend_list := get_trends(
    #             rss_download_path=rss_download_path,
    #             working_path=working_path,
    #             delete_rss_xml_path=False,
    #         ),
    #         TrendList
    #     ):
    #         return 1
    #     if output_log_path and output_log_path.exists():
    #         save_trendlist(trend_list, output_log_path)
    #     if not is_loaded:
    #         is_loaded = True
    # else:
    #     if output_log_path and output_log_path.exists():
    #         trend_list = load_trendlist(output_log_path)
    #     else:
    #         print(f"File {output_log_path} does not exist.")
    #         sys.exit(0)

    # # 2. [MAIN PATH - AI PROMPT TEXT CREATION] Create TTS prompt input
    # if working_path and working_path.exists():
    #     output_log_path = working_path / "trends_2.json"
    # if finalphore.get(SemaphoreKey.TWO):
    #     create_trend_prompt(
    #         trend_list=trend_list,
    #         overwrite_file=False,
    #         write_file=False,
    #     )
    #     if output_log_path and output_log_path.exists():
    #         save_trendlist(trend_list, output_log_path)
    # else:
    #     if output_log_path and output_log_path.exists():
    #         trend_list = load_trendlist(output_log_path)
    #     else:
    #         print(f"File {output_log_path} does not exist.")
    #         sys.exit(0)

    # # 3. [MAIN PATH - AI PROMPT EXECUTION] Query TTS prompt to obtain its result
    # if working_path and working_path.exists():
    #     output_log_path = working_path / "trends_3.json"
    # if finalphore.get(SemaphoreKey.THREE):
    #     query_models(
    #         trend_list=trend_list,
    #         user_counter=hyper_random_for_openroute_user_tts,
    #         model_counter=hyper_random_for_openroute_model_tts,
    #     )
    #     if output_log_path and output_log_path.exists():
    #         save_trendlist(trend_list, output_log_path)
    # else:
    #     if output_log_path and output_log_path.exists():
    #         trend_list = load_trendlist(output_log_path)
    #     else:
    #         print(f"File {output_log_path} does not exist.")
    #         sys.exit(0)

    # # 4/5. [BRANCH A - AI SOLUTION]
    # if image_mood_input_by_ai:

    #     # 4.A [BRANCH A - AI PROMPT TEXT CREATION] Create Image/Mood prompt input
    #     output_log_path = working_path / "trends_4A.json"
    #     if Semaphore.FOUR_A:
    #         save_trendlist(trend_list, output_log_path)
    #     else:
    #         if output_log_path.exists():
    #             trend_list = load_trendlist(output_log_path)
    #         else:
    #             print(f"File {output_log_path} does not exist.")
    #             sys.exit(0)

    #     # 5.A [BRANCH A - AI PROMPT EXECUTION] Query Image/Mood prompt to obtain its result
    #     output_log_path = working_path / "trends_5A.json"
    #     if Semaphore.FIVE_A:
    #         save_trendlist(trend_list, output_log_path)
    #     else:
    #         if output_log_path.exists():
    #             trend_list = load_trendlist(output_log_path)
    #         else:
    #             print(f"File {output_log_path} does not exist.")
    #             sys.exit(0)


    # # 4/5. [BRANCH B - HEURISTICS SOLUTION]
    # else:

    #     # 4.B [BRANCH B - HEURISTICS IMAGE KEYWORD CREATION] Create Image query keywords based on data
    #     output_log_path = working_path / "trends_4B.json"
    #     if Semaphore.FOUR_B:
    #         save_trendlist(trend_list, output_log_path)
    #     else:
    #         if output_log_path.exists():
    #             trend_list = load_trendlist(output_log_path)
    #         else:
    #             print(f"File {output_log_path} does not exist.")
    #             sys.exit(0)


    #     # 5.B.I [BRANCH B - HEURISTICS MOOD QUERY CREATION] Create mood query based on heuristics
    #     output_log_path = working_path / "trends_5Bi.json"
    #     if Semaphore.FIVE_BI:
    #         save_trendlist(trend_list, output_log_path)
    #     else:
    #         if output_log_path.exists():
    #             trend_list = load_trendlist(output_log_path)
    #         else:
    #             print(f"File {output_log_path} does not exist.")
    #             sys.exit(0)


    #     # 5.B.II [BRANCH B - HEURISTICS MOOD PREDICTION] Predict mood query based on heuristics
    #     output_log_path = working_path / "trends_5Bii.json"
    #     if Semaphore.FIVE_BII:
    #         predict_mood(trend_list=trend_list)
    #         save_trendlist(trend_list, output_log_path)
    #     else:
    #         if output_log_path.exists():
    #             trend_list = load_trendlist(output_log_path)
    #         else:
    #             print(f"File {output_log_path} does not exist.")
    #             sys.exit(0)

    # # 6. [MAIN PATH - XXXXXXX] Search for images
    # output_log_path = working_path / "trends_6.json"
    # if Semaphore.SIX:
    #     save_trendlist(trend_list, output_log_path)
    # else:
    #     if output_log_path.exists():
    #         trend_list = load_trendlist(output_log_path)
    #     else:
    #         print(f"File {output_log_path} does not exist.")
    #         sys.exit(0)

    # # 7. [MAIN PATH - XXXXXXX] Download images
    # output_log_path = working_path / "trends_7.json"
    # if Semaphore.SEVEN:
    #     # download_images(trend_list)  # TODO: implement
    #     save_trendlist(trend_list, output_log_path)
    # else:
    #     if output_log_path.exists():
    #         trend_list = load_trendlist(output_log_path)
    #     else:
    #         print(f"File {output_log_path} does not exist.")
    #         sys.exit(0)

    # # 8. [MAIN PATH - XXXXXXX] Parse images:
    # #    - Standardize file extensions resolving compression
    # #    - Remove duplicates by name and by AI
    # #    - Standardize numeric ordered name
    # output_log_path = working_path / "trends_8.json"
    # if Semaphore.EIGHT:
    #     save_trendlist(trend_list, output_log_path)
    # else:
    #     if output_log_path.exists():
    #         trend_list = load_trendlist(output_log_path)
    #     else:
    #         print(f"File {output_log_path} does not exist.")
    #         sys.exit(0)

    # # 9. [MAIN PATH - XXXXXXX] Create audio tts from query model's responses
    # output_log_path = working_path / "trends_9.json"
    # if Semaphore.NINE:
    #     save_trendlist(trend_list, output_log_path)
    # else:
    #     if output_log_path.exists():
    #         trend_list = load_trendlist(output_log_path)
    #     else:
    #         print(f"File {output_log_path} does not exist.")
    #         sys.exit(0)

    # # 10. [MAIN PATH - XXXXXXX] Generate background music based on mood and audio's length
    # output_log_path = working_path / "trends_10.json"
    # if Semaphore.TEN:
    #     save_trendlist(trend_list, output_log_path)
    # else:
    #     if output_log_path.exists():
    #         trend_list = load_trendlist(output_log_path)
    #     else:
    #         print(f"File {output_log_path} does not exist.")
    #         sys.exit(0)

    # # 11. [MAIN PATH - XXXXXXX] Create thumbnails, ribbons and metadata
    # output_log_path = working_path / "trends_11.json"
    # if Semaphore.ELEVEN:
    #     save_trendlist(trend_list, output_log_path)
    # else:
    #     if output_log_path.exists():
    #         trend_list = load_trendlist(output_log_path)
    #     else:
    #         print(f"File {output_log_path} does not exist.")
    #         sys.exit(0)

    # # 12. [MAIN PATH - XXXXXXX] Create video from: tts audio, images downloaded, background music
    # output_log_path = working_path / "trends_12.json"
    # if Semaphore.TWELVE:
    #     save_trendlist(trend_list, output_log_path)
    # else:
    #     if output_log_path.exists():
    #         trend_list = load_trendlist(output_log_path)
    #     else:
    #         print(f"File {output_log_path} does not exist.")
    #         sys.exit(0)

    # # 13. [MAIN PATH - XXXXXXX] Upload video to youtube with correct thumbs and metadata
    # output_log_path = working_path / "trends_13.json"
    # if Semaphore.THIRTEEN:
    #     save_trendlist(trend_list, output_log_path)
    # else:
    #     if output_log_path.exists():
    #         trend_list = load_trendlist(output_log_path)
    #     else:
    #         print(f"File {output_log_path} does not exist.")
    #         sys.exit(0)

    return 0


# --------------------------------------------------------------------------------------
# Exports
# --------------------------------------------------------------------------------------
__all__: list[str] = [
    "acta_core",
]

# -------------------------------------------------------------------------------------
# Test
# python -m uqbar acta /Users/egg/acta/content/ -d '2026-01-21' -s 0,1 > out.txt 2>&1
# python -m uqbar acta /Users/egg/acta/content/ -d '2026-01-21' -s 0,2 > out.txt 2>&1
# python -m uqbar acta /Users/egg/acta/content/ -d '2026-01-21' -s 0,3 > out.txt 2>&1
# -------------------------------------------------------------------------------------
# if __name__ == "__main__":
#     ...
