import os
import time
from pathlib import Path

# A scheduler may start us anywhere: work next to our files
os.chdir(Path(__file__).resolve().parent)

from phone_bot import tg, OWNERS   # the same bot as the phone

BEAT = Path("heartbeat.txt")
FLAG = Path("alarm.flag")      # exists while an alarm is open
MAX_AGE = 26 * 3600     # daily agent: 24 h plus 2 h of slack

def tell(text):
    tg("sendMessage", chat_id=min(OWNERS), text=text)

def check():
    note, age = "no heartbeat file", None
    if BEAT.exists():
        first, _, note = BEAT.read_text().partition("\n")
        age = time.time() - float(first)
    silent = age is None or age > MAX_AGE
    if silent and not FLAG.exists():
        since = "never ran"
        if age is not None:
            since = f"{age / 3600:.0f} hours"
        tell(f"Research agent silent: {since}. "
             f"Last note: {note}. "
             "First check: is the service running?")
        FLAG.write_text("sent")   # one alarm, not one per check
    elif not silent and FLAG.exists():
        tell(f"Research agent is back. Last note: {note}.")
        FLAG.unlink()

if __name__ == "__main__":
    check()
