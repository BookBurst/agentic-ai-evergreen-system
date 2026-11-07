AGENTS = {"neo", "pulse", "pixel"}
FIELDS = ["from", "to", "task", "context", "expected"]

def make_handoff(sender, to, task, context, expected):
    # One shape for every handover in the team
    return {"from": sender, "to": to, "task": task,
            "context": context, "expected": expected}

def check_handoff(message):
    # Return the problems found; an empty list means usable
    problems = []
    for name in FIELDS:
        value = message.get(name)
        if not isinstance(value, str) or not value.strip():
            problems.append(f"{name} is missing or empty")
    if message.get("to") not in AGENTS:
        problems.append("to is not an agent on the team")
    if len(message.get("context", "")) > 1500:
        problems.append("context is over 1500 characters")
    return problems

if __name__ == "__main__":
    good = make_handoff(
        "pulse", "pixel", "Draw how a letter reaches a mailbox",
        "Steps: drop-off, sorting center, truck, local office, "
        "carrier, mailbox.",
        "A diagram with a one-sentence caption.")
    print(check_handoff(good))
    bad = dict(good, to="robot", context="")
    print(check_handoff(bad))
