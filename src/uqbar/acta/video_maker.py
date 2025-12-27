# SPDX-License-Identifier: MIT
# uqbar/acta/video_maker.py
"""
Acta Diurna | Video Maker
=========================

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

import math
import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CarouselConfig:
    time_each_pic: float = 3.0  # seconds each image is shown (not counting overlap)
    total_duration: float = 300.0  # total output duration in seconds
    transition_duration: float = 0.75  # seconds; set 0 for hard cuts
    fps: int = 30
    width: int = 1920
    height: int = 1080

    # How to fit images into the output frame:
    # "cover" = center-crop to fill frame (no black bars)
    # "contain" = letterbox/pillarbox to preserve full image
    fit_mode: str = "cover"  # "cover" | "contain"

    # If you want varying transitions, keep a list; it will cycle.
    # Good options: fade, wipeleft, wiperight, wipeup, wipedown,
    # slideleft, slideright, slideup, slidedown, circleopen, circleclose, radial, smoothleft, smoothright
    transitions: tuple[str, ...] = (
        "fade",
        "wipeleft",
        "wiperight",
        "slideleft",
        "slideright",
        "circleopen",
        "circleclose",
        "radial",
        "smoothleft",
        "smoothright",
    )

    video_codec: str = "libx264"
    crf: int = 18
    preset: str = "medium"
    audio_codec: str = "aac"
    audio_bitrate: str = "192k"


def _run(cmd: list[str]) -> None:
    print("▶︎", " ".join(shlex.quote(c) for c in cmd))
    subprocess.run(cmd, check=True)


def _list_images(picture_path: Path) -> list[Path]:
    exts = (".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff")
    imgs = [
        p for p in picture_path.iterdir() if p.is_file() and p.suffix.lower() in exts
    ]
    imgs.sort(key=lambda p: p.name.lower())
    if not imgs:
        raise FileNotFoundError(
            f"No images found in {picture_path} (supported: {exts})"
        )
    return imgs


def _build_scale_filter(cfg: CarouselConfig) -> str:
    w, h = cfg.width, cfg.height
    if cfg.fit_mode == "cover":
        # Scale to cover, then crop to exact size.
        return (
            f"scale={w}:{h}:force_original_aspect_ratio=increase,"
            f"crop={w}:{h},"
            "setsar=1"
        )
    if cfg.fit_mode == "contain":
        # Scale to fit inside, then pad to exact size.
        return (
            f"scale={w}:{h}:force_original_aspect_ratio=decrease,"
            f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,"
            "setsar=1"
        )
    raise ValueError("fit_mode must be 'cover' or 'contain'")


def make_carousel_video(
    picture_path: Path,
    audio_path: Path,
    output_video_path: Path,
    cfg: CarouselConfig = CarouselConfig(),
) -> None:
    """
    Creates an MP4 slideshow (carousel) with optional smooth transitions and an audio track.

    - Images are shown for cfg.time_each_pic seconds each (excluding overlap).
    - Output is cfg.total_duration seconds (trimmed).
    - If cfg.transition_duration > 0, uses xfade transitions (can vary per step).
    - Audio is looped to fill the video and trimmed to cfg.total_duration.
    """
    picture_path = picture_path.expanduser().resolve()
    audio_path = audio_path.expanduser().resolve()
    output_video_path = output_video_path.expanduser().resolve()
    output_video_path.parent.mkdir(parents=True, exist_ok=True)

    imgs = _list_images(picture_path)

    # How many image slots needed to reach total_duration (roughly).
    # Each new clip adds ~time_each_pic seconds of "new" time (transition overlaps).
    n_slots = max(1, int(math.ceil(cfg.total_duration / cfg.time_each_pic)))

    # Cycle through images if we need more slots than unique images.
    seq = [imgs[i % len(imgs)] for i in range(n_slots)]

    td = max(0.0, float(cfg.transition_duration))
    clip_t = cfg.time_each_pic + (td if td > 0 else 0.0)

    # Build ffmpeg inputs: one looping image input per slot
    cmd = ["ffmpeg", "-y", "-hide_banner"]
    for img in seq:
        cmd += ["-loop", "1", "-t", f"{clip_t:.3f}", "-i", str(img)]

    # Add audio input, loop forever (stream_loop -1), then trim with -t later
    cmd += ["-stream_loop", "-1", "-i", str(audio_path)]

    scale_filter = _build_scale_filter(cfg)

    # Prepare each image stream: scale/pad/crop, force format for xfade, set fps
    # Label them as [v0], [v1], ...
    filter_parts: list[str] = []
    for i in range(n_slots):
        filter_parts.append(f"[{i}:v]{scale_filter},format=rgba,fps={cfg.fps}[v{i}]")

    # Chain transitions (xfade) if td>0 and multiple clips
    if td > 0 and n_slots >= 2:
        # xfade offset = when transition starts on the current timeline
        # start transitions at t = time_each_pic, 2*time_each_pic, ...
        current = "v0"
        for i in range(1, n_slots):
            trans = cfg.transitions[(i - 1) % len(cfg.transitions)]
            offset = cfg.time_each_pic * i  # start of transition i on timeline
            out = f"vx{i}"
            filter_parts.append(
                f"[{current}][v{i}]xfade=transition={trans}:duration={td:.3f}:offset={offset:.3f}[{out}]"
            )
            current = out
        vout_label = current
    else:
        # No transitions: just take v0, but we still want a "timeline" of length total_duration.
        # We'll use concat if multiple inputs and td==0
        if n_slots == 1:
            vout_label = "v0"
        else:
            # Concatenate hard-cuts
            # concat filter expects N inputs, outputs 1
            inputs = "".join(f"[v{i}]" for i in range(n_slots))
            filter_parts.append(f"{inputs}concat=n={n_slots}:v=1:a=0[vcat]")
            vout_label = "vcat"

    # Final trim to exact total duration
    filter_parts.append(
        f"[{vout_label}]trim=duration={cfg.total_duration:.3f},setpts=PTS-STARTPTS[vfinal]"
    )

    filter_complex = ";".join(filter_parts)

    # Audio is last input index = n_slots
    aidx = n_slots
    # Trim audio and reset timestamps
    audio_filter = f"[{aidx}:a]atrim=duration={cfg.total_duration:.3f},asetpts=PTS-STARTPTS[afinal]"

    cmd += [
        "-filter_complex",
        f"{filter_complex};{audio_filter}",
        "-map",
        "[vfinal]",
        "-map",
        "[afinal]",
        "-t",
        f"{cfg.total_duration:.3f}",
        "-r",
        str(cfg.fps),
        "-c:v",
        cfg.video_codec,
        "-pix_fmt",
        "yuv420p",
        "-preset",
        cfg.preset,
        "-crf",
        str(cfg.crf),
        "-c:a",
        cfg.audio_codec,
        "-b:a",
        cfg.audio_bitrate,
        "-movflags",
        "+faststart",
        str(output_video_path),
    ]

    _run(cmd)


# --------------------------------------------------------------------------------------
# Exports
# --------------------------------------------------------------------------------------
__all__: list[str] = [
    "make_carousel_video",
]

# -------------------------------------------------------------------------------------
# Test | python -m uqbar.acta.video_maker > out.txt 2>&1
# -------------------------------------------------------------------------------------
# if __name__ == "__main__":
#     # Example usage (edit paths)
#     make_carousel_video(
#         picture_path=Path("/path/to/pictures"),
#         audio_path=Path("/path/to/audio.m4a"),
#         output_video_path=Path("/path/to/output.mp4"),
#         cfg=CarouselConfig(
#             time_each_pic=3.0,
#             total_duration=300.0,
#             transition_duration=0.75,
#             fps=30,
#             width=1920,
#             height=1080,
#             fit_mode="cover",
#         ),
#     )
