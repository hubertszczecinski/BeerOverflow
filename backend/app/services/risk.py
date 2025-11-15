from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Tuple

from flask import current_app

from app import db
from app.models import BehaviorProfile, TransactionEvent
from .hf_model import score_with_hf_model


def _safe_float(x, default=0.0) -> float:
    try:
        return float(x)
    except Exception:
        return float(default)


def get_or_create_profile(user_id: int) -> BehaviorProfile:
    prof = BehaviorProfile.query.filter_by(user_id=user_id).first()
    if prof is None:
        prof = BehaviorProfile(user_id=user_id)
        db.session.add(prof)
        db.session.flush()
    return prof


def update_profile_from_tx(user_id: int, tx: Dict[str, Any]) -> BehaviorProfile:
    prof = get_or_create_profile(user_id)
    amount = _safe_float(tx.get('amount'))
    channel = str(tx.get('channel') or '')
    location = tx.get('location') or ''
    recipient = tx.get('recipient_id') or ''
    # timestamp string to hour
    ts = tx.get('timestamp')
    hour = 0
    try:
        hour = datetime.fromisoformat(str(ts).replace('Z', '+00:00')).hour
    except Exception:
        hour = 0
    prof.record(amount=amount, channel=channel, location=location, recipient_id=recipient, hour=hour)
    return prof


def compute_local_risk(prof: BehaviorProfile, tx: Dict[str, Any]) -> Tuple[float, List[str]]:
    cfg = current_app.config
    flags: List[str] = []

    amount = _safe_float(tx.get('amount'))
    # z-score based on profile stats
    mean = prof.avg_amount
    std = prof.std_amount
    std = max(std, 1e-6)
    z = abs(amount - mean) / std
    z_cap = float(cfg.get('RISK_AMOUNT_STD_CAP', 5.0))
    z_norm = min(z / z_cap, 1.0)
    if z > 3.0 and prof.tx_count > 10:
        flags.append('amount_outlier')

    # unseen channel/location/recipient
    channels = prof._get_map('channels')
    locations = prof._get_map('locations')
    recipients = prof._get_map('recipients')
    hours = prof._get_map('hours')

    ch_pen = float(cfg.get('RISK_UNSEEN_CHANNEL_PENALTY', 0.3)) if tx.get('channel') and tx.get('channel') not in channels else 0.0
    if ch_pen:
        flags.append('new_channel')
    loc_pen = float(cfg.get('RISK_UNSEEN_LOCATION_PENALTY', 0.3)) if tx.get('location') and tx.get('location') not in locations else 0.0
    if loc_pen:
        flags.append('new_location')
    rec_pen = float(cfg.get('RISK_NEW_RECIPIENT_PENALTY', 0.1)) if tx.get('recipient_id') and tx.get('recipient_id') not in recipients else 0.0
    if rec_pen:
        flags.append('new_recipient')

    # off-hours
    off_pen = 0.0
    try:
        hour = datetime.fromisoformat(str(tx.get('timestamp')).replace('Z', '+00:00')).hour
        if hours:
            # Consider off-hours if hour frequency is in the bottom 25% of observed hours
            freq = [int(v) for v in hours.values()]
            cutoff = sorted(freq)[max(0, int(0.75 * (len(freq) - 1)))] if freq else 0
            if int(hours.get(str(hour), 0)) <= cutoff:
                off_pen = float(cfg.get('RISK_OFF_HOURS_PENALTY', 0.2))
                flags.append('off_hours')
    except Exception:
        pass

    # balance drop
    bal_pen = 0.0
    try:
        before = _safe_float(tx.get('balance_before'))
        after = _safe_float(tx.get('balance_after'))
        if before > 0 and (before - after) / before >= 0.5:
            bal_pen = float(cfg.get('RISK_BALANCE_DROP_PENALTY', 0.2))
            flags.append('large_balance_drop')
    except Exception:
        pass

    base = 0.5 * z_norm
    local = max(0.0, min(1.0, base + ch_pen + loc_pen + rec_pen + off_pen + bal_pen))
    return local, flags


def evaluate_transaction(tx: Dict[str, Any]) -> Dict[str, Any]:
    """Compute local profile risk and global HF model score, persist event, and return scores."""
    # Persist event first
    user_id = int((tx.get('user_id') or 0) if isinstance(tx.get('user_id'), int) else str(tx.get('user_id')).split('-')[-1] or 0)
    ev = TransactionEvent(
        user_id=user_id,
        amount=_safe_float(tx.get('amount')),
        currency=str(tx.get('currency') or ''),
        type=str(tx.get('type') or ''),
        channel=str(tx.get('channel') or ''),
        recipient_id=tx.get('recipient_id'),
        location=tx.get('location'),
        balance_before=_safe_float(tx.get('balance_before')) if tx.get('balance_before') is not None else None,
        balance_after=_safe_float(tx.get('balance_after')) if tx.get('balance_after') is not None else None,
    )

    # parse timestamp
    try:
        ev.timestamp = datetime.fromisoformat(str(tx.get('timestamp')).replace('Z', '+00:00'))
    except Exception:
        ev.timestamp = datetime.utcnow()
    ev.set_raw_dict(tx)

    # Update profile and compute local risk
    prof = update_profile_from_tx(user_id, tx)
    local, flags = compute_local_risk(prof, tx)

    # Global score via HF model
    global_score = score_with_hf_model(tx)

    # Combine
    wl = float(current_app.config.get('RISK_COMBINED_WEIGHT_LOCAL', 0.6))
    wg = float(current_app.config.get('RISK_COMBINED_WEIGHT_GLOBAL', 0.4))
    combined = max(0.0, min(1.0, wl * local + wg * global_score))

    ev.risk_local = local
    ev.risk_global = global_score
    ev.risk_combined = combined
    try:
        import json
        ev.flags = json.dumps(flags)
    except Exception:
        ev.flags = None

    db.session.add(ev)
    db.session.commit()

    alert_threshold = float(current_app.config.get('RISK_ALERT_THRESHOLD', 0.7))
    return {
        'risk': {
            'local': local,
            'global': global_score,
            'combined': combined,
            'threshold': alert_threshold,
            'alert': combined >= alert_threshold,
            'flags': flags,
        },
        'event_id': ev.id,
        'user_id': user_id,
    }

