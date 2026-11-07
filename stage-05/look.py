import sqlite3
db = sqlite3.connect("board.db")
query = "SELECT topic, author, day, text FROM board"
for row in db.execute(query):
    print(row)
for row in db.execute("SELECT day, task, steps FROM tasks"):
    print(row)
