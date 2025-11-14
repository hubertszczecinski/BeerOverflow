from __future__ import annotations

import json
from typing import List, Tuple, Dict, Set

from config import get_settings
import pdf_ingest, embeddings, ner_extraction, products
from groq_client import GroqClient
from vector_store import (
    init_db,
    insert_chunks,
    delete_pdf,
    store_embeddings,
    list_products,
    get_products_by_ids,
)
from vector_store import get_all_embeddings_with_chunks, DocumentChunk

settings = get_settings()


def index_pdf(pdf_path: str) -> None:
    init_db()
    chunks_ingested = pdf_ingest.load_and_chunk_pdf(pdf_path)
    if not chunks_ingested:
        print("No text extracted from PDF.")
        return

    delete_pdf(pdf_path)

    chunk_dicts = [
        {
            "page": c.page,
            "chunk_index": c.chunk_index,
            "text": c.text,
            "metadata": c.metadata,
        }
        for c in chunks_ingested
    ]
    db_chunks = insert_chunks(pdf_path, chunk_dicts)

    texts = [c.text for c in db_chunks]
    vecs = embeddings.encode_texts(texts)
    store_embeddings([c.id for c in db_chunks], vecs)

    ents_by_chunk = ner_extraction.extract_entities_for_chunks(db_chunks)
    product_cards = products.build_products_from_entities(
        pdf_path=pdf_path,
        chunks=db_chunks,
        entities_by_chunk=ents_by_chunk,
    )
    from vector_store import upsert_products

    upsert_products(pdf_path, products.products_to_serializable(product_cards))

    print(f"Indexed {len(db_chunks)} chunks and {len(product_cards)} product cards.")


def answer_question(question: str, top_k: int | None = None) -> str:
    init_db()
    top_k = top_k or settings.top_k_default
    # use embeddings module to get best chunks
    from embeddings import search_similar

    results: List[Tuple[DocumentChunk, float]] = search_similar(question, top_k=top_k)
    if not results:
        return "No data indexed yet. Please index at least one PDF."

    merged = _merge_adjacent_results(results, window_size=settings.neighbor_window_size)
    context_parts = [
        f"[Score {m['score']:.3f} | {m['pdf_path']} p{m['page']} idx {m['start_index']}..{m['end_index']}]\n{m['text']}"
        for m in merged
    ]
    context = "\n\n---\n\n".join(context_parts)

    client = GroqClient()
    return client.ask_with_context(question, context)


def answer_question_for_file(
    pdf_path: int,
    question: str,
    top_k: int | None = None,
) -> str:
    """
    Answer a question using only chunks associated with a specific product.
    """
    init_db()
    # get all product ids for this pdf_path
    product_ids = [p.id for p in list_products() if p.pdf_path == pdf_path]
    prods = get_products_by_ids(product_ids)
    if not prods:
        return f"No product found for path {pdf_path}."

    prod = prods[0]
    data = prod.data or {}
    chunk_ids = data.get("chunk_ids") or []
    if not chunk_ids:
        return f"Product {pdf_path} has no associated text chunks to answer from."

    top_k = top_k or settings.top_k_default
    from embeddings import search_similar_for_chunk_ids

    results: List[Tuple[DocumentChunk, float]] = search_similar_for_chunk_ids(question, chunk_ids, top_k=top_k)
    if not results:
        return f"No matching chunks found for product {pdf_path}. Try re-indexing the PDF."

    merged = _merge_adjacent_results(results, window_size=settings.neighbor_window_size)
    context_parts = [
        f"[Product {pdf_path} | Score {m['score']:.3f} | {m['pdf_path']} p{m['page']} idx {m['start_index']}..{m['end_index']}]\n{m['text']}"
        for m in merged
    ]
    context = "\n\n---\n\n".join(context_parts)

    client = GroqClient()
    scoped_question = f"For product {pdf_path}, {question}"
    return client.ask_with_context(scoped_question, context)


def list_all_products() -> List[dict]:
    init_db()
    prods = list_products()
    return [
        {
            "id": p.id,
            "pdf_path": p.pdf_path,
            "name": p.name,
            "type": p.type,
        }
        for p in prods
    ]


def compare_products(product_ids: List[int], question: str) -> str:
    init_db()
    prods = get_products_by_ids(product_ids)
    if not prods:
        return "No matching products found for the given IDs."

    prods_data = [p.data for p in prods]
    products_json = json.dumps(prods_data, indent=2)
    client = GroqClient()
    return client.compare_products(products_json, question)


def debug_show_chunks_and_scores(question: str, top_k: int | None = None):
    from embeddings import search_similar

    top_k = top_k or settings.top_k_default
    results: List[Tuple[DocumentChunk, float]] = search_similar(question, top_k=top_k)
    merged = _merge_adjacent_results(results, window_size=settings.neighbor_window_size)
    for m in merged:
        print("=" * 80)
        print(
            f"SCORE: {m['score']:.3f} | {m['pdf_path']} p{m['page']} idx {m['start_index']}..{m['end_index']}"
        )
        print(m['text'][:1000])


def _merge_adjacent_results(
    results: List[Tuple[DocumentChunk, float]],
    window_size: int = 1,
) -> List[Dict[str, object]]:
    """
    Merge adjacent chunks around top results into coherent windows.

    Returns a list of dicts with keys:
      pdf_path, page, start_index, end_index, text, score
    in ranked order based on seed result ordering.
    """
    if not results:
        return []

    # Build lookup of all chunks by (pdf_path, page, chunk_index)
    all_chunks = get_all_embeddings_with_chunks()
    by_page: Dict[tuple, Dict[int, DocumentChunk]] = {}
    for ch, _vec in all_chunks:
        key = (ch.pdf_path, ch.page)
        if key not in by_page:
            by_page[key] = {}
        by_page[key][ch.chunk_index] = ch

    # Expand each selected result to include neighbors
    seed_keys: List[tuple] = []
    for ch, _score in results:
        seed_keys.append((ch.pdf_path, ch.page, ch.chunk_index))

    included: Set[tuple] = set()
    for ch, _score in results:
        page_key = (ch.pdf_path, ch.page)
        index_map = by_page.get(page_key, {})
        for delta in range(-window_size, window_size + 1):
            idx = ch.chunk_index + delta
            if idx in index_map:
                included.add((ch.pdf_path, ch.page, idx))

    # Group included into contiguous ranges per page
    grouped: Dict[tuple, List[Tuple[int, DocumentChunk]]] = {}
    for (pdf_path, page, idx) in included:
        key = (pdf_path, page)
        grouped.setdefault(key, []).append((idx, by_page[key][idx]))
    for key in grouped:
        grouped[key].sort(key=lambda t: t[0])

    # Build contiguous segments
    segments: Dict[tuple, Dict[str, object]] = {}
    for key, items in grouped.items():
        if not items:
            continue
        start = None
        prev = None
        bucket: List[Tuple[int, DocumentChunk]] = []
        for idx, ch in items:
            if start is None:
                start = idx
                prev = idx
                bucket = [(idx, ch)]
                continue
            if idx == prev + 1:
                bucket.append((idx, ch))
                prev = idx
            else:
                seg_key = (key[0], key[1], start, prev)
                segments[seg_key] = {
                    "pdf_path": key[0],
                    "page": key[1],
                    "start_index": start,
                    "end_index": prev,
                    "text": "\n".join([c.text for (_i, c) in bucket]),
                    "score": 0.0,
                }
                # start new bucket
                start = idx
                prev = idx
                bucket = [(idx, ch)]
        # flush last bucket
        if start is not None and bucket:
            seg_key = (key[0], key[1], start, prev)
            segments[seg_key] = {
                "pdf_path": key[0],
                "page": key[1],
                "start_index": start,
                "end_index": prev,
                "text": "\n".join([c.text for (_i, c) in bucket]),
                "score": 0.0,
            }

    # Assign a score to each segment based on the best seed inside it
    seed_set = set(seed_keys)
    for seg_key in segments.keys():
        pdf_path, page, start_idx, end_idx = seg_key
        best = 0.0
        for (ch, sc) in results:
            if ch.pdf_path == pdf_path and ch.page == page and start_idx <= ch.chunk_index <= end_idx:
                best = max(best, float(sc))
        segments[seg_key]["score"] = best

    # Order segments by the order their seed first appears in results (stable)
    ordered: List[Dict[str, object]] = []
    seen: Set[tuple] = set()
    for ch, _sc in results:
        # find the segment that contains this seed
        for seg_key, seg in segments.items():
            pdf_path, page, start_idx, end_idx = seg_key
            if seg_key in seen:
                continue
            if ch.pdf_path == pdf_path and ch.page == page and start_idx <= ch.chunk_index <= end_idx:
                ordered.append(seg)
                seen.add(seg_key)
                break

    return ordered
