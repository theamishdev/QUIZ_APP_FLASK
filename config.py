import os
from datetime import timedelta

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///site.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    CHATBOT_MOCK_MODE = False  # Force disabled to use Groq API
    # GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    # GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

# Get configuration based on environment
config_name = os.environ.get('FLASK_ENV', 'development')
if config_name == 'production':
    config = ProductionConfig
elif config_name == 'testing':
    config = TestingConfig
else:
    config = DevelopmentConfig
