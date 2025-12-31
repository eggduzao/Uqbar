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

from enum import Enum
from pathlib import Path
import sys


from uqbar.acta.utils import (
    PAYWALL_DOMAINS,
    GO_EMOTIONS_LABELS,
    NEWS_CATEGORIES,
    deprecated,
    dtnow,
    save_trendlist,
    load_trendlist,
    hyper_random,
    MoodLevel,
    QueryConfig,
    MoodItem,
    DateTimeUTC,
    Trend,
    TrendList,
)

from uqbar.acta.trend_download_scraper import get_trends
from uqbar.acta.trend_prompt_parser import (
    create_trend_tts_prompt,
    create_trend_image_mood_prompt,
)
from uqbar.acta.trend_newstext_maker import query_models, query_image_and_mood

from uqbar.acta.mood_predictor import predict_mood

# from uqbar.acta.image_scraper import
# from uqbar.acta.image_downloader import
# from uqbar.acta.image_processor import

# from uqbar.acta.audio_maker import
# from uqbar.acta.video_maker import

# -------------------------------------------------------------------------------------
# Constants
# -------------------------------------------------------------------------------------
ROOT_PATH = Path("/Users/egg/acta/content")


class Semaphore(Enum):
    """Placeholder"""
    ONE: bool = False
    TWO: bool = True
    THREE: bool = False
    FOUR_A: bool = False
    FIVE_A: bool = False
    FOUR_B: bool = False
    FIVE_BI: bool = False
    FIVE_BII: bool = False
    SIX: bool = False
    SEVEN: bool = False
    EIGHT: bool = False
    NINE: bool = False
    TEN: bool = False
    ELEVEN: bool = False
    TWELVE: bool = False
    THIRTEEN: bool = False

TESTING: bool = True


# ------------------------------------------------------------------------------------audi--
# Functions
# --------------------------------------------------------------------------------------
def acta_core(
    positional_argument,
    *,
    args: dict[str, Any] | None = None,
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

    # Options
    image_mood_input_by_ai: bool = False
    hyper_random_for_openroute_user_tts: int = hyper_random([0, 47])
    hyper_random_for_openroute_model_tts: int = hyper_random([0, 487])
    hyper_random_for_openroute_user_imgmood: int = hyper_random([0, 47])
    hyper_random_for_openroute_model_imgmood: int = hyper_random([0, 487])

    # Initialization - Date string
    datetime_utc = dtnow(fmt=False).split(" ")[0]
    if TESTING:
        datetime_utc = "2025-12-27"
    working_path: Path = ROOT_PATH / datetime_utc
    try:
        working_path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"An error occurred during path creation: {e}")

    # 1. [MAIN PATH] Get trend xml file
    output_log_path = working_path / "trends_1.json"
    if Semaphore.ONE:
        rss_download_path: Path = working_path / "rss_trend.html"
        trend_list: TrendList = get_trends(
            rss_download_path=rss_download_path,
            working_path=working_path,
            delete_rss_xml_path=True,
        )

        if trend_list is None:
            print("[Error] Trend list is None.")
            return 1

        save_trendlist(trend_list, output_log_path)
    else:
        if output_log_path.exists():
            trend_list = load_trendlist(output_log_path)
        else:
            print(f"File {output_log_path} does not exist.")
            sys.exit(0)

    # 2. [MAIN PATH - AI PROMPT TEXT CREATION] Create TTS prompt input
    output_log_path = working_path / "trends_2.json"
    if Semaphore.TWO:
        create_trend_tts_prompt(
            trend_list=trend_list,
            overwrite_file=False,
            write_file=False,
        )
        save_trendlist(trend_list, output_log_path)
    else:
        if output_log_path.exists():
            trend_list = load_trendlist(output_log_path)
        else:
            print(f"File {output_log_path} does not exist.")
            sys.exit(0)

    # 3. [MAIN PATH - AI PROMPT EXECUTION] Query TTS prompt to obtain its result
    output_log_path = working_path / "trends_3.json"
    if Semaphore.THREE:
        query_models(
            trend_list=trend_list,
            user_counter=hyper_random_for_openroute_user_tts,
            model_counter=hyper_random_for_openroute_model_tts,
        )
        save_trendlist(trend_list, output_log_path)
    else:
        if output_log_path.exists():
            trend_list = load_trendlist(output_log_path)
        else:
            print(f"File {output_log_path} does not exist.")
            sys.exit(0)

    # 4/5. [BRANCH A - AI SOLUTION]
    if image_mood_input_by_ai:
       
        # 4.A [BRANCH A - AI PROMPT TEXT CREATION] Create Image/Mood prompt input
        output_log_path = working_path / "trends_4A.json"
        if Semaphore.FOUR_A:
            create_trend_image_mood_prompt(
                trend_list=trend_list,
                overwrite_file=False,
                write_file=False,
            )
            save_trendlist(trend_list, output_log_path)
        else:
            if output_log_path.exists():
                trend_list = load_trendlist(output_log_path)
            else:
                print(f"File {output_log_path} does not exist.")
                sys.exit(0)

        # 5.A [BRANCH A - AI PROMPT EXECUTION] Query Image/Mood prompt to obtain its result
        output_log_path = working_path / "trends_5A.json"
        if Semaphore.FIVE_A:
            query_image_and_mood(
                trend_list=trend_list,
                user_counter=hyper_random_for_openroute_user_imgmood,
                model_counter=hyper_random_for_openroute_model_imgmood,
            )
            save_trendlist(trend_list, output_log_path)
        else:
            if output_log_path.exists():
                trend_list = load_trendlist(output_log_path)
            else:
                print(f"File {output_log_path} does not exist.")
                sys.exit(0)


    # 4/5. [BRANCH B - HEURISTICS SOLUTION]
    else:

        # 4.B [BRANCH B - HEURISTICS IMAGE KEYWORD CREATION] Create Image query keywords based on data
        output_log_path = working_path / "trends_4B.json"
        if Semaphore.FOUR_B:
            save_trendlist(trend_list, output_log_path)
        else:
            if output_log_path.exists():
                trend_list = load_trendlist(output_log_path)
            else:
                print(f"File {output_log_path} does not exist.")
                sys.exit(0)


        # 5.B.I [BRANCH B - HEURISTICS MOOD QUERY CREATION] Create mood query based on heuristics
        output_log_path = working_path / "trends_5Bi.json"
        if Semaphore.FIVE_BI:
            save_trendlist(trend_list, output_log_path)
        else:
            if output_log_path.exists():
                trend_list = load_trendlist(output_log_path)
            else:
                print(f"File {output_log_path} does not exist.")
                sys.exit(0)


        # 5.B.II [BRANCH B - HEURISTICS MOOD PREDICTION] Predict mood query based on heuristics
        output_log_path = working_path / "trends_5Bii.json"
        if Semaphore.FIVE_BII:
            predict_mood(trend_list=trend_list)
            save_trendlist(trend_list, output_log_path)
        else:
            if output_log_path.exists():
                trend_list = load_trendlist(output_log_path)
            else:
                print(f"File {output_log_path} does not exist.")
                sys.exit(0)

    # 6. [MAIN PATH - XXXXXXX] Search for images
    output_log_path = working_path / "trends_6.json"
    if Semaphore.SIX:
        save_trendlist(trend_list, output_log_path)
    else:
        if output_log_path.exists():
            trend_list = load_trendlist(output_log_path)
        else:
            print(f"File {output_log_path} does not exist.")
            sys.exit(0)

    # 7. [MAIN PATH - XXXXXXX] Download images
    output_log_path = working_path / "trends_7.json"
    if Semaphore.SEVEN:
        download_images(trend_list)
        save_trendlist(trend_list, output_log_path)
    else:
        if output_log_path.exists():
            trend_list = load_trendlist(output_log_path)
        else:
            print(f"File {output_log_path} does not exist.")
            sys.exit(0)

    # 8. [MAIN PATH - XXXXXXX] Parse images:
    #    - Standardize file extensions resolving compression
    #    - Remove duplicates by name and by AI
    #    - Standardize numeric ordered name
    output_log_path = working_path / "trends_8.json"
    if Semaphore.EIGHT:
        save_trendlist(trend_list, output_log_path)
    else:
        if output_log_path.exists():
            trend_list = load_trendlist(output_log_path)
        else:
            print(f"File {output_log_path} does not exist.")
            sys.exit(0)

    # 9. [MAIN PATH - XXXXXXX] Create audio tts from query model's responses
    output_log_path = working_path / "trends_9.json"
    if Semaphore.NINE:
        save_trendlist(trend_list, output_log_path)
    else:
        if output_log_path.exists():
            trend_list = load_trendlist(output_log_path)
        else:
            print(f"File {output_log_path} does not exist.")
            sys.exit(0)

    # 10. [MAIN PATH - XXXXXXX] Generate background music based on mood and audio's length
    output_log_path = working_path / "trends_10.json"
    if Semaphore.TEN:
        save_trendlist(trend_list, output_log_path)
    else:
        if output_log_path.exists():
            trend_list = load_trendlist(output_log_path)
        else:
            print(f"File {output_log_path} does not exist.")
            sys.exit(0)

    # 11. [MAIN PATH - XXXXXXX] Create thumbnails, ribbons and metadata
    output_log_path = working_path / "trends_11.json"
    if Semaphore.ELEVEN:
        save_trendlist(trend_list, output_log_path)
    else:
        if output_log_path.exists():
            trend_list = load_trendlist(output_log_path)
        else:
            print(f"File {output_log_path} does not exist.")
            sys.exit(0)

    # 12. [MAIN PATH - XXXXXXX] Create video from: tts audio, images downloaded, background music
    output_log_path = working_path / "trends_12.json"
    if Semaphore.TWELVE:
        save_trendlist(trend_list, output_log_path)
    else:
        if output_log_path.exists():
            trend_list = load_trendlist(output_log_path)
        else:
            print(f"File {output_log_path} does not exist.")
            sys.exit(0)

    # 13. [MAIN PATH - XXXXXXX] Upload video to youtube with correct thumbs and metadata
    output_log_path = working_path / "trends_13.json"
    if Semaphore.THIRTEEN:
        save_trendlist(trend_list, output_log_path)
    else:
        if output_log_path.exists():
            trend_list = load_trendlist(output_log_path)
        else:
            print(f"File {output_log_path} does not exist.")
            sys.exit(0)

    return 0


# --------------------------------------------------------------------------------------
# Exports
# --------------------------------------------------------------------------------------
__all__: list[str] = [
    "acta_core",
]

# -------------------------------------------------------------------------------------
# Test | python -m uqbar acta > out.txt 2>&1
# -------------------------------------------------------------------------------------
# if __name__ == "__main__":
#     ...
