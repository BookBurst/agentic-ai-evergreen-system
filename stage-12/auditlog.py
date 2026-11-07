import hashlib, hmac, json, os, time
from pathlib import Path

def load_env(path=".env"):
    # Copy each KEY=value line of .env into the environment
    # utf-8-sig also reads a file saved with an invisible mark
    for line in Path(path).read_text("utf-8-sig").splitlines():
        if "=" in line and not line.startswith("#"):
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())

load_env()  # the log keys live in .env
LOG = Path("audit.jsonl")
ZERO = "0" * 64

def digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def sign(agent, body):
    # One secret key per agent, kept in .env as LOG_KEY_<NAME>
    key = os.environ[f"LOG_KEY_{agent.upper()}"].encode("utf-8")
    data = body.encode("utf-8")
    return hmac.new(key, data, "sha256").hexdigest()

def last_hash():
    if not LOG.exists() or LOG.stat().st_size == 0:
        return ZERO
    return digest(LOG.read_text("utf-8").splitlines()[-1])

def write_event(agent, run, action, phase, content):
    # The log keeps a hash of the content, never the content
    event = {"time": time.strftime("%Y-%m-%d %H:%M:%S"),
             "agent": agent, "run": run, "action": action,
             "phase": phase, "content": digest(content),
             "prev": last_hash()}
    body = json.dumps(event, sort_keys=True)
    event["sig"] = sign(agent, body)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, sort_keys=True) + "\n")
    return event

def verify():
    if not LOG.exists():
        return "log is empty, 0 events"
    prev = ZERO
    lines = LOG.read_text("utf-8").splitlines()
    for number, line in enumerate(lines, 1):
        try:
            event = json.loads(line)
            sig = event.pop("sig")
            body = json.dumps(event, sort_keys=True)
            good = sign(event["agent"], body)
        except (ValueError, KeyError):
            return f"line {number}: cannot be checked"
        if event.get("prev") != prev:
            return f"line {number}: the chain is broken"
        if not hmac.compare_digest(sig, good):
            return f"line {number}: the signature is wrong"
        prev = digest(line)
    return f"log is intact, {len(lines)} events"

if __name__ == "__main__":
    print(verify())
