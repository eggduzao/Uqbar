# SPDX-License-Identifier: MIT
# uqbar/lola/todo_maker.py
"""
Lola | TO-DO Maker
==================

Requires: pyyaml (pip install pyyaml)

Overview
--------
Placeholder.

Metadata
--------
- Project: Lola
- License: MIT
"""

# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, astuple
from datetime import date, datetime, timedelta
from enum import Enum, auto
from math import floor
from pathlib import Path
from typing import Any
import yaml


# -------------------------------------------------------------------------------------
# Constants
# -------------------------------------------------------------------------------------
ROOT: Path = Path("/Users/egg/Projects/Uqbar/src/uqbar/lola/assets/")

HOLIDAY_YAML_PATH: Path = ROOT / "holiday_2026.yaml"

DAYMAP_YAML_PATH: Path = ROOT / "dayname.yaml"

MEETINGS_YAML_PATH: Path = ROOT / "meetings.yaml"

BILLS_YAML_PATH: Path = ROOT / "bills.yaml"

BDAYS_YAML_PATH: Path = ROOT / "birthdays.yaml"


WEEK_RULER_LENGTH: int = 150

BIG_RULER_LENGTH: int = 100

SMALL_RULER_LENGTH: int = 3


class HolidayType(Enum):
    PUBLIC_HOLIDAY = auto()      # National / State / City Official Holiday
    PUBLIC_OBSERVANCE = auto()   # National / State / City Observances
    HOLIDAY = auto()             # Personal vacation
    INSTITUTE = auto()           # Institutional Recess
    CONFERENCE = auto()          # Conference time block
    OTHER = auto()               # Catch-all


@dataclass
class DayName():
    name_en: str | None = None
    name_pt: str | None = None
    def __str__(self) -> str:
        return f"DayName({self.name_en}, {self.name_pt})"
    def __repr__(self) -> str:
        return f"DayName({self.name_en}, {self.name_pt})"

@dataclass
class Bill:
    day: str | None = None
    type: str | None = None
    subtype: str | None = None
    def __str__(self) -> str:
        return f"DayName({self.day}, {self.type}, {self.subtype})"
    def __repr__(self) -> str:
        return f"DayName({self.day}, {self.type}, {self.subtype})"


@dataclass
class Birthday:
    day: str | None = None
    person: str | None = None
    location: str | None = None
    def __str__(self) -> str:
        return f"DayName({self.day}, {self.person}, {self.location})"
    def __repr__(self) -> str:
        return f"DayName({self.day}, {self.person}, {self.location})"


@dataclass
class Meeting:
    day: str | None = None
    type: str | None = None
    start_time: str | None = None
    end_time: str | None = None
    def __str__(self) -> str:
        return (
            f"Meeting({self.day}, {self.type}, "
            f"{self.start_time}, {self.end_time})"
        )
    def __repr__(self) -> str:
        return (
            f"Meeting({self.day}, {self.type}, "
            f"{self.start_time}, {self.end_time})"
        )


# --------------------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------------------
@dataclass(frozen=True)
class HolidayRule:
    """
    A rule describing a date or date period that should be labeled.
    Kinds supported:
      - single_annual:   same month/day every year (e.g., Dec 25)
      - single_absolute: exact single date (e.g., 2025-03-19)
      - range_annual:    same month/day -> month/day every year (can cross year boundary)
      - range_absolute:  exact start/end dates (inclusive)
    """
    kind: str                                  # "single_annual" | "single_absolute" | "range_annual" | "range_absolute"
    label: str                                  # e.g., "Natal", "Recesso", "SBG 2025", ...
    type: HolidayType = HolidayType.OTHER

    # For single_annual: (month, day)
    md: tuple[int, int] | None = None

    # For single_absolute: dt
    dt: date | None = None

    # For range_annual: (m1, d1) -> (m2, d2) (can cross year)
    md_start: tuple[int, int] | None = None
    md_end: tuple[int, int] | None = None

    # For range_absolute: start_dt -> end_dt (inclusive)
    start_dt: date | None = None
    end_dt: date | None = None

    def matches(self, d: date) -> bool:
        if self.kind == "single_annual":
            m, day = self.md  # type: ignore
            return (d.month, d.day) == (m, day)

        if self.kind == "single_absolute":
            return d == self.dt  # type: ignore

        if self.kind == "range_annual":
            m1, d1 = self.md_start  # type: ignore
            m2, d2 = self.md_end    # type: ignore
            start = date(d.year, m1, d1)
            # If the annual window crosses Dec→Jan, the end falls in next year
            if (m2, d2) >= (m1, d1):
                end = date(d.year, m2, d2)
            else:
                end = date(d.year + 1, m2, d2)
                # If our test date is in Jan (or early year),
                # the start likely was in previous year
                if d < date(d.year, m1, d1):
                    start = date(d.year - 1, m1, d1)
            return start <= d <= end

        if self.kind == "range_absolute":
            return (self.start_dt  # type: ignore
                    <= d
                    <= self.end_dt)  # type: ignore

        raise ValueError(f"Unknown rule kind: {self.kind}")


def _load_yaml_dict(*, yaml_path: Path) -> dict[str, Any]:
    """
    Loads a YAML file into a Python dict using safe parsing.
    """
    if not yaml_path.exists():
        raise FileNotFoundError(f"YAML file not found: {yaml_path}")

    text = yaml_path.read_text(encoding="utf-8")
    data = yaml.safe_load(text)

    if data is None:
        raise ValueError(f"YAML file is empty: {yaml_path}")
    if not isinstance(data, dict):
        raise TypeError(f"Expected top-level YAML mapping (dict), got {type(data).__name__}")

    return data


def _parse_holiday_rules(*, data: dict[str, Any]) -> list[HolidayRule]:
    """
    Parses:
      data[HolidayRule] = list of items like:
        - rule: single_absolute | single_annual | range_absolute
          label: str
          holiday_type: enum-name-as-string
          dt: YYYY-MM-DD              (for single_absolute)
          md: [m, d]                  (for single_annual)
          start_dt: YYYY-MM-DD        (for range_absolute)
          end_dt: YYYY-MM-DD          (for range_absolute)

    Assumes HolidayRule and HolidayType exist in your codebase.
    """
    # ---- helpers (kept local on purpose; you can move them out later) ----
    def _require_str(item: dict[str, Any], key: str) -> str:
        v = item.get(key)
        if not isinstance(v, str) or not v.strip():
            raise ValueError(f"Holiday item missing/invalid '{key}': {item}")
        return v

    def _parse_iso_date(v: Any, *, key: str, item: dict[str, Any]) -> date:
        if not isinstance(v, str):
            raise ValueError(f"Holiday item '{key}' must be ISO date string, got {type(v).__name__}: {item}")
        try:
            return date.fromisoformat(v)
        except ValueError as e:
            raise ValueError(f"Holiday item '{key}' invalid ISO date '{v}': {item}") from e

    def _parse_md(v: Any, *, item: dict[str, Any]) -> tuple[int, int]:
        if not (isinstance(v, (list, tuple)) and len(v) == 2):
            raise ValueError(f"Holiday item 'md' must be [month, day], got {v!r}: {item}")
        m, d = v
        if not (isinstance(m, int) and isinstance(d, int)):
            raise ValueError(f"Holiday item 'md' must contain ints, got {v!r}: {item}")
        if not (1 <= m <= 12 and 1 <= d <= 31):
            raise ValueError(f"Holiday item 'md' out of range, got {v!r}: {item}")
        return (m, d)

    def _parse_holiday_type(v: Any, *, item: dict[str, Any]) -> "HolidayType":
        if not isinstance(v, str) or not v.strip():
            raise ValueError(f"Holiday item 'holiday_type' must be a non-empty string: {item}")
        try:
            # supports Enum lookups: HolidayType["PUBLIC_HOLIDAY"]
            return HolidayType[v]
        except Exception as e:
            raise ValueError(f"Unknown holiday_type '{v}'. Expected a HolidayType member name. Item: {item}") from e

    # ---- main parsing ----
    raw_list = data.get("holidays")
    if not isinstance(raw_list, list) or not raw_list:
        raise ValueError("YAML must contain a non-empty top-level 'holidays' list.")

    out: list[HolidayRule] = []

    for item in raw_list:
        if not isinstance(item, dict):
            raise TypeError(f"Each holiday entry must be a dict, got {type(item).__name__}: {item!r}")

        rule = _require_str(item, "rule")
        label = _require_str(item, "label")
        holiday_type = _parse_holiday_type(item.get("holiday_type"), item=item)

        if rule == "single_absolute":
            dt = _parse_iso_date(item.get("dt"), key="dt", item=item)
            out.append(HolidayRule(rule, label, holiday_type, dt=dt))

        elif rule == "single_annual":
            md = _parse_md(item.get("md"), item=item)
            out.append(HolidayRule(rule, label, holiday_type, md=md))

        elif rule == "range_absolute":
            start_dt = _parse_iso_date(item.get("start_dt"), key="start_dt", item=item)
            end_dt = _parse_iso_date(item.get("end_dt"), key="end_dt", item=item)
            out.append(HolidayRule(rule, label, holiday_type, start_dt=start_dt, end_dt=end_dt))

        else:
            raise ValueError(
                f"Unknown rule '{rule}'. Expected one of: single_absolute, single_annual, range_absolute. Item: {item}"
            )

    return out


def _parse_default_dict(*, data: dict[str, Any]) -> defaultdict[str, list[Any]]:
    """
    Generic parser for the "simple mapping -> list[str]" YAML pattern.

    Accepts YAML content shaped like:
      key1: [ "line1", "line2" ]
      key2:
        - "line3"
        - "line4"

    Returns:
      defaultdict(list) where each key maps to a list[str].

    Notes:
    - Keys are coerced to str (so YAML keys like 1 or "01" both become
      "1" or "01" as written).
    - Values must be either:
        * a single string
        * a list of strings
      Anything else raises (so you don't silently generate garbage).
    """
    out: defaultdict[str, list[Any]] = defaultdict(list)

    if not isinstance(data, dict):
        raise TypeError(f"Expected dict from YAML loader, got {type(data).__name__}")

    for raw_key, raw_val in data.items():
        key = str(raw_key)

        # Allow a single string as shorthand, normalize to list[str]
        if isinstance(raw_val, str):
            out[key].append(raw_val)
            continue

        # The common case: list[str]
        if isinstance(raw_val, list):
            for i, item in enumerate(raw_val):
                if not isinstance(item, str):
                    raise TypeError(
                        f"Value list for key '{key}' must contain only strings; "
                        f"item #{i} is {type(item).__name__}: {item!r}"
                    )
                out[key].append(item)
            continue

        raise TypeError(
            f"Value for key '{key}' must be a string or list[str], "
            f"got {type(raw_val).__name__}: {raw_val!r}"
        )

    return out


def _parse_dayname_dict(*, data: dict[str, Any]) -> dict[str, DayName]:
    """
    """
    out: dict[str, DayName] = dict()

    if not isinstance(data, dict):
        raise TypeError(f"Expected dict from YAML loader, got {type(data).__name__}")

    for raw_key, raw_val in data.items():
        key: str = str(raw_key)
        val: list[str] = list([str(x) for x in raw_val])
        out[key] = DayName(name_en=val[0], name_pt=val[1])

    return out


def _parse_bill_dict(*, data: dict[str, Any]) -> dict[str, list[Bill]]:
    """
    """
    out: dict[str, list[Bill]] = dict()

    if not isinstance(data, dict):
        raise TypeError(f"Expected dict from YAML loader, got {type(data).__name__}")

    for raw_key, raw_val in data.items():
        day: str = str(raw_key)
        day_val: list[Bill] = []
        for val in raw_val:
            day_val.append(Bill(day=day, type=val[0], subtype=val[1]))

        out[raw_key] = day_val

    return out


def _parse_birthday_dict(*, data: dict[str, Any]) -> dict[str, list[Birthday]]:
    """
    """
    out: dict[str, list[Birthday]] = dict()

    if not isinstance(data, dict):
        raise TypeError(f"Expected dict from YAML loader, got {type(data).__name__}")

    for raw_key, raw_val in data.items():
        day: str = str(raw_key)
        day_val: list[Birthday] = []
        for val in raw_val:
            day_val.append(Birthday(day=day, person=val[0], location=val[1]))

        out[raw_key] = day_val

    return out


def _parse_meeting_dict(*, data: dict[str, Any]) -> dict[str, list[Meeting]]:
    """
    """
    out: dict[str, list[Meeting]] = dict()

    if not isinstance(data, dict):
        raise TypeError(f"Expected dict from YAML loader, got {type(data).__name__}")

    for raw_key, raw_val in data.items():
        day: str = str(raw_key)
        day_val: list[Meeting] = []
        for val in raw_val:
            day_val.append(Meeting(
                day=day,
                type=val[0],
                start_time=val[1],
                end_time=val[2])
            )

        out[raw_key] = day_val
        
    return out


def _holiday_tag_for_date(d: date, rules: list[HolidayRule]) -> str:
    """All labels that apply to date d (can be multiple)."""
    value = ""
    for r in rules:
        if not r.matches(d):
            continue
        if r.type == HolidayType.PUBLIC_HOLIDAY:
            value = f"[PHoliday - {r.label}]"
            return value
        elif r.type == HolidayType.PUBLIC_OBSERVANCE:
            value = f"[Observance - {r.label}]"
            return value
        elif r.type == HolidayType.HOLIDAY:
            value = f"[Holiday - {r.label}]"
            return value
        elif r.type == HolidayType.INSTITUTE:
            value = f"[Institute - {r.label}]"
            return value
        elif r.type == HolidayType.CONFERENCE:
            value = f"[Conference - {r.label}]"
            return value
        elif r.type == HolidayType.OTHER:
            value = f"[Other - {r.label}]"
            return value
    return value


def _parse_date(s: str) -> date:
    """
    Parse a date string into a datetime.date.

    Accepted formats:
    - YYYY-MM-DD
    - DD.MM.YYYY
    - DD/MM/YYYY
    """
    formats: tuple[str, str, str] = (
        "%Y-%m-%d",
        "%d.%m.%Y",
        "%d/%m/%Y",
    )

    for fmt in formats:
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue

    raise ValueError(
        f"Unrecognized date format: {s!r}. "
        "Use YYYY-MM-DD, DD.MM.YYYY, or DD/MM/YYYY."
    )


def _get_date(cur_day: date):

    day_nb = cur_day.strftime('%d')  # Day with leading zero (01–31)
    month_nb = cur_day.strftime("%m")  # Month with leading zero (01–12)
    month_name = cur_day.strftime("%B") # Month name
    year_nb = cur_day.strftime("%Y") # Year with leading zero (0001–9999)
    cur_day_week = cur_day.strftime("%A") # Day of the week (str)

    return day_nb, month_nb, month_name, year_nb, cur_day_week


def _calculate_separation(
    total_length: int,
    left_length: int,
    right_length: int,
) -> tuple[int, int]:

    splen = total_length - (left_length + right_length)
    if splen % 2 == 0:
        half_splen = int(splen/2)
        return half_splen-1, half_splen
    half_splen = int(floor(float(splen/2)))
    return half_splen, half_splen


# --------------------------------------------------------------------------------------
# Functions
# --------------------------------------------------------------------------------------
def todo_generator(
    start_date_str: str,
    end_date_str: str,
    output_path: Path,
    *,
    holiday_yaml_path: Path = HOLIDAY_YAML_PATH,
    daymap_yaml_path: Path = DAYMAP_YAML_PATH,
    meetings_yaml_path: Path = MEETINGS_YAML_PATH,
    bills_yaml_path: Path = BILLS_YAML_PATH,
    bdays_yaml_path: Path = BDAYS_YAML_PATH,
) -> None:
    """
    Generates the to-do list, given the auxiliary files, as:

    ==========================================================================  # 1
    2026-01-11 | Sunday | Domingo       •        Corpus Christi | January | 01  # 2
    --------------------------------------------------------------------------  # 3
    > [ ] Appointment | Therapy | 18:30 - 19:30                                 # 4
    ---                                                                         # 5
    > [ ] Birthday | Rusti | Love                                               # 6
    > [ ] Bill | Internet Services | OpenAI
    --------------------------------------------------------------------------
    [ ] <Main : Topic> Do this and that {01:30}.                                # 7
    [ ] <Organization : Email> Clean Spam {00:30}.
    --------------------------------------------------------------------------  # 8

    1 <--- Topmost ruler made by "="
    2 <--- Date in this format followed by English and pt version of day-of-the-week
    3 <--- All other separators made by "-"
    4 <--- Section 1 = Weekly appointments with fixed time (therapy, meetings, etc.)
    5 <--- Mini-ruler because we will stay on the "tasks on loop - based"
    6 <--- Section 2 = Weekly/Monthly/Anual tasks without a necessary time to be done
                       like bills, birthdays, holidays, etc.
    7 <--- Section 3 = Daily to-do topics (mostly empty; I populate weekly given the
                       "master" list of items to-do.
    8 <--- We'll finish a card with the "-" ruler since the next one starts with a "="
           ruler (not heavy viz).

    """

    # RULES
    holiday_yaml_dict: dict[str, Any] = _load_yaml_dict(yaml_path=holiday_yaml_path)
    holiday_rule_list: list[HolidayRule] = _parse_holiday_rules(data=holiday_yaml_dict)
    
    # day_map_dict
    daymap_yaml_dict: dict[str, Any] = _load_yaml_dict(yaml_path=daymap_yaml_path)
    daymap_dict: dict[str, DayName] = _parse_dayname_dict(
        data=daymap_yaml_dict
    )

    # meeting_dict, appointment_dict
    meetings_yaml_dict: dict[str, Any] = _load_yaml_dict(yaml_path=meetings_yaml_path)
    meetings_dict: dict[str, list[Meeting]] = _parse_meeting_dict(
        data=meetings_yaml_dict
    )

    # bills_dict
    bills_yaml_dict: dict[str, Any] = _load_yaml_dict(yaml_path=bills_yaml_path)
    bills_dict: dict[str, list[Bill]] = _parse_bill_dict(
        data=bills_yaml_dict
    )

    # birthdate_dict
    bdays_yaml_dict: dict[str, Any] = _load_yaml_dict(yaml_path=bdays_yaml_path)
    bdays_dict: dict[str, list[Birthday]] = _parse_birthday_dict(
        data=bdays_yaml_dict
    )

    todo_placeholder: str = "\n".join(
        ["[ ] <Main : Topic> Placeholder {03:00}"] * 4
    )

    header_line: str = "=" * BIG_RULER_LENGTH
    big_ruler_line: str = "-" * BIG_RULER_LENGTH
    small_ruler_line: str = "-" * SMALL_RULER_LENGTH

    with open(output_path, "w") as f:

        start_date: date = _parse_date(start_date_str)
        end_date: date = _parse_date(end_date_str)
        if end_date < start_date:
            raise ValueError("End week must be the same as or after start week.")

        current_day: date = start_date
        while current_day <= end_date:

            # Get all day attributes
            (
                current_day_number,
                current_month_number,
                current_month_name,
                current_year_number,
                current_day_week,
             ) = _get_date(current_day)

            # Map name of Week Day
            current_day_week_name: DayName = daymap_dict.get(
                current_day_week,
                DayName(),
            )

            # Check Sunday Status
            is_sunday: bool = current_day_week_name.name_en == "Sunday"

            # Get meetings
            meetings_list: list[Meeting] = meetings_dict.get(
                f"{current_day_week_name.name_en}",
                [],
            )

            # Get birthdays
            bdays_list: list[Birthday] = bdays_dict.get(
                f"{current_day_number}.{current_month_number}",
                [],
            )

            # Get bills
            bills_list: list[Bill] = bills_dict.get(f"{current_day_number}", [])

            # Get Holiday Tag
            holiday_tag: str = _holiday_tag_for_date(
                current_day,
                holiday_rule_list
            )

            date_line_start: str = (
                f"{"-".join([
                    current_year_number,
                    current_month_number,
                    current_day_number
                ])} | "
                f"{" | ".join(list(astuple(current_day_week_name)))}"
            )

            date_line_end: str = (
                f"{" | ".join(
                    [holiday_tag, current_month_name, current_day_number]
                )}"
            )

            splen: tuple[int, int] = _calculate_separation(
                    BIG_RULER_LENGTH,
                    len(date_line_start),
                    len(date_line_end),
            )

            date_line_sp: str = f"{" " * splen[0]}•{" " * splen[1]}"

            week_sep_line: str = ""
            if is_sunday:
                week_sep_line: str = f"\n\n{"#" * WEEK_RULER_LENGTH}\n"

            format_meeting_list: list[str] = []
            format_bills_list: list[str] = []
            format_bdays_list: list[str] = []
            if meetings_list:
                for meet in meetings_list:
                    mstr = (
                        f"> [ ] Meeting | {meet.type} | "
                        f"{meet.start_time} - {meet.end_time}"
                    )
                    format_meeting_list.append(mstr)
            if bills_list:
                for bill in bills_list:
                    mstr = f"> [ ] Bill | {bill.type} | {bill.subtype}"
                    format_bills_list.append(mstr)
            if bdays_list:
                for bday in bdays_list:
                    mstr = f"> [ ] Birthday | {bday.person} | {bday.location}"
                    format_bdays_list.append(mstr)

            # Putting a newline symbol at the end of each major format list
            for flist in [format_meeting_list, format_bills_list, format_bdays_list]:
                if flist:
                    flist[-1] += "\n"

            big_str = f"""
{header_line}
{date_line_start}{date_line_sp}{date_line_end}
{big_ruler_line}
{"\n".join(format_meeting_list)}{small_ruler_line}
{"\n".join(format_bills_list)}{"\n".join(format_bdays_list)}{big_ruler_line}
{todo_placeholder}
{big_ruler_line}{week_sep_line}
"""
            f.write(big_str)
            current_day += timedelta(days=1)


# --------------------------------------------------------------------------------------
# Exports
# --------------------------------------------------------------------------------------
__all__: list[str] = [
    "todo_generator",
]
