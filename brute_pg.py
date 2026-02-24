import psycopg2

guesses = ['Amishh@2004', 'Amishh', 'Amish', 'postgres', 'admin', 'password', '1234', '']
for guess in guesses:
    try:
        conn = psycopg2.connect(
            user='postgres',
            password=guess,
            host='localhost',
            port=5432,
            database='postgres'
        )
        print(f"✓ Success with password: '{guess}'")
        conn.close()
        break
    except Exception as e:
        print(f"✗ Failed with password: '{guess}'")
else:
    print("Could not find correct password.")
