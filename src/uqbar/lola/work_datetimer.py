# SPDX-License-Identifier: MIT
# uqbar/lola/work_datetimer.py
"""
Lola | Work DateTime Functions
==============================

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
import locale
import random
from pathlib import Path
from datetime import datetime, timedelta

random.seed(1987)

def generate_weekdays(start_date: str, end_date: str):
    # Set locale to Portuguese
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
    
    # Convert string dates to datetime objects
    start = datetime.strptime(start_date, "%d.%m.%Y")
    end = datetime.strptime(end_date, "%d.%m.%Y")
    space_dict ={x:y for x,y in enumerate([3, 5, 4, 4, 5])}

    # Iterate over days and print only weekdays (Monday to Friday)
    current = start
    previous_week = None
    while current <= end:
        if current.weekday() < 5:  # Monday to Friday
            week_number = current.strftime("%U")  # Get the week number
            if previous_week and week_number != previous_week:
                print("")  # Separate different weeks
            spaces = " " * space_dict[current.weekday()]
            unique_time_1 = ":".join([f"{random.randint(9, 11):02}", f"{random.randint(0, 59):02}"])
            unique_time_2 = ":".join([f"{random.randint(19, 21):02}", f"{random.randint(0, 59):02}"])
            unique_time = "-".join([unique_time_1, unique_time_2])
            print(f"{current.strftime('%A').split(" ")[0]} ({current.strftime('%d.%m.%Y')}):" + spaces + unique_time)
            previous_week = week_number
        current += timedelta(days=1)

def generate_monday_day(start_date: str, end_date: str, output_path: Path):
    """
    Write all Mondays between start_date and end_date to output_path.
    Format:
        MM/YYYY: DD
    Blank line between months, and '---' between years.
    """

    # Set locale to Portuguese (Brazil)
    try:
        locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
    except locale.Error:
        print("Aviso: locale pt_BR.UTF-8 não disponível; usando padrão do sistema.")

    # Convert strings to datetime
    start = datetime.strptime(start_date, "%d.%m.%Y")
    end = datetime.strptime(end_date, "%d.%m.%Y")

    # Move to the first Monday on or after start_date
    while start.weekday() != 0:
        start += timedelta(days=1)

    current_year = start.year
    current_month = start.month

    with open(output_path, "w", encoding="utf-8") as f:
        date = start
        while date <= end:
            year, month, day = date.year, date.month, date.day

            # Write header for month/year if starting or new month
            if year != current_year:
                f.write("\n---\n\n")
                current_year = year
            if month != current_month:
                f.write("\n")
                current_month = month

            # Write formatted line
            f.write(f"{month:02d}/{year}: {day:02d}\n")

            # Next Monday
            date += timedelta(days=7)

if __name__ == "__main__":

	# start_date = "01.06.2025"
	# end_date = "31.12.2025"
	# generate_weekdays(start_date, end_date)

    start_date = "01.09.2023"
    end_date = "08.11.2025"
    output_path = Path("/Users/egg/Projects/organization/_code/mondays.txt")
    generate_monday_day(start_date, end_date, output_path)
