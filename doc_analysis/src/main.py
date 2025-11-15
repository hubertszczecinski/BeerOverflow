from typing import Any, Dict, List, Optional

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from .pipeline import (
  index_pdf as _index_pdf,
  list_all_products,
  answer_question,
  answer_question_for_file,
  compare_products,
  ner_basic_answers_for_product,
)

app = FastAPI(title="Doc Analysis Service")


@app.get("/products")
async def products():
  try:
      items = list_all_products()
  except Exception as e:
      raise HTTPException(500, f"Failed to list products: {e}")
  return {"items": items}


@app.post("/ask")
async def ask(payload: Dict[str, Any]):
  question = (payload.get("question") or "").strip()
  if not question:
      raise HTTPException(400, "'question' is required")

  pdf_path: Optional[str] = payload.get("pdf_path")
  top_k: Optional[int] = payload.get("top_k")

  try:
      if pdf_path:
          ans = answer_question_for_file(pdf_path, question)
      else:
          ans = answer_question(question, top_k=top_k)
  except Exception as e:
      raise HTTPException(500, f"Failed to answer: {e}")

  return {"answer": ans}


@app.post("/compare")
async def compare(payload: Dict[str, Any]):
  ids = payload.get("product_ids") or []
  question = payload.get("question") or ""

  if not isinstance(ids, list) or not all(isinstance(i, int) for i in ids):
      raise HTTPException(400, "'product_ids' must be a list of integers")

  try:
      answer = compare_products(ids, question)
  except Exception as e:
      raise HTTPException(500, f"Failed to compare: {e}")

  return {"answer": answer}


@app.get("/ner-qa")
async def ner_qa(pdf_path: str):
  if not pdf_path:
      raise HTTPException(400, "'pdf_path' is required")
  try:
      out = ner_basic_answers_for_product(pdf_path)
  except Exception as e:
      raise HTTPException(500, f"Failed to run NER QA: {e}")
  return {"result": out}


@app.post("/index-pdf")
async def index_pdf(pdf: UploadFile = File(...)):
  # Where PDFs will be stored inside the container
  import os

  base_dir = "/app/data"
  os.makedirs(base_dir, exist_ok=True)
  save_path = os.path.join(base_dir, pdf.filename)

  try:
      contents = await pdf.read()
      with open(save_path, "wb") as f:
          f.write(contents)
      _index_pdf(save_path)
  except Exception as e:
      raise HTTPException(500, f"Failed to index PDF: {e}")

  return {"status": "ok", "pdf_path": save_path}


@app.get("/health")
async def health():
  return {"status": "healthy"}
