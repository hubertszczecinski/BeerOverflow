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

config = {
    'default': Config
}
