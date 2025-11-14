from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any

from pypdf import PdfReader

from config import get_settings

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


def _chunk_page_text(
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
      page_chunks = _chunk_page_text(
          pdf_path=path,
          page_idx=i,
          text=raw_text,
          max_chars=settings.chunk_max_chars,
          overlap=settings.chunk_overlap_chars,
      )
      all_chunks.extend(page_chunks)
  return all_chunks
