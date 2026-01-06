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

import re
import unicodedata
from collections.abc import Sequence
from pathlib import Path

import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from spacy.language import Language

from uqbar.acta.image_processor import (
    clean_convert_path_image_names,
    clean_name,
    image_dedup,
)
from uqbar.acta.image_scaper import get_image_links
from uqbar.acta.utils import QueryConfig, TrendList

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
def _normalize_text(s: str, cfg: QueryConfig) -> str:
    s = s.strip()
    s = unicodedata.normalize("NFKC", s)
    if cfg.ascii_only:
        s = unicodedata.normalize("NFKD", s)
        s = "".join(ch for ch in s if not unicodedata.combining(ch))
    # normalize whitespace
    s = re.sub(r"\s+", " ", s)
    return s


def _load_spacy() -> Language | None:
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
