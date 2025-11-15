from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy import Index
from sqlalchemy.types import Text, JSON as SAJSON
import json
import enum


class AccountType(enum.Enum):
    """Enumeration for account types"""
    CHECKING = "checking"
    SAVINGS = "savings"
    BUSINESS = "business"
    INVESTMENT = "investment"


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    photo= db.Column(db.LargeBinary)
    transactions = db.relationship('Transaction', backref='user', lazy='dynamic')
    accounts = db.relationship('Account', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    # Optional flag to mark a user as senior for specialized policies
    is_senior = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

    @staticmethod
    def get_user_photo(user_id):
        user = User.query.get(user_id)
        if user is None:
            return None
        return user.photo


class Account(db.Model):
    """Bank accounts linked to users"""
    __tablename__ = 'accounts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    account_type = db.Column(db.Enum(AccountType), nullable=False)
    account_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    balance = db.Column(db.Numeric(12, 2), nullable=False, default=0.00)
    currency = db.Column(db.String(3), nullable=False, default='USD')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    transaction_events = db.relationship('TransactionEvent', backref='account', lazy='dynamic',
                                        foreign_keys='TransactionEvent.account_id')

    def __repr__(self):
        return f'<Account {self.account_number} ({self.account_type.value})>'

    def to_dict(self):
        """Convert account to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'account_type': self.account_type.value,
            'account_number': self.account_number,
            'balance': float(self.balance),
            'currency': self.currency,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<Transaction {self.id} - {self.amount}>'


class TransactionEvent(db.Model):
    """Raw transaction ingestion aligned to the incoming JSON schema.
    This does not replace the legacy Transaction model; it complements it.
    Also serves as a queue for pending transactions.
    """
    __tablename__ = 'transaction_events'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=True, index=True)  # New: link to account
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(8), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, index=True)
    type = db.Column(db.String(64), nullable=False)
    channel = db.Column(db.String(32), nullable=False)
    recipient_id = db.Column(db.String(128), nullable=True)
    location = db.Column(db.String(128), nullable=True)
    balance_before = db.Column(db.Float, nullable=True)
    balance_after = db.Column(db.Float, nullable=True)
    raw = db.Column(Text, nullable=True)  # Stored JSON string for provenance
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # Risk outputs captured at evaluation time
    risk_local = db.Column(db.Float, nullable=True)
    risk_global = db.Column(db.Float, nullable=True)
    risk_combined = db.Column(db.Float, nullable=True)
    flags = db.Column(Text, nullable=True)  # JSON array of strings

    # New fields for transaction processing
    status = db.Column(db.String(20), nullable=True, default='PENDING', index=True)  # PENDING, PROCESSING, COMPLETED, FAILED
    processed_at = db.Column(db.DateTime, nullable=True)
    description = db.Column(db.Text, nullable=True)  # User-friendly description

    def set_raw_dict(self, data: dict) -> None:
        self.raw = json.dumps(data)

    def get_flags(self):
        try:
            return json.loads(self.flags) if self.flags else []
        except Exception:
            return []

    def to_dict(self):
        """Convert transaction event to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'account_id': self.account_id,
            'amount': self.amount,
            'currency': self.currency,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'type': self.type,
            'channel': self.channel,
            'recipient_id': self.recipient_id,
            'location': self.location,
            'balance_before': self.balance_before,
            'balance_after': self.balance_after,
            'status': self.status,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'risk_local': self.risk_local,
            'risk_global': self.risk_global,
            'risk_combined': self.risk_combined,
            'flags': self.get_flags()
        }


class BehaviorProfile(db.Model):
    """Simple per-user behavioral profile to compute local risk."""
    __tablename__ = 'behavior_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False, index=True)

    # Amount stats
    tx_count = db.Column(db.Integer, default=0)
    amount_sum = db.Column(db.Float, default=0.0)
    amount_sumsq = db.Column(db.Float, default=0.0)

    # Histories (serialized JSON)
    channels = db.Column(Text, default='{}')  # dict channel -> count
    locations = db.Column(Text, default='{}')  # dict location -> count
    recipients = db.Column(Text, default='{}')  # dict recipient_id -> count
    hours = db.Column(Text, default='{}')  # dict hour(0-23) -> count

    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def _get_map(self, field: str):
        try:
            return json.loads(getattr(self, field) or '{}')
        except Exception:
            return {}

    def _set_map(self, field: str, value: dict):
        setattr(self, field, json.dumps(value))

    def incr_map(self, field: str, key: str, inc: int = 1):
        m = self._get_map(field)
        if key:
            m[key] = int(m.get(key, 0)) + inc
        self._set_map(field, m)

    @property
    def avg_amount(self) -> float:
        return (self.amount_sum / self.tx_count) if self.tx_count else 0.0

    @property
    def std_amount(self) -> float:
        if self.tx_count <= 1:
            return 0.0
        mean = self.amount_sum / self.tx_count
        var = max((self.amount_sumsq / self.tx_count) - (mean * mean), 0.0)
        return var ** 0.5

    def record(self, *, amount: float, channel: str, location: str | None, recipient_id: str | None, hour: int):
        self.tx_count = int(self.tx_count or 0) + 1
        self.amount_sum = float(self.amount_sum or 0.0) + float(amount)
        self.amount_sumsq = float(self.amount_sumsq or 0.0) + float(amount) * float(amount)
        self.incr_map('channels', channel or '')
        self.incr_map('locations', location or '')
        self.incr_map('recipients', recipient_id or '')
        self.incr_map('hours', str(int(hour) % 24))

Index('ix_transaction_events_user_time', TransactionEvent.user_id, TransactionEvent.timestamp)

