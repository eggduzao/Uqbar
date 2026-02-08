#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse, urljoin

import requests


@dataclass(frozen=True, slots=True)
class GitHubBlob:
    owner: str
    repo: str
    branch: str
    path: str  # path inside repo (e.g. "RUVSeq/README.md")


BLOB_RE = re.compile(
    r"^https?://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+)/blob/(?P<branch>[^/]+)/(?P<path>.+)$"
)

# Basic Markdown image syntaxes + HTML <img src="...">
MD_IMG_RE = re.compile(r"!\[[^\]]*\]\((?P<url>[^) \t]+)(?:\s+\"[^\"]*\")?\)")
HTML_IMG_RE = re.compile(r'<img[^>]+src=["\'](?P<url>[^"\']+)["\']', re.IGNORECASE)


def parse_github_blob_url(url: str) -> GitHubBlob | None:
    m = BLOB_RE.match(url.strip())
    if not m:
        return None
    return GitHubBlob(
        owner=m.group("owner"),
        repo=m.group("repo"),
        branch=m.group("branch"),
        path=m.group("path"),
    )


def raw_url(owner: str, repo: str, branch: str, path: str) -> str:
    # Raw content host
    return f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}"


def safe_filename(name: str) -> str:
    name = name.strip().replace("\0", "")
    name = re.sub(r"[^\w.\-]+", "_", name, flags=re.UNICODE)
    return name[:200] if len(name) > 200 else name


def extract_image_urls_from_markdown(md_text: str) -> list[str]:
    urls: list[str] = []
    for m in MD_IMG_RE.finditer(md_text):
        urls.append(m.group("url"))
    for m in HTML_IMG_RE.finditer(md_text):
        urls.append(m.group("url"))
    # de-dup preserve order
    seen: set[str] = set()
    out: list[str] = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def absolutize_and_rawify(img_url: str, blob: GitHubBlob) -> str | None:
    """
    Convert image references from README into a direct-download URL.
    Handles:
      - absolute URLs (https://...)
      - root-relative (/Bioconductor/BiocStickers/blob/...)
      - repo-relative (./sticker.png or sticker.png)
    """
    img_url = img_url.strip()

    # Ignore anchors/mailto/etc
    if img_url.startswith("#") or img_url.startswith("mailto:"):
        return None

    # If already raw.githubusercontent.com, keep
    if img_url.startswith("https://raw.githubusercontent.com/"):
        return img_url

    # If it's a GitHub "blob" link to an image, convert to raw
    if "github.com/" in img_url and "/blob/" in img_url:
        b = parse_github_blob_url(img_url)
        if b:
            return raw_url(b.owner, b.repo, b.branch, b.path)
        return img_url  # unknown form, keep as-is

    # If it's an absolute URL (e.g. https://...png), keep
    if img_url.startswith("http://") or img_url.startswith("https://"):
        # Some READMEs use githubusercontent "user-images" etc -> downloadable as-is
        return img_url

    # Root-relative path on GitHub site (rare but possible)
    if img_url.startswith("/"):
        # Turn into GitHub URL then rawify if it is blob-like; else leave
        gh = urljoin("https://github.com", img_url)
        b = parse_github_blob_url(gh)
        if b:
            return raw_url(b.owner, b.repo, b.branch, b.path)
        return gh

    # Otherwise it's relative to the README directory inside the repo
    # Example blob.path = "RUVSeq/README.md" -> base_dir = "RUVSeq/"
    base_dir = blob.path.rsplit("/", 1)[0] if "/" in blob.path else ""
    base_dir = f"{base_dir}/" if base_dir else ""
    resolved_path = os.path.normpath(base_dir + img_url).replace("\\", "/")

    return raw_url(blob.owner, blob.repo, blob.branch, resolved_path)


def download(url: str, out_path: Path, timeout: float = 30.0) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    headers = {"User-Agent": "Mozilla/5.0"}
    with requests.get(url, headers=headers, stream=True, timeout=timeout) as r:
        r.raise_for_status()
        tmp = out_path.with_suffix(out_path.suffix + ".part")
        with tmp.open("wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 128):
                if chunk:
                    f.write(chunk)
        tmp.replace(out_path)


def guess_ext_from_url(u: str) -> str:
    path = urlparse(u).path
    for ext in (".png", ".jpg", ".jpeg", ".webp", ".svg", ".gif"):
        if path.lower().endswith(ext):
            return ext
    return ".img"


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="download-biocstickers",
        description="Download sticker images referenced by open GitHub BiocStickers README tabs.",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=Path("stickers_downloaded"),
        help="Output directory (default: stickers_downloaded/)",
    )
    ap.add_argument(
        "--tabs-file",
        type=Path,
        default=None,
        help="Optional file containing one URL per line. If omitted, reads from stdin.",
    )
    ap.add_argument(
        "--only",
        default="Bioconductor/BiocStickers",
        help='Filter: only process blob URLs from this repo "owner/repo" (default: Bioconductor/BiocStickers).',
    )
    ap.add_argument(
        "--max-per-readme",
        type=int,
        default=6,
        help="Safety cap: max images to download per README (default: 10).",
    )
    ap.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="HTTP timeout seconds (default: 30).",
    )
    args = ap.parse_args()

    text = args.tabs_file.read_text(encoding="utf-8", errors="replace") if args.tabs_file else sys.stdin.read()
    urls = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not urls:
        print("No URLs provided.", file=sys.stderr)
        return 2

    only_owner, only_repo = args.only.split("/", 1)

    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})

    processed = 0
    downloaded = 0

    for u in urls:
        blob = parse_github_blob_url(u)
        if not blob:
            continue
        if (blob.owner, blob.repo) != (only_owner, only_repo):
            continue
        if not blob.path.lower().endswith("readme.md"):
            continue

        # Get raw README
        readme_raw = raw_url(blob.owner, blob.repo, blob.branch, blob.path)
        try:
            r = session.get(readme_raw, timeout=args.timeout)
            r.raise_for_status()
        except Exception as e:
            print(f"[skip] README fetch failed: {u}\n       {e}", file=sys.stderr)
            continue

        md = r.text
        img_refs = extract_image_urls_from_markdown(md)
        if not img_refs:
            print(f"[info] No images found in: {blob.path}")
            processed += 1
            continue

        # Convert refs to direct URLs
        img_urls: list[str] = []
        for ref in img_refs:
            real = absolutize_and_rawify(ref, blob)
            if real:
                img_urls.append(real)

        # Heuristic: prefer images that look like stickers
        # (BiocStickers typically has at least one PNG/SVG in folder)
        img_urls_sorted = sorted(
            img_urls,
            key=lambda x: (0 if any(x.lower().endswith(ext) for ext in (".png", ".svg")) else 1, len(x)),
        )

        # download up to cap
        pkg_dir = blob.path.split("/", 1)[0]  # e.g. "RUVSeq"
        out_dir = args.out / safe_filename(pkg_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        taken = 0
        for img_u in img_urls_sorted:
            if taken >= args.max_per_readme:
                break
            ext = guess_ext_from_url(img_u)
            fname = safe_filename(Path(urlparse(img_u).path).name) or f"image_{taken}{ext}"
            if not fname.lower().endswith(ext):
                fname += ext
            out_path = out_dir / fname
            if out_path.exists():
                continue
            try:
                download(img_u, out_path, timeout=args.timeout)
                print(f"[ok] {pkg_dir}: {img_u} -> {out_path}")
                downloaded += 1
                taken += 1
            except Exception as e:
                print(f"[warn] download failed: {img_u}\n       {e}", file=sys.stderr)

        processed += 1

    print(f"\nDone. Processed READMEs: {processed}. Downloaded files: {downloaded}. Output: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

