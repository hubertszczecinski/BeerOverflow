from flask import Flask, jsonify  # Added jsonify here
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_cors import CORS
from config import config
import os

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page'
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))


@login_manager.unauthorized_handler
def unauthorized():
    """Return JSON response instead of redirecting to login page"""
    return jsonify({'message': 'Authentication required'}), 401


def create_app(config_name=None):
    app = Flask(__name__)

    # Fix: Handle config_name properly
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'default')

    app.config.from_object(config[config_name])

    # Enable CORS for API requests
    allowed_origins = [
        'http://localhost:5173',
        'http://localhost:8080',
        'http://localhost:3000',
        'http://commerzbank.valchak.com',
        'https://commerzbank.valchak.com',
    ]

    # Add custom domain from environment if set
    custom_domain = os.environ.get('DOMAIN_NAME')
    if custom_domain and custom_domain != 'localhost':
        allowed_origins.extend([
            f'http://{custom_domain}',
            f'https://{custom_domain}'
        ])

    CORS(app,
         supports_credentials=True,
         origins=allowed_origins,
         allow_headers=['Content-Type', 'Authorization'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp, url_prefix='/api')

    # API blueprint that exposes src.pipeline features under /api
    try:
        from app.api import bp as api_bp
        app.register_blueprint(api_bp, url_prefix='/api')
    except Exception as e:
        # Avoid crashing the whole app if API import fails
        app.logger.warning(f"API blueprint not registered: {e}")

    # Remove duplicate registration of main_bp
    # app.register_blueprint(main_bp, url_prefix='/api')  # This line is duplicate

    return app