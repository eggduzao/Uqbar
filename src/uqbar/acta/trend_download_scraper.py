# SPDX-License-Identifier: MIT
# uqbar/acta/trend_scraper.py
"""
Acta Diurna | Trend Scraper
===========================

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

from dataclasses import dataclass
from datetime import timezone, timedelta
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse
import re
import subprocess
import xml.etree.ElementTree as ET

from uqbar.acta.utils import deprecated, Trend, TrendList

import sys
# -------------------------------------------------------------------------------------
# Constants
# -------------------------------------------------------------------------------------
DEFAULT_VOLUME: float = 10000.0

CHROME_COMMAND: str = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

RSS_URL: str = "https://trends.google.com/trending/rss?geo=US"

RSS_DOWNLOAD_PATH: Path = Path("/Users/egg/Desktop/web.html")


_AMP_SANITIZE_RE = re.compile(r"&(?!(amp|lt|gt|quot|apos|#\d+|#x[0-9A-Fa-f]+);)")

_TRAFFIC_RE = re.compile(r"^\s*([0-9]*\.?[0-9]+)\s*([KMB]?)\+?\s*$", re.IGNORECASE)


# ------------------------------------ DEPRECATED -------------------------------------
@deprecated("Version 0.1.0 - Manual Download")
def constants_legacy() -> None:
    """
    Legacy Constants
    """
    # Mock URL
    MOCK_URL = Path("/Users/egg/Desktop/web.html")

    # Precompiled patterns
    TREND_BREAKDOWN_RE = re.compile(r"Trend breakdown")
    DATA_TERM_RE = re.compile(r'data-term="([^"]+)"')
    NEWS_HEADER_RE = re.compile(r"In the news")
    URL_RE = re.compile(r"https://[^\s\"'>]+")


# -------------------------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------------------------
def _download_rss_feed(
    *,
    chrome_command: str = CHROME_COMMAND,
    rss_url: str = RSS_URL,
    rss_download_path: Path = RSS_DOWNLOAD_PATH,
) -> tuple[str, str]:
    """
    Fetch the rendered DOM of `rss_url` using headless Chrome and save it to disk.

    Notes
    -----
    - Does not rely on shell aliases.
    - Avoids shell redirection; writes output via Python.
    """
    rss_download_path.parent.mkdir(parents=True, exist_ok=True)

    command: list[str] = [
        chrome_command,
        "--headless=new",
        "--dump-dom",
        "--disable-notifications",
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) HeadlessChrome Safari/537.36",
        rss_url,
    ]

    result = subprocess.run(command, capture_output=True, text=True, check=True)

    rss_download_path.write_text(result.stdout, encoding="utf-8")
    return result.stdout, result.stderr


def _extract_rss_xml_text(raw_text: str) -> str:
    """
    Your file is often a browser-rendered view with a preamble line.
    We extract the real <rss>...</rss> block.
    """
    start = raw_text.find("<rss")
    if start == -1:
        raise ValueError("Could not find <rss ...> in the provided file.")

    end = raw_text.rfind("</rss>")
    if end == -1:
        raise ValueError("Could not find </rss> in the provided file.")

    xml_block = raw_text[start : end + len("</rss>")]

    # Sanitize bare '&' that are not valid XML entities
    xml_block = _AMP_SANITIZE_RE.sub("&amp;", xml_block)
    return xml_block


def _localname(tag: str) -> str:
    # tag can be "title" or "{namespace}approx_traffic"
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def _child_text_by_localname(elem: ET.Element, name: str) -> str | None:
    for child in list(elem):
        if _localname(child.tag) == name:
            return (child.text or "").strip() or None
    return None


def _children_by_localname(elem: ET.Element, name: str) -> list[ET.Element]:
    out: list[ET.Element] = []
    for child in list(elem):
        if _localname(child.tag) == name:
            out.append(child)
    return out


def _parse_approx_traffic(s: str | None) -> float | None:
    """
    Examples: "200+", "20K+", "2M+", "1.5M+"
    Returns absolute count as float.
    """
    if not s:
        return None
    m = _TRAFFIC_RE.match(s)
    if not m:
        # last resort: strip '+' and try float
        s2 = s.replace("+", "").strip()
        try:
            return float(s2)
        except ValueError:
            return None

    num = float(m.group(1))
    suffix = (m.group(2) or "").upper()

    mult = 1.0
    if suffix == "K":
        mult = 1_000.0
    elif suffix == "M":
        mult = 1_000_000.0
    elif suffix == "B":
        mult = 1_000_000_000.0

    return num * mult


def _delete_trends_local_url(rss_download_path: Path) -> tuple[str, str]:

    file_path = str(rss_download_path)

    result = subprocess.run(
        ["rm", "-rf", file_path],
        capture_output=True,
        text=True,
        check=True,
    )

    return result.stdout, result.stderr


# ------------------------------------ DEPRECATED -------------------------------------
@deprecated("Version 0.1.0 - Manual Download")
def _get_trends_from_local_url_legacy(url_path: Path) -> list[str]:

    parsed_file = []

    with open(url_path, "r") as file:
        for line in file:
            ll = line.strip()
            l = len(ll)
            if l <= 1000:
                parsed_file.append(ll)
                continue
            curr_line = []
            for c in ll:
                if c != ">":
                    curr_line.append(c)
                    continue
                curr_line.append(c)
                parsed_file.append("".join(curr_line))
                curr_line = []

        return parsed_file


@deprecated("Version 0.1.0 - Manual Download")
def _delete_trends_local_url_legacy(url_path: Path) -> tuple[str, str]:

    file_path = str(url_path)
    folder_path = str(url_path.parent / url_path.stem) + "_files/"

    subprocess.run(
        ["rm", "-rf", file_path, folder_path],
        capture_output=True,
        text=True,
        check=True,
    )

    return stdout, stderr


# -------------------------------------------------------------------------------------
# Functions
# -------------------------------------------------------------------------------------
def parse_trend_rss_feed(
    rss_feed_path: Path,
    working_path: Path,
) -> TrendList:
    """
    Parse a Google Trends RSS feed file as saved from a browser.

    Robustness features for the browser-saved variant:
    - strips any non-XML preamble before <rss>
    - sanitizes bare '&' characters to '&amp;'
    """
    raw_text = rss_feed_path.read_text(encoding="utf-8", errors="replace")
    xml_text = _extract_rss_xml_text(raw_text)

    root = ET.fromstring(xml_text)
    channel = root.find("channel")
    if channel is None:
        return []

    all_items = channel.findall("item")
    trend_list: TrendList = TrendList()

    for counter, item in enumerate(all_items, start=1):
        trend: Trend = Trend()

        trend.title = _child_text_by_localname(item, "title")

        approx = _child_text_by_localname(item, "approx_traffic")
        trend.volume = _parse_approx_traffic(approx)

        pub = _child_text_by_localname(item, "pubDate")
        # print(f"pub = {pub} | type(pub) = {type(pub)}")
        # sys.exit(0)

        if counter == 1:
            if not trend_list.datetime_utc:
                trend_list.datetime_utc = pub
            # print(f"trend_list.datetime_utc = {trend_list.datetime_utc} | type(trend_list.datetime_utc) = {type(trend_list.datetime_utc)}")
            # sys.exit(0)
            trend_list.update_datetime()
        
        trend.picture_source = _child_text_by_localname(item, "picture_source")

        news_items = _children_by_localname(item, "news_item")[:3]
        for idx, news in enumerate(news_items, start=1):
            title = _child_text_by_localname(news, "news_item_title")
            url = _child_text_by_localname(news, "news_item_url")
            source = _child_text_by_localname(news, "news_item_source")

            setattr(trend, f"news_item_title_{idx}", title)
            setattr(trend, f"news_item_url_{idx}", url)
            setattr(trend, f"news_item_source_{idx}", source)

        if news_items:
            trend.update_paywall()

        if trend.volume is None:
            trend.volume = DEFAULT_VOLUME
        trend_list.append(trend)

        # Initialization - Path
        trend.content_path: Path = working_path / f"trend_{counter:02d}"
        trend.image_path: Path = trend.content_path / "pics"
        trend.video_path: Path = trend.content_path / "vids"
        trend.audio_path: Path = trend.content_path / "audi"
        path_list = [trend.image_path, trend.video_path, trend.audio_path]
        for path_name in path_list:
            try:
                path_name.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                print(f"An error occurred during path creation: {e}")

    return trend_list


def get_trends(
    *,
    rss_download_path: str = RSS_DOWNLOAD_PATH,
    working_path: Path,
    delete_rss_xml_path: bool = False,
) -> TrendList | None:
    """
    Returns trending tags and the 3 articles of news articles related to the trend.
    """

    # If file does not exist, try to download
    if not rss_download_path.exists():

        # Download rss feed to download path
        try:
            download_out, download_err = _download_rss_feed(
                rss_download_path=rss_download_path,
            )
        except Exception as e:
            raise e

        # Still does not exist, halt
        if not rss_download_path.exists():
            print("[ERROR] Trend xml file does not exist!")
            return None

    # Create Trends and TrendList
    trend_list: TrendList = parse_trend_rss_feed(
        rss_feed_path=rss_download_path,
        working_path=working_path,
    )

    if not trend_list:
        print("[ERROR] Trend List is Empty!")
        return None

    if delete_rss_xml_path and rss_download_path.exists():

        print("Deleting trend xml file...")
        delete_out, delete_err = _delete_trends_local_url(rss_download_path)

        if not rss_download_path.exists():
            print("Trend xml file deleted successfully!")
            return trend_list

        print("[ERROR] Trend xml file count not be deleted.")
        return None

    return trend_list


# ------------------------------------ DEPRECATED -------------------------------------


@deprecated("Version 0.1.0 - Manual Download")
def get_trend_tags_legacy(
    trend_list: list[str],
    *,
    max_num: int | None = None,
) -> list[str]:
    """
    Extract trend tags from newline-forced HTML chunks.

    The function:
    - waits for the third occurrence of the literal text "Trend breakdown"
    - then collects values from attributes of the form data-term="<TREND>"
    - stops when another full set of three "Trend breakdown" occurrences is found
    - removes duplicates while preserving insertion order
    """
    collecting = False
    breakdown_count = 0
    collected: list[str] = []
    seen: set[str] = set()

    for line in trend_list:
        # Count "Trend breakdown"
        if "TREND_BREAKDOWN_RE".search(line):
            breakdown_count += 1

            if breakdown_count == 3:
                collecting = True
                continue

            if collecting and breakdown_count == 6:
                break

        if not collecting:
            continue

        # Extract data-term values
        for match in "DATA_TERM_RE".findall(line):
            if match not in seen:
                seen.add(match)
                collected.append(match)

                if max_num is not None and len(collected) >= max_num:
                    return collected

    return collected


@deprecated("Version 0.1.0 - Manual Download")
def get_trend_news_urls_legacy(
    trend_list: list[str],
) -> list[str]:
    """
    Extract up to three news article URLs from newline-forced HTML chunks.

    The function:
    - finds the unique occurrence of the literal text "In the news"
    - then extracts the first three URLs starting with "https://"
    - stops immediately after collecting three URLs
    """
    collecting = False
    urls: list[str] = []

    for line in trend_list:
        if not collecting:
            if "NEWS_HEADER_RE".search(line):
                collecting = True
            continue

        # Once collecting, extract URLs
        for match in "URL_RE".findall(line):
            urls.append(match)
            if len(urls) == 3:
                return urls

    return urls


@deprecated("Version 0.1.0 - Manual Download")
def get_trends_legacy(
    *,
    url_path: str = "MOCK_URL",
    delete_url: bool = False,
) -> tuple[list[str], list[str]] | None:
    """
    Returns trending tags and the 3 articles of news articles related to the trend.
    """
    trend_list = _get_trends_from_local_url_legacy(url_path)

    if not trend_list:
        print("Trend List is Empty!")
        return None, None

    tags = get_trend_tags_legacy(trend_list)
    news = get_trend_news_urls_legacy(trend_list)

    if not news:
        print("News URL List is Empty!")
        return None, None

    if delete_url:
        _delete_trends_local_url_legacy(url_path)

    return tags, news


# --------------------------------------------------------------------------------------
# Exports
# --------------------------------------------------------------------------------------
__all__: list[str] = [
    "get_trends",
]


# -------------------------------------------------------------------------------------
# Test | python -m uqbar.acta.trend_download_scraper > out.txt 2>&1
# -------------------------------------------------------------------------------------
# if __name__ == "__main__":
#     result = get_trends(delete_rss_xml_path=True)
