# SPDX-License-Identifier: MIT
# uqbar/milou/utils.py
"""
Milou | Utils
=============

Overview
--------
Placeholder.

Metadata
--------
- Project: Milou
- License: MIT
"""

# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from __future__ import annotations

from collections.abc import MutableSequence, Iterable
from dataclasses import dataclass, field
from datetime import timezone, timedelta, datetime
from email.utils import parsedate_to_datetime
import functools
from pathlib import Path
from typing import overload, Any
from urllib.parse import urlparse
import warnings


# -------------------------------------------------------------------------------------
# Constants
# -------------------------------------------------------------------------------------


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


def _pubdate_to_tz(
    pubdate: str | None, tz: timezone
) -> tuple[str | None, dict[str, str | None]]:
    """
    Input is RFC2822-like: "Tue, 16 Dec 2025 14:40:00 -0800"
    We parse the offset (e.g., -0800) and convert to tz.
    Returned string is: YYYY-MM-DDTHH:MM:SS  (no offset appended)
    """
    parts = _empty_parts()
    if not pubdate:
        return None, parts

    dt = parsedate_to_datetime(
        pubdate
    )  # tz-aware because your input includes an offset
    dt_tz = dt.astimezone(tz)

    parts["year"] = f"{dt_tz.year:04d}"
    parts["month"] = f"{dt_tz.month:02d}"
    parts["day"] = f"{dt_tz.day:02d}"
    parts["hour"] = f"{dt_tz.hour:02d}"
    parts["minute"] = f"{dt_tz.minute:02d}"
    parts["second"] = f"{dt_tz.second:02d}"

    iso = (
        f"{parts['year']}-{parts['month']}-{parts['day']}"
        f"T{parts['hour']}:{parts['minute']}:{parts['second']}"
    )
    return iso, parts


# --------------------------------------------------------------------------------------
# Functions
# --------------------------------------------------------------------------------------
def deprecated(reason: str):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            warnings.warn(
                f"{func.__name__} is deprecated: {reason}",
                DeprecationWarning,
                stacklevel=2,
            )
            return func(*args, **kwargs)

        return wrapper

    return decorator


def dtnow(*, fmt: bool = True):
    if fmt:
        return f"[{str(datetime.now()).split(".")[0]}]"
    return datetime.now()


# --------------------------------------------------------------------------------------
# Classes
# --------------------------------------------------------------------------------------
@dataclass(frozen=True)
class QueryConfig:
    """
    Query Configuration Dataclass
    """

    max_phrases: int = 3  # quoted phrases for precision query
    max_keywords: int = 10  # unquoted tokens for both queries
    min_token_len: int = 2
    phrase_ngram_range: tuple[int, int] = (2, 3)
    phrase_min_score: float = 0.05  # TF-IDF threshold (tune for short titles)
    keep_unicode_letters: bool = True  # keep accented letters
    ascii_only: bool = False  # if True, strip accents entirely


@dataclass(slots=True)
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

    # Trigger attribute (user assigns RFC2822 string to this)
    datetime_utc: str | None = None

    # Derived attributes
    datetime_br: str | None = None
    datetime_us: str | None = None

    datetime_utc_parts: dict[str, str | None] = field(default_factory=_empty_parts)
    datetime_br_parts: dict[str, str | None] = field(default_factory=_empty_parts)
    datetime_us_parts: dict[str, str | None] = field(default_factory=_empty_parts)

    # Internal: avoid triggering during __init__
    _initializing: bool = field(default=True, init=False, repr=False)

    def __post_init__(self) -> None:
        # Initialization should NOT trigger the “manual assignment” behavior.
        self._initializing = False

    def __setattr__(self, name: str, value: Any) -> None:
        # Normal set first
        super().__setattr__(name, value)

        # Trigger only after init and only when user sets datetime_utc
        if name == "datetime_utc" and not getattr(self, "_initializing", True):
            iso_utc, parts_utc = _pubdate_to_tz(value, UTC)
            iso_br, parts_br = _pubdate_to_tz(value, BRAZIL_TZ)
            iso_us, parts_us = _pubdate_to_tz(value, US_EAST_TZ)

            super().__setattr__("datetime_utc", iso_utc)
            super().__setattr__("datetime_br", iso_br)
            super().__setattr__("datetime_us", iso_us)

            super().__setattr__("datetime_utc_parts", parts_utc)
            super().__setattr__("datetime_br_parts", parts_br)
            super().__setattr__("datetime_us_parts", parts_us)

    # --- required by MutableSequence ---

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
        if isinstance(index, slice):
            if not isinstance(value, Iterable):
                raise TypeError("Slice assignment requires an iterable of Trend.")
            self._items[index] = list(value)
        else:
            if not isinstance(value, Trend):
                raise TypeError(f"Expected Trend, got {type(value)!r}.")
            self._items[index] = value

    def __delitem__(self, index: int | slice) -> None:
        del self._items[index]

    def insert(self, index: int, value: Trend) -> None:
        if not isinstance(value, Trend):
            raise TypeError(f"Expected Trend, got {type(value)!r}.")
        self._items.insert(index, value)

    # --- optional niceties ---

    def __repr__(self) -> str:
        return f"TrendList(datetime_br={self.datetime_br!r}, n={len(self._items)})"

    def to_list(self) -> list[Trend]:
        """Return a shallow copy of the underlying list."""
        return list(self._items)


@dataclass(slots=True)
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

    title: str | None = None
    volume: float | None = None

    picture_source: str | None = None

    news_item_title_1: str | None = None
    news_item_url_1: str | None = None
    news_item_source_1: str | None = None
    news_item_paywall_flag_1: bool | None = None

    news_item_title_2: str | None = None
    news_item_url_2: str | None = None
    news_item_source_2: str | None = None
    news_item_paywall_flag_2: bool | None = None

    news_item_title_3: str | None = None
    news_item_url_3: str | None = None
    news_item_source_3: str | None = None
    news_item_paywall_flag_3: bool | None = None

    tts_prompt_query: str | None = None
    file_prompt_query: str | None = None

    tts_prompt_response: list[list[str]] = field(default_factory=list)

    _initializing: bool = field(default=True, init=False, repr=False)

    content_path: Path = field(default_factory=Path)
    image_path: Path = field(default_factory=Path)
    video_path: Path = field(default_factory=Path)
    audio_path: Path = field(default_factory=Path)

    def __post_init__(self) -> None:
        # Set flags based on any URLs provided at construction time
        for url_field, flag_field in _URL_TO_FLAG.items():
            url = getattr(self, url_field)
            setattr(self, flag_field, _is_paywalled(url))
        self._initializing = False

    def __setattr__(self, name: str, value: Any) -> None:
        super().__setattr__(name, value)

        # If a URL changes after init, keep its paywall flag in sync
        if not getattr(self, "_initializing", True) and name in _URL_TO_FLAG:
            flag_field = _URL_TO_FLAG[name]
            super().__setattr__(flag_field, _is_paywalled(value))


# --------------------------------------------------------------------------------------
# Exports
# --------------------------------------------------------------------------------------
__all__: list[str] = [
    "deprecated",
    "dtnow",
]
