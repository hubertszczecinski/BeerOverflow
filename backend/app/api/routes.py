import os
from typing import Any, Dict

import requests
from flask import request, jsonify

from app.api import bp
from app.services.risk import evaluate_transaction

DOC_ANALYSIS_URL = os.getenv("DOC_ANALYSIS_URL", "http://doc-analysis:9000")


def _svc(path: str) -> str:
    return f"{DOC_ANALYSIS_URL.rstrip('/')}{path}"


def _json_error(message: str, status: int = 400):
    return jsonify({"error": message}), status


@bp.route("/products", methods=["GET"])
def list_products():
    try:
        resp = requests.get(_svc("/products"), timeout=60)
        resp.raise_for_status()
        return jsonify(resp.json())
    except Exception as e:
        return _json_error(f"Doc-analysis error: {e}", 502)


@bp.route("/ask", methods=["POST"])
def ask():
    data: Dict[str, Any] = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()
    if not question:
        return _json_error("'question' is required", 400)

    try:
        resp = requests.post(_svc("/ask"), json=data, timeout=120)
        resp.raise_for_status()
        return jsonify(resp.json())
    except Exception as e:
        return _json_error(f"Doc-analysis error: {e}", 502)


@bp.route("/compare", methods=["POST"])
def compare():
    data: Dict[str, Any] = request.get_json(silent=True) or {}
    product_ids = data.get("product_ids") or []

    if not isinstance(product_ids, list) or not all(isinstance(i, int) for i in product_ids):
        return _json_error("'product_ids' must be a list of integers", 400)

    try:
        resp = requests.post(_svc("/compare"), json=data, timeout=120)
        resp.raise_for_status()
        return jsonify(resp.json())
    except Exception as e:
        return _json_error(f"Doc-analysis error: {e}", 502)


@bp.route("/ner-qa", methods=["GET"])
def ner_qa():
    pdf_path = (request.args.get("pdf_path") or "").strip()
    if not pdf_path:
        return _json_error("'pdf_path' is required", 400)

    try:
        resp = requests.get(_svc("/ner-qa"), params={"pdf_path": pdf_path}, timeout=60)
        resp.raise_for_status()
        return jsonify(resp.json())
    except Exception as e:
        return _json_error(f"Doc-analysis error: {e}", 502)


@bp.route("/index-pdf", methods=["POST"])
def index_pdf():
    if "pdf" not in request.files and "file" not in request.files:
        return _json_error("Missing 'pdf' (or 'file') in form-data", 400)

    f = request.files.get("pdf") or request.files.get("file")
    if not f or not f.filename:
        return _json_error("Empty file upload", 400)

    filename = f.filename
    files = {
        "pdf": (filename, f.stream, f.mimetype or "application/pdf"),
    }

    try:
        resp = requests.post(_svc("/index-pdf"), files=files, timeout=300)
        resp.raise_for_status()
        return jsonify(resp.json())
    except Exception as e:
        return _json_error(f"Doc-analysis error: {e}", 502)


@bp.route("/fraud/evaluate", methods=["POST"])
def fraud_evaluate():
    data: Dict[str, Any] = request.get_json(silent=True) or {}
    # Basic shape check
    required = ["user_id", "amount", "currency", "timestamp", "type", "channel", "recipient_id", "location", "balance_before", "balance_after"]
    missing = [k for k in required if k not in data]
    if missing:
        return _json_error(f"Missing fields: {', '.join(missing)}", 400)
    try:
        result = evaluate_transaction(data)
        return jsonify(result), 200
    except Exception as e:
        return _json_error(f"Risk evaluation error: {e}", 500)
