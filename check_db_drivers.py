try:
    import psycopg2
    print("psycopg2 is available")
except ImportError as e:
    print(f"psycopg2 is NOT available: {e}")

try:
    import pg8000
    print("pg8000 is available")
except ImportError as e:
    print(f"pg8000 is NOT available: {e}")
