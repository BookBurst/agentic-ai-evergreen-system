import sqlite3, sys
from pathlib import Path

db = sqlite3.connect("tasks.db")
db.execute("create table if not exists tasks "
           "(key text primary key, state text)")
OUTBOX = Path("outbox.txt")  # stands in for a real mail service

def send_email(key, text):
    with OUTBOX.open("a", encoding="utf-8") as f:
        f.write(f"{key}: {text}\n")

def already_sent(key):
    # Ask the outside world, not only your own table
    if not OUTBOX.exists():
        return False
    lines = OUTBOX.read_text("utf-8").splitlines()
    return any(line.startswith(key + ":") for line in lines)

def queue(key):
    sql = "insert or ignore into tasks values (?, 'PENDING')"
    db.execute(sql, (key,))
    db.commit()

def set_state(key, state):
    db.execute("update tasks set state = ? where key = ?",
               (state, key))
    db.commit()

def run_once(key, text, crash=False):
    state = db.execute("select state from tasks where key = ?",
                       (key,)).fetchone()[0]
    if state == "COMPLETED":
        print(key, "was already done, skipping")
        return
    set_state(key, "IN_PROGRESS")
    if not already_sent(key):
        send_email(key, text)
    if crash:
        sys.exit("crashed after sending, before COMPLETED")
    set_state(key, "COMPLETED")
    print(key, "done")

if __name__ == "__main__":
    key = "reminder-invoice-1042-2026-11-04"
    queue(key)
    run_once(key, "Invoice 1042 is due on Friday.",
             crash="crash" in sys.argv)
