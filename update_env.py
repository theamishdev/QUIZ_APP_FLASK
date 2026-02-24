import os

with open('.env', 'w') as f:
    f.write("# Development environment variables\n")
    f.write("FLASK_ENV=development\n")
    f.write("FLASK_APP=run.py\n")
    f.write("FLASK_HOST=127.0.0.1\n")
    f.write("FLASK_PORT=5000\n")
    f.write("DATABASE_URL=postgresql+psycopg2://postgres:Amish%402004@localhost:5432/quiz_db\n")
    f.write("SECRET_KEY=dev-secret-key-change-in-production\n")

print("✓ .env file updated successfully")
