import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not installed, that's okay for development
    pass

from app import create_app, db

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db}

if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
            print("✓ Database initialized successfully")
        except Exception as e:
            print(f"✗ Error initializing database: {e}")
            
    # Get configuration from environment
    host = os.environ.get('FLASK_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    print(f"\n{'='*50}")
    print(f"Starting Quizify on http://{host}:{port}")
    print(f"Press CTRL+C to stop the server")
    print(f"{'='*50}\n")
    
    app.run(host=host, port=port, debug=debug)


