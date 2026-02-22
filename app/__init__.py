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
    app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)

    from app.main.routes import main
    from app.auth.routes import auth
    from app.quiz.routes import quiz
    from app.classroom.routes import classroom
    
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(quiz)
    app.register_blueprint(classroom)

    return app
