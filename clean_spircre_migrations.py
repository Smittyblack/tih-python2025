# internethub/internethub/clean_spircre_migrations.py
import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()
cursor.execute("DELETE FROM django_migrations WHERE app='spircre'")
conn.commit()
conn.close()
print("Removed spircre migration records from default database.")