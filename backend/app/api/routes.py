import os
from datetime import datetime
from typing import Any, Dict

from flask import request, jsonify, current_app
from werkzeug.utils import secure_filename

from app.api import bp
# from app.main import bp


def _json_error(message: str, status: int = 400):
    return jsonify({"error": message}), status


@bp.route("/products", methods=["GET"])
def list_products():
    try:
        from src.config import get_settings
        from src.pipeline import list_all_products  # lazy import to avoid heavy deps at startup
    except Exception as e:
        return _json_error(f"Pipeline import error: {e}", 501)

    try:
        products = list_all_products()
    except Exception as e:
        return _json_error(f"Failed to list products: {e}", 500)

    return jsonify({"items": products})


@bp.route("/ask", methods=["POST"])
def ask():
    data: Dict[str, Any] = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()
    if not question:
        return _json_error("'question' is required", 400)

    pdf_path = data.get("pdf_path")
    top_k = data.get("top_k")

    try:
        from src.pipeline import answer_question, answer_question_for_file
    except Exception as e:
        return _json_error(f"Pipeline import error: {e}", 501)

    try:
        if pdf_path:
            ans = answer_question_for_file(pdf_path, question)
        else:
            ans = answer_question(question, top_k=top_k)
    except Exception as e:
        return _json_error(f"Failed to answer: {e}", 500)

    return jsonify({"answer": ans})


@bp.route("/compare", methods=["POST"])
def compare():
    data: Dict[str, Any] = request.get_json(silent=True) or {}
    product_ids = data.get("product_ids") or []
    question = data.get("question")

    if not isinstance(product_ids, list) or not all(isinstance(i, int) for i in product_ids):
        return _json_error("'product_ids' must be a list of integers", 400)

    try:
        from src.pipeline import compare_products
    except Exception as e:
        return _json_error(f"Pipeline import error: {e}", 501)

    try:
        answer = compare_products(product_ids, question or "")
    except Exception as e:
        return _json_error(f"Failed to compare: {e}", 500)

    return jsonify({"answer": answer})


@bp.route("/ner-qa", methods=["GET"])
def ner_qa():
    pdf_path = (request.args.get("pdf_path") or "").strip()
    if not pdf_path:
        return _json_error("'pdf_path' is required", 400)

    try:
        from src.pipeline import ner_basic_answers_for_product
    except Exception as e:
        return _json_error(f"Pipeline import error: {e}", 501)

    try:
        out = ner_basic_answers_for_product(pdf_path)
    except Exception as e:
        return _json_error(f"Failed to run NER QA: {e}", 500)

    return jsonify({"result": out})


@bp.route("/index-pdf", methods=["POST"])
def index_pdf():
    if "pdf" not in request.files and "file" not in request.files:
        return _json_error("Missing 'pdf' (or 'file') in form-data", 400)
    f = request.files.get("pdf") or request.files.get("file")
    if not f or not f.filename:
        return _json_error("Empty file upload", 400)

    filename = secure_filename(f.filename)
    base_dir = os.path.abspath(os.path.join(current_app.root_path, os.pardir, os.pardir))
    pdf_dir = os.path.join(base_dir, "data")
    os.makedirs(pdf_dir, exist_ok=True)
    save_path = os.path.join(pdf_dir, filename)
    f.save(save_path)

    try:
        from src.pipeline import index_pdf as _index_pdf
    except Exception as e:
        return _json_error(f"Pipeline import error: {e}", 501)

    try:
        _index_pdf(save_path)
    except Exception as e:
        return _json_error(f"Failed to index PDF: {e}", 500)

    return jsonify({"status": "ok", "pdf_path": save_path})

