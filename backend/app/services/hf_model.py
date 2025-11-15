import os
from typing import Any, Dict

from flask import current_app

_PIPELINE = None


def _build_text_from_tx(tx: Dict[str, Any]) -> str:
    # Simple feature serialization for text models
    parts = [
        f"amount:{tx.get('amount', 0)} {tx.get('currency', '')}",
        f"type:{tx.get('type', '')}",
        f"channel:{tx.get('channel', '')}",
        f"recipient:{tx.get('recipient_id', '')}",
        f"location:{tx.get('location', '')}",
    ]
    # Balance dynamics provide helpful context
    if 'balance_before' in tx and 'balance_after' in tx:
        try:
            before = float(tx.get('balance_before') or 0.0)
            after = float(tx.get('balance_after') or 0.0)
            delta = after - before
            parts.append(f"balance_delta:{delta:.2f}")
            parts.append(f"balance_ratio:{(after/(before or 1.0)):.3f}")
        except Exception:
            pass
    return ' | '.join(parts)


def _lazy_load_pipeline():
    global _PIPELINE
    if _PIPELINE is not None:
        return _PIPELINE
    try:
        from transformers import pipeline  # type: ignore
        model_name = (current_app and current_app.config.get('HF_FRAUD_MODEL')) or os.getenv('HF_FRAUD_MODEL')
        task = (current_app and current_app.config.get('HF_TASK')) or os.getenv('HF_TASK', 'text-classification')
        device = (current_app and current_app.config.get('HF_DEVICE')) or os.getenv('HF_DEVICE', 'cpu')
        _PIPELINE = pipeline(task, model=model_name, device=0 if device == 'cuda' else -1)
    except Exception:
        _PIPELINE = None
    return _PIPELINE


def score_with_hf_model(tx: Dict[str, Any]) -> float:
    """Returns a fraud probability in [0,1] using a HF model if available.
    Falls back to a heuristic if model/pipeline is unavailable.
    """
    pipe = _lazy_load_pipeline()
    text = _build_text_from_tx(tx)
    if pipe is None:
        # Fallback heuristic: higher amounts and online channel => slightly higher score
        amt = float(tx.get('amount') or 0)
        base = min(amt / 5000.0, 1.0)
        if str(tx.get('channel', '')).lower() == 'online':
            base = min(base + 0.1, 1.0)
        return float(base)

    try:
        out = pipe(text)
        # Common pipeline returns a list of dicts with 'label' and 'score'
        pred = out[0] if isinstance(out, list) else out
        score = float(pred.get('score', 0.0))
        label = str(pred.get('label', '')).lower()
        # Map labels to probability fraud if the model uses NON_FRAUD/LEGIT classes
        if 'non' in label or 'legit' in label or 'safe' in label:
            score = 1.0 - score
        return max(0.0, min(1.0, score))
    except Exception:
        return 0.0

