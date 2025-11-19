import sqlite3

conn = sqlite3.connect('game_scores.sqlite3')
cursor = conn.cursor()

# Get all table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [row[0] for row in cursor.fetchall()]

# Check row counts for each table
for table in tables:
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"{table}: {count} rows")
    except sqlite3.OperationalError as e:
        print(f"{table}: Error - {e}")

conn.close()