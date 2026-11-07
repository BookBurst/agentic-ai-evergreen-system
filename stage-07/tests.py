import json
from pathlib import Path
from check import deliver, read_rows

def rows(*items):
    return [{"date": "2026-10-01", "category": name,
             "amount": str(amount), "currency": "USD"}
            for name, amount in items]

CASES = {
    "one row": rows(("Meals", 28.15)),
    "three rows": rows(("Meals", 28.15), ("Travel", 312.45),
                       ("Meals", 41.60)),
    "a refund": rows(("Software", 129.00),
                     ("Software", -129.00), ("Meals", 36.85)),
    "one category": rows(("Office", 64.72), ("Office", 203.18),
                         ("Office", 12.40)),
    "fourteen rows": read_rows(),
}

def run_all():
    memory = Path("last_run.json")
    old = {}
    if memory.exists():
        old = json.loads(memory.read_text("utf-8"))
    new = {}
    for name, data in CASES.items():
        new[name] = deliver(data)["status"] == "CHECKED"
        changed = name in old and old[name] != new[name]
        note = "<- changed since last run" if changed else ""
        print("PASS" if new[name] else "FAIL", name, note)
    memory.write_text(json.dumps(new), "utf-8")

if __name__ == "__main__":
    run_all()
