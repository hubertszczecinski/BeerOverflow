from __future__ import annotations

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


def build_products_from_entities(
        pdf_path: str,
        chunks: List[Any],
        entities_by_chunk: Dict[int, List[Entity]],
) -> List[ProductCard]:
    """
    Very simple heuristic: each chunk becomes one product-like card.
    You can later merge cards belonging to the same named product.
    """
    products: List[ProductCard] = []
    for ch in chunks:
        ents = entities_by_chunk.get(ch.id, [])
        money = [e.normalized for e in ents if e.label == "MONEY"]
        dates = [e.normalized for e in ents if e.label == "DATE"]
        durations = [e.normalized for e in ents if e.label == "DURATION"]

        if not (money or dates or durations):
            continue

        # naive product type/name detection
        text_lower = ch.text.lower()
        if "deposit" in text_lower:
            p_type = "deposit"
        elif "credit" in text_lower or "loan" in text_lower:
            p_type = "credit"
        else:
            p_type = None

        name = "Deposit product" if p_type == "deposit" else (
            "Credit product" if p_type == "credit" else "Banking product"
        )

        card = ProductCard(
            pdf_path=pdf_path,
            name=name,
            type=p_type,
            money=money,
            dates=dates,
            durations=durations,
            chunk_ids=[ch.id],
            extra={"snippet": ch.text[:500]},
        )
        products.append(card)
    return products


def products_to_serializable(products: List[ProductCard]) -> List[Dict[str, Any]]:
    return [p.model_dump() for p in products]
