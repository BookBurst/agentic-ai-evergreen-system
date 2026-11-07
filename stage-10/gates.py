import json
from pathlib import Path

STOP = Path("STOP")        # while it exists, nothing runs
REVIEW = Path("review.jsonl")  # held proposals wait here
ALLOWED = {"refund", "reply"}
MAX_AMOUNT = 100           # dollars; start a real agent at 0
MAX_BROKEN = 3             # broken in a row, then stop
broken_in_a_row = 0

def gate(text):
    # Plain code, no model. Returns a verdict and a detail
    try:
        proposal = json.loads(text)
        action, amount = proposal["action"], proposal["amount"]
    except (ValueError, KeyError, TypeError):
        return "broken", "no JSON with action and amount"
    if isinstance(amount, bool) or not isinstance(
            amount, (int, float)):
        return "broken", "amount is not a number"
    if action not in ALLOWED:
        return "broken", f"action {action!r} is not allowed"
    if amount < 0:
        return "broken", "amount is negative"
    if amount > MAX_AMOUNT:
        return "review", f"amount {amount} is over the limit"
    return "run", proposal

def handle(text):
    global broken_in_a_row
    if STOP.exists():
        raise SystemExit("STOP file found, nothing runs")
    verdict, detail = gate(text)
    if verdict == "run":
        broken_in_a_row = 0
        return verdict, detail
    with REVIEW.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"proposal": text, "why": detail})
                + "\n")
    if verdict == "broken":
        broken_in_a_row += 1
        if broken_in_a_row >= MAX_BROKEN:
            STOP.write_text("too many broken\n", "utf-8")
    return verdict, detail
