import pg8000

try:
    conn = pg8000.connect(user='quizuser', password='secret', host='127.0.0.1', port=5432, database='quizdb')
    conn.close()
    print('PG connect ok')
except Exception as e:
    print('PG connect failed:', repr(e))
