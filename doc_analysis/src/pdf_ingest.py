from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import List, Dict, Any

from pypdf import PdfReader
from transformers import AutoTokenizer, PreTrainedTokenizerBase

from .config import get_settings

settings = get_settings()


@dataclass
class IngestedChunk:
  pdf_path: str
  page: int
  chunk_index: int
  text: str
  metadata: Dict[str, Any]


def _clean_text(text: str) -> str:
  return " ".join(text.split())


@lru_cache(maxsize=1)
def _get_segmentation_tokenizer() -> PreTrainedTokenizerBase:
  return AutoTokenizer.from_pretrained(settings.segmentation_tokenizer_name)


def _chunk_page_text_by_tokens(
  pdf_path: str,
  page_idx: int,
  text: str,
  max_tokens: int,
  overlap_tokens: int,
) -> List[IngestedChunk]:
  clean = _clean_text(text)
  tok = _get_segmentation_tokenizer()
  enc = tok(
      clean,
      add_special_tokens=False,
      return_offsets_mapping=True,
      truncation=False,
  )
  offsets = enc.get("offset_mapping")
  if not offsets:
      # Fallback to char-based if offsets missing
      return _chunk_page_text_by_chars(pdf_path, page_idx, clean, settings.chunk_max_chars, settings.chunk_overlap_chars)

  n = len(offsets)
  chunks: List[IngestedChunk] = []
  start_tok = 0
  idx = 0
  while start_tok < n:
      end_tok = min(n, start_tok + max_tokens)
      # derive character span for selected tokens
      char_start = offsets[start_tok][0]
      char_end = offsets[end_tok - 1][1]
      if char_end <= char_start:
          # safety fallback
          break
      chunk_text = clean[char_start:char_end]
      chunks.append(
          IngestedChunk(
              pdf_path=pdf_path,
              page=page_idx,
              chunk_index=idx,
              text=chunk_text,
              metadata={"source": "pdf", "page": page_idx},
          )
      )
      idx += 1
      if end_tok == n:
          break
      start_tok = max(0, end_tok - overlap_tokens)
  return chunks


def _chunk_page_text_by_chars(
  pdf_path: str,
  page_idx: int,
  text: str,
  max_chars: int,
  overlap: int,
) -> List[IngestedChunk]:
  text = _clean_text(text)
  chunks: List[IngestedChunk] = []
  start = 0
  idx = 0
  while start < len(text):
      end = min(len(text), start + max_chars)
      chunk_text = text[start:end]
      chunks.append(
          IngestedChunk(
              pdf_path=pdf_path,
              page=page_idx,
              chunk_index=idx,
              text=chunk_text,
              metadata={"source": "pdf", "page": page_idx},
          )
      )
      idx += 1
      if end == len(text):
          break
      start = end - overlap
  return chunks


def load_and_chunk_pdf(pdf_path: str) -> List[IngestedChunk]:
  path = str(Path(pdf_path))
  reader = PdfReader(path)
  all_chunks: List[IngestedChunk] = []
  for i, page in enumerate(reader.pages):
      raw_text = page.extract_text() or ""
      # Prefer token-based segmentation, fallback to chars if tokenizer fails
      try:
          page_chunks = _chunk_page_text_by_tokens(
              pdf_path=path,
              page_idx=i,
              text=raw_text,
              max_tokens=settings.segment_max_tokens,
              overlap_tokens=settings.segment_overlap_tokens,
          )
      except Exception:
          page_chunks = _chunk_page_text_by_chars(
              pdf_path=path,
              page_idx=i,
              text=raw_text,
              max_chars=settings.chunk_max_chars,
              overlap=settings.chunk_overlap_chars,
          )
      all_chunks.extend(page_chunks)
  return all_chunks
