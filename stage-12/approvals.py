import hashlib, json, sys
from pathlib import Path
from auditlog import write_event

PENDING = Path("pending")
OUTBOX = Path("outbox.txt")          # stands in for mail
READ_ONLY = {"read_note"}            # run without asking
RISKY = {"send_email"}               # wait for a person

def send_email(to, subject, body):
    with OUTBOX.open("a", encoding="utf-8") as f:
        f.write(f"To: {to} | {subject}\n")

ACTIONS = {"send_email": send_email}

def fingerprint(tool, args):
    text = json.dumps([tool, args], sort_keys=True)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:10]

def request(agent, run, tool, args):
    # The program calls this when the model asks for a tool
    if tool in READ_ONLY:
        return "run"
    if tool not in RISKY:
        text = json.dumps(args)
        write_event(agent, run, tool, "refused", text)
        return "refused"             # unknown tools never run
    request_id = fingerprint(tool, args)
    PENDING.mkdir(exist_ok=True)
    item = {"id": request_id, "agent": agent, "run": run,
            "tool": tool, "args": args}
    path = PENDING / f"{request_id}.json"
    path.write_text(json.dumps(item), "utf-8")
    write_event(agent, run, tool, "proposed", json.dumps(args))
    return "waiting"

def approve(request_id):
    # Runs only on your own command, never from the agent
    path = PENDING / f"{request_id}.json"
    item = json.loads(path.read_text("utf-8"))
    if fingerprint(item["tool"], item["args"]) != request_id:
        return "refused: the request was changed"
    path.unlink()           # a second approval finds nothing
    write_event("you", item["run"], item["tool"], "approved",
                json.dumps(item["args"]))
    ACTIONS[item["tool"]](**item["args"])
    return "done"

if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else "list"
    if command == "list":
        for path in sorted(PENDING.glob("*.json")):
            print(path.stem, path.read_text("utf-8")[:90])
    elif command == "approve":
        print(approve(sys.argv[2]))
