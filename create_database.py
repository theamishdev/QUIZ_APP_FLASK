import os
from urllib.parse import urlparse, unquote

try:
    import pg8000
except ImportError:
    raise SystemExit("pg8000 not installed. Run: pip install pg8000")

url = os.environ.get('DATABASE_URL')
if not url:
    raise SystemExit('DATABASE_URL not set in environment')

p = urlparse(url)

username = unquote(p.username) if p.username else None
password = unquote(p.password) if p.password else None
host = p.hostname or 'localhost'
port = p.port or 5432
# path may start with /dbname
dbname = p.path.lstrip('/') or None

if not dbname:
    raise SystemExit('No database name found in DATABASE_URL')

print(f"Creating database '{dbname}' on {host}:{port} as user '{username}'")

# Connect to default 'postgres' database to run CREATE DATABASE
conn = None
try:
    conn = pg8000.connect(user=username, password=password, host=host, port=port, database='postgres')
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(f"CREATE DATABASE \"{dbname}\"")
    print('Database created successfully')
except pg8000.dbapi.ProgrammingError as e:
    msg = str(e)
    if 'already exists' in msg or 'already exists' in msg.lower():
        print('Database already exists')
    else:
        raise
except Exception as e:
    raise
finally:
    if conn:
        try:
            conn.close()
        except Exception:
            pass
