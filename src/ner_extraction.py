from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import List, Dict, Any, Optional, Tuple
import re

from transformers import (
    pipeline,
    AutoTokenizer,
    AutoModelForTokenClassification,
)

from .config import get_settings

settings = get_settings()


@dataclass
class Entity:
    label: str
    text: str
    start: int
    end: int
    normalized: Any


@lru_cache(maxsize=1)
def _get_ner_pipeline():
    tokenizer = AutoTokenizer.from_pretrained(settings.ner_model_name)
    tokenizer.model_max_length = 512

    model = AutoModelForTokenClassification.from_pretrained(
        settings.ner_model_name
    )

    return pipeline(
        "token-classification",
        model=model,
        tokenizer=tokenizer,
        aggregation_strategy="simple",
    )


def _normalize_value(label: str, text: str) -> Any:
    if label == "MONEY":
        cleaned = text.replace(",", "").replace("€", "").replace("$", "").strip()
        parts = cleaned.split()
        try:
            value = float(parts[0])
            currency = parts[1] if len(parts) > 1 else None
            return {"amount": value, "currency": currency}
        except Exception:
            return {"raw": text}
    return text


def extract_entities_for_text(text: str) -> List[Entity]:
    """
    Apply NER model to the given text and extract MONEY, DATE, DURATION entities.
    :param text:
    :return:
    """
    ner = _get_ner_pipeline()
    raw = ner(
        text,
    )
    entities: List[Entity] = []
    for r in raw:
        label = r.get("entity_group") or r.get("entity")
        if label not in {"MONEY", "DATE", "DURATION"}:
            continue
        ent = Entity(
            label=label,
            text=r["word"],
            start=int(r["start"]),
            end=int(r["end"]),
            normalized=_normalize_value(label, r["word"]),
        )
        entities.append(ent)
    return entities


def _find_keywords(window: str, patterns: List[re.Pattern]) -> bool:
    lw = window.lower()
    return any(p.search(lw) for p in patterns)


OPENING_PATTERNS = [
    re.compile(r"opening\s+balance"),
    re.compile(r"minimum\s+(deposit|amount|balance)"),
    re.compile(r"initial\s+(deposit|amount)"),
    re.compile(r"start(?:ing)?\s+from"),
    re.compile(r"open(?:ing)?\s+deposit"),
]

FEE_PATTERNS = [
    re.compile(r"fee[s]?"),
    re.compile(r"charge[s]?"),
    re.compile(r"commission[s]?"),
    re.compile(r"maintenance\s+fee"),
    re.compile(r"monthly\s+fee"),
    re.compile(r"account\s+fee"),
]

TERM_PATTERNS = [
    re.compile(r"term[s]?"),
    re.compile(r"tenor"),
    re.compile(r"duration"),
    re.compile(r"period"),
    re.compile(r"available\s+until"),
    re.compile(r"valid\s+until"),
]


def answer_simple_questions_for_chunks(
    chunks: List[Any],
    context_window: int = 60,
) -> Dict[str, Any]:
    """
    Given a set of chunks (with .text), answer:
      - opening_balance: MONEY near opening/minimum/initial keywords
      - available_terms: list of DURATION/DATE near term/valid-until words
      - fees: list of MONEY near fee/charge/commission words
    Returns dict with keys: opening_balance (dict|str|None), available_terms (list[str]), fees (list[dict|str]).
    """
    opening_candidates: List[Tuple[float, Any]] = []
    fees_list: List[Any] = []
    terms_set: List[str] = []

    for ch in chunks:
        text = ch.text or ""
        ents = extract_entities_for_text(text)
        for e in ents:
            # get local context around entity
            left = max(0, e.start - context_window)
            right = min(len(text), e.end + context_window)
            window = text[left:right]

            if e.label == "MONEY":
                # Opening balance?
                if _find_keywords(window, OPENING_PATTERNS):
                    norm = e.normalized
                    if isinstance(norm, dict) and "amount" in norm:
                        try:
                            opening_candidates.append((float(norm["amount"]), norm))
                        except Exception:
                            opening_candidates.append((float("inf"), norm))
                    else:
                        opening_candidates.append((float("inf"), norm))
                # Fees?
                if _find_keywords(window, FEE_PATTERNS):
                    fees_list.append(e.normalized)

            elif e.label in {"DATE", "DURATION"}:
                if _find_keywords(window, TERM_PATTERNS):
                    # Prefer normalized string
                    terms_set.append(str(e.normalized))

    # pick the smallest opening balance amount if available
    opening_balance: Optional[Any] = None
    if opening_candidates:
        opening_candidates.sort(key=lambda t: t[0])
        opening_balance = opening_candidates[0][1]

    # de-duplicate simple items while preserving order
    def _dedupe(seq: List[Any]) -> List[Any]:
        seen = set()
        out = []
        for x in seq:
            key = str(x)
            if key in seen:
                continue
            seen.add(key)
            out.append(x)
        return out

    return {
        "opening_balance": opening_balance,
        "available_terms": _dedupe(terms_set),
        "fees": _dedupe(fees_list),
    }


def extract_entities_for_chunks(
    chunks: List[Any],
) -> Dict[int, List[Entity]]:
    """
    chunks: list of ORM DocumentChunk instances (must have id, text).
    Returns mapping: chunk_id -> [Entity, ...]
    """
    result: Dict[int, List[Entity]] = {}
    for c in chunks:
        ents = extract_entities_for_text(c.text)
        result[c.id] = ents
    return result
