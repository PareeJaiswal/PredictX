
import sqlite3
from pathlib import Path

database_path = Path(__file__).resolve().parent / "database" / "maintenance.db"

connection = sqlite3.connect(database_path)

print("DATABASE PATH:", database_path)

tables = connection.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
""").fetchall()

print("\nTABLES:")
for table in tables:
    print(table[0])

print("\nPREDICTIONS TABLE COLUMNS:")
columns = connection.execute("PRAGMA table_info(predictions)").fetchall()

for column in columns:
    print(column)

print("\nTOTAL PREDICTIONS:")
count = connection.execute(
    "SELECT COUNT(*) FROM predictions"
).fetchone()[0]

print(count)

print("\nEXISTING PREDICTIONS:")
records = connection.execute(
    "SELECT * FROM predictions ORDER BY id"
).fetchall()

for record in records:
    print(record)

connection.close()
