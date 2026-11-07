import sqlite3
from datetime import date, timedelta

state = sqlite3.connect("state.db")     # what is happening now
memory = sqlite3.connect("memory.db")   # what is worth keeping
memory.execute("CREATE TABLE IF NOT EXISTS notes "
               "(note TEXT, created TEXT, expires TEXT)")

def remember(note, days):
    today = date.today()
    expires = today + timedelta(days)
    memory.execute("INSERT INTO notes VALUES (?, ?, ?)",
                   (note, str(today), str(expires)))
    memory.commit()

def consolidate():
    # Run at night: drop expired notes and exact duplicates
    memory.execute("DELETE FROM notes WHERE expires < ?",
                   (str(date.today()),))
    memory.execute("DELETE FROM notes WHERE rowid NOT IN "
                   "(SELECT MAX(rowid) FROM notes "
                   "GROUP BY note)")
    memory.commit()
