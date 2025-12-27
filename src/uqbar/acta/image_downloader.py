# SPDX-License-Identifier: MIT
# uqbar/acta/image_downloader.py
"""
Acta Diurna | Image Downloader
==============================

Lightweight "best search query" builder from multiple titles.


brew install wget


Goals:
- Normalize + tokenize (+ lemmatize if spaCy is available)
- Remove stopwords / low-information glue words
- Prefer consensus terms across titles (document frequency)
- Prefer informative tokens (IDs, hyphenated codes, ALLCAPS, digit+letters)
- Prefer frequent multi-word phrases (2–3 grams) as quoted anchors
- Emit two queries: precision (quotes) + recall (broader)

Install (recommended):
  python -m pip install -U spacy scikit-learn
  python -m spacy download en_core_web_sm

If spaCy/model isn't available, it will fallback to a decent regex tokenizer.

Overview
--------
Find near-duplicate images in a directory using imagededup's CNN method.

Metadata
--------
- Project: Acta diurna
- License: MIT
"""

# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import subprocess
from typing import Iterable, Sequence
import unicodedata

import spacy
from spacy.language import Language
from sklearn.feature_extraction.text import TfidfVectorizer

from acta.utils import QueryConfig, Trend, TrendList
from acta.image_scaper import get_image_links
from acta.image_processor import (
    clean_name,
    image_dedup,
    clean_convert_path_image_names,
)


# -------------------------------------------------------------------------------------
# Constants
# -------------------------------------------------------------------------------------
GENERIC_PENALTY_WORDS: set[str] = {
    # common "researchy" low-signal words
    "toward",
    "towards",
    "however",
    "nevertheless",
    "nonetheless",
    "thus",
    "conversely" "therefore",
    "whereas",
}

DEFAULT_STOPWORDS_FALLBACK: set[str] = {
    # tiny fallback list (spaCy is much better if available)
    "the",
    "a",
    "an",
    "and",
    "or",
    "but",
    "of",
    "to",
    "in",
    "on",
    "at",
    "for",
    "from",
    "by",
    "with",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "as",
    "that",
    "this",
    "these",
    "those",
    "it",
    "its",
    "their",
    "there",
    "here",
    "we",
    "you",
    "i",
    "they",
    "them",
    "our",
    "your",
}


# --------------------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------------------
def _download_path(download_url: str, output_path: Path) -> Path | tuple(str, str):
    """
    Downloads the argument path.

    GNU Wget 1.25.0, a non-interactive network retriever.
    Usage: wget [OPTION]... [URL]...

    Mandatory arguments to long options are mandatory for short options too.

    Startup:
      -V,  --version                   display the version of Wget and exit
      -h,  --help                      print this help
      -b,  --background                go to background after startup
      -e,  --execute=COMMAND           execute a `.wgetrc'-style command

    Logging and input file:
      -o,  --output-file=FILE          log messages to FILE
      -a,  --append-output=FILE        append messages to FILE
      -d,  --debug                     print lots of debugging information
      -q,  --quiet                     quiet (no output)
      -v,  --verbose                   be verbose (this is the default)
      -nv, --no-verbose                turn off verboseness, without being quiet
           --report-speed=TYPE         output bandwidth as TYPE.  TYPE can be bits
      -i,  --input-file=FILE           download URLs found in local or external FILE
      -F,  --force-html                treat input file as HTML
      -B,  --base=URL                  resolves HTML input-file links (-i -F)
                                         relative to URL
           --config=FILE               specify config file to use
           --no-config                 do not read any config file
           --rejected-log=FILE         log reasons for URL rejection to FILE

    Download:
      -t,  --tries=NUMBER              set number of retries to NUMBER (0 unlimits)
           --retry-connrefused         retry even if connection is refused
           --retry-on-host-error       consider host errors as non-fatal, transient errors
           --retry-on-http-error=ERRORS    comma-separated list of HTTP errors to retry
      -O,  --output-document=FILE      write documents to FILE
      -nc, --no-clobber                skip downloads that would download to
                                         existing files (overwriting them)
           --no-netrc                  don't try to obtain credentials from .netrc
      -c,  --continue                  resume getting a partially-downloaded file
           --start-pos=OFFSET          start downloading from zero-based position OFFSET
           --progress=TYPE             select progress gauge type
           --show-progress             display the progress bar in any verbosity mode
      -N,  --timestamping              don't re-retrieve files unless newer than
                                         local
           --no-if-modified-since      don't use conditional if-modified-since get
                                         requests in timestamping mode
           --no-use-server-timestamps  don't set the local file's timestamp by
                                         the one on the server
      -S,  --server-response           print server response
           --spider                    don't download anything
      -T,  --timeout=SECONDS           set all timeout values to SECONDS
           --dns-timeout=SECS          set the DNS lookup timeout to SECS
           --connect-timeout=SECS      set the connect timeout to SECS
           --read-timeout=SECS         set the read timeout to SECS
      -w,  --wait=SECONDS              wait SECONDS between retrievals
                                         (applies if more then 1 URL is to be retrieved)
           --waitretry=SECONDS         wait 1..SECONDS between retries of a retrieval
                                         (applies if more then 1 URL is to be retrieved)
           --random-wait               wait from 0.5*WAIT...1.5*WAIT secs between retrievals
                                         (applies if more then 1 URL is to be retrieved)
           --no-proxy                  explicitly turn off proxy
      -Q,  --quota=NUMBER              set retrieval quota to NUMBER
           --bind-address=ADDRESS      bind to ADDRESS (hostname or IP) on local host
           --limit-rate=RATE           limit download rate to RATE
           --no-dns-cache              disable caching DNS lookups
           --restrict-file-names=OS    restrict chars in file names to ones OS allows
           --ignore-case               ignore case when matching files/directories
      -4,  --inet4-only                connect only to IPv4 addresses
      -6,  --inet6-only                connect only to IPv6 addresses
           --prefer-family=FAMILY      connect first to addresses of specified family,
                                         one of IPv6, IPv4, or none
           --user=USER                 set both ftp and http user to USER
           --password=PASS             set both ftp and http password to PASS
           --ask-password              prompt for passwords
           --use-askpass=COMMAND       specify credential handler for requesting
                                         username and password.  If no COMMAND is
                                         specified the WGET_ASKPASS or the SSH_ASKPASS
                                         environment variable is used.
           --no-iri                    turn off IRI support
           --local-encoding=ENC        use ENC as the local encoding for IRIs
           --remote-encoding=ENC       use ENC as the default remote encoding
           --unlink                    remove file before clobber
           --xattr                     turn on storage of metadata in extended file attributes

    Directories:
      -nd, --no-directories            don't create directories
      -x,  --force-directories         force creation of directories
      -nH, --no-host-directories       don't create host directories
           --protocol-directories      use protocol name in directories
      -P,  --directory-prefix=PREFIX   save files to PREFIX/..
           --cut-dirs=NUMBER           ignore NUMBER remote directory components

    HTTP options:
           --http-user=USER            set http user to USER
           --http-password=PASS        set http password to PASS
           --no-cache                  disallow server-cached data
           --default-page=NAME         change the default page name (normally
                                         this is 'index.html'.)
      -E,  --adjust-extension          save HTML/CSS documents with proper extensions
           --ignore-length             ignore 'Content-Length' header field
           --header=STRING             insert STRING among the headers
           --compression=TYPE          choose compression, one of auto, gzip and none. (default: none)
           --max-redirect              maximum redirections allowed per page
           --proxy-user=USER           set USER as proxy username
           --proxy-password=PASS       set PASS as proxy password
           --referer=URL               include 'Referer: URL' header in HTTP request
           --save-headers              save the HTTP headers to file
      -U,  --user-agent=AGENT          identify as AGENT instead of Wget/VERSION
           --no-http-keep-alive        disable HTTP keep-alive (persistent connections)
           --no-cookies                don't use cookies
           --load-cookies=FILE         load cookies from FILE before session
           --save-cookies=FILE         save cookies to FILE after session
           --keep-session-cookies      load and save session (non-permanent) cookies
           --post-data=STRING          use the POST method; send STRING as the data
           --post-file=FILE            use the POST method; send contents of FILE
           --method=HTTPMethod         use method "HTTPMethod" in the request
           --body-data=STRING          send STRING as data. --method MUST be set
           --body-file=FILE            send contents of FILE. --method MUST be set
           --content-disposition       honor the Content-Disposition header when
                                         choosing local file names (EXPERIMENTAL)
           --content-on-error          output the received content on server errors
           --auth-no-challenge         send Basic HTTP authentication information
                                         without first waiting for the server's
                                         challenge

    HTTPS (SSL/TLS) options:
           --secure-protocol=PR        choose secure protocol, one of auto, SSLv2,
                                         SSLv3, TLSv1, TLSv1_1, TLSv1_2, TLSv1_3 and PFS
           --https-only                only follow secure HTTPS links
           --no-check-certificate      don't validate the server's certificate
           --certificate=FILE          client certificate file
           --certificate-type=TYPE     client certificate type, PEM or DER
           --private-key=FILE          private key file
           --private-key-type=TYPE     private key type, PEM or DER
           --ca-certificate=FILE       file with the bundle of CAs
           --ca-directory=DIR          directory where hash list of CAs is stored
           --crl-file=FILE             file with bundle of CRLs
           --pinnedpubkey=FILE/HASHES  Public key (PEM/DER) file, or any number
                                       of base64 encoded sha256 hashes preceded by
                                       'sha256//' and separated by ';', to verify
                                       peer against
           --random-file=FILE          file with random data for seeding the SSL PRNG

           --ciphers=STR           Set the priority string (GnuTLS) or cipher list string (OpenSSL) directly.
                                       Use with care. This option overrides --secure-protocol.
                                       The format and syntax of this string depend on the specific SSL/TLS engine.
    HSTS options:
           --no-hsts                   disable HSTS
           --hsts-file                 path of HSTS database (will override default)

    FTP options:
           --ftp-user=USER             set ftp user to USER
           --ftp-password=PASS         set ftp password to PASS
           --no-remove-listing         don't remove '.listing' files
           --no-glob                   turn off FTP file name globbing
           --no-passive-ftp            disable the "passive" transfer mode
           --preserve-permissions      preserve remote file permissions
           --retr-symlinks             when recursing, get linked-to files (not dir)

    FTPS options:
           --ftps-implicit                 use implicit FTPS (default port is 990)
           --ftps-resume-ssl               resume the SSL/TLS session started in the control connection when
                                             opening a data connection
           --ftps-clear-data-connection    cipher the control channel only; all the data will be in plaintext
           --ftps-fallback-to-ftp          fall back to FTP if FTPS is not supported in the target server
    WARC options:
           --warc-file=FILENAME        save request/response data to a .warc.gz file
           --warc-header=STRING        insert STRING into the warcinfo record
           --warc-max-size=NUMBER      set maximum size of WARC files to NUMBER
           --warc-cdx                  write CDX index files
           --warc-dedup=FILENAME       do not store records listed in this CDX file
           --no-warc-compression       do not compress WARC files with GZIP
           --no-warc-digests           do not calculate SHA1 digests
           --no-warc-keep-log          do not store the log file in a WARC record
           --warc-tempdir=DIRECTORY    location for temporary files created by the
                                         WARC writer

    Recursive download:
      -r,  --recursive                 specify recursive download
      -l,  --level=NUMBER              maximum recursion depth (inf or 0 for infinite)
           --delete-after              delete files locally after downloading them
      -k,  --convert-links             make links in downloaded HTML or CSS point to
                                         local files
           --convert-file-only         convert the file part of the URLs only (usually known as the basename)
           --backups=N                 before writing file X, rotate up to N backup files
      -K,  --backup-converted          before converting file X, back up as X.orig
      -m,  --mirror                    shortcut for -N -r -l inf --no-remove-listing
      -p,  --page-requisites           get all images, etc. needed to display HTML page
           --strict-comments           turn on strict (SGML) handling of HTML comments

    Recursive accept/reject:
      -A,  --accept=LIST               comma-separated list of accepted extensions
      -R,  --reject=LIST               comma-separated list of rejected extensions
           --accept-regex=REGEX        regex matching accepted URLs
           --reject-regex=REGEX        regex matching rejected URLs
           --regex-type=TYPE           regex type (posix)
      -D,  --domains=LIST              comma-separated list of accepted domains
           --exclude-domains=LIST      comma-separated list of rejected domains
           --follow-ftp                follow FTP links from HTML documents
           --follow-tags=LIST          comma-separated list of followed HTML tags
           --ignore-tags=LIST          comma-separated list of ignored HTML tags
      -H,  --span-hosts                go to foreign hosts when recursive
      -L,  --relative                  follow relative links only
      -I,  --include-directories=LIST  list of allowed directories
           --trust-server-names        use the name specified by the redirection
                                         URL's last component
      -X,  --exclude-directories=LIST  list of excluded directories
      -np, --no-parent                 don't ascend to the parent directory

    Email bug reports, questions, discussions to <bug-wget@gnu.org>
    and/or open issues at

    Notes
    -----
    - Does not rely on shell aliases.
    - Avoids shell redirection; writes output via Python.
    """
    if not path.exists():
        print(f"Download path does not exist: {path}.")

    command: list[str] = (
        [  # --no-clobber --page-requisites --convert-links --adjust-extension
            "wget",
            "-c",
            "--tries=10",
            "-T",
            "10" "--span-hosts",
            (
                "--user-agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit"
                "/537.36 (KHTML, like Gecko) Chrome/143.0.7499.169 Safari/537.36'"
            ),
            "-P",
            str(output_path),
            str(download_url),
        ]
    )
    result = subprocess.run(command, capture_output=True, text=True, check=True)

    download_path = output_path / str(download_url.split("/")[-1].strip())
    download_path.resolve()

    if download_path.exists():
        return download_path
    else:
        return result.stdout, result.stderr


def _normalize_text(s: str, cfg: QueryConfig) -> str:
    s = s.strip()
    s = unicodedata.normalize("NFKC", s)
    if cfg.ascii_only:
        s = unicodedata.normalize("NFKD", s)
        s = "".join(ch for ch in s if not unicodedata.combining(ch))
    # normalize whitespace
    s = re.sub(r"\s+", " ", s)
    return s


def _load_spacy() -> "Language | None":
    if spacy is None:
        return None
    try:
        return spacy.load("en_core_web_sm", disable=["parser"])  # keep tagger+ner
    except Exception:
        try:
            # if model missing, still allow blank tokenizer
            return spacy.blank("en")
        except Exception:
            return None


def _looks_informative(tok: str) -> bool:
    # bonus if looks like an ID/code: contains digits, is ALLCAPS, has hyphen/underscore,
    # or is alnum mixed.
    if any(ch.isdigit() for ch in tok):
        return True
    if tok.isupper() and len(tok) >= 2:
        return True
    if "-" in tok or "_" in tok:
        return True
    if re.search(r"[A-Za-z]\d|\d[A-Za-z]", tok):
        return True
    return False


def _regex_tokenize(text: str, cfg: QueryConfig) -> list[str]:
    # keep hyphenated codes, alphanumerics; optionally keep unicode letters
    if cfg.keep_unicode_letters:
        # \w is unicode-aware; but includes underscore. We'll post-filter.
        raw = re.findall(r"[0-9A-Za-z_\-]+", text)
    else:
        raw = re.findall(r"[0-9A-Za-z_\-]+", text)

    toks = []
    for t in raw:
        t = t.strip("-_")
        if len(t) < cfg.min_token_len:
            continue
        toks.append(t)
    return toks


def _tokenize_titles(
    titles: Sequence[str],
    cfg: QueryConfig,
) -> tuple[list[list[str]], set[str]]:
    """
    Returns:
      docs_tokens: list of token lists per title
      stopwords: chosen stopword set
    """
    nlp = _load_spacy()
    docs_tokens: list[list[str]] = []

    if nlp is not None and spacy is not None:
        # best stopwords: spaCy's
        stopwords = set(getattr(nlp, "Defaults", type("D", (), {"stop_words": set()})).stop_words)  # type: ignore
        if not stopwords:
            stopwords = set(DEFAULT_STOPWORDS_FALLBACK)

        for t in titles:
            t_norm = _normalize_text(t, cfg)
            doc = nlp(t_norm)
            toks: list[str] = []
            for tok in doc:
                if tok.is_space or tok.is_punct:
                    continue
                # lemma is best for search-query normalization
                lemma = tok.lemma_.strip()
                if not lemma:
                    continue
                lemma_low = lemma.lower()
                if lemma_low in stopwords:
                    continue
                if len(lemma_low) < cfg.min_token_len:
                    continue
                # drop pure underscores etc
                if re.fullmatch(r"[_\-]+", lemma_low):
                    continue
                toks.append(lemma_low)
            # fallback if blank model produced weird lemmas
            if not toks:
                toks = [
                    x.lower()
                    for x in _regex_tokenize(t_norm, cfg)
                    if x.lower() not in stopwords
                ]
            docs_tokens.append(toks)

        return docs_tokens, stopwords

    # fallback: regex tokenization + small stopword list
    stopwords = set(DEFAULT_STOPWORDS_FALLBACK)
    for t in titles:
        t_norm = _normalize_text(t, cfg)
        toks = [
            x.lower()
            for x in _regex_tokenize(t_norm, cfg)
            if x.lower() not in stopwords
        ]
        docs_tokens.append(toks)
    return docs_tokens, stopwords


def _score_tokens(docs_tokens: list[list[str]]) -> dict[str, float]:
    """
    Token score = (doc frequency ratio) + informativeness bonus - generic penalty
    """
    n_docs = len(docs_tokens)
    df: dict[str, int] = {}
    tf: dict[str, int] = {}

    for toks in docs_tokens:
        seen = set()
        for tok in toks:
            tf[tok] = tf.get(tok, 0) + 1
            if tok not in seen:
                df[tok] = df.get(tok, 0) + 1
                seen.add(tok)

    scores: dict[str, float] = {}
    for tok, dfi in df.items():
        df_ratio = dfi / max(1, n_docs)
        base = df_ratio

        # bonus for informative-looking tokens
        bonus = 0.30 if _looks_informative(tok) else 0.0

        # mild bonus for appearing many times overall (within titles)
        bonus += min(0.20, 0.02 * tf.get(tok, 0))

        # penalty for generic research words
        penalty = 0.30 if tok in GENERIC_PENALTY_WORDS else 0.0

        scores[tok] = base + bonus - penalty

    return scores


def _extract_phrases_tfidf(
    titles: Sequence[str],
    stopwords: set[str],
    cfg: QueryConfig,
) -> list[tuple[str, float]]:
    """
    Uses TF-IDF over 2–3-grams of the titles to find good quoted anchors.
    """
    # Vectorizer tokenization: keep words/codes/hyphens; lowercase
    token_pat = r"(?u)\b[0-9A-Za-z][0-9A-Za-z_\-]+\b"
    vect = TfidfVectorizer(
        lowercase=True,
        stop_words=list(stopwords),
        ngram_range=cfg.phrase_ngram_range,
        token_pattern=token_pat,
    )
    X = vect.fit_transform(titles)
    feats = vect.get_feature_names_out()
    # score phrases by max TF-IDF across titles
    scores = X.max(axis=0).A1  # type: ignore[attr-defined]

    pairs = [
        (feats[i], float(scores[i]))
        for i in range(len(feats))
        if scores[i] >= cfg.phrase_min_score
    ]
    pairs.sort(key=lambda x: x[1], reverse=True)

    # prune phrases that are mostly generic
    cleaned: list[tuple[str, float]] = []
    for phr, sc in pairs:
        words = phr.split()
        if all(w in GENERIC_PENALTY_WORDS for w in words):
            continue
        cleaned.append((phr, sc))
    return cleaned


# --------------------------------------------------------------------------------------
# Functions
# --------------------------------------------------------------------------------------
def build_search_queries(
    titles: Sequence[str],
    *,
    cfg: QueryConfig = QueryConfig(),
) -> dict[str, object]:
    """
    Placeholder
    """

    if not titles:
        raise ValueError("titles must be a non-empty list of strings")

    titles_norm = [_normalize_text(t, cfg) for t in titles]
    docs_tokens, stopwords = _tokenize_titles(titles_norm, cfg)

    token_scores = _score_tokens(docs_tokens)
    top_tokens = sorted(token_scores.items(), key=lambda kv: kv[1], reverse=True)
    top_tokens = [t for t, _ in top_tokens if len(t) >= cfg.min_token_len][
        : cfg.max_keywords
    ]

    phrase_scores = _extract_phrases_tfidf(titles_norm, stopwords, cfg)
    top_phrases = [p for p, _ in phrase_scores[: cfg.max_phrases]]

    # Precision query: quote phrases + add top tokens (excluding phrase words)
    phrase_words = set(w for p in top_phrases for w in p.split())
    precision_tokens = [t for t in top_tokens if t not in phrase_words][
        : cfg.max_keywords
    ]

    query_precision = "+".join(
        [f'"{p}"' for p in top_phrases] + precision_tokens
    ).strip()

    # Recall query: no quotes, include more tokens + unquoted phrases (as words)
    recall_words = []
    for p in top_phrases:
        recall_words.extend(p.split())
    # merge + deduplicate preserving order
    seen = set()
    recall_seq = []
    for w in recall_words + top_tokens:
        if w not in seen:
            recall_seq.append(w)
            seen.add(w)
    query_recall = "+".join(recall_seq[: max(cfg.max_keywords, 14)]).strip()

    query_stats = {
        "query_precision": query_precision,
        "query_recall": query_recall,
        "top_phrases": phrase_scores[:10],
        "top_tokens": [(t, token_scores[t]) for t in top_tokens[:20]],
    }

    return query_stats


def download_images(trend_list: TrendList) -> None:

    # Check image directory
    if not image_root_path.is_dir():
        raise SystemExit(f"Not a directory: {image_root_path}")

    for trend in trend_list:

        # 1. Create trend list
        news_item_title_list: list[str] = [
            trend.news_item_title_1,
            trend.news_item_title_2,
            trend.news_item_title_3,
        ]

        # 2. Build search query based on trends
        trend.query_stats: dict[str, object] = build_search_queries(
            titles=news_item_title_list,
        )

        # 3. Get query
        image_query = trend.query_stats.get("query_precision", None)
        if not image_query:
            image_query = trend.query_stats.get("query_recall", None)
        if not image_query:
            return

        # 4. Get links via image scraper
        image_link_list: list[str] = get_image_links(image_query)

        if not image_link_list:
            return

        # 5. Download each image
        image_path: Path = trend.image_path
        for image_link in image_link_list:

            dpath = _download_path(download_url=image_link, output_path=image_path)

            if isinstance(dpath, tuple):
                print(dpath)
                continue

            new_file_name = Path(clean_name(str(dpath))).resolve()

            if not new_file_name.exists():
                print("File does not exist.")
                continue

        # 6. Clean and convert all files to png format with image processor
        clean_convert_path_image_names(input_path=image_path)

        # 7. Deduplicate images with image processor
        image_dedup(image_root_path=image_path)

    return None


# --------------------------------------------------------------------------------------
# Exports
# --------------------------------------------------------------------------------------
__all__: list[str] = [
    "build_search_queries",
    "download_images",
]

# -------------------------------------------------------------------------------------
# Test | python -m uqbar.acta.image_downloader > out.txt 2>&1
# -------------------------------------------------------------------------------------
# if __name__ == "__main__":
#     demo_titles = [
#         "How do you sync docs and in-app content for better support?",
#         "Connecting documentation and in-product help content (APIs vs manual sync)",
#         "Best way to keep user docs and app UI help in sync",
#         "Docs + in-app answers: syncing knowledge base with product content",
#     ]
#     out = build_search_queries(demo_titles)
#     print("Precision:", out["query_precision"])
#     print("Recall:   ", out["query_recall"])
#     print("\nTop phrases:", out["top_phrases"][:5])
#     print("Top tokens: ", out["top_tokens"][:10])
