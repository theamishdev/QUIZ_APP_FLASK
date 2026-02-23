import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

def create_app():
    app = Flask(__name__)
    
    # Use environment variable for SECRET_KEY, fallback to a default for development
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database configuration - supports different databases based on environment
    db_path = os.environ.get('DATABASE_URL', 'sqlite:///site.db')
    if db_path.startswith('sqlite://'):
        # Ensure instance folder exists for SQLite
        os.makedirs(os.path.join(os.path.dirname(__file__), '..', 'instance'), exist_ok=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_path
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Additional security settings
    app.config['SESSION_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') == 'production'
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

    db.init_app(app)
    login_manager.init_app(app)

    # Register blueprints
    from app.main.routes import main
    from app.auth.routes import auth
    from app.quiz.routes import quiz
    from app.classroom.routes import classroom
    
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(quiz)
    app.register_blueprint(classroom)
    
    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return {'error': 'Page not found'}, 404
    
    @app.errorhandler(403)
    def forbidden(e):
        return {'error': 'Access denied'}, 403
    
    @app.errorhandler(500)
    def internal_error(e):
        db.session.rollback()
        return {'error': 'Internal server error'}, 500

    return app

