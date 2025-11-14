from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
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
    """Load user by ID"""
    from app.models import User
    return User.query.get(int(user_id))


def create_app(config_name=None):
    app = Flask(__name__)
    
    config_name = config_name or os.getenv('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])
    
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    # API blueprint that exposes src.pipeline features under /api
    try:
        from app.api import bp as api_bp  # type: ignore
        app.register_blueprint(api_bp, url_prefix='/api')
    except Exception as e:
        # Avoid crashing the whole app if API import fails (e.g., missing src deps)
        app.logger.warning(f"API blueprint not registered: {e}")
    
    return app
