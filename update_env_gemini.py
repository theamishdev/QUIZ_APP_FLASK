import os

env_content = """SECRET_KEY=dev-secret-key-change-in-production
DATABASE_URL=sqlite:///site.db
FLASK_APP=run.py
FLASK_ENV=development
GEMINI_API_KEY=AIzaSyCTVlykAPaMiXcDsJeoQdVLj108WUhGy0I
"""

with open('.env', 'w') as f:
    f.write(env_content)

print(".env updated successfully")
