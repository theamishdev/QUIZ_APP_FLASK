import psycopg2

passwords = ['Amishh@2004', 'Amish@2004', 'Amishh', 'Amish', 'postgres', 'admin']
for p in passwords:
    try:
        conn = psycopg2.connect(
            user='postgres',
            password=p,
            host='localhost',
            port=5432,
            database='postgres'
        )
        print(f"✓ Success with password: '{p}'")
        conn.close()
        break
    except Exception as e:
        print(f"✗ Failed with password: '{p}'")
else:
    print("All failed.")
