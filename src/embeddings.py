from __future__ import annotations

from functools import lru_cache
from typing import List, Tuple

import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel

from config import get_settings
from vector_store import get_all_embeddings_with_chunks

settings = get_settings()


@lru_cache(maxsize=1)
def _get_embedding_model() -> Tuple[AutoTokenizer, AutoModel, torch.device]:
    tokenizer = AutoTokenizer.from_pretrained(settings.embedding_model_name)
    model = AutoModel.from_pretrained(settings.embedding_model_name)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()
    return tokenizer, model, device


def encode_texts(texts: List[str], batch_size: int = 8) -> np.ndarray:
    tokenizer, model, device = _get_embedding_model()
    all_vecs: List[np.ndarray] = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i: i + batch_size]
        with torch.no_grad():
            inputs = tokenizer(
                batch,
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors="pt",
            ).to(device)
            outputs = model(**inputs)
            last_hidden_state = outputs.last_hidden_state
            attention_mask = inputs["attention_mask"].unsqueeze(-1)
            masked = last_hidden_state * attention_mask
            sum_vec = masked.sum(dim=1)
            lengths = attention_mask.sum(dim=1)
            mean_pooled = sum_vec / lengths
            vecs = mean_pooled.cpu().numpy().astype("float32")
            all_vecs.append(vecs)
    return np.vstack(all_vecs) if all_vecs else np.zeros((0, 768), dtype=np.float32)


def search_similar(
        query: str,
        top_k: int | None = None,
) -> List[Tuple[str, float]]:
    """
    Returns list of (chunk_text, score).
    """
    if top_k is None:
        top_k = settings.top_k_default

    query_vec = encode_texts([query])[0]
    chunks_with_vecs = get_all_embeddings_with_chunks()
    if not chunks_with_vecs:
        return []

    chunk_texts: List[str] = []
    chunk_vecs: List[np.ndarray] = []
    for chunk, vec in chunks_with_vecs:
        chunk_texts.append(chunk.text)
        chunk_vecs.append(vec)

    mat = np.vstack(chunk_vecs)
    q = query_vec / (np.linalg.norm(query_vec) + 1e-9)
    m = mat / (np.linalg.norm(mat, axis=1, keepdims=True) + 1e-9)
    scores = m @ q
    idxs = np.argsort(scores)[::-1][:top_k]
    return [(chunk_texts[i], float(scores[i])) for i in idxs]


def search_similar_for_chunk_ids(
        query: str,
        chunk_ids: List[int],
        top_k: int | None = None,
) -> List[Tuple[str, float]]:
    """
    Returns list of (chunk_text, score) restricted to given chunk IDs.
    """
    if not chunk_ids:
        return []

    if top_k is None:
        top_k = settings.top_k_default

    query_vec = encode_texts([query])[0]
    allowed_ids = set(chunk_ids)
    chunks_with_vecs = [
        (chunk, vec)
        for chunk, vec in get_all_embeddings_with_chunks()
        if chunk.id in allowed_ids
    ]
    if not chunks_with_vecs:
        return []

    chunk_texts: List[str] = []
    chunk_vecs: List[np.ndarray] = []
    for chunk, vec in chunks_with_vecs:
        chunk_texts.append(chunk.text)
        chunk_vecs.append(vec)

    mat = np.vstack(chunk_vecs)
    q = query_vec / (np.linalg.norm(query_vec) + 1e-9)
    m = mat / (np.linalg.norm(mat, axis=1, keepdims=True) + 1e-9)
    scores = m @ q
    idxs = np.argsort(scores)[::-1][:top_k]
    return [(chunk_texts[i], float(scores[i])) for i in idxs]
