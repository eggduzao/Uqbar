# SPDX-License-Identifier: MIT
# uqbar/milou/search_queries.py
"""
Milou | Core
============

Process all the resources necessary for the actual search.

Overview
--------
Three main utilities:

1) parse_query(...) -> list[str]
   - Turn a single query string (or a file of lines) into "+"-joined,
     diacritic-free queries.

2) get_search_engine_links(search_engines=...) -> list[str]
   - Map famous engine names (or URLs) to canonical query URL prefixes.

3) form_final_query_list(query_list=..., search_engine_list=...) -> list[str]
   - Combine engine prefixes + queries, then minimally verify URLs are reachable.

Imlementation Notes
-------------------
- "Minimal verification" here means: a fast HEAD if possible, otherwise
  a tiny GET (streamed, no full download), with short timeouts.
- Some engines may redirect to consent pages; we still treat HTTP 2xx/3xx
  as "reachable".

Usage
-----
Placeholder.

Usage Details
-------------
Placeholder.

Metadata
--------
- Project: Milou
- License: MIT
"""

# -------------------------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------------------------
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit

import requests


# -------------------------------------------------------------------------------------
# Constants
# -------------------------------------------------------------------------------------
@dataclass(frozen=True)
class _Engine:
    name: str
    prefix: str  # full URL prefix up to and including
                 # the query param key (e.g. "...?q=")


# Split on spaces, commas, semicolons, pipes, dashes, plus signs (1+ occurrences)
_SPLIT_RE = re.compile(r"[\s,;|\-+]+")


_FORMATS_ALLOWED: list[str] = [
    "pdf",
    "epub",
    "mobi",
    "azw3",
    "txt",
    "html",
    "htm",
    "xml",
    "rtf",
    "doc",
    "docx",
    "odt",
    "md",
    "tex",
    "json",
    "yaml",
    "csv",
    "djvu",
    "lit",
    "prc",
    "xhtml"
]


_ENGINE_MAP: dict[str, _Engine] = {
    # canonical query patterns
    "google": _Engine("google", "https://www.google.com/search?q="),
    "bing": _Engine("bing", "https://www.bing.com/search?q="),
    "yahoo": _Engine("yahoo", "https://search.yahoo.com/search?p="),
    "baidu": _Engine("baidu", "https://www.baidu.com/s?wd="),
    "duckduckgo": _Engine("duckduckgo", "https://duckduckgo.com/?q="),
    "ddg": _Engine("duckduckgo", "https://duckduckgo.com/?q="),
    "yandex": _Engine("yandex", "https://yandex.com/search/?text="),
}


# -------------------------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------------------------
def _strip_diacritics(s: str, *, fmt: str = "str") -> str | list[str] | None:
    # NFKD splits letters + diacritics; drop combining marks
    normalized = unicodedata.normalize("NFKD", s)
    if fmt == "str":
        return "".join(ch for ch in normalized if not unicodedata.combining(ch))
    if fmt == "list":
        return [ch for ch in normalized if not unicodedata.combining(ch)]
    return


def _normalize_query(s: str) -> str | None:
    s = s.strip()
    if not s:
        return None

    s: str | list[str] | None = _strip_diacritics(s, fmt="str")
    if s is None or isinstance(s, list):
        return None

    s = s.lower()

    parts = [p for p in _SPLIT_RE.split(s) if p]
    if not parts:
        return None

    # join everything by '+'
    return "+".join(parts)


def _looks_like_url(s: str) -> bool:
    try:
        u = urlsplit(s)
        return u.scheme in {"http", "https"} and bool(u.netloc)
    except Exception:
        return False


def _canonicalize_url_prefix(url: str) -> str:
    """
    Minimal cleanup:
    - ensure https scheme if missing (only if looks like domain)
    - keep as-is otherwise
    """
    url = url.strip()
    if not url:
        return url

    if _looks_like_url(url):
        return url

    # If user passed something like "www.google.com/search?q="
    if re.match(r"^[A-Za-z0-9.-]+\.[A-Za-z]{2,}(/.*)?$", url):
        return "https://" + url.lstrip("/")

    return url


def _url_reachable(url: str, *, timeout_s: float = 6.0) -> bool:
    """
    “Minimally invasive” reachability check:
    - Try HEAD first (cheap).
    - If HEAD fails or is blocked (405/403 sometimes), do a tiny streamed GET.
    Treat 2xx and 3xx as reachable.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/123.0 Safari/537.36"
        )
    }

    try:
        r = requests.head(
            url,
            allow_redirects=True,
            timeout=timeout_s,
            headers=headers,
        )
        if 200 <= r.status_code < 400:
            return True

        # Some sites reject HEAD; fall through to GET in those common cases
        if r.status_code in {401, 403, 405}:
            pass
        else:
            return False
    except requests.RequestException:
        # fall through to GET
        pass

    try:
        with requests.get(
            url,
            allow_redirects=True,
            timeout=timeout_s,
            headers=headers,
            stream=True,
        ) as r:
            if 200 <= r.status_code < 400:
                # don’t download the whole page; just touch a small chunk
                _ = next(r.iter_content(chunk_size=256), b"")
                return True
            return False
    except requests.RequestException:
        return False


# --------------------------------------------------------------------------------------
# Functions
# --------------------------------------------------------------------------------------
def parse_query(*, single_query: str | None, input_path: Path | None) -> list[str]:
    """
    - If single_query is provided: parse it as X-separated list of words,
      where X in [\\ ,;|-\\+]+.
    - If input_path is provided: read lines, strip, treat each line like single_query.
    - Return list of "+-separated" normalized queries.
    - If both are None: raise ValueError.
    """
    if single_query is None and input_path is None:
        raise ValueError(
            "Both single_query and input_path "
            "are None; provide at least one."
        )

    out: list[str] = []

    if single_query is not None:
        q = _normalize_query(single_query)
        if q is not None:
            out.append(q)

    if input_path is not None:
        if not input_path.exists():
            raise FileNotFoundError(f"input_path does not exist: {input_path}")
        if not input_path.is_file():
            raise ValueError(f"input_path is not a file: {input_path}")

        for line in input_path.read_text(
            encoding="utf-8",
            errors="replace"
        ).splitlines():
            q = _normalize_query(line)
            if q is not None:
                out.append(q)

    return out


def get_search_engine_links(*, search_engines: str) -> list[str]:
    """
    Input: a string containing engine names or URLs (often one item like "google").
    Behavior:
    - Split by the same separators used for queries.
    - For known names: map to a canonical "https://...queryparam=" prefix.
    - For URLs: accept them as-is (canonicalize lightly).
    - If empty result: raise ValueError.
    """
    if not search_engines or not search_engines.strip():
        raise ValueError("search_engines is empty.")

    tokens = [t for t in _SPLIT_RE.split(search_engines.strip().lower()) if t]
    out: list[str] = []

    for tok in tokens:
        if tok in _ENGINE_MAP:
            out.append(_ENGINE_MAP[tok].prefix)
            continue

        # If user provided a URL-ish token, accept it
        maybe_url = _canonicalize_url_prefix(tok)
        if _looks_like_url(maybe_url):
            out.append(maybe_url)

    if not out:
        raise ValueError(
            "No valid search engines recognized. Use names like: "
            "google, bing, yahoo, baidu, duckduckgo, yandex (or "
            "provide full https URLs)."
        )

    return out


def verify_query_formats(
    *,
    formats_allowed: list[str],
) -> list[str] | None:
    """
    - epub, mobi, azw3 - common ebook/container formats
    - txt - plain text
    - html, htm, xhtml - web pages / online articles
    - xml, json, yaml - structured markup/data (often documentation)
    - rtf - rich text
    - doc, docx, odt - word processor files
    - md, tex - markup/source text for articles/books
    - csv - text corpus/tabular text
    - djvu - scanned/doc archive text format
    - lit, prc - legacy ebook formats
    """

    if not formats_allowed:
        return None

    ext_list: list[str] = _normalize_query(formats_allowed).split("+")
    ext_list = [x.strip(".") for x in ext_list]
    ext_list = [x for x in ext_list if x in _FORMATS_ALLOWED]

    return ext_list


def form_final_query_list(
    *,
    query_list: list[str],
    search_engine_list: list[str],
    format_list: list[str],
) -> list[str]:
    """
    Join every engine prefix with every query, verify reachability,
    and return working URLs.
    """
    if not query_list:
        raise ValueError("query_list is empty.")
    if not search_engine_list:
        raise ValueError("search_engine_list is empty.")
    if not format_list:
        raise ValueError("format_list is empty.")

    final_urls: list[str] = []

    for engine_prefix in search_engine_list:
        engine_prefix = engine_prefix.strip()
        if not engine_prefix:
            continue

        for q in query_list:
            q = q.strip()
            if not q:
                continue

            for f in format_list:
                f = f.strip()
                if not f:
                    continue

                url = f"{engine_prefix}{q}+{f}"
                if _url_reachable(url):
                    final_urls.append(url)

    return final_urls


# --------------------------------------------------------------------------------------
# Exports
# --------------------------------------------------------------------------------------
__all__: list[str] = [
    "parse_query",
    "get_search_engine_links",
    "form_final_query_list",
    "verify_query_formats",
]
