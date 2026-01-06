"""
pip install yt-dlp
pip install ffmpeg
---
brew install ffmpeg
micromamba install -c conda-forge yt-dlp
"""

from __future__ import annotations

import os
from pathlib import Path
from time import sleep

import yt_dlp


def download_youtube_as_m4a(
    url: str,
    *,
    output_path: Path = Path("/Users/egg/Downloads/"),
) -> None:
    """
    Downloads the audio from a YouTube URL and converts it to M4A format.

    Args:
        url (str): The YouTube video URL.
        output_path (str): The directory to save the file.
    """

    # Ensure the output directory exists
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # yt-dlp options for M4A conversion
    ydl_opts = {
        "format": "bestaudio[ext=m4a]/bestaudio[ext=mp4]/bestaudio",  # Prioritize native M4A, fall back to best audio
        "outtmpl": os.path.join(output_path, "%(title)s.%(ext)s"),  # Output template
        "noplaylist": True,  # Only download single video if a playlist link is provided
        "progress_hooks": [my_progress_hook],  # Optional: add a progress hook function
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "m4a",
                "preferredquality": "192",  # Bitrate: e.g., 128, 192, 256, 320
            }
        ],
        "merge_output_format": "m4a",
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Starting download for: {url}")
            ydl.download([url])
        print("Download complete and converted to M4A.")

    except Exception as e:
        print(f"An error occurred: {e}")


def my_progress_hook(d):
    """Optional: Hook to monitor download progress."""
    if d["status"] == "finished":
        print("\nDone downloading, starting conversion...")


if __name__ == "__main__":

    output_path = Path("/Users/egg/Desktop/musicas_natal/")
    output_path.mkdir(parents="True", exist_ok="True")

    youtube_link_list: list[str] = [
        "https://www.youtube.com/watch?v=Jne9t8sHpUc",  # Alanis Morissette - Ironic
        "https://www.youtube.com/watch?v=eLOtl3nLR7Q",  # Justice - DVNO
        "https://www.youtube.com/watch?v=sy1dYFGkPUE",  # Justice - D.A.N.C.E.
        "https://www.youtube.com/watch?v=A2VpR8HahKc",  # Daft Punk - One More Time
        "https://www.youtube.com/watch?v=oor2uIqys8M",  # Daft Punk - Crescendolls
        "https://www.youtube.com/watch?v=RKsL90gkbNY",  # Justice - Civilization
        "https://www.youtube.com/watch?v=TIW1m3jbEsg",  # Justice - On n On 1
        "https://www.youtube.com/watch?v=-ecNe7eS-F8",  # Justice - New Lands
        "https://www.youtube.com/watch?v=u6RqBUa3nq8",  # Justice - On n On 2
        "https://www.youtube.com/watch?v=uXj8FM7lTrw",  # Justice - Safe and Sound
        "https://www.youtube.com/watch?v=nr90nbqxuZk",  # Justice - We are Your Friends
        "https://www.youtube.com/watch?v=H9nZgVYxh9M",  # Justice - Generator
        "https://www.youtube.com/watch?v=VMUvI8CjGVU",  # Justice - Afterimage
        "https://www.youtube.com/watch?v=laDm1rIvI-s",  # Justice - Incognito
        "https://www.youtube.com/watch?v=GeRaEMAkZGo",  # Justice - Mannequim Love
        "https://www.youtube.com/watch?v=hunnx7a_wYs",  # Pink Floyd - Summer 68
        "https://www.youtube.com/watch?v=IkgaMFjo_lI",  # Pink Floyd - Fearless
        "https://www.youtube.com/watch?v=2PMnJ_Luk_o",  # Pink Floyd - Great Gig in The Sky
        "https://www.youtube.com/watch?v=QFdkM40KOhE",  # Pink Floyd - Brain Damage
        "https://www.youtube.com/watch?v=o7MlC_Qrmmc",  # Pink Floyd - Mother
        "https://www.youtube.com/watch?v=pPrte-OhUh4",  # Pink Floyd - Hey You
        "https://www.youtube.com/watch?v=Eq8ZiZ9xiLw",  # Pink Floyd - Have a Cigar
        "https://www.youtube.com/watch?v=gOqblSqx_VI",  # Pink Floyd - Pigs
        "https://www.youtube.com/watch?v=HJIqf4YnF4Y",  # Pink Floyd - The Trial
        "https://www.youtube.com/watch?v=Rp5_Ul-qG0w",  # Pink Floyd - Post War Dream
        "https://www.youtube.com/watch?v=sm82kwaaGVw",  # Pink Floyd - When The Tiggers Broke Free
        "https://www.youtube.com/watch?v=Cy0ABjAP0TI",  # Pink Floyd - The Gunner's Dream
        "https://www.youtube.com/watch?v=OzL7u5teZhg",  # Radiohead - You
        "https://www.youtube.com/watch?v=DPpug5FUQsc",  # Radiohead - Stop Whispering
        "https://www.youtube.com/watch?v=i_GZJLH0ynY",  # Radiohead - Anyone Can Play Guitar
        "https://www.youtube.com/watch?v=g0az4OkM02Y",  # Radiohead - Planet Telex
        "https://www.youtube.com/watch?v=K8z8hLvjb_U",  # Radiohead - The Bends
        "https://www.youtube.com/watch?v=7qFfFVSerQo",  # Radiohead - High & Dry
        "https://www.youtube.com/watch?v=pRU-6vaKaf4",  # Radiohead - My Iron Lungs
        "https://www.youtube.com/watch?v=d7lbzUUXj0k",  # Radiohead - Black Star
        "https://www.youtube.com/watch?v=-SLb6BdCHlE",  # Radiohead - Sulk
        "https://www.youtube.com/watch?v=jNY_wLukVW0",  # Radiohead - Airbag
        "https://www.youtube.com/watch?v=Bf01riuiJWA",  # Radiohead - Exit Music (For a Film)
        "https://www.youtube.com/watch?v=yuZYQvvLXVY",  # Radiohead - Lucky
        "https://www.youtube.com/watch?v=svwJTnZOaco",  # Radiohead - Idioteque
        "https://www.youtube.com/watch?v=2Lpw3yMCWro",  # Radiohead - Knives Out
        "https://www.youtube.com/watch?v=Fe6X9fLLp0Y",  # Radiohead - Go To Sleep
        "https://www.youtube.com/watch?v=PxOO8YkB_Og",  # Radiohead - Mixomatosis
        "https://www.youtube.com/watch?v=LUjGtyYEi90",  # Radiohead - Weird Fishes (Arpeggi)
        "https://www.youtube.com/watch?v=IxBQ8Er8DYc",  # Radiohead - Bloom
        "https://www.youtube.com/watch?v=yI2oS2hoL0k",  # Radiohead - Burn The Witch
        "https://www.youtube.com/watch?v=hetqKun4XFg",  # Radiohead - Tinker Tailor Soldier Sailor Rich Man Poor Man Beggar Man Thief
        "https://www.youtube.com/watch?v=FLGJXbl6g8o",  # Morcheeba - Rome Wasn't Built in a Day
        "https://www.youtube.com/watch?v=FuS_u8CwZPw",  # Morcheeba - Enjoy the Ride
        "https://www.youtube.com/watch?v=YHxtuwyC_Xk",  # Morcheeba - Part of The Process
        "https://www.youtube.com/watch?v=Crhgeap_o5k",  # Morcheeba - Blaze Away
        "https://www.youtube.com/watch?v=knJCjwZFTgw",  # Morcheeba - Never Undo
        "https://www.youtube.com/watch?v=4qQyUi4zfDs",  # Portishead - Glory Box
        "https://www.youtube.com/watch?v=oCAIsPz8nWg",  # Portishead - Machine Gun
        "https://www.youtube.com/watch?v=hbe3CQamF8k",  # Massive Attack - Angel
        "https://www.youtube.com/watch?v=u7K72X4eo_s",  # Massive Attack - Teardrop
        "https://www.youtube.com/watch?v=ZWmrfgj0MZI",  # Massive Attack - Unfinished Sympathy
        "https://www.youtube.com/watch?v=6hUkyKBsGtQ",  # Massive Attack - Paradise Circus
        "https://www.youtube.com/watch?v=UlmORqMze-0",  # Massive Attack - Karmacoma
        "https://www.youtube.com/watch?v=sE7xyn28wjg",  # Massive Attack - Inertia Creeps
        "https://www.youtube.com/watch?v=C-9yxZHVJ_I",  # Massive Attack - Atlas Air
        "https://www.youtube.com/watch?v=-wAKzgh_SsU",  # Massive Attack - United Snakes
        "https://www.youtube.com/watch?v=W6ldHDrQ_no",  # Massive Attack - Risington
    ]

    for youtube_link in youtube_link_list:
        download_youtube_as_m4a(url=youtube_link, output_path=output_path)
        sleep(3.41)
