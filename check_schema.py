import os
import psycopg2
from urllib.parse import urlparse, unquote

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

db_url = os.environ.get('DATABASE_URL')
p = urlparse(db_url)

try:
    conn = psycopg2.connect(
        user=unquote(p.username),
        password=unquote(p.password),
        host=p.hostname,
        port=p.port,
        database=p.path.lstrip('/')
    )
    cur = conn.cursor()
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='quiz'")
    columns = [row[0] for row in cur.fetchall()]
    print(f"Columns in 'quiz' table: {columns}")
    if 'is_template' in columns:
        print("✓ 'is_template' column exists.")
    else:
        print("✗ 'is_template' column MISSING. Need to run migrations.")
    conn.close()
except Exception as e:
    print(f"Error checking schema: {e}")
