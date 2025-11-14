from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any

from pydantic import BaseModel

from ner_extraction import Entity


class ProductCard(BaseModel):
    id: int | None = None
    pdf_path: str
    name: str
    type: str | None = None  # e.g. "deposit" / "credit"
    money: List[Any] = []
    dates: List[Any] = []
    durations: List[Any] = []
    chunk_ids: List[int] = []
    extra: Dict[str, Any] = {}


# You can tune this list for your PDFs (I added some Polish banking words too)
PRODUCT_KEYWORDS = [
    "deposit",
    "term deposit",
    "savings account",
    "current account",
    "account",
    "loan",
    "credit",
    "mortgage",
    "overdraft",
    "credit card",
    "card",
    "lokata",
    "konto",
    "rachunek",
    "kredyt",
    "pożyczka",
]

# How many consecutive “no-signal” chunks we still attach as context
MAX_SILENT_CONTEXT_CHUNKS = 3


def _guess_product_type(text_lower: str) -> str | None:
    if "deposit" in text_lower or "lokata" in text_lower or "savings" in text_lower:
        return "deposit"
    if (
        "loan" in text_lower
        or "credit" in text_lower
        or "kredyt" in text_lower
        or "pożyczka" in text_lower
        or "mortgage" in text_lower
    ):
        return "credit"
    return None


def _default_name_for_type(p_type: str | None) -> str:
    if p_type == "deposit":
        return "Deposit product"
    if p_type == "credit":
        return "Credit product"
    return "Banking product"


def _guess_product_name_from_text(text: str, fallback: str) -> str:
    """
    Take the first line (or sentence) as a potential product title.
    If it's too short / useless, fall back to a generic name.
    """
    cleaned = text.strip()
    if not cleaned:
        return fallback
    # split on newline first, then on period
    first_line = cleaned.split("\n", 1)[0]
    first_line = first_line.strip()
    if "." in first_line and len(first_line.split(".")) > 1:
        first_line = first_line.split(".", 1)[0].strip()

    # collapse whitespace
    first_line = " ".join(first_line.split())

    if len(first_line) < 10:
        return fallback

    # limit length so listing products is readable
    return first_line[:80]


def build_products_from_entities(
    pdf_path: str,
    chunks: List[Any],
    entities_by_chunk: Dict[int, List[Entity]],
) -> List[ProductCard]:
    """
    New strategy:
      - we walk through chunks in reading order
      - NER + keywords mark "signal" chunks
      - we start a product on a signal chunk and keep attaching nearby chunks
      - we allow a few 'silent' chunks with no signal as extra context
    """
    if not chunks:
        return []

    # Ensure deterministic order
    sorted_chunks = sorted(chunks, key=lambda c: (c.page, c.chunk_index))

    products: List[ProductCard] = []
    current: ProductCard | None = None
    silent_in_row = 0

    for ch in sorted_chunks:
        ents = entities_by_chunk.get(ch.id, []) or []
        money = [e.normalized for e in ents if e.label == "MONEY"]
        dates = [e.normalized for e in ents if e.label == "DATE"]
        durations = [e.normalized for e in ents if e.label == "DURATION"]

        text_lower = (ch.text or "").lower()
        has_kw = any(kw in text_lower for kw in PRODUCT_KEYWORDS)
        has_entities = bool(money or dates or durations)
        has_signal = has_kw or has_entities

        if current is None:
            # Not inside any product yet – start one only if we see a signal
            if not has_signal:
                continue

            p_type = _guess_product_type(text_lower)
            default_name = _default_name_for_type(p_type)
            name = _guess_product_name_from_text(ch.text, default_name)

            current = ProductCard(
                pdf_path=pdf_path,
                name=name,
                type=p_type,
                money=money,
                dates=dates,
                durations=durations,
                chunk_ids=[ch.id],
                extra={"snippet": ch.text[:500] if ch.text else ""},
            )
            silent_in_row = 0
            continue

        # We already have an open product
        if has_signal:
            # If we see a strong signal on a new page and we already
            # accumulated some context, it might be a *new* product.
            last_chunk_id = current.chunk_ids[-1]
            last_chunk = next(cc for cc in sorted_chunks if cc.id == last_chunk_id)

            same_page = (last_chunk.page == ch.page)
            close_index = abs(ch.chunk_index - last_chunk.chunk_index) <= 2

            if not same_page or not close_index:
                # Start new product
                products.append(current)

                p_type = _guess_product_type(text_lower)
                default_name = _default_name_for_type(p_type)
                name = _guess_product_name_from_text(ch.text, default_name)

                current = ProductCard(
                    pdf_path=pdf_path,
                    name=name,
                    type=p_type,
                    money=money,
                    dates=dates,
                    durations=durations,
                    chunk_ids=[ch.id],
                    extra={"snippet": ch.text[:500] if ch.text else ""},
                )
                silent_in_row = 0
            else:
                # Same product, just add another chunk with signal
                current.chunk_ids.append(ch.id)
                current.money.extend(money)
                current.dates.extend(dates)
                current.durations.extend(durations)
                # extend snippet a bit
                snippet = current.extra.get("snippet", "")
                if len(snippet) < 500 and ch.text:
                    remaining = 500 - len(snippet)
                    snippet = (snippet + "\n" + ch.text[:remaining]).strip()
                    current.extra["snippet"] = snippet
                silent_in_row = 0
        else:
            # No signal in this chunk – maybe just supporting context
            if silent_in_row < MAX_SILENT_CONTEXT_CHUNKS:
                current.chunk_ids.append(ch.id)
                # extend snippet if needed
                snippet = current.extra.get("snippet", "")
                if len(snippet) < 500 and ch.text:
                    remaining = 500 - len(snippet)
                    snippet = (snippet + "\n" + ch.text[:remaining]).strip()
                    current.extra["snippet"] = snippet
                silent_in_row += 1
            else:
                # Too far from last signal – close this product
                products.append(current)
                current = None
                silent_in_row = 0

    if current is not None:
        products.append(current)

    return products


def products_to_serializable(products: List[ProductCard]) -> List[Dict[str, Any]]:
    return [p.model_dump() for p in products]
