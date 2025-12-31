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

from pathlib import Path


from uqbar.acta.utils import (
    PAYWALL_DOMAINS,
    GO_EMOTIONS_LABELS,
    NEWS_CATEGORIES,
    deprecated,
    dtnow,
    save_trendlist,
    load_trendlist,
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


# ------------------------------------------------------------------------------------audi--
# Functions
# --------------------------------------------------------------------------------------
def acta_core(
    positional_argument,
    *,
    args: dict[str, Any] | None = None,
) -> int:
    """
    Entry point for `python -m acta` and the console script.


    Notes
    -----
    Results is a list[list[list[str]]]

    Parameters
    ----------
    place_holder :
        Placeolder
    """

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

    # Initialization - Date string
    # datetime_utc = dtnow(fmt=False).split(" ")[0]
    datetime_utc = "2025-12-27"
    working_path: Path = ROOT_PATH / datetime_utc
    # try:
    #     working_path.mkdir(parents=True, exist_ok=True)
    # except Exception as e:
    #     print(f"An error occurred during path creation: {e}")

    # # 1. Get trend xml file
    # rss_download_path: Path = working_path / "rss_trend.html"
    # trend_list: TrendList = get_trends(
    #     rss_download_path=rss_download_path,
    #     working_path=working_path,
    #     delete_rss_xml_path=True,
    # )

    # if trend_list is None:
    #     print("[Error] Trend list is None.")
    #     return 1

    output_path_1 = working_path / "trends_1.json"
    # # save_trendlist(trend_list, output_path_1)
    # trend_list = load_trendlist(output_path_1)

    # # 2. Create prompt input
    # create_trend_tts_prompt(
    #     trend_list=trend_list,
    #     overwrite_file=False,
    #     write_file=False,
    # )

    output_path_2 = working_path / "trends_2.json"
    # save_trendlist(trend_list, output_path_2)
    trend_list = load_trendlist(output_path_2)

    # 3. Create news text prompt result
    query_models(trend_list=trend_list)

    output_path_3 = working_path / "trends_3.json"
    save_trendlist(trend_list, output_path_3)
    # # trend_list = load_trendlist(output_path_3)

    # # 4. Create mood and image prompt results
    # create_trend_image_mood_prompt
    # query_image_and_mood(trend_list=trend_list)


    # output_path_4 = working_path / "trends_4.json"
    # save_trendlist(trend_list, output_path_4)
    # # trend_list = load_trendlist(output_path_4)

    # # 5. Create mood results
    # predict_mood(trend_list=trend_list)

    # output_path_5 = working_path / "trends_5.json"
    # save_trendlist(trend_list, output_path_5)
    # trend_list = load_trendlist(output_path_5)

    # 6. Download images
    # download_images(trend_list)

    # 7. Create audio tts from query model's responses

    # 8. Generate background music based on audio's length

    # 9. Create video from: tts audio, images downloaded, background music

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
