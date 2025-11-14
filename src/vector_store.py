from __future__ import annotations

from contextlib import contextmanager
from typing import Iterable, List, Tuple, Dict, Any, Sequence

import numpy as np
from sqlalchemy import (
  create_engine,
  Column,
  Integer,
  String,
  Text,
  JSON,
  LargeBinary,
  ForeignKey,
  UniqueConstraint,
  select,
  delete,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, Session

from config import get_settings

settings = get_settings()

engine = create_engine(settings.db_url, future=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, future=True)
Base = declarative_base()


class DocumentChunk(Base):
  __tablename__ = "document_chunks"

  id = Column(Integer, primary_key=True)
  pdf_path = Column(String, index=True, nullable=False)
  page = Column(Integer, nullable=False)
  chunk_index = Column(Integer, nullable=False)
  text = Column(Text, nullable=False)
  doc_metadata = Column(JSON, nullable=True)

  embedding = relationship(
      "EmbeddingRecord",
      back_populates="chunk",
      uselist=False,
      cascade="all, delete-orphan",
  )

  __table_args__ = (
      UniqueConstraint("pdf_path", "page", "chunk_index", name="uix_chunk"),
  )


class EmbeddingRecord(Base):
  __tablename__ = "embeddings"

  id = Column(Integer, primary_key=True)
  chunk_id = Column(Integer, ForeignKey("document_chunks.id"), unique=True, index=True)
  embedding = Column(LargeBinary, nullable=False)

  chunk = relationship("DocumentChunk", back_populates="embedding")


class ProductRecord(Base):
  __tablename__ = "products"

  id = Column(Integer, primary_key=True)
  pdf_path = Column(String, index=True, nullable=False)
  name = Column(String, nullable=False)
  type = Column(String, nullable=True)
  data = Column(JSON, nullable=False)


def init_db() -> None:
  Base.metadata.create_all(bind=engine)


@contextmanager
def get_session() -> Iterable[Session]:
  session = SessionLocal()
  try:
      yield session
      session.commit()
  except Exception:
      session.rollback()
      raise
  finally:
      session.close()


def delete_pdf(pdf_path: str) -> None:
  with get_session() as session:
      # delete products
      session.execute(delete(ProductRecord).where(ProductRecord.pdf_path == pdf_path))
      # delete chunks (cascades embeddings)
      session.execute(delete(DocumentChunk).where(DocumentChunk.pdf_path == pdf_path))


def insert_chunks(
  pdf_path: str,
  chunks: Sequence[Dict[str, Any]],
) -> List[DocumentChunk]:
  """
  chunks: [{'page': int, 'chunk_index': int, 'text': str, 'metadata': dict}, ...]
  """
  db_chunks: List[DocumentChunk] = []
  with get_session() as session:
      for c in chunks:
          db_chunk = DocumentChunk(
              pdf_path=pdf_path,
              page=c["page"],
              chunk_index=c["chunk_index"],
              text=c["text"],
              doc_metadata=c.get("metadata") or {},
          )
          session.add(db_chunk)
          db_chunks.append(db_chunk)
      # merge identical chunks
      unique_chunks = {}
      for chunk in db_chunks:
          key = (chunk.pdf_path, chunk.page, chunk.chunk_index)
          if key not in unique_chunks:
              unique_chunks[key] = chunk
      db_chunks = list(unique_chunks.values())

      session.flush()  # assign ids
      for _ in db_chunks:
          session.expunge(_)  # detach so caller can use
  return db_chunks


def store_embeddings(
  chunk_ids: Sequence[int],
  embeddings: np.ndarray,
) -> None:
  assert len(chunk_ids) == embeddings.shape[0]
  with get_session() as session:
      for cid, emb_vec in zip(chunk_ids, embeddings):
          emb_bytes = np.asarray(emb_vec, dtype=np.float32).tobytes()
          existing: EmbeddingRecord | None = session.scalar(
              select(EmbeddingRecord).where(EmbeddingRecord.chunk_id == cid)
          )
          if existing:
              existing.embedding = emb_bytes
          else:
              session.add(EmbeddingRecord(chunk_id=cid, embedding=emb_bytes))


def get_all_embeddings_with_chunks() -> List[Tuple[DocumentChunk, np.ndarray]]:
  with get_session() as session:
      rows: List[Tuple[EmbeddingRecord, DocumentChunk]] = [
          (e, e.chunk)
          for e in session.scalars(select(EmbeddingRecord).join(EmbeddingRecord.chunk)).all()
      ]
      result: List[Tuple[DocumentChunk, np.ndarray]] = []
      for emb_rec, chunk in rows:
          vec = np.frombuffer(emb_rec.embedding, dtype=np.float32)
          result.append((chunk, vec))
      return result


def upsert_products(
  pdf_path: str,
  products: List[Dict[str, Any]],
) -> List[ProductRecord]:
  """
  products: list of dicts with at least 'name', 'type', 'data' (or just data).
  """
  with get_session() as session:
      session.execute(delete(ProductRecord).where(ProductRecord.pdf_path == pdf_path))
      db_products: List[ProductRecord] = []
      for p in products:
          db_p = ProductRecord(
              pdf_path=pdf_path,
              name=p.get("name") or "Unknown product",
              type=p.get("type"),
              data=p,
          )
          session.add(db_p)
          db_products.append(db_p)
      session.flush()
      for _ in db_products:
          session.expunge(_)
  return db_products


def list_products() -> List[ProductRecord]:
  with get_session() as session:
      products = session.scalars(select(ProductRecord)).all()
      for p in products:
          session.expunge(p)
      return products


def get_products_by_ids(ids: Sequence[int]) -> List[ProductRecord]:
  if not ids:
      return []
  with get_session() as session:
      stmt = select(ProductRecord).where(ProductRecord.id.in_(list(ids)))
      products = session.scalars(stmt).all()
      for p in products:
          session.expunge(p)
      return products


def get_chunks_by_ids(ids: Sequence[int]) -> List[DocumentChunk]:
  if not ids:
      return []
  with get_session() as session:
      stmt = select(DocumentChunk).where(DocumentChunk.id.in_(list(ids)))
      chunks = session.scalars(stmt).all()
      for c in chunks:
          session.expunge(c)
      # Ensure deterministic ordering
      chunks.sort(key=lambda c: (c.page, c.chunk_index))
      return chunks
