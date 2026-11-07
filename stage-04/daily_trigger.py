import time
from datetime import date, datetime
from pathlib import Path

def do_work(reason):
    stamp = datetime.now().strftime("%H:%M:%S")
    print(stamp, "working:", reason)

last_run = None   # the day the morning job last ran
seen = set()      # files already handled
while True:
    now = datetime.now()
    if now.hour >= 7 and last_run != date.today():
        do_work("morning schedule")
        last_run = date.today()
    for path in Path("inbox").glob("*.txt"):
        if path.name not in seen:
            seen.add(path.name)
            do_work(f"new file {path.name}")
    time.sleep(30)
