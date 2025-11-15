from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_cors import CORS
from config import config
import os

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
# Remove Flask-Login default HTML redirects
login_manager.login_view = None
login_manager.login_message = None


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
    
    app.config.from_object(config['default'])

    # Enable CORS for API requests
    # Support both development (localhost) and production (custom domain)
    allowed_origins = [
        'http://localhost:5173',  # Vite dev server
        'http://localhost:8080',  # Docker dev
        'http://localhost:3000',  # Alternative dev port
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

    return app

