# SPDX-License-Identifier: MIT
# uqbar/lola/xxxxxx.py
"""
Lola | xxxx
===========

Honeybun,

1. Now I would like a script to play the Marseille tarot.

2. Inputs:
    - Directory location with the cards named "0.jpg" ... "77.jpg" (i.e. each draw can select a number between 0 and 77).
    - To emulate the user's energy, I would like you to create a modulus function that receives up to 10 integers. This function will be used throughout as the function to draw random cards (if you can do that) or to serve as "function to get a random seed" that will be used in couple with any random generator.
    - The program will, at each turn ask the user for ANY number (integer, within bounds of reality)
    - The program will use this number in conjunction with the pre-existing 10-number random generator to create a number between 0 and 77.
    - The program shall wait X seconds (before random number is calculated) to calculate and draw a number from 0 to 77.
    - The program will print "Your card for Y (later I will say the order) is:" - and then open the card in whichever way it is better.
    - The "box with the image of the card" must stay open for as long as the user desires.
    - As soon as the box closes, the program asks: "Are you ready for the next card W (I will tell the order)" and the user must press enter and then select another number and everything is repeated until the closure card.
    - It is important that before asking for a number you say "Are you ready for the next card W (I will tell the order)" - even the first one.

3. Messages that describe the card order:

    3.1. "Are you ready to draw the SELF?"
         "Please, pick a number for the SELF: "
         "Your SELF is: "

    3.2. "Are you ready to draw the OBSTACLE?"
         "Please, pick a number for the OBSTACLE: "
         "Your OBSTACLE is: "

    3.3. "Are you ready to draw the COUNSEL?"
         "Please, pick a number for the COUNSEL: "
         "Your COUNSEL is: "

    3.4. "Are you ready to draw the POSITIVE?"
         "Please, pick a number for the POSITIVE: "
         "Your POSITIVE is: "

    3.5. "Are you ready to draw the NEGATIVE?"
         "Please, pick a number for the NEGATIVE: "
         "Your NEGATIVE is: "

    3.6. "Are you ready to draw the HIDDEN?"
         "Please, pick a number for the HIDDEN: "
         "Your HIDDEN is: "

    3.7. "Are you ready to draw the CLOSURE?"
         "Please, pick a number for the CLOSURE: "
         "Your CLOSURE is: "

4. Program ends after user closes the last card (CLOSURE).

5. Please, when in possession of the final number, if even, show the card as it is on the image. If odd, invert the card (rotate by 90-degrees-only clockwise [it's easier to see])

GO!

21
33
34
40
55
60
03

Overview
--------
Placeholder.

Usage
-----
Placeholder.

Usage Details
-------------
Placeholder.

Metadata
--------
- Project: xxxx
- License: MIT
"""

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import random
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path


# ----------------------------
# Tarot Marseille CLI Drawer
# ----------------------------
# Cards must be named: 0.jpg ... 77.jpg (78 cards total)
#
# Orientation rule (per your spec):
# - final_number even -> show as-is
# - final_number odd  -> rotate 90° clockwise
#
# Note: Rotating by 90° is not the traditional “reversed” tarot, but I’m implementing
# exactly what you requested.


def rename_jpgs_sequential(folder: str | Path) -> None:
    folder = Path(folder)

    if not folder.is_dir():
        raise ValueError(f"{folder} is not a valid directory")

    files = sorted(folder.glob("*.jpg"))

    for i, file in enumerate(files):
        new_name = folder / f"{i}.jpg"
        file.rename(new_name)



@dataclass(frozen=True, slots=True)
class PromptSpec:
    key: str
    ready_msg: str
    pick_msg: str
    result_msg: str


ORDER: list[PromptSpec] = [
    PromptSpec("SELF",
               "Are you ready to draw the SELF?",
               "Please, pick a number for the SELF: ",
               "Your SELF is: "),
    PromptSpec("OBSTACLE",
               "Are you ready to draw the OBSTACLE?",
               "Please, pick a number for the OBSTACLE: ",
               "Your OBSTACLE is: "),
    PromptSpec("COUNSEL",
               "Are you ready to draw the COUNSEL?",
               "Please, pick a number for the COUNSEL: ",
               "Your COUNSEL is: "),
    PromptSpec("POSITIVE",
               "Are you ready to draw the POSITIVE?",
               "Please, pick a number for the POSITIVE: ",
               "Your POSITIVE is: "),
    PromptSpec("NEGATIVE",
               "Are you ready to draw the NEGATIVE?",
               "Please, pick a number for the NEGATIVE: ",
               "Your NEGATIVE is: "),
    PromptSpec("HIDDEN",
               "Are you ready to draw the HIDDEN?",
               "Please, pick a number for the HIDDEN: ",
               "Your HIDDEN is: "),
    PromptSpec("CLOSURE",
               "Are you ready to draw the CLOSURE?",
               "Please, pick a number for the CLOSURE: ",
               "Your CLOSURE is: "),
]


def _modulus_mix(*nums: int) -> int:
    """
    "Energy mixer" modulus function.
    Accepts up to 10 integers and returns a deterministic mixed integer.

    This is NOT cryptographic. It's just a stable mixer to create a seed-like value.
    """
    if len(nums) == 0:
        raise ValueError("Provide at least 1 integer to _modulus_mix().")
    if len(nums) > 10:
        raise ValueError("Provide at most 10 integers to _modulus_mix().")

    # Force integers and keep them bounded to avoid huge intermediate growth.
    xs = [int(n) for n in nums]

    # A simple avalanche-ish mix: xor/rotate/multiply style (32-bit-ish).
    # This is deterministic across runs and platforms.
    h = 0x9E3779B9  # golden ratio constant
    for i, x in enumerate(xs, start=1):
        x &= 0xFFFFFFFFFFFFFFFF  # bound to 64-bit
        h ^= (x + 0x9E3779B97F4A7C15 + (h << 6) + (h >> 2)) & 0xFFFFFFFFFFFFFFFF
        h = (h * 0xBF58476D1CE4E5B9) & 0xFFFFFFFFFFFFFFFF
        h ^= (h >> 27)

    # Return a positive python int
    return h & 0x7FFFFFFFFFFFFFFF


def _ask_any_int(prompt: str) -> int:
    while True:
        raw = input(prompt).strip()
        try:
            return int(raw)
        except ValueError:
            print("Please enter a valid integer (e.g., -3, 0, 42).")


def _open_image_macos(path: Path) -> None:
    """
    Opens the image in macOS Preview (or default image viewer).
    This call returns immediately, but the image window stays open
    as long as the user keeps it open.
    """
    subprocess.run(["open", str(path)], check=False)


def _make_rotated_copy(card_path: Path) -> Path:
    """
    Create a 90° clockwise-rotated copy using macOS built-in `sips`.
    Output goes to a temporary sibling file (overwritten each time).
    """
    rotated = card_path.with_name(f"{card_path.stem}__rot90.jpg")

    # `sips -r` rotates clockwise by degrees.
    # We overwrite rotated file each time.
    subprocess.run(
        ["sips", "-s", "format", "jpeg", "-r", "90", str(card_path), "--out", str(rotated)],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return rotated


def _card_path(cards_dir: Path, n: int) -> Path:
    p = cards_dir / f"{n}.jpg"
    if not p.exists():
        raise FileNotFoundError(f"Missing card file: {p}")
    return p


def _draw_card_index(
    user_number: int,
    *,
    base_numbers: list[int],
    wait_seconds: float,
    modulo: int = 78,
) -> int:
    """
    Combine user's number with the pre-existing "energy" base numbers to produce a draw in [0, 77].
    Waits before computing, per spec.
    """
    if wait_seconds > 0:
        time.sleep(wait_seconds)

    # Mix seed-like value from base numbers + current user number
    mix = _modulus_mix(*base_numbers, user_number)

    # Use that mix to seed a local RNG, then draw
    rng = random.Random(mix)
    # Still keep a modulus-based deterministic guard to ensure bounds
    drawn = rng.randrange(0, modulo)
    return int(drawn)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="tarot-marseille",
        description="Interactive Marseille Tarot drawer (0.jpg..77.jpg).",
    )
    parser.add_argument(
        "cards_dir",
        type=Path,
        help='Directory containing the tarot card images named "0.jpg"..."77.jpg".',
    )
    parser.add_argument(
        "--wait",
        type=float,
        default=2.5,
        help="Seconds to wait before drawing each card (default: 2.5).",
    )
    parser.add_argument(
        "--base",
        type=int,
        nargs="+",
        default=[3, 1, 4, 1, 5, 9, 2, 6, 5],
        help="Up to 10 integers used as the persistent 'energy' seed base (default: 10 digits).",
    )

    args = parser.parse_args(argv)
    cards_dir: Path = args.cards_dir.expanduser().resolve()
    wait_seconds: float = float(args.wait)
    base_numbers: list[int] = [int(x) for x in args.base]

    if not cards_dir.is_dir():
        print(f"ERROR: cards_dir is not a directory: {cards_dir}", file=sys.stderr)
        return 2

    if len(base_numbers) == 0 or len(base_numbers) > 10:
        print("ERROR: --base must contain between 1 and 10 integers.", file=sys.stderr)
        return 2

    # Quick sanity check: ensure at least 0..77 exist
    missing = [n for n in range(78) if not (cards_dir / f"{n}.jpg").exists()]
    if missing:
        print(
            f"ERROR: cards_dir must contain all files 0.jpg..77.jpg. Missing: {missing[:10]}"
            + (" ..." if len(missing) > 10 else ""),
            file=sys.stderr,
        )
        return 2

    print("\nMarseille Tarot — interactive draw\n")

    for spec in ORDER:
        input(f"{spec.ready_msg}\n(Press Enter when ready) ")

        user_n = _ask_any_int(spec.pick_msg)

        final_n = _draw_card_index(
            user_n,
            base_numbers=base_numbers,
            wait_seconds=wait_seconds,
            modulo=78,
        )

        print(f"{spec.result_msg}{final_n}\n")

        card = _card_path(cards_dir, final_n)

        # Even -> show as-is; Odd -> rotate 90° clockwise
        to_open = card if (final_n % 2 == 0) else _make_rotated_copy(card)

        # Open the image; it stays open as long as the user wants.
        _open_image_macos(to_open)

        # Gate the next step on user acknowledgement after they close the card window.
        # We cannot reliably detect "window closed" from Preview via `open`,
        # so we ask the user to confirm when they are done.
        input("(Close the card window when you are done, then press Enter to continue) ")
        print()

    print("Reading complete. Goodbye.\n")
    return 0


# -------------------------------------------------------------------------------------
# Test | python marseille.py /Users/egg/Desktop/cards --wait 5 --base 21 33 34 40 55 60 03
# Test | python marseille.py /Users/egg/Desktop/cards --wait 2 --base 393 782 3 55 2589 0 33
# -------------------------------------------------------------------------------------
if __name__ == "__main__":
    # rename_jpgs_sequential("/Users/egg/Desktop/cards")
    raise SystemExit(main())


