import os

base_dir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    AWS_REGION = os.environ.get('AWS_REGION', 'eu-central-1')
    # Allow overriding the database file location via env so we can mount a volume.
    # If DB_PATH is set (e.g. /app/data/bank.db), use it; else fall back to previous location.
    DB_PATH = os.environ.get('DB_PATH') or os.path.join(base_dir, 'bank.db')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DB_PATH
    # Ensure directory for DB exists (especially when using a mounted volume directory)
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    # Session configuration for API usage
    # In production with HTTPS, use Secure cookies
    # In development, allow non-secure cookies
    DEPLOYMENT_MODE = os.environ.get('DEPLOYMENT_MODE', 'development')

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'  # Allow cookies from same-site requests
    SESSION_COOKIE_SECURE = (DEPLOYMENT_MODE == 'production')  # Require HTTPS in production

    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = 'Lax'
    REMEMBER_COOKIE_SECURE = (DEPLOYMENT_MODE == 'production')  # Require HTTPS in production

    # Fraud/risk configuration
    RISK_AMOUNT_STD_CAP = float(os.environ.get('RISK_AMOUNT_STD_CAP', '5.0'))
    RISK_UNSEEN_CHANNEL_PENALTY = float(os.environ.get('RISK_UNSEEN_CHANNEL_PENALTY', '0.3'))
    RISK_UNSEEN_LOCATION_PENALTY = float(os.environ.get('RISK_UNSEEN_LOCATION_PENALTY', '0.3'))
    RISK_OFF_HOURS_PENALTY = float(os.environ.get('RISK_OFF_HOURS_PENALTY', '0.2'))
    RISK_NEW_RECIPIENT_PENALTY = float(os.environ.get('RISK_NEW_RECIPIENT_PENALTY', '0.1'))
    RISK_BALANCE_DROP_PENALTY = float(os.environ.get('RISK_BALANCE_DROP_PENALTY', '0.2'))
    RISK_COMBINED_WEIGHT_LOCAL = float(os.environ.get('RISK_COMBINED_WEIGHT_LOCAL', '0.6'))
    RISK_COMBINED_WEIGHT_GLOBAL = float(os.environ.get('RISK_COMBINED_WEIGHT_GLOBAL', '0.4'))
    RISK_ALERT_THRESHOLD = float(os.environ.get('RISK_ALERT_THRESHOLD', '0.7'))

    # Hugging Face model config (override as needed)
    HF_FRAUD_MODEL = os.environ.get('HF_FRAUD_MODEL', 'mrm8488/bert-tiny-finetuned-fraud-detection')
    HF_TASK = os.environ.get('HF_TASK', 'text-classification')
    HF_DEVICE = os.environ.get('HF_DEVICE', 'cpu')

config = {
    'default': Config,
    'development': Config,
    'production': Config,
}
