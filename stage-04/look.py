import sqlite3

db = sqlite3.connect("state.db")
query = "SELECT url, status, tries FROM pages"
for row in db.execute(query):
    print(row)
for row in db.execute("SELECT key, value FROM meta"):
    print(row)
