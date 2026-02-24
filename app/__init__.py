import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import config

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

def create_app(config_class=config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI')

    # If the DATABASE_URL / SQLALCHEMY_DATABASE_URI looks malformed (for
    # example something like `2004@localhost` without a scheme), fall back to a
    # local sqlite file so the app is usable for development without Postgres.
    if db_uri and '://' not in db_uri:
        print('Warning: malformed SQLALCHEMY_DATABASE_URI detected; falling back to sqlite:///site.db for development')
        db_uri = 'sqlite:///site.db'

    if db_uri:
        # Normalize Heroku-style Postgres URL (postgres://) to SQLAlchemy-compatible (postgresql://)
        if db_uri.startswith('postgres://'):
            db_uri = db_uri.replace('postgres://', 'postgresql://', 1)

        # Support both psycopg2 and pg8000 fallbacks
        if db_uri.startswith('postgresql://') or db_uri.startswith('postgresql+psycopg2://'):
            try:
                import psycopg2  # type: ignore
            except Exception:
                print('psycopg2 not found, attempting pg8000 fallback')
                if '+pg8000' not in db_uri:
                    db_uri = db_uri.replace('postgresql://', 'postgresql+pg8000://', 1)
                    db_uri = db_uri.replace('postgresql+psycopg2://', 'postgresql+pg8000://', 1)

        # If using SQLite ensure instance folder exists
        if db_uri.startswith('sqlite://'):
            os.makedirs(os.path.join(os.path.dirname(__file__), '..', 'instance'), exist_ok=True)

        app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    

    db.init_app(app)
    
    # Configure engine options for stability
    if db_uri and db_uri.startswith('postgresql'):
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'connect_timeout': 10,
            'pool_pre_ping': True,
            'pool_recycle': 3600,
        }
        
    login_manager.init_app(app)
    # Initialize Flask-Migrate
    migrate.init_app(app, db)

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

