# internethub/internethub/check_game_scores_migrations.py
import sqlite3

conn = sqlite3.connect('game_scores.sqlite3')
cursor = conn.cursor()
cursor.execute("SELECT app, name FROM django_migrations WHERE app='spircre'")
spircre_migrations = cursor.fetchall()
for app, name in spircre_migrations:
    print(f"Applied: {app}.{name}")
conn.close()