# SPDX-License-Identifier: MIT
# uqbar/lola/todo_maker.py
"""
Lola | TO-DO Maker
==================

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

from pathlib import Path
from enum import Enum, auto
from dataclasses import dataclass
from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import Iterable, List, Optional, Tuple, Dict


# -------------------------------------------------------------------------------------
# Constants
# -------------------------------------------------------------------------------------


# --------------------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------------------



# --------------------------------------------------------------------------------------
# Functions
# --------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------------
# Classes
# --------------------------------------------------------------------------------------


# --------------------------------------------------------------------------------------
# Exports
# --------------------------------------------------------------------------------------


class KeyAwareDict(dict[str, List[str]]):
    def finalize(self) -> Dict[str, List[str]]:
        return {
            key: [item.format(key=key) if isinstance(item, str) else item for item in vlist]
            for key, vlist in self.items()
        }


class HolidayType(Enum):
    PUBLIC_HOLIDAY = auto()      # National / State / City Official Holiday
    PUBLIC_OBSERVANCE = auto()   # National / State / City Observances
    HOLIDAY = auto()             # Personal vacation
    INSTITUTE = auto()           # Institutional Recess
    CONFERENCE = auto()          # Conference time block
    OTHER = auto()               # Catch-all


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
    md: Optional[Tuple[int, int]] = None

    # For single_absolute: dt
    dt: Optional[date] = None

    # For range_annual: (m1, d1) -> (m2, d2) (can cross year)
    md_start: Optional[Tuple[int, int]] = None
    md_end: Optional[Tuple[int, int]] = None

    # For range_absolute: start_dt -> end_dt (inclusive)
    start_dt: Optional[date] = None
    end_dt: Optional[date] = None

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


# -------------------------------
# Example rules (Brazil-flavored)
# -------------------------------
RULES: List[HolidayRule] = [

    # --- Global / Collapsed Holidays ---
    HolidayRule(
        "single_annual",
        "[BRA, USA, GBR, DEU, CHN] New Year's Day",
        HolidayType.PUBLIC_HOLIDAY,
        md=(1, 1),
    ),

    HolidayRule(
        "single_annual",
        "[BRA, DEU, GBR] Labor Day",
        HolidayType.PUBLIC_HOLIDAY,
        md=(5, 1),
    ),

    HolidayRule(
        "single_annual",
        "[BRA, USA, GBR, DEU] Christmas Day",
        HolidayType.PUBLIC_HOLIDAY,
        md=(12, 25),
    ),

    # --- Brazil / Pernambuco / Recife (2026) ---
    HolidayRule(
        "single_annual",
        "[BRA] Pernambuco State Magna Date",
        HolidayType.PUBLIC_HOLIDAY,
        md=(3, 6),
    ),

    HolidayRule(
        "single_absolute",
        "[BRA] Good Friday",
        HolidayType.PUBLIC_HOLIDAY,
        dt=date(2026, 4, 3),
    ),

    HolidayRule(
        "single_absolute",
        "[BRA] Easter Sunday",
        HolidayType.PUBLIC_HOLIDAY,
        dt=date(2026, 4, 5),
    ),

    HolidayRule(
        "single_annual",
        "[BRA] Tiradentes",
        HolidayType.PUBLIC_HOLIDAY,
        md=(4, 21),
    ),

    HolidayRule(
        "single_absolute",
        "[BRA] Corpus Christi",
        HolidayType.PUBLIC_HOLIDAY,
        dt=date(2026, 6, 4),
    ),

    HolidayRule(
        "single_annual",
        "[BRA] Saint John (Northeast tradition)",
        HolidayType.PUBLIC_HOLIDAY,
        md=(6, 24),
    ),

    HolidayRule(
        "single_annual",
        "[BRA] Our Lady of Mount Carmel (Recife Patroness)",
        HolidayType.PUBLIC_HOLIDAY,
        md=(7, 16),
    ),

    HolidayRule(
        "single_annual",
        "[BRA] Brazilian Independence Day",
        HolidayType.PUBLIC_HOLIDAY,
        md=(9, 7),
    ),

    HolidayRule(
        "single_annual",
        "[BRA] Our Lady Aparecida",
        HolidayType.PUBLIC_HOLIDAY,
        md=(10, 12),
    ),

    HolidayRule(
        "single_annual",
        "[BRA] All Souls' Day",
        HolidayType.PUBLIC_HOLIDAY,
        md=(11, 2),
    ),

    HolidayRule(
        "single_annual",
        "[BRA] Proclamation of the Republic",
        HolidayType.PUBLIC_HOLIDAY,
        md=(11, 15),
    ),

    HolidayRule(
        "single_annual",
        "[BRA] Black Awareness Day",
        HolidayType.PUBLIC_HOLIDAY,
        md=(11, 20),
    ),

    HolidayRule(
        "single_annual",
        "[BRA] Our Lady of the Conception (Recife)",
        HolidayType.PUBLIC_HOLIDAY,
        md=(12, 8),
    ),

    # --- Brazil: Optional / Facultative Points (2026) ---
    HolidayRule(
        "single_absolute",
        "[BRA] Carnival Monday",
        HolidayType.PUBLIC_OBSERVANCE,
        dt=date(2026, 2, 16),
    ),

    HolidayRule(
        "single_absolute",
        "[BRA] Carnival Tuesday",
        HolidayType.PUBLIC_OBSERVANCE,
        dt=date(2026, 2, 17),
    ),

    HolidayRule(
        "single_absolute",
        "[BRA] Ash Wednesday (morning only)",
        HolidayType.PUBLIC_OBSERVANCE,
        dt=date(2026, 2, 18),
    ),

    HolidayRule(
        "single_annual",
        "[BRA] Public Servant's Day",
        HolidayType.PUBLIC_OBSERVANCE,
        md=(10, 28),
    ),

    HolidayRule(
        "single_annual",
        "[BRA] Christmas Eve (after 2pm)",
        HolidayType.PUBLIC_OBSERVANCE,
        md=(12, 24),
    ),

    HolidayRule(
        "single_annual",
        "[BRA] New Year's Eve (after 2pm)",
        HolidayType.PUBLIC_OBSERVANCE,
        md=(12, 31),
    ),

    # --- Personal: Important Events ---

    # Institutional annual recess (15-day window crossing year)
    HolidayRule(
        "range_absolute",
        "[BRA] PersonalHoliday",
        HolidayType.HOLIDAY,
        start_dt=date(2026, 1, 1),
        end_dt=date(2026, 1, 11)
    ),
    HolidayRule(
        "range_absolute",
        "[BRA] PersonalHoliday",
        HolidayType.HOLIDAY,
        start_dt=date(2026, 12, 21),
        end_dt=date(2027, 1, 1)
    ),

    # Conference (absolute range, one-off)
    HolidayRule(
        "single_absolute",
        "[BRA] AWS Certification Exam",
        HolidayType.OTHER,
        dt=date(2026, 3, 1),
    ),
]


# ---------------------------
# Query helpers
# ---------------------------
def holiday_tag_for_date(d: date, rules: Iterable[HolidayRule] = RULES) -> List[str]:
    """All labels that apply to date d (can be multiple)."""
    value = []
    for r in rules:
        if not r.matches(d):
            continue
        if r.type == HolidayType.PUBLIC_HOLIDAY:
            value.append("[PublicHoliday()]")
        elif r.type == HolidayType.PUBLIC_OBSERVANCE:
            value.append("[Observance()]")
        elif r.type == HolidayType.HOLIDAY:
            value.append("[Holiday()]")
        elif r.type == HolidayType.INSTITUTE:
            value.append("[Institute()]")
        elif r.type == HolidayType.CONFERENCE:
            value.append("[Conference()]")
        elif r.type == HolidayType.OTHER:
            value.append("[Other()]")
    return value

def labels_for_date(d: date, rules: Iterable[HolidayRule] = RULES) -> List[str]:
    """All labels that apply to date d (can be multiple)."""
    return [r.label for r in rules if r.matches(d)]

def types_for_date(d: date, rules: Iterable[HolidayRule] = RULES) -> List[HolidayType]:
    """All holiday types that apply to date d."""
    return [r.type for r in rules if r.matches(d)]

def is_holiday(d: date, rules: Iterable[HolidayRule] = RULES) -> bool:
    """Whether any rule matches date d."""
    return any(r.matches(d) for r in rules)

###

def parse_date(s: str) -> date:
    """
    Parse 'DD.MM.YYYY' or 'YYYY-MM-DD' into a date (no time).
    """
    for fmt in ("%d.%m.%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    raise ValueError(f"Unrecognized date format: {s!r}. Use 'DD.MM.YYYY' or 'YYYY-MM-DD'.")

def get_date(cur_day: str):

    day_nb = cur_day.strftime('%d')  # Day with leading zero (01–31)
    month_nb = cur_day.strftime("%m")  # Month with leading zero (01–12)
    month_name = cur_day.strftime("%B")
    year_nb = cur_day.strftime("%Y") # Year with leading zero (0001–9999)
    cur_day_week = cur_day.strftime("%A") # Day of the week (str)

    return day_nb, month_nb, month_name, year_nb, cur_day_week

def todo_generator(
    start_date_str: str,
    end_date_str: str,
    meeting_dict: Dict[str, List[str]],
    appointment_dict: Dict[str, List[str]],
    birthdate_dict: Dict[str, str],
    bills_dict: Dict[str, str],
    out_path: Path,
) -> None:
    """
    Generates the to-do list, given the auxiliary files, as:

    Header
    ------

    Meetings Work
    ---
    Appointments
    ---
    Birthdays
    ---
    Bills

    -----------------------------------------------------------------------------------
    ```C
    31.12.2025 - 31/December/2025 (Wednesday; Quarta)
    =================================================
    > [ ] "Meeting GSUS5: <in locus>" (13:30 - 15:00) - Wednesday; Quarta
    ---
    > [ ] "Terapia - Letícia: <Different Link>" (18:00 - 18:40) - Wednesday; Quarta
    ---
    ---
    ```
    > [ ] <Project : Task> Placeholder.
    > [ ] <Project : Task> Placeholder.
    > [ ] <Project : Task> Placeholder.
    > [ ] <Project : Task> Placeholder.
    > [ ] <Project : Task> Placeholder.
    > [ ] <Project : Task> Placeholder.
    > [ ] <Project : Task> Placeholder.
    > [ ] <Project : Task> Placeholder.
    > [ ] <Organization : Email> Delete & Archive at least 100 emails.
    -----------------------------------------------------------------------------------

    """

    with open(out_path, "w") as f:

        start_date = parse_date(start_date_str)
        end_date = parse_date(end_date_str)
        if end_date < start_date:
            raise ValueError("End week must be the same as or after start week.")

        current_day = start_date
        while current_day <= end_date:

            # Get all day attributes
            (current_day_number,
             current_month_number,
             current_month_name,
             current_year_number,
             current_day_week) = get_date(current_day)
            current_day_week_mapped = day_map_dict[current_day_week]

            # Check Sunday Status
            is_sunday = current_day_week == "Sunday"

            # Check meeting_dict
            current_meeting_vec = meeting_dict.get(current_day_week, [])

            # Check current_appointment_vec
            current_appointment_vec = appointment_dict.get(current_day_week, [])

            # Check birthdate_dict
            birthdate_dict_vec = birthdate_dict.get(f"{current_day_number}.{current_month_number}", [])

            # Check bills_dict
            bills_dict_vec = bills_dict.get(f"{current_day_number}", [])

            # Check Holiday Tag
            holiday_tag_list = holiday_tag_for_date(current_day)

            date_line = (
                f"{".".join([current_day_number, current_month_number, current_year_number])} - "
                f"{"/".join([current_day_number, current_month_number, current_year_number])} ({current_day_week_mapped})"
            )
            if holiday_tag_list:
                date_line += " "+" ".join(holiday_tag_list)
            header_line = "="*(len(date_line))
            header_todo_line = []
            if current_meeting_vec:
                for e in current_meeting_vec:
                    header_todo_line.append(e+"\n")
            header_todo_line.append("---\n")
            if current_appointment_vec:
                for e in current_appointment_vec:
                    header_todo_line.append(e+"\n")
            header_todo_line.append("---\n")
            if birthdate_dict_vec:
                for e in birthdate_dict_vec:
                    header_todo_line.append(e+"\n")
            header_todo_line.append("---\n")
            if bills_dict_vec:
                for e in bills_dict_vec:
                    header_todo_line.append(e+"\n")
            ending_line = "\n"
            header_todo_line[-1] = header_todo_line[-1][:-1]
            if is_sunday:
                ending_line += "-"*147 + "\n"
            big_str = f"""```C
{date_line}
{header_line}
{"".join(header_todo_line)}
```
> [ ] <Project : Task> Placeholder.
> [ ] <Project : Task> Placeholder.
> [ ] <Project : Task> Placeholder.
> [ ] <Project : Task> Placeholder.
> [ ] <Project : Task> Placeholder.
> [ ] <Project : Task> Placeholder.
> [ ] <Project : Task> Placeholder.
> [ ] <Project : Task> Placeholder.
> [ ] <Organization : Email> Delete & Archive at least 100 emails.
{ending_line}
"""
            f.write(big_str)
            current_day += timedelta(days=1)

# -----------------------------
# Example usage:
# todo_generator("18.08.2025", "15.09.2025")
# todo_generator("2025-08-18", "2025-09-15")
if __name__ == "__main__":

    # Start and End Dates
    start_date_str = "25.08.2025"
    end_date_str = "31.01.2026"

    # Day-names list
    day_name_list = [
        "Monday; Segunda",
        "Tuesday; Terça",
        "Wednesday; Quarta",
        "Thursday; Quinta",
        "Friday; Sexta",
        "Saturday; Sábado",
        "Sunday; Domingo",
    ]

    # Day-names mappings
    day_map_dict = {
        "Monday": "Monday; Segunda",
        "Tuesday": "Tuesday; Terça",
        "Wednesday": "Wednesday; Quarta",
        "Thursday": "Thursday; Quinta",
        "Friday": "Friday; Sexta",
        "Saturday": "Saturday; Sábado",
        "Sunday": "Sunday; Domingo",
    }

    # Meetings Dictionary per week
    meeting_dict = KeyAwareDict(
        Monday=[
            f"> [ ] \"Meeting GSUS1: meet.google.com/pgp-cmzc-htw\" (11:00 - 12:00) - {day_map_dict["Monday"]}",
            f"> [ ] \"Meeting GSUS4: <in locus>\" (13:30 - 15:00) - {day_map_dict["Monday"]}",
        ],
        Tuesday=[
            f"> [ ] \"Meeting GSUS2: meet.google.com/qde-wdps-iiq\" (09:00 - 10:00) - {day_map_dict["Tuesday"]}",
        ],
        Wednesday=[
            f"> [ ] \"Meeting GSUS5: <in locus>\" (13:30 - 15:00) - {day_map_dict["Wednesday"]}",
        ],
        Thursday=[
            f"> [ ] \"Meeting GSUS3: meet.google.com/odu-vyyt-ice\" (10:30 - 11:30) - {day_map_dict["Thursday"]}",
            f"> [ ] \"Meeting GSUS6: bit.ly/3Hp8EqM / ID da Reunião: 256 758 374 412 / Senha: NX3pF6tp\" (16:00 - 17:30) - {day_map_dict["Thursday"]}",
        ],
        Friday=[
        ],
    ).finalize()

    # Appointments Dictionary per week
    appointment_dict = KeyAwareDict(
        Monday=[
        ],
        Tuesday=[
        ],
        Wednesday=[
            f"> [ ] \"Terapia - Letícia: <Different Link>\" (18:00 - 18:40) - {day_map_dict["Wednesday"]}",
        ],
        Thursday=[
        ],
        Friday=[
            f"> [ ] \"Terapia - Letícia: <Different Link>\" (09:00 - 09:40) - {day_map_dict["Friday"]}",
        ],
    ).finalize()


    # Birthday Dictionary
    birthdate_dict = defaultdict(list)
    birthdate_dict["01.01"].append("> [ ] Birthday(\"Murilo Brasil\") - Send happy birthday! # Dourado")
    birthdate_dict["03.01"].append("> [ ] Birthday(\"Rayssa Medeiros\") - Send happy birthday! # Work")
    birthdate_dict["07.01"].append("> [ ] Birthday(\"Ed Carrazzon\") - Send happy birthday! # Mae")
    birthdate_dict["12.01"].append("> [ ] Birthday(\"Iago Gade\") - Send happy birthday! # Mae")
    birthdate_dict["11.02"].append("> [ ] Birthday(\"Bosco Miranda\") - Send happy birthday! # Pai")
    birthdate_dict["16.02"].append("> [ ] Birthday(\"Mario Oliveira\") - Send happy birthday! # JO")
    birthdate_dict["09.05"].append("> [ ] Birthday(\"Renata Almeida\") - Send happy birthday! # Work")
    birthdate_dict["03.06"].append("> [ ] Birthday(\"Vanessa Vianna\") - Send happy birthday! # Love")
    birthdate_dict["05.06"].append("> [ ] Birthday(\"Cauê Martins\") - Send happy birthday! # Pai")
    birthdate_dict["05.06"].append("> [ ] Birthday(\"Lucas Martins\") - Send happy birthday! # Pai")
    birthdate_dict["07.06"].append("> [ ] Birthday(\"Ricardo XXXXX\") - Send happy birthday! # Mae")
    birthdate_dict["13.06"].append("> [ ] Birthday(\"Sayonara Gonçalves\") - Send happy birthday! # Work")
    birthdate_dict["19.06"].append("> [ ] Birthday(\"Halisson Alberdan\") - Send happy birthday! # Work")
    birthdate_dict["21.06"].append("> [ ] Birthday(\"João Miranda\") - Send happy birthday! # Pai")
    birthdate_dict["09.07"].append("> [ ] Birthday(\"Opa Gade\") - Send happy birthday! # Mae")
    birthdate_dict["15.07"].append("> [ ] Birthday(\"Norma Lucena\") - Send happy birthday! # Work")
    birthdate_dict["13.08"].append("> [ ] Birthday(\"André Miranda\") - Send happy birthday! # Pai")
    birthdate_dict["16.08"].append("> [ ] Birthday(\"Vanessa Teixeira\") - Send happy birthday! # Work")
    birthdate_dict["21.10"].append("> [ ] Birthday(\"Floarian Krawitz\") - Send happy birthday! # Love")
    birthdate_dict["22.08"].append("> [ ] Birthday(\"Matheus Carvalho\") - Send happy birthday! # Work")
    birthdate_dict["31.08"].append("> [ ] Birthday(\"Ravi Miranda\") - Send happy birthday! # Pai")
    birthdate_dict["03.09"].append("> [ ] Birthday(\"Christiani Gade\") - Send happy birthday! # Mae")
    birthdate_dict["07.09"].append("> [ ] Birthday(\"Guiga Gade\") - Send happy birthday! # Mae")
    birthdate_dict["11.09"].append("> [ ] Birthday(\"Thales Martins\") - Send happy birthday! # Pai")
    birthdate_dict["04.10"].append("> [ ] Birthday(\"Rusti Ponte de Sousa\") - Send happy birthday! # Love")
    birthdate_dict["15.10"].append("> [ ] Birthday(\"Hudson Medeiros\") - Send happy birthday! # Love")
    birthdate_dict["20.10"].append("> [ ] Birthday(\"Paula Farias\") - Send happy birthday! # Work")
    birthdate_dict["30.10"].append("> [ ] Birthday(\"Thiago Martins\") - Send happy birthday! # Pai")
    birthdate_dict["04.11"].append("> [ ] Birthday(\"Dani Oliveira\") - Send happy birthday! # JO")
    birthdate_dict["18.11"].append("> [ ] Birthday(\"Oma Gade\") - Send happy birthday! # Mae")
    birthdate_dict["28.11"].append("> [ ] Birthday(\"Joselita Oliveira\") - Send happy birthday! # JO")
    birthdate_dict["02.12"].append("> [ ] Birthday(\"Eduardo Gade\") - Send happy birthday! # Mae")
    birthdate_dict["02.12"].append("> [ ] Birthday(\"Neila Caroline\") - Send happy birthday! # Work")
    birthdate_dict["06.12"].append("> [ ] Birthday(\"Piera Gade\") - Send happy birthday! # Mae")
    birthdate_dict["08.12"].append("> [ ] Birthday(\"Carmem Miranda\") - Send happy birthday! # Pai")
    birthdate_dict["08.12"].append("> [ ] Birthday(\"Danilo Japiassu\") - Send happy birthday! # Dourado")
    birthdate_dict["13.12"].append("> [ ] Birthday(\"Hiolanda Nayara\") - Send happy birthday! # Work")
    birthdate_dict["24.12"].append("> [ ] Birthday(\"Cybelle Oliveira\") - Send happy birthday! # JO")
    birthdate_dict["24.12"].append("> [ ] Birthday(\"Teca Gade\") - Send happy birthday! # Mae")
    birthdate_dict["30.12"].append("> [ ] Birthday(\"Andre Oliveira\") - Send happy birthday! # JO")

    # Birthday Dictionary
    bills_dict = defaultdict(list)
    bills_dict["01"].append("> [ ] Payment(\"Credit Card\") - Due Bill!")
    bills_dict["02"].append("> [ ] Payment(\"Therapy - Leticia\") - Due Bill!")
    bills_dict["03"].append("> [ ] Payment(\"Therapy - Leticia\") - Due Bill!")
    bills_dict["04"].append("> [ ] Payment(\"Therapy - Leticia\") - Due Bill!")
    bills_dict["05"].append("> [ ] Payment(\"Bill - Energy\") - Due Bill!")
    bills_dict["05"].append("> [ ] Payment(\"Bill - Water\") - Due Bill!")
    bills_dict["05"].append("> [ ] Payment(\"Bill - IPTU\") - Due Bill!")
    bills_dict["05"].append("> [ ] Payment(\"Bill - Condominium\") - Due Bill!")
    bills_dict["05"].append("> [ ] Payment(\"Bill - Rent\") - Due Bill!")
    bills_dict["05"].append("> [ ] Payment(\"Bill - Mortgage\") - Due Bill!")
    bills_dict["06"].append("> [ ] Payment(\"Mobile - Vivo\") - Due Bill!")
    bills_dict["07"].append("> [ ] Payment(\"Health Insurance - Christiani\") - Due Bill!")
    bills_dict["08"].append("> [ ] Payment(\"Health Insurance - Rusti\") - Due Bill!")
    bills_dict["09"].append("> [ ] Payment(\"Health Insurance - Eduardo\") - Due Bill!")
    bills_dict["10"].append("> [ ] Payment(\"Therapy - Hudson\") - Due Bill!")
    bills_dict["11"].append("> [ ] Payment(\"Medicine Stack\") - Due Bill!")
    bills_dict["12"].append("> [x] Payment(\"Internet Services - OpenAI, Amazon, GoDaddy\") - Due Bill!")

    root = Path("/Users/egg/Projects/organization/_code/")
    out_path = root / "all_todo.md"

    todo_generator(
        start_date_str,
        end_date_str,
        meeting_dict,
        appointment_dict,
        birthdate_dict,
        bills_dict,
        out_path,
    )

