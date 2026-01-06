# SPDX-License-Identifier: MIT
# uqbar/acta/mood_predictor.py
"""
Acta Diurna | Mood Predictor
============================

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

import warnings
from dataclasses import asdict
from math import floor
from typing import Any

warnings.filterwarnings("ignore")


import numpy as np
from transformers import pipeline

from uqbar.acta.utils import GO_EMOTIONS_LABELS, NEWS_CATEGORIES, MoodItem, MoodLevel

# -------------------------------------------------------------------------------------
# Constants
# -------------------------------------------------------------------------------------
_S120: float = 1.20
_S110: float = 1.10
_S105: float = 1.05
_S100: float = 1.00
_S095: float = 0.95
_S090: float = 0.90
_S085: float = 0.85
_S080: float = 0.80
_S075: float = 0.75
_S070: float = 0.70
_S065: float = 0.65
_S060: float = 0.60
_S055: float = 0.55
_S050: float = 0.50
_S045: float = 0.45
_S040: float = 0.40
_S035: float = 0.35
_S030: float = 0.30
_S025: float = 0.25
_S020: float = 0.20
_S015: float = 0.15
_S010: float = 0.10


_POS: set[str] = {
    "joy",
    "love",
    "gratitude",
    "admiration",
    "approval",
    "optimism",
    "pride",
    "relief",
    "amusement",
    "excitement",
}
_NEG: set[str] = {
    "grief",
    "sadness",
    "remorse",
    "fear",
    "anger",
    "disgust",
    "disapproval",
    "annoyance",
    "disappointment",
    "nervousness",
}


# -------------------------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------------------------
def _floor_to_multiple(number: float, multiple: float = 0.5) -> float:
    return floor(number / multiple) * multiple


def _mlv(mood: float) -> MoodLevel:
    """
    Map a GoEmotions per-label score in [0, 1] to a 5-level bucket.

    These scores are best treated as "strength/confidence that this emotion is present",
    not calibrated probabilities.
    """
    if mood is None or not (mood == mood):  # NaN-safe
        return MoodLevel.VERY_LOW

    # Clamp if something weird slips through
    if mood < 0.0:
        mood = 0.0
    elif mood > 1.0:
        mood = 1.0

    if mood >= 0.60:
        return MoodLevel.VERY_HIGH
    if mood >= 0.35:
        return MoodLevel.HIGH
    if mood >= 0.20:
        return MoodLevel.AVERAGE
    if mood >= 0.10:
        return MoodLevel.LOW
    return MoodLevel.VERY_LOW


def _mhigh(mood: float, mood_level: MoodLevel | list[MoodLevel]) -> bool:
    """
    True if mood is "high enough".

    - If mood_level is a single MoodLevel: True iff _mlv(mood) in {HIGH, VERY_HIGH}.
      (Per your spec, the passed-in single value is ignored as a threshold.)
    - If mood_level is a list[MoodLevel]: compare _mlv(mood).value >= floored mean(level.value).
    """
    level_of_mood = _mlv(mood).value  # 1..5

    if isinstance(mood_level, MoodLevel):
        return level_of_mood >= MoodLevel.HIGH.value

    if not isinstance(mood_level, list) or len(mood_level) == 0:
        raise ValueError(
            "mood_level must be a MoodLevel or a non-empty list[MoodLevel]."
        )

    avg_level = sum(ml.value for ml in mood_level) / len(mood_level)
    threshold = _floor_to_multiple(avg_level, multiple=0.5)  # e.g., 3.5

    return level_of_mood >= threshold


def _predict_mood(
    input_text: str,
    *,
    model: str = "SamLowe/roberta-base-go_emotions",
    task: str = "text-classification",
    top_k: int | None = None,  # None => return all labels
    device: int | str | None = None,  # None => transformers auto (cpu/mps/cuda)
    batch_size: int = 32,  # unused for single text, kept for symmetry
    truncation: bool = True,
    max_length: int | None = None,
    padding: bool | str = False,
    return_all_scores_fallback: bool = True,  # if top_k None isn't supported in your version
    suppress_warnings: bool = True,
    suppress_transformers_logging: bool = True,
    _classifier: Any | None = None,  # inject a prebuilt pipeline if you want reuse
) -> MoodItem:
    """
    Classify a single text into GoEmotions labels and return a dense mapping:
        {label: score}

    Notes:
    - These "scores" are model outputs (often normalized per label set),
      useful for ranking/thresholding, but not a calibrated probability.
    - For your use case, you want a full vector across all labels.
    """
    if not isinstance(input_text, str) or not input_text.strip():
        raise ValueError("input_text must be a non-empty string.")

    if suppress_warnings:
        warnings.filterwarnings("ignore")

    if suppress_transformers_logging:
        # Quiet HF/transformers logging without touching your global logging config too much.
        try:
            from transformers.utils import logging as hf_logging

            hf_logging.set_verbosity_error()
        except Exception:
            pass

    # Build (or reuse) classifier
    classifier = _classifier
    if classifier is None:
        pipe_kwargs: dict[str, Any] = {"task": task, "model": model, "top_k": top_k}
        if device is not None:
            pipe_kwargs["device"] = device
        classifier = pipeline(**pipe_kwargs)

    # Run inference
    call_kwargs: dict[str, Any] = {
        "truncation": truncation,
        "padding": padding,
    }
    if max_length is not None:
        call_kwargs["max_length"] = max_length

    outputs = classifier(input_text, **call_kwargs)

    # transformers can return:
    # - if top_k=None: list[dict(label, score)] for the single input
    # - if top_k is int: list[dict] of size top_k
    # - in some versions, you may need return_all_scores=True to get all labels
    if isinstance(outputs, dict):
        # single dict => top-1 only; not what we want
        outputs = [outputs]

    # Fallback to return_all_scores if we didn't get a full distribution
    # (Some pipeline versions behave differently with top_k=None)
    got_many = (
        isinstance(outputs, list)
        and outputs
        and isinstance(outputs[0], dict)
        and len(outputs) > 1
    )
    if not got_many and return_all_scores_fallback:
        outputs = classifier(
            input_text,
            return_all_scores=True,
            **call_kwargs,
        )
        # return_all_scores=True typically returns list[list[dict]] even for single input
        if isinstance(outputs, list) and outputs and isinstance(outputs[0], list):
            outputs = outputs[0]

    # Convert sparse list-of-dicts -> dense vector like your y_probas_all row
    y = np.zeros(len(GO_EMOTIONS_LABELS), dtype=float)
    label_to_idx = {lab: i for i, lab in enumerate(GO_EMOTIONS_LABELS)}

    for item in outputs:
        lab = item.get("label")
        score = float(item.get("score", 0.0))
        if lab in label_to_idx:
            y[label_to_idx[lab]] = score

    return MoodItem(**{lab: float(y[i]) for i, lab in enumerate(GO_EMOTIONS_LABELS)})


def _score_heuristics(
    admiration: float,
    amusement: float,
    anger: float,
    annoyance: float,
    approval: float,
    caring: float,
    confusion: float,
    curiosity: float,
    desire: float,
    disappointment: float,
    disapproval: float,
    disgust: float,
    embarrassment: float,
    excitement: float,
    fear: float,
    gratitude: float,
    grief: float,
    joy: float,
    love: float,
    nervousness: float,
    optimism: float,
    pride: float,
    realization: float,
    relief: float,
    remorse: float,
    sadness: float,
    surprise: float,
    neutral: float,
    valence: float,
    neutral_gate: float,
) -> dict[int, float]:

    scores: dict[int, float] = {}
    ambiguous = False  # placeholder

    # 1. Breaking News (High Alert/Surprise): surprise + nervousness/fear, but not deeply tragic
    scores[1] = (
        _S120 * surprise
        + _S050 * nervousness
        + _S035 * fear
        + _S025 * neutral
        - _S080 * grief
        - _S050 * sadness
    )

    # 2. Investigative (Deep Focus/Intrigue): curiosity + realization + neutral, low joy
    scores[2] = (
        _S110 * curiosity
        + _S060 * realization
        + _S050 * neutral
        + _S025 * confusion
        - _S035 * joy
        - _S020 * amusement
    )

    # 3. Political Reform (Diplomacy/Optimism): optimism + approval + pride + neutral, low anger
    scores[3] = (
        _S100 * optimism
        + _S070 * approval
        + _S045 * pride
        + _S035 * neutral
        - _S060 * anger
        - _S040 * disapproval
    )

    # 5. Economic Trends (Stability/Analytical): neutral + realization, low extremes
    scores[5] = (
        _S120 * neutral
        + _S055 * realization
        + _S025 * curiosity
        - _S035 * surprise
        - _S025 * joy
        - _S025 * anger
    )

    # 6. Environmental Crisis (Concern/Melancholy): sadness + fear + remorse + disappointment, some curiosity
    scores[6] = (
        _S095 * sadness
        + _S075 * fear
        + _S070 * remorse
        + _S055 * disappointment
        + _S025 * curiosity
        + _S010 * neutral
    )

    # 7. Scientific Breakthrough (Wonder/Curiosity): curiosity + surprise + admiration + joy/excitement
    scores[7] = (
        _S100 * curiosity
        + _S070 * surprise
        + _S065 * admiration
        + _S045 * excitement
        + _S035 * joy
        - _S025 * fear
    )

    # 8. Humanitarian Profile (Empathy/Resilience): caring + gratitude + admiration + optimism (+ a touch of sadness)
    scores[8] = (
        _S100 * caring
        + _S075 * gratitude
        + _S055 * admiration
        + _S045 * optimism
        + _S025 * sadness
        - _S030 * amusement
    )

    # 9. Social Justice & Rights (Tension/Conviction): anger + disapproval + annoyance (+ pride/optimism as conviction)
    scores[9] = (
        _S105 * anger
        + _S080 * disapproval
        + _S055 * annoyance
        + _S035 * pride
        + _S020 * optimism
        + _S010 * neutral
    )

    # 10. Technology & Future (Innovation/Pace): curiosity + excitement + optimism + neutral
    scores[10] = (
        _S095 * curiosity
        + _S075 * excitement
        + _S060 * optimism
        + _S035 * neutral
        + _S020 * surprise
        - _S025 * sadness
    )

    # 11. Health & Wellness (Reassurance/Care): caring + relief + optimism + neutral, low fear
    scores[11] = (
        _S100 * caring
        + _S085 * relief
        + _S060 * optimism
        + _S035 * neutral
        - _S060 * fear
    )

    # 12. Local Community (Neighborly/Familiar): neutral + approval + caring, low extremes
    scores[12] = (
        _S090 * neutral
        + _S055 * approval
        + _S045 * caring
        + _S020 * gratitude
        - _S035 * anger
        - _S025 * fear
    )

    # 13. Sports Commentary (Energy/Achievement): excitement + joy + pride + admiration
    scores[13] = (
        _S110 * excitement
        + _S085 * joy
        + _S070 * pride
        + _S045 * admiration
        - _S035 * sadness
    )

    # 14. Global Summits (Formal/Procedural): neutral + approval + realization (procedural), low surprise
    scores[14] = (
        _S105 * neutral
        + _S055 * approval
        + _S050 * realization
        + _S020 * curiosity
        - _S035 * surprise
    )

    # 15. Arts & Culture (Sophistication/Whimsy): admiration + amusement + surprise (+ joy)
    scores[15] = (
        _S090 * admiration
        + _S075 * amusement
        + _S055 * surprise
        + _S035 * joy
        + _S015 * curiosity
    )

    # 16. Crime & Justice (Judgment/Caution): fear + disgust + disapproval + anger
    scores[16] = (
        _S095 * fear
        + _S080 * disgust
        + _S070 * disapproval
        + _S065 * anger
        + _S020 * neutral
    )

    # 17. Education & Youth (Potential/Development): optimism + curiosity + approval (+ joy)
    scores[17] = (
        _S095 * optimism
        + _S075 * curiosity
        + _S060 * approval
        + _S040 * joy
        + _S020 * neutral
    )

    # 19. Weather & Nature (Movement/Awe): surprise + neutral + curiosity (sometimes fear lightly)
    scores[19] = _S095 * surprise + _S060 * neutral + _S055 * curiosity + _S025 * fear

    # 20. Opinion & Editorial (Dialogue/Persuasion): realization + (approval/disapproval) + neutral
    scores[20] = (
        _S090 * realization
        + _S045 * neutral
        + _S035 * approval
        + _S035 * disapproval
        + _S020 * curiosity
    )

    # --- Fallbacks ---
    # 21. Fallback 1 (Valence generalization): if emotion exists but category is ambiguous → +/- bed
    scores[21] = _S050 * abs(valence) + _S025 * (_S100 - neutral)

    # 22. Fallback 2 (Absolute neutrality): if neutral dominates or top categories too close → ultra-neutral
    scores[22] = _S110 * neutral + (_S025 if ambiguous else 0.0)

    # If neutral is high, bias toward analytic/procedural categories unless strong alternative exists
    if neutral >= neutral_gate:
        scores[5] += _S020
        scores[14] += _S020
        scores[2] += _S010
        scores[22] += _S020


def _softmax(list_of_items: list[float]) -> list[float]:
    arr = np.array(list_of_items, dtype=float)
    arr -= arr.max()  # numerical stability
    exp = np.exp(arr)
    return (exp / exp.sum()).tolist()


# -------------------------------------------------------------------------------------
# Functions
# -------------------------------------------------------------------------------------
def predict_mood(trend_list: TrendList) -> None:
    """
    Placeholder

    Example
    -------
    {
        "category_id": best_id,
        "category_name": category_name,
        "audio_brief": audio_brief,
        "scores": {k: float(v) for k, v in scores.items()},
        "top_emotions": top_emotions[:6],
        "notes": (
            f"neutral={neutral:.3f}, valence≈{valence:.3f}, ambiguous={ambiguous}. "
            f"best_score≈{best_score:.3f}"
        ),
    }
    """

    for trend in trend_list:

        # Get mood keywords
        mood_keywords: list[str] = trend.mood_prompt_response
        input_text = " ".join(mood_keywords)

        # Predict mood
        mood_scores: MoodItem = _predict_mood(input_text)
        list_of_scores: list[float] = mood_scores.as_list()

        # Create softmax mood_scores
        softmax_scores: list[float] = _softmax(list_of_scores)
        mood_scores.from_list(softmax_scores)

        # TODO: choose_news_music_style implementation
        # choose_news_music_style(mood_scores)
        trend.mood_scores = mood_scores

    return


def choose_news_music_style(
    mood: MoodItem,
    *,
    # knobs (keep them simple; you can tune later)
    high: MoodLevel = MoodLevel.HIGH,
    very_high: MoodLevel = MoodLevel.VERY_HIGH,
    neutral_gate: float = 0.30,  # if neutral >= this, bias toward analytical/procedural
    ambiguity_margin: float = 0.04,  # if top2 scores are close, prefer neutrality
) -> dict[str, Any]:
    """
    Returns:
      {
        "category_id": int,
        "category_name": str,
        "audio_brief": str,
        "scores": dict[int, float],        # per-category heuristic scores
        "top_emotions": list[tuple[str,float]],
        "notes": str
      }

    Assumes MoodItem fields are floats in [0,1] (multi-label style).
    """
    d = asdict(mood)
    def get(k):
        return float(d.get(k) or 0.0)

    # Convenience
    admiration = get("admiration")
    amusement = get("amusement")
    anger = get("anger")
    annoyance = get("annoyance")
    approval = get("approval")
    caring = get("caring")
    confusion = get("confusion")
    curiosity = get("curiosity")
    desire = get("desire")
    disappointment = get("disappointment")
    disapproval = get("disapproval")
    disgust = get("disgust")
    embarrassment = get("embarrassment")
    excitement = get("excitement")
    fear = get("fear")
    gratitude = get("gratitude")
    grief = get("grief")
    joy = get("joy")
    love = get("love")
    nervousness = get("nervousness")
    optimism = get("optimism")
    pride = get("pride")
    realization = get("realization")
    relief = get("relief")
    remorse = get("remorse")
    sadness = get("sadness")
    surprise = get("surprise")
    neutral = get("neutral")

    # Top emotions (useful for debugging / logging)
    top_emotions = sorted(
        ((k, float(v or 0.0)) for k, v in d.items()), key=lambda x: x[1], reverse=True
    )
    top2 = top_emotions[:2]
    ambiguous = (top2[0][1] - top2[1][1]) <= ambiguity_margin

    # Valence proxy for Fallback 1
    pos = sum(get(k) for k in _POS) / len(_POS)
    neg = sum(get(k) for k in _NEG) / len(_NEG)
    valence = pos - neg  # positive => upbeat-ish; negative => heavy-ish

    # Hard guards first (very “editorial policy”)
    # 18. Obituary / Tribute: grief OR (sadness+admiration/gratitude) dominates
    if _mlv(grief) in {very_high, high} or (
        _mlv(sadness) in {very_high, high} and (admiration + gratitude) >= 0.30
    ):
        return {
            "category_id": 18,
            "category_name": "Obituary or Tribute (Memory/Honor)",
            "audio_brief": "A singular, repeating cello note with a soft choral pad. Gracious, quiet, and final.",
            "scores": {},
            "top_emotions": top_emotions[:6],
            "notes": "Guard triggered: grief/sadness is high → obituary/tribute treatment.",
        }

    # 4. Conflict & Crisis: fear/anger + sadness/negative heaviness
    if (_mlv(fear) in {very_high, high} and _mlv(anger) in {very_high, high}) or (
        _mlv(fear) in {very_high, high} and sadness >= 0.25
    ):
        return {
            "category_id": 4,
            "category_name": "Conflict & Crisis (Solemnity/Grief)",
            "audio_brief": "Sustained, high-register strings with a deep, slow bass note. Mournful but dignifying.",
            "scores": {},
            "top_emotions": top_emotions[:6],
            "notes": "Guard triggered: fear/anger (and often sadness) indicates crisis coverage.",
        }

    # Heuristic scoring for the rest
    scores: dict[int, float] = _score_heuristics(
        admiration,
        amusement,
        anger,
        annoyance,
        approval,
        caring,
        confusion,
        curiosity,
        desire,
        disappointment,
        disapproval,
        disgust,
        embarrassment,
        excitement,
        fear,
        gratitude,
        grief,
        joy,
        love,
        nervousness,
        optimism,
        pride,
        realization,
        relief,
        remorse,
        sadness,
        surprise,
        neutral,
        valence,
        neutral_gate,
    )

    # Pick best category
    best_id = max(scores, key=lambda k: scores[k])
    best_score = scores[best_id]

    # If ambiguous among the top categories, prefer Absolute Neutrality (22) unless something is clearly emotional
    top_sorted = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    if (
        len(top_sorted) >= 2
        and (top_sorted[0][1] - top_sorted[1][1]) <= ambiguity_margin
    ):
        # if the text isn't strongly emotional, go ultra-neutral
        strong_emotion = any(
            _mlv(get(k)) in {very_high, high} for k in _NEG.union(_POS)
        )
        if not strong_emotion:
            best_id = 22

    # Category metadata
    category_name, audio_brief = NEWS_CATEGORIES.get(best_id, NEWS_CATEGORIES[22])

    return {
        "category_id": best_id,
        "category_name": category_name,
        "audio_brief": audio_brief,
        "scores": {k: float(v) for k, v in scores.items()},
        "top_emotions": top_emotions[:6],
        "notes": (
            f"neutral={neutral:.3f}, valence≈{valence:.3f}, ambiguous={ambiguous}. "
            f"best_score≈{best_score:.3f}"
        ),
    }


# --------------------------------------------------------------------------------------
# Exports
# --------------------------------------------------------------------------------------
__all__: list[str] = [
    "predict_mood",
    "choose_news_music_style",
    "_POS",
    "_NEG",
]


# -------------------------------------------------------------------------------------
# Test | python -m uqbar.acta.mood_predictor > out.txt 2>&1
# -------------------------------------------------------------------------------------
# if __name__ == "__main__":
#     ...
