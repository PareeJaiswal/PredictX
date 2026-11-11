
from database.db_operations import get_connection

connection = get_connection()

try:
    records = connection.execute(
        "SELECT * FROM predictions ORDER BY id DESC LIMIT 5"
    ).fetchall()

    print("Recent machine predictions:\n")

    for record in records:
        print(dict(record))

finally:
    connection.close()
