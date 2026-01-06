# SPDX-License-Identifier: MIT
# uqbar/acta/image_processor.py
"""
Acta Diurna | Image Processor
=============================

Overview
--------
Placeholder.

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
import subprocess
import unicodedata
from pathlib import Path

from imagededup.methods.cnn import CNN

# -------------------------------------------------------------------------------------
# Constants
# -------------------------------------------------------------------------------------
IMAGE_ROOT_PATH: Path = Path("/Users/egg/Desktop/pics")

SIMILARITY_SCORE: float = 0.95

LIST_OF_COMMON_EXTENSIONS: set[str] = {
    ".jpg",
    ".jpeg",
    ".png",
    ".svg",
    ".tif",
    ".tiff",
    ".webp",
    ".gif",
}


_CLEAN_RE = re.compile(r"[a-z0-9_]+")


# -------------------------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------------------------
def _strip_diacritics(s: str) -> str:
    normalized = unicodedata.normalize("NFKD", s)
    return "".join(c for c in normalized if not unicodedata.combining(c))


def _sorted_files(path: Path) -> list[Path]:
    return sorted(
        [p for p in path.iterdir() if p.is_file()], key=lambda p: p.name.lower()
    )


def _run_magick(args: list[str]) -> None:
    subprocess.run(
        ["magick", *args],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _remove_image(image_path: Path) -> None:
    """
    Removes the argument path.

    Notes
    -----
    - Does not rely on shell aliases.
    - Avoids shell redirection; writes output via Python.
    """
    if not image_path.exists():
        print(f"Image does not exist. Not removing {image_path}.")

    command: list[str] = ["rm", "-rf", str(image_path)]
    result = subprocess.run(command, capture_output=True, text=True, check=True)

    return result.stdout, result.stderr


# -------------------------------------------------------------------------------------
# Functions
# -------------------------------------------------------------------------------------
def clean_name(input_name: str) -> str | None:
    """
    Clean an arbitrary filename into a restricted pattern.

    Accepted output pattern:
        [a-z0-9_]+.[a-z]{3,4}

    Returns:
        - cleaned filename if extension is valid
        - None otherwise
    """
    if not input_name or "." not in input_name:
        return None

    # Separate name and extension (single extension only)
    name_part, ext_part = input_name.rsplit(".", 1)

    # Normalize
    name_part = _strip_diacritics(name_part.lower())
    ext_part = _strip_diacritics(ext_part.lower())

    # Clean base name
    tokens = _CLEAN_RE.findall(name_part)
    if not tokens:
        return None

    clean_base = "_".join(tokens)

    clean_ext = f".{ext_part}"
    if clean_ext not in LIST_OF_COMMON_EXTENSIONS:
        return None

    # Enforce final pattern
    if not re.fullmatch(r"[a-z0-9_]+\.[a-z]{3,4}", clean_base + clean_ext):
        return None

    return clean_base + clean_ext


def clean_convert_path_image_names(input_path: Path) -> None:
    if not input_path.is_dir():
        raise ValueError(f"{input_path} is not a directory")

    idx = 1

    for file_path in _sorted_files(input_path):
        cleaned = clean_name(file_path.name)
        if cleaned is None:
            continue

        ext = file_path.suffix.lower()

        target_png = input_path / f"{idx}.png"

        try:
            # --- JPEG / TIFF → PNG ---
            if ext in {".jpg", ".jpeg", ".tif", ".tiff"}:
                _run_magick([str(file_path), str(target_png)])
                file_path.unlink()
                idx += 1

            # --- PNG (rename only) ---
            elif ext == ".png":
                if file_path.name != target_png.name:
                    file_path.rename(target_png)
                idx += 1

            # --- GIF / WEBP (container handling) ---
            elif ext in {".gif", ".webp"}:
                # magick expands frames automatically: out_%03d.png
                pattern = input_path / "__frame_%03d.png"
                _run_magick([str(file_path), str(pattern)])

                frames = sorted(input_path.glob("__frame_*.png"), key=lambda p: p.name)

                for frame in frames:
                    frame.rename(input_path / f"{idx}.png")
                    idx += 1

                file_path.unlink()

            # --- SVG or others: ignore for now ---
            else:
                continue

        except Exception:
            # Fail-safe: do not increment idx on failure
            continue


def image_dedup(
    *,
    similarity_score: float = SIMILARITY_SCORE,
    image_root_path: Path = IMAGE_ROOT_PATH,
) -> None:

    # Check image directory
    if not image_root_path.is_dir():
        raise SystemExit(f"Not a directory: {image_root_path}")

    # Initialize CNN encoder (downloads model on first run)
    encoder = CNN()

    # Encode all images in the folder
    # this returns a dict: { 'img1.jpg': embedding_array, ... }
    encodings = encoder.encode_images(image_dir=str(image_root_path))

    # Find duplicates
    # this returns: { 'img1.jpg': ['close1.jpg', 'close2.png'], ... }
    duplicates = encoder.find_duplicates(
        encoding_map=encodings,
        min_similarity_threshold=similarity_score,
    )

    # Remove similar images
    image_to_remove_path_list: list[Path] = []
    for _img, dupes in duplicates.items():

        if not dupes:  # empty list -> no dupes
            continue

        for d in dupes:
            # d is a dict like {'filename': 'foo.jpg', 'similarity': 0.97}
            # depending on imagededup version, sometimes it's just the filename.
            if isinstance(d, dict):
                Path(d["filename"]).resolve()
                image_to_remove_path_list.append()
            else:
                Path(d).resolve()
                image_to_remove_path_list.append()

    for image_path in image_to_remove_path_list:
        _remove_image(image_path)


# --------------------------------------------------------------------------------------
# Exports
# --------------------------------------------------------------------------------------
__all__: list[str] = [
    "clean_name",
    "clean_convert_path_image_names",
    "image_dedup",
]


# -------------------------------------------------------------------------------------
# Test | python -m uqbar.acta.image_processor > out.txt 2>&1
# -------------------------------------------------------------------------------------
# if __name__ == "__main__":
#     ...
