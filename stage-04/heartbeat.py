import time
from pathlib import Path

BEAT = Path("heartbeat.txt")

def beat(note="ok"):
    # Call this once after every finished run
    temp = BEAT.with_suffix(".tmp")
    temp.write_text(f"{time.time()}\n{note}")
    temp.replace(BEAT)   # never half-written
