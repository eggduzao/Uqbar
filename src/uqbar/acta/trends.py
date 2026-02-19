# SPDX-License-Identifier: MIT
# uqbar/acta/__init__.py
"""
Acta Diurna
===========

Overview
--------
Placeholder.

Metadata
--------
- Project: Acta diurna
- License: MIT
"""

# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from __future__ import annotations

import json
from collections.abc import Iterable, MutableSequence
from dataclasses import dataclass, field, fields
from pathlib import Path
from typing import Any, overload
from urllib.parse import urlparse

# -------------------------------------------------------------------------------------
# Constants
# -------------------------------------------------------------------------------------
UTC_DEFAULT_OFFSET = -8

UTC_USAEAST_OFFSET = -5

UTC_BRAZIL_OFFSET = -3


PAYWALL_DOMAINS: set[str] = {  # common hard/soft paywalls
    "nytimes.com", "wsj.com", "ft.com", "economist.com", "bloomberg.com",
    "washingtonpost.com", "theatlantic.com", "newyorker.com", "times.com", # UK
    "thetimes.co.uk", "telegraph.co.uk",
}

_URL_TO_FLAG: dict[str, str] = {
    "news_item_url_1": "news_item_paywall_flag_1",
    "news_item_url_2": "news_item_paywall_flag_2",
    "news_item_url_3": "news_item_paywall_flag_3",
}


_MONTHS_DICT: dict[str, str] = {
    "jan": "01", "feb": "02", "fev": "02", "mar": "03", "apr": "04", "abr": "04",
    "may": "05", "mai": "05", "jun": "06", "jul": "07", "aug": "08",
    "ago": "08", "agu": "08", "sep": "09", "set": "09", "oct": "10", "okt": "10",
    "out": "10", "nov": "11", "dec": "12", "dez": "12", "des": "12",
}


GO_EMOTIONS_LABELS: list[str] = [
    "admiration",
    "amusement",
    "anger",
    "annoyance",
    "approval",
    "caring",
    "confusion",
    "curiosity",
    "desire",
    "disappointment",
    "disapproval",
    "disgust",
    "embarrassment",
    "excitement",
    "fear",
    "gratitude",
    "grief",
    "joy",
    "love",
    "nervousness",
    "optimism",
    "pride",
    "realization",
    "relief",
    "remorse",
    "sadness",
    "surprise",
    "neutral",
]


@dataclass()
class MoodItem:
    admiration: float | None = None
    amusement: float | None = None
    anger: float | None = None
    annoyance: float | None = None
    approval: float | None = None
    caring: float | None = None
    confusion: float | None = None
    curiosity: float | None = None
    desire: float | None = None
    disappointment: float | None = None
    disapproval: float | None = None
    disgust: float | None = None
    embarrassment: float | None = None
    excitement: float | None = None
    fear: float | None = None
    gratitude: float | None = None
    grief: float | None = None
    joy: float | None = None
    love: float | None = None
    nervousness: float | None = None
    optimism: float | None = None
    pride: float | None = None
    realization: float | None = None
    relief: float | None = None
    remorse: float | None = None
    sadness: float | None = None
    surprise: float | None = None
    neutral: float | None = None

    # ---------- BIG GETTER ----------
    def as_list(self) -> list[float | None]:
        """
        Return the mood values as a list ordered by GO_EMOTIONS_LABELS.
        """
        return [getattr(self, name) for name in GO_EMOTIONS_LABELS]

    # ---------- BIG SETTER ----------
    def from_list(self, values: Iterable[float | None]) -> None:
        """
        Populate mood values from a list ordered by GO_EMOTIONS_LABELS.
        """
        values = list(values)
        if len(values) != len(GO_EMOTIONS_LABELS):
            raise ValueError(
                f"Expected {len(GO_EMOTIONS_LABELS)} values, got {len(values)}."
            )
        for name, value in zip(GO_EMOTIONS_LABELS, values, strict=False):
            setattr(self, name, value)


# --------------------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------------------
def _is_paywalled(url: str | None) -> bool:
    if not url:
        return False
    host = (urlparse(url).netloc or "").lower()
    host = host.split(":")[0]
    return any(host == d or host.endswith("." + d) for d in PAYWALL_DOMAINS)


def _empty_parts() -> dict[str, str | None]:
    return {
        "year": None,
        "month": None,
        "day": None,
        "hour": None,
        "minute": None,
        "second": None,
    }

def _trend_to_dict(t: Trend) -> dict[str, Any]:
    data: dict[str, Any] = {}
    for f in fields(Trend):
        v = getattr(t, f.name)

        # Reconstruct Path on load, serialize as str on save
        if isinstance(v, Path):
            data[f.name] = str(v)
        else:
            data[f.name] = v

    return data


def _dict_to_trend(data: dict[str, Any]) -> Trend:
    # Start from defaults, then overwrite fields present in snapshot
    t = Trend()

    trend_field_names = {f.name for f in fields(Trend)}
    path_field_names = {
        f.name for f in fields(Trend)
        if f.type is Path or str(f.type) == "pathlib.Path"
    }

    for k, v in data.items():
        if k not in trend_field_names:
            continue  # ignore unknown fields (forward compatibility)

        if k in path_field_names:
            if v is None:
                setattr(t, k, None)  # allow None if you decide to use Optional later
            else:
                setattr(t, k, Path(v))
        else:
            setattr(t, k, v)

    return t


# --------------------------------------------------------------------------------------
# Functions
# --------------------------------------------------------------------------------------
# def chunked_list_to_str(chunked_list: list[list[str]]) -> str:
#     """Converts a chunked list in a text."""
#     texty = " ".join([" ".join(el) for el in chunked_list])
#     return texty.strip()

def save_trendlist(trend_list: TrendList, path: Path) -> None:
    payload: dict[str, Any] = {
        "schema_version": "1.0",  # _SCHEMA_VERSION
        "trendlist": {
            "datetime_utc": trend_list.datetime_utc,
            "datetime_br": trend_list.datetime_br,
            "datetime_us": trend_list.datetime_us,
            "datetime_utc_parts": trend_list.datetime_utc_parts,
            "datetime_br_parts": trend_list.datetime_br_parts,
            "datetime_us_parts": trend_list.datetime_us_parts,
        },
        "items": [_trend_to_dict(t) for t in trend_list],
    }

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def load_trendlist(path: Path) -> TrendList:
    payload: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))

    tl_meta: dict[str, Any] = payload.get("trendlist", {})
    tl = TrendList(
        datetime_utc=tl_meta.get("datetime_utc"),
        datetime_br=tl_meta.get("datetime_br"),
        datetime_us=tl_meta.get("datetime_us"),
    )

    # If present in file, overwrite the default empty parts
    if isinstance(tl_meta.get("datetime_utc_parts"), dict):
        tl.datetime_utc_parts = tl_meta["datetime_utc_parts"]
    if isinstance(tl_meta.get("datetime_br_parts"), dict):
        tl.datetime_br_parts = tl_meta["datetime_br_parts"]
    if isinstance(tl_meta.get("datetime_us_parts"), dict):
        tl.datetime_us_parts = tl_meta["datetime_us_parts"]

    items: list[str] = payload.get("items", [])

    for item in items:
        if not isinstance(item, dict):
            raise TypeError(f"Invalid snapshot: each item must be a dict, got {type(item)!r}.")
        tl.append(_dict_to_trend(item))

    return tl

# --------------------------------------------------------------------------------------
# Classes
# --------------------------------------------------------------------------------------
class DateTimeUTC:
    """
    Placeholder
    """
    def __init__(self, xml_time: str):
        """
        Placeholder
        """
        self.xml_time = xml_time
        self.months_dict: dict[str, str] = _MONTHS_DICT
        self.utc_datetime: str | None = None
        self.usa_datetime: str | None = None
        self.bra_datetime: str | None = None
        self.utc_parts: dict[str, Any] = _empty_parts()
        self.usa_parts: dict[str, Any] = _empty_parts()
        self.bra_parts: dict[str, Any] = _empty_parts()
        self._parse_dates_times()

    def _parse_dates_times(self) -> None:
        """
        Parses a RFC2822-like string exactly like this:
        "Sat, 27 Dec 2025 04:10:00 -0800"
        Given timezones and parts
        """

        # 1. Clean
        self.xml_time.strip()
        string = "".join(self.xml_time.split(","))

        # 2. Get parts by space
        datetime_list = string.split(" ")
        datetime_day = int(datetime_list[1])
        datetime_mon = self._translate_month(datetime_list[2])
        datetime_mon = int(datetime_mon) if datetime_mon is not None else datetime_list[2]
        datetime_yea = int(datetime_list[3])

        time_list = datetime_list[4].split(":")
        datetime_hou = int(time_list[0])
        datetime_min = int(time_list[1])
        datetime_sec = int(time_list[2])

        # 3. Calculating offset
        datetime_offset = int(datetime_list[5])
        utc_offset = UTC_DEFAULT_OFFSET - datetime_offset
        usa_offset = UTC_USAEAST_OFFSET - datetime_offset
        bra_offset = UTC_BRAZIL_OFFSET - datetime_offset
        utc_hour = min(datetime_hou + utc_offset, 23)
        usa_hour = min(datetime_hou + usa_offset, 23)
        bra_hour = min(datetime_hou + bra_offset, 23)

        # 4. Populate parts
        self.utc_parts["year"] = str(f"{datetime_yea:04d}")
        self.utc_parts["month"] = str(f"{int(datetime_mon):02d}")
        self.utc_parts["day"] = str(f"{datetime_day:02d}")
        self.utc_parts["hour"] = str(f"{utc_hour:02d}")
        self.utc_parts["minute"] = str(f"{datetime_min:02d}")
        self.utc_parts["second"] = str(f"{datetime_sec:02d}")
        self.usa_parts["year"] = str(f"{datetime_yea:04d}")
        self.usa_parts["month"] = str(f"{int(datetime_mon):02d}")
        self.usa_parts["day"] = str(f"{datetime_day:02d}")
        self.usa_parts["hour"] = str(f"{usa_hour:02d}")
        self.usa_parts["minute"] = str(f"{datetime_min:02d}")
        self.usa_parts["second"] = str(f"{datetime_sec:02d}")
        self.bra_parts["year"] = str(f"{datetime_yea:04d}")
        self.bra_parts["month"] = str(f"{int(datetime_mon):02d}")
        self.bra_parts["day"] = str(f"{datetime_day:02d}")
        self.bra_parts["hour"] = str(f"{bra_hour:02d}")
        self.bra_parts["minute"] = str(f"{datetime_min:02d}")
        self.bra_parts["second"] = str(f"{datetime_sec:02d}")

        # 5. Creating iso strings
        iso_utc_dlist = [self.utc_parts["year"], self.utc_parts["month"], self.utc_parts["day"]]
        iso_utc_hlist = [self.utc_parts["hour"], self.utc_parts["minute"], self.utc_parts["second"]]
        self.utc_datetime = f"{"-".join(iso_utc_dlist)}_{":".join(iso_utc_hlist)}"
        usa_utc_dlist = [self.usa_parts["year"], self.usa_parts["month"], self.usa_parts["day"]]
        usa_utc_hlist = [self.usa_parts["hour"], self.usa_parts["minute"], self.usa_parts["second"]]
        self.usa_datetime = f"{"-".join(usa_utc_dlist)}_{":".join(usa_utc_hlist)}"
        bra_utc_dlist = [self.bra_parts["year"], self.bra_parts["month"], self.bra_parts["day"]]
        bra_utc_hlist = [self.bra_parts["hour"], self.bra_parts["minute"], self.bra_parts["second"]]
        self.bra_datetime = f"{"-".join(bra_utc_dlist)}_{":".join(bra_utc_hlist)}"

    def _translate_month(self, month_name: str):
        """
        Translates month to numeric form as a string.
        """
        return self.months_dict.get(month_name.lower(), None)

    def _chunk_string(self, string: str, start: int, end: int):
        """
        Crops a string from start to end and returns the cropped part
        and the original string without the cropped part.
        """
        # 1. Extract the chunk
        chunk = string[start:end]

        # 2. Create the new chunkless string
        chunkless_original = string[:start] + string[end:]

        # 3. Return both
        return chunk, chunkless_original


@dataclass()
class Trend:
    """
    Container for Trend Items.

    Usage Examples
    --------------

    >>> tl[0].promt_query = "write me a news story..."
    >>> tl[0].prompt_response.append(["Line 1", "Line 2"])

    >>> tl = TrendList()  # no trigger during init
    >>> tl.datetime_utc = "Tue, 16 Dec 2025 14:40:00 -0800"  # triggers conversion
    >>> print(tl.datetime_utc, tl.datetime_br, tl.datetime_us)
    >>> print(tl.datetime_br_parts)
    """

    # Main fields
    title: str | None = None
    volume: float | None = None
    picture_source: str | None = None

    # News fields 1
    news_item_title_1: str | None = None
    news_item_url_1: str | None = None
    news_item_source_1: str | None = None
    news_item_paywall_flag_1: bool | None = None

    # News fields 2
    news_item_title_2: str | None = None
    news_item_url_2: str | None = None
    news_item_source_2: str | None = None
    news_item_paywall_flag_2: bool | None = None

    # News fields 3
    news_item_title_3: str | None = None
    news_item_url_3: str | None = None
    news_item_source_3: str | None = None
    news_item_paywall_flag_3: bool | None = None

    # Path fields
    content_path: Path = field(default_factory=Path)
    image_path: Path = field(default_factory=Path)
    video_path: Path = field(default_factory=Path)
    audio_path: Path = field(default_factory=Path)

    # Prompt Fields
    tts_prompt_query: str | None = None
    tts_file_prompt_query: str | None = None
    image_mood_prompt_query: str | None = None
    image_mood_file_prompt_query: str | None = None

    # Prompt Response Fields
    tts_presult_full_text: list[list[list[str]]] = field(default_factory=lambda: [])
    tts_presult_summary_text: list[str] = field(default_factory=lambda: [])
    image_presult_keywords: list[list[str]] = field(default_factory=lambda: [])
    mood_presult_keyword: list[str] = field(default_factory=lambda: [])

    # News mood fields
    # mood_scores: MoodItem = field(default_factory=MoodItem)

    # ----- Methods -----
    def update_paywall(self) -> None:

        for url_field, flag_field in _URL_TO_FLAG.items():
            url = getattr(self, url_field)
            if not url:
                print(f"URL field not assigned. Skipping paywall updatefor {url_field}.")
                continue
            setattr(self, flag_field, _is_paywalled(url))


class TrendList(MutableSequence[Trend]):
    """
    A thin, typed wrapper around list[Trend], with shared metadata.

    Usage Example
    -------------
    >>>  tl = TrendList(datetime_br="2025-12-22T09:00:00-03:00")
    >>>  tl.append(Trend(title="michael badgley", volume=200.0))
    >>>  tl.append(Trend(title="something else", volume=150.0))

    >>> t = Trend(news_item_url_a="https://www.nytimes.com/...")
    >>> print(t.news_item_paywall_flag_a)  # True

    >>> t.news_item_url_a = "https://example.com/free"
    >>> print(t.news_item_paywall_flag_a)  # False
    """

    # User should assign a RFC2822 string to this
    datetime_utc: str | None = None

    # Derived attributes
    datetime_br: str | None = None
    datetime_us: str | None = None

    datetime_utc_parts: dict[str, str | None]
    datetime_br_parts: dict[str, str | None]
    datetime_us_parts: dict[str, str | None]

    # Field dedicated to errors
    stdout_message: str | None = None
    stderr_message: str | None = None

    # Creating required list
    _items: list[Trend]

    def __init__(
        self,
        *,
        datetime_utc: str | None = None,
        datetime_br: str | None = None,
        datetime_us: str | None = None,
        stdout_message: str | None = None,
        stderr_message: str | None = None,
    ) -> None:
        self.datetime_utc = datetime_utc
        self.datetime_br = datetime_br
        self.datetime_us = datetime_us

        self.datetime_utc_parts = _empty_parts()
        self.datetime_br_parts = _empty_parts()
        self.datetime_us_parts = _empty_parts()

        self.stdout_message = stdout_message
        self.stderr_message = stderr_message

        self._items = []

    # ----- Functions required by MutableSequence -----
    def __len__(self) -> int:
        return len(self._items)

    @overload
    def __getitem__(self, index: int) -> Trend: ...
    @overload
    def __getitem__(self, index: slice) -> list[Trend]: ...

    def __getitem__(self, index: int | slice) -> Trend | list[Trend]:
        return self._items[index]

    @overload
    def __setitem__(self, index: int, value: Trend) -> None: ...
    @overload
    def __setitem__(self, index: slice, value: Iterable[Trend]) -> None: ...

    def __setitem__(self, index: int | slice, value: Trend | Iterable[Trend]) -> None:
        """
        Assign one `Trend` by integer index or many `Trend` items by slice.

        Parameters
        ----------
        index : int | slice
            Target position or slice.
        value : Trend | Iterable[Trend]
            A single Trend for integer assignment, or an iterable of Trends for slice assignment.

        Raises
        ------
        TypeError
            If `value` has the wrong type for the given `index`.
        """
        if isinstance(index, slice):
            # Guard: str/bytes are iterables but semantically wrong here.
            if isinstance(value, Iterable):

                # Normalize to list to support repeated validation and list slice assignment.
                try:
                    items: list[Trend] = list(value)
                except TypeError as e:
                    raise TypeError("Slice assignment requires an iterable of Trend.") from e

                # Validate element types with a helpful error.
                for x in items:
                    self._items[index] = items
                return
        elif isinstance(value, Trend):
            self._items[index] = value

    def __delitem__(self, index: int | slice) -> None:
        del self._items[index]

    def insert(self, index: int, value: Trend) -> None:
        # if not isinstance(value, Trend):
        #     raise TypeError(f"Expected Trend, got {type(value)!r}.")
        self._items.insert(index, value)


    # ----- Functions -----
    def update_datetime(self) -> None:

        # Trigger only after init and only when user sets datetime_utc
        if not self.datetime_utc:
            print("`datetime_utc` must exist. Not updating fields.")
            return None

        datetimeutc = DateTimeUTC(self.datetime_utc)
        self.datetime_utc = datetimeutc.utc_datetime
        self.datetime_utc_parts = datetimeutc.utc_parts
        self.datetime_br = datetimeutc.bra_datetime
        self.datetime_br_parts = datetimeutc.bra_parts
        self.datetime_us = datetimeutc.usa_datetime
        self.datetime_us_parts = datetimeutc.usa_parts

    # ----- Utility functions -----
    def __repr__(self) -> str:
        return f"TrendList(datetime_br={self.datetime_br!r}, n={len(self._items)})"

    def to_list(self) -> list[Trend]:
        """Return a shallow copy of the underlying list."""
        return list(self._items)


# --------------------------------------------------------------------------------------
# Exports
# --------------------------------------------------------------------------------------
__all__: list[str] = [
    "DateTimeUTC",
    "Trend",
    "TrendList",
    "MoodItem",
    "GO_EMOTIONS_LABELS",
]
