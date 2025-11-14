from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import List, Dict, Any

from transformers import (
    pipeline,
    AutoTokenizer,
    AutoModelForTokenClassification,
)

from config import get_settings

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
