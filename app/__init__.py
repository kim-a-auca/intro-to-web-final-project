from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config_name='development'):
    app = Flask(__name__, template_folder='templates', static_folder='static')
    
    # Load configuration from config.py
    from app.config import DevelopmentConfig, ProductionConfig, TestingConfig
    
    config_dict = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
    }
    
    app.config.from_object(config_dict.get(config_name, DevelopmentConfig))
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'quiz.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    # Register user_loader callback
    from app.models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    from app.views import quiz_bp, api_bp
    app.register_blueprint(quiz_bp)
    app.register_blueprint(api_bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app
