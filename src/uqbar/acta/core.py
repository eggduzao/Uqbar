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
            raise KeyError(f"{dtnow} Invalid semaphore key: {key!r}") from e


# --------------------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------------------
def _resolve_semaphore(raw_string: str | None) -> Semaphore:
    """ Resolves Semaphores"""

    # Create Semaphore
    semaphore: Semaphore = Semaphore()

    # Update Semaphore
    if raw_string is None:
        semaphore.set_all(True)
    else:
        SPLIT_RE = r" ,;"
        str_list: list[str] = re.split(raw_string, SPLIT_RE)
        int_list: list[int] = [int(e) for e in str_list if int(e)]
        semaphore.update_many(int_list, True)

    return semaphore


def _prev_checkpoint_path(
    *,
    key: SemaphoreKey,
    working_path: Path,
    filename: str,
    first_key: SemaphoreKey,
) -> Path | None:
    """
    Find the nearest existing checkpoint strictly before `key`.

    Assumes checkpoint filenames are of the form 'trends_<N>.json' (as in your example),
    where N matches SemaphoreKey numeric values.

    Parameters
    ----------
    key
        Current step.
    working_path
        Folder where checkpoints live.
    filename
        Current step filename (unused for discovery other than assuming the same scheme).
    first_key
        Numerical first step.

    Returns
    -------
    Path | None
        Path to the nearest previous checkpoint, or None if none exist.
    """
    # Use the convention you already showed: trends_<i>.json
    for i in range(key.value - 1, first_key.value - 1, -1):
        candidate = working_path / f"trends_{i}.json"
        if candidate.exists():
            return candidate
    return None


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
    Gap-aware checkpoint runner/loader controlled by `finalphore`.

    Behavior
    --------
    - If `finalphore.get(key)` is False:
        - If checkpoint exists: load and return it.
        - Else: return `state` unchanged.
    - If `finalphore.get(key)` is True:
        - If `key` is the numerical first step: run with `state`, save, return.
        - Else: find nearest earlier checkpoint in decreasing order; load it; run; save; return.
          If none exist: raise FileNotFoundError.
        - If `run()` does not return a TrendList: return None (caller can treat as failure).

    Parameters
    ----------
    key
        Current step key.
    finalphore
        Semaphore controlling which steps run.
    working_path
        Folder where checkpoints live.
    filename
        Checkpoint filename for this step (e.g. "trends_1.json").
    state
        In-memory TrendList used when passing through or when running the first step.
    run
        Step function taking a TrendList and returning a TrendList.

    Returns
    -------
    TrendList | None
        The loaded or newly computed TrendList, or None if `run()` failed.

    Raises
    ------
    FileNotFoundError
        If the step is enabled but no earlier checkpoint exists and `key` is not the first step.
    """
    checkpoint_path = working_path / filename

    # If this step is disabled: load if possible, otherwise pass-through.
    if not finalphore.get(key):
        if checkpoint_path.exists():
            return load_trendlist(checkpoint_path)
        return state

    # Enabled step: determine the numerical first step (lowest enum value).
    first_key = min(SemaphoreKey, key=lambda k: k.value)

    # First step: no previous TrendList required.
    if key == first_key:
        new_state = run(state)
        save_trendlist(new_state, checkpoint_path)
        return new_state

    # Non-first step: must backfill from nearest earlier checkpoint.
    prev_path = _prev_checkpoint_path(
        key=key,
        working_path=working_path,
        filename=filename,
        first_key=first_key,
    )
    if prev_path is None:
        raise FileNotFoundError(
            f"{dtnow} Cannot run step {key.name} (value={key.value}): "
            f"no earlier checkpoint found under {working_path}. "
            f"Expected one of trends_{key.value-1}.json .. trends_{first_key.value}.json."
        )

    prev_state = load_trendlist(prev_path)
    new_state = run(prev_state)
    save_trendlist(new_state, checkpoint_path)
    return new_state


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

    # Step 0: CLI handles + Semaphore logic + any preprocessing [OK]
    if finalphore.get(SemaphoreKey.ZERO):
        working_path = root_path / datetime_utc
        try:
            working_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"An error occurred during path creation: {e}")
        rss_download_path = working_path / "rss_trend.html"

    if not working_path:
        return 1

    # Step 1: Google Trends API - Fetching Trends [OK]
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

    # Step 2: Create prompt strings: TTS-friendly News Text, News Mood, Image
    # Query Keywords and Thumb prompt-ask [--]
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

    # Step 3.1: Use ``DeepSeek-R1-Distill-Qwen-32B-4bit`` to get News Texts
    # (based on prompt from 2) [ ]
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

    # Step 3.2: Use ``SamLowe/roberta-base-go_emotions`` to get News Texts
    # Emotions (based on prompt from 2) [ ]

    # Step 3.3: Use ``sentence-transformers/all-MiniLM-L6-v2`` with ``KeyBERT``
    # to get Image Query String (based on prompt from 2) [ ]

    # Step 3.4: Use ``DeepSeek-R1-Distill-Qwen-32B-4bit`` to generate a thumbnail
    # query prompt text [ ]

    # Step 4: Fetch images using ``requests`` + ``Selenium`` and Image Query String
    # (from 3.3) [ ]

    # Step 5: Create TTS audio using ``piper``, ``wave``, ``soundfile``, ``pydub``,
    # ``ffmpeg`` and News Texts (from 3.1) [ ]

    # Step 6: Select background music mapping music library to News Text Emotion
    # (from 3.2) [ ]

    # Step 7: Assign sound effects with ``BBC Sound Effects Archive`` coordinated with
    # the TTS Audio from 5 using `piper`, `wave`, `soundfile`, `pydub`, `ffmpeg` [ ]

    # Step 8: Create thumbnail 'main' with `segmind/SSD-1B` based on 3.4, put background
    # with `Pillow` and upscale with `stabilityai/stable-diffusion-x4-upscaler` [ ]

    # Step 9: Orchestrate ``TTS + SFX + Background Audio`` with Carousel Image with Ken
    # Burns effect (and maybe others) using ``ffmpeg`` and ``moviepy`` [ ]

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
