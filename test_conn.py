import psycopg2
from urllib.parse import urlparse, unquote

db_url = "postgresql://postgres:Amishh%402004@localhost:5432/postgres"
print(f"Testing connection to: {db_url.replace('Amishh%402004', '****')}")

try:
    p = urlparse(db_url)
    conn = psycopg2.connect(
        user=unquote(p.username),
        password=unquote(p.password),
        host=p.hostname,
        port=p.port,
        database='postgres'
    )
    print("✓ Connection successful!")
    conn.close()
except Exception as e:
    print(f"✗ Connection failed: {e}")
    import traceback
    traceback.print_exc()
