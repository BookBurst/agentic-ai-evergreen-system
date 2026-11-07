import json
from pathlib import Path

RECORD = Path("shadow_record.jsonl")   # what the new one did
NEEDED = 0.8      # decided before the trial: share of agreement
ACTUAL = {}       # what the live agent did

def live_tools():
    def set_priority(request, level):
        ACTUAL[request] = level   # really: change the ticket
        return {"ok": True}
    return {"set_priority": set_priority}

def shadow_tools():
    def set_priority(request, level):
        entry = {"request": request, "level": level}
        with RECORD.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
        return {"ok": True}        # says yes, changes nothing
    return {"set_priority": set_priority}

def live_agent(request, tools):
    # A stand-in for the live agent: two small word lists
    text, level = request.lower(), "normal"
    if any(w in text for w in ("down", "cannot")):
        level = "urgent"
    elif any(w in text for w in ("next week", "whenever")):
        level = "low"
    tools["set_priority"](request, level)

def new_agent(request, tools):
    # A stand-in for the new version: more words in the list
    text, level = request.lower(), "normal"
    urgent = ("down", "cannot", "error", "crash", "urgent")
    if any(w in text for w in urgent):
        level = "urgent"
    elif any(w in text for w in ("next week", "whenever")):
        level = "low"
    tools["set_priority"](request, level)

def trial(requests):
    ACTUAL.clear()
    RECORD.unlink(missing_ok=True)
    for request in requests:
        live_agent(request, live_tools())      # acts for real
        new_agent(request, shadow_tools())     # only a record
    wanted = {}
    if RECORD.exists():
        with RECORD.open(encoding="utf-8") as f:
            for line in f:
                entry = json.loads(line)
                wanted[entry["request"]] = entry["level"]
    differ = []
    for request in requests:
        live = ACTUAL.get(request, "none")
        new = wanted.get(request, "none")
        if live != new:
            differ.append((request, live, new))
    return 1 - len(differ) / len(requests), differ
