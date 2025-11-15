import os
import re
from statistics import median
from typing import Any, Dict, List, Optional

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
        data = resp.json() or {}
        # The doc-analysis service returns {"items": [...]}.
        # Frontend expects a plain array.
        items = data.get("items") if isinstance(data, dict) else None
        return jsonify(items if isinstance(items, list) else [])
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

    # Frontend selects a single offer and expects numeric match metrics.
    # Compute simple heuristics using NER output from doc-analysis.
    try:
        if len(product_ids) == 1:
            pid = int(product_ids[0])

            # 1) Map product id -> pdf_path using /products
            resp_products = requests.get(_svc("/products"), timeout=60)
            resp_products.raise_for_status()
            items = (resp_products.json() or {}).get("items", [])
            product = next((it for it in items if isinstance(it, dict) and it.get("id") == pid), None)
            if not product:
                return _json_error(f"Product id {pid} not found", 404)

            pdf_path = product.get("pdf_path")
            if not pdf_path:
                return _json_error(f"Product id {pid} has no pdf_path", 502)

            # 2) Ask NER QA for basic structured hints (opening balance, terms, fees) as text
            resp_ner = requests.get(_svc("/ner-qa"), params={"pdf_path": pdf_path}, timeout=60)
            resp_ner.raise_for_status()
            ner_payload = resp_ner.json() or {}
            ner_text: str = ner_payload.get("result") or ""

            # 3) Parse NER output
            opening_amount = _parse_opening_balance(ner_text)
            terms = _parse_available_terms(ner_text)
            fees = _parse_fees(ner_text)

            # 4) Score heuristics in [0,1]
            cost = _score_cost(opening_amount, len(fees))
            length = _score_length(terms)
            comfort = _score_comfort(len(terms), len(fees))
            overall = max(0.0, min(1.0, 0.5 * cost + 0.2 * length + 0.3 * comfort))

            return jsonify({
                "cost": cost,
                "length": length,
                "comfort": comfort,
                "overall": overall,
            })

        # Fallback: for multi-product compare, proxy raw compare answer
        resp = requests.post(_svc("/compare"), json=data, timeout=120)
        resp.raise_for_status()
        return jsonify(resp.json())
    except Exception as e:
        return _json_error(f"Doc-analysis error: {e}", 502)


# -------------------------
# Helpers for NER parsing + scoring
# -------------------------

_RE_NUMBER = re.compile(r"(?P<num>\d+(?:[\.,]\d+)?)")
_RE_TERM = re.compile(
    r"(?P<num>\d+(?:[\.,]\d+)?)\s*(?P<unit>years?|yrs?|y|months?|mos?|m)\b",
    flags=re.IGNORECASE,
)


def _to_float(s: str) -> Optional[float]:
    try:
        return float(s.replace(",", "."))
    except Exception:
        return None


def _parse_opening_balance(ner_text: str) -> Optional[float]:
    # Expects line like: "Opening balance: 100 EUR" or "Opening balance: -"
    for line in ner_text.splitlines():
        if line.lower().startswith("opening balance:"):
            # Extract first number on the line
            m = _RE_NUMBER.search(line)
            if not m:
                return None
            return _to_float(m.group("num"))
    return None


def _parse_available_terms(ner_text: str) -> List[str]:
    # Expects line like: "Available terms: 3 months, 6 months" or "-"
    for line in ner_text.splitlines():
        if line.lower().startswith("available terms:"):
            payload = line.split(":", 1)[-1].strip()
            if payload == "-":
                return []
            return [x.strip() for x in payload.split(",") if x.strip()]
    return []


def _parse_fees(ner_text: str) -> List[str]:
    # Expects line like: "Fees: 5 EUR, 10 EUR" or "-"
    for line in ner_text.splitlines():
        if line.lower().startswith("fees:"):
            payload = line.split(":", 1)[-1].strip()
            if payload == "-":
                return []
            return [x.strip() for x in payload.split(",") if x.strip()]
    return []


def _score_cost(opening_amount: Optional[float], fee_count: int) -> float:
    # Lower opening balance and fewer fees => better (higher score)
    if opening_amount is None:
        base = 0.5
    else:
        # Smoothly map amounts around ~1000 baseline into (0,1]
        base = 1.0 / (1.0 + max(0.0, opening_amount) / 1000.0)
    penalty = min(0.5, 0.10 * max(0, fee_count))
    return max(0.0, min(1.0, base * (1.0 - penalty)))


def _score_length(terms: List[str]) -> float:
    # Convert textual durations into months and scale up to 24 months
    months: List[float] = []
    for t in terms:
        m = _RE_TERM.search(t)
        if not m:
            continue
        num = _to_float(m.group("num"))
        if num is None:
            continue
        unit = (m.group("unit") or "").lower()
        if unit.startswith("y"):
            months.append(num * 12)
        else:
            months.append(num)
    if not months:
        return 0.5
    med = median(months)
    return max(0.0, min(1.0, med / 24.0))


def _score_comfort(term_count: int, fee_count: int) -> float:
    # More options is somewhat better; more fees reduces comfort.
    base = 0.6
    bonus = min(0.2, 0.05 * max(0, term_count))
    malus = min(0.6, 0.10 * max(0, fee_count))
    return max(0.0, min(1.0, base + bonus - malus))


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
