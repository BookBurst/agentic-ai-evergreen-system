import json
from pathlib import Path

FILE = Path("corrections.jsonl")
SHOWN = 3     # how many corrections go into one prompt

def words(text):
    # The longer words of a text, without punctuation
    cleaned = (w.strip(".,!?:").lower() for w in text.split())
    return {w for w in cleaned if len(w) > 3}

def save(task, wrong, right):
    entry = {"task": task, "wrong": wrong, "right": right}
    with FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

def relevant(task):
    if not FILE.exists():
        return []
    with FILE.open(encoding="utf-8") as f:
        entries = [json.loads(line) for line in f]
    scored = []
    for entry in reversed(entries):          # newest first
        overlap = len(words(task) & words(entry["task"]))
        if overlap:
            scored.append((overlap, entry))
    scored.sort(key=lambda pair: -pair[0])   # ties keep newest
    return [entry for _, entry in scored[:SHOWN]]

def build_prompt(base, task):
    shown = relevant(task)
    if not shown:
        return base
    lines = [base, "", "Corrections from before, follow them "
             "when they apply:"]
    for e in shown:
        lines.append(f"- Task: {e['task']}")
        lines.append(f"  Wrong: {e['wrong']}")
        lines.append(f"  Right: {e['right']}")
    return "\n".join(lines)
