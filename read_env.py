try:
    with open('.env', 'r') as f:
        print("--- CONTENT OF .env ---")
        print(f.read())
        print("--- END OF .env ---")
except Exception as e:
    print(f"Error reading .env: {e}")
