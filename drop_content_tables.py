import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

tables_to_drop = [
    'content_post',
    'content_comment',
    'content_vote',
    'content_imageattachment'
]

for table in tables_to_drop:
    try:
        cursor.execute(f"DROP TABLE IF EXISTS {table}")
        print(f"Dropped {table}")
    except sqlite3.OperationalError as e:
        print(f"Error dropping {table}: {e}")

conn.commit()
conn.close()
print("Content tables cleanup complete.")