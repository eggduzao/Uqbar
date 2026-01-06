# SPDX-License-Identifier: MIT
# uqbar/acta/audio_background_maker.py
"""
Acta Diurna | Audio Background Maker
====================================

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

import subprocess
from pathlib import Path

# -------------------------------------------------------------------------------------
# Constants
# -------------------------------------------------------------------------------------
MODEL_PATH = Path("/Users/egg/acta_diurna/data/piper_lessac/en_US-lessac-medium")


# -------------------------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------------------------
def piper_tts(
    text: str,
    output_wav_path: Path,
    *,
    model_path: Path = MODEL_PATH,
) -> None:
    """
    Executes Piper TTS on a string.

    Example
    -------
    python3 -m piper \
        -m /Users/egg/acta_diurna/data/piper_lessac/en_US-lessac-medium \
        -f output.wav \
        -- "On the news today: Rob Reiner, 78, and his wife, Michele Singer \
        Reiner, 68, were found dead inside their Brentwood home on Sunday \
        afternoon, and authorities are treating the case as an apparent \
        homicide. Police say no suspect has been identified and nobody is \
        in custody yet - while tributes from politicians, actors, and \
        longtime colleagues began pouring in almost immediately."
    """

    subprocess.run(
        ["piper", "--model", str(model_path), "--output_file", str(output_wav_path)],
        input=text,
        text=True,
        check=True,
    )

# -------------------------------------------------------------------------------------
# Example Code (commented out)
# -------------------------------------------------------------------------------------
# # 3. Minimal native Piper example (pure Python)
#
# from piper.voice import PiperVoice
#
# voice = PiperVoice.load(
#     Path("en_US-lessac-medium.onnx"),
#     Path("en_US-lessac-medium.onnx.json"),
# )
#
# audio_chunks = []
#
# for chunk in voice.synthesize("Hello Honey. This is Piper."):
#     audio_chunks.append(chunk.audio_int16)
#
# # Combine all chunks
# audio: NDArray[np.int16] = np.concatenate(audio_chunks)
#
#
# # --------
#
# # 4. Writing to WAV (cleanest first step)
#
# import wave
#
# with wave.open("out.wav", "wb") as wf:
#     wf.setnchannels(1)
#     wf.setsampwidth(2)  # int16
#     wf.setframerate(voice.config.sample_rate)
#     wf.writeframes(audio.tobytes())
#
#
# # --------
#
# # 5. Using soundfile (recommended)
#
# import soundfile as sf
#
# sf.write(
#     "out.wav",
#     audio,
#     voice.config.sample_rate,
#     subtype="PCM_16",
# )
#
# # --------
#
# # 6. Working with chunks (important for paragraph TTS)
#
# # chunk.audio_int16        # numpy array
# # chunk.audio_int16_bytes  # raw bytes
#
# # Insert silence between paragraphs
#
# def silence(seconds: float, sr: int):
#     return np.zeros(int(seconds * sr), dtype=np.int16)
#
# audio = np.concatenate([
#     paragraph_1_audio,
#     silence(0.3, sr),
#     paragraph_2_audio,
# ])
#
# # --------
#
# # 7. Audio manipulation objects you should love
#
# from pydub import AudioSegment
#
# seg = AudioSegment(
#     audio.tobytes(),
#     frame_rate=sr,
#     sample_width=2,
#     channels=1,
# )
#
# seg = seg.fade_in(50).fade_out(100)
# seg.export("out.mp3", format="mp3")
#
#
# # --------
#
# import numpy as np
# import pandas as pd
# import scipy as sc
#
# print(np.__version__)
# print(sc.__version__)
# print(pd.__version__)
#
# # libsndfile ffmpeg
#
# # python -c "import pydub as pb; print(pb.__version__)"
# # python -c "import wave as wa; print(wa.__version__)"
#
# import numpy as np
# import soundfile as sf
# from piper.voice import PiperVoice
# from pydub import AudioSegment
#
# print(np.__version__)
# print(sf.__libsndfile_version__)


# -------------------------------------------------------------------------------------
# Functions
# -------------------------------------------------------------------------------------
def create_audio_track(input_name: str) -> str | None:
    """
    Placeholder
    """
    ...

# --------------------------------------------------------------------------------------
# Exports
# --------------------------------------------------------------------------------------
__all__: list[str] = [
    "create_audio_track",
]


# -------------------------------------------------------------------------------------
# Test | python -m uqbar.acta.audio_background_maker > out.txt 2>&1
# -------------------------------------------------------------------------------------
# if __name__ == "__main__":
#     ...

