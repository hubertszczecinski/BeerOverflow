from __future__ import annotations

import json
from typing import List

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
from vector_store import get_all_embeddings_with_chunks

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

    results = search_similar(question, top_k=top_k)
    if not results:
        return "No data indexed yet. Please index at least one PDF."

    context_parts = [f"[Score {score:.3f}]\n{text}" for text, score in results]
    context = "\n\n---\n\n".join(context_parts)

    client = GroqClient()
    return client.ask_with_context(question, context)


def answer_question_for_product(
    product_id: int,
    question: str,
    top_k: int | None = None,
) -> str:
    """
    Answer a question using only chunks associated with a specific product.
    """
    init_db()
    prods = get_products_by_ids([product_id])
    if not prods:
        return f"No product found with id {product_id}."

    prod = prods[0]
    data = prod.data or {}
    chunk_ids = data.get("chunk_ids") or []
    if not chunk_ids:
        return f"Product {product_id} has no associated text chunks to answer from."

    top_k = top_k or settings.top_k_default
    from embeddings import search_similar_for_chunk_ids

    results = search_similar_for_chunk_ids(question, chunk_ids, top_k=top_k)
    if not results:
        return f"No matching chunks found for product {product_id}. Try re-indexing the PDF."

    context_parts = [f"[Product {product_id} | Score {score:.3f}]\n{text}" for text, score in results]
    context = "\n\n---\n\n".join(context_parts)

    client = GroqClient()
    scoped_question = f"For product id {product_id}, {question}"
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
    results = search_similar(question, top_k=top_k)
    for text, score in results:
        print("=" * 80)
        print(f"SCORE: {score:.3f}")
        print(text[:1000])
