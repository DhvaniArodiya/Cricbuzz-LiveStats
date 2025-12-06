import sqlite3

conn = sqlite3.connect("cricbuzz.db")
cur = conn.cursor()

print("Tables in cricbuzz.db:")
cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cur.fetchall()
for t in tables:
    print(" -", t[0])

conn.close()
