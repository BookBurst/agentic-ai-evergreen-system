import json, sys
from pathlib import Path

STEPS = ["fetch", "summarize", "save", "send"]
CHECKPOINT = Path("checkpoint.json")

def load():
    if CHECKPOINT.exists():
        return json.loads(CHECKPOINT.read_text())
    return {"done": []}

def save(state):
    # Write a temp file, then swap it in: never half-written
    temp = CHECKPOINT.with_suffix(".tmp")
    temp.write_text(json.dumps(state))
    temp.replace(CHECKPOINT)

def run_step(name):
    if name == "save" and "--crash" in sys.argv:
        raise RuntimeError("disk full")  # a simulated crash
    print("ran", name)

state = load()
for step in STEPS:
    if step in state["done"]:
        print("skipped", step, "(already done)")
        continue
    run_step(step)
    state["done"].append(step)
    save(state)  # checkpoint after every step
CHECKPOINT.unlink()  # the whole job finished
