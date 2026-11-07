import json, os, sqlite3, sys, time, urllib.request
from datetime import date
from pathlib import Path
from openai import OpenAI

def load_env(path=".env"):
    # Copy each KEY=value line of .env into the environment
    for line in Path(path).read_text("utf-8").splitlines():
        if "=" in line and not line.startswith("#"):
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())

load_env()
client = OpenAI(api_key=os.environ["API_KEY"],
                base_url=os.environ.get("BASE_URL") or None)
MODEL = os.environ["MODEL_NAME"]
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
OWNER_ID = int(os.environ.get("OWNER_ID") or 0)
TG_URL = os.environ.get("TELEGRAM_API",
                        "https://api.telegram.org")
TEAM = Path("team")
AGENTS = ["neo", "pulse", "pixel"]
MAX_STEPS, MAX_TASKS_PER_DAY = 3, 20

db = sqlite3.connect("board.db")
db.execute("""CREATE TABLE IF NOT EXISTS board (
    topic TEXT PRIMARY KEY, author TEXT,
    text TEXT, day TEXT)""")
db.execute("""CREATE TABLE IF NOT EXISTS tasks (
    day TEXT, task TEXT, steps TEXT)""")

FIELDS = ["from", "to", "task", "context", "expected"]

def make_handoff(sender, to, task, context, expected):
    # One shape for every handover in the team
    return {"from": sender, "to": to, "task": task,
            "context": context, "expected": expected}

def check_handoff(message):
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

def ask(system, user):
    # One model call that must answer in JSON
    reply = client.chat.completions.create(
        model=MODEL,
        response_format={"type": "json_object"},
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": user}])
    return json.loads(reply.choices[0].message.content)

def route(task):
    # The router has no tools: it only picks the agents
    first = lambda n: (TEAM / n / "agent.md").read_text(
        encoding="utf-8").splitlines()[0]
    lines = [(name, first(name)) for name in AGENTS]
    team = "\n".join(f"- {n}: {text}" for n, text in lines)
    system = (f"You route a task to a team.\n{team}\n"
              'Reply as JSON: {"steps": ["agent", ...]}, '
              f"one to {MAX_STEPS} agents in the order they "
              "should work. Use one agent when one is enough. "
              "Choose only agents whose job covers the task. "
              "If the task asks for something none of them "
              "does, such as booking or buying, "
              'reply {"steps": []}.')
    steps = ask(system, task).get("steps", [])
    if not isinstance(steps, list) or len(steps) > MAX_STEPS:
        return []
    return steps if all(s in AGENTS for s in steps) else []

def post(author, note):
    # One owner per topic: others cannot overwrite it
    if not isinstance(note, dict):
        return
    topic = str(note.get("topic", "")).strip().lower()[:60]
    text = str(note.get("text", "")).strip()[:300]
    if not topic or not text:
        return
    row = db.execute("SELECT author FROM board WHERE topic=?",
                     (topic,)).fetchone()
    if row and row[0] != author:
        print(f"  note '{topic}' refused: belongs to {row[0]}")
        return
    db.execute("INSERT OR REPLACE INTO board VALUES (?,?,?,?)",
               (topic, author, text, str(date.today())))
    db.commit()

def board_text():
    rows = db.execute(
        "SELECT topic, author, text, day FROM board "
        "ORDER BY day DESC LIMIT 8").fetchall()
    return "\n".join(f"- {t} ({a}, {d}): {x}"
                     for t, a, x, d in rows)

def run_agent(name, message):
    folder = TEAM / name
    role = "\n".join((folder / f).read_text("utf-8")
                     for f in ("agent.md", "identity.md"))
    system = (f"{role}\nShared board, read only:\n"
              f"{board_text() or '(empty)'}\n\n"
              'Reply as JSON: {"result": "your work", "note": '
              '{"topic": "short label", "text": "one fact '
              'worth sharing"}}')
    answer = ask(system, json.dumps(message))
    result = str(answer["result"])
    (folder / "out").mkdir(exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    (folder / "out" / f"{stamp}.md").write_text(result, "utf-8")
    post(name, answer.get("note"))
    return result

def run_task(task):
    day = str(date.today())
    used = db.execute("SELECT COUNT(*) FROM tasks WHERE day=?",
                      (day,)).fetchone()[0]
    if used >= MAX_TASKS_PER_DAY:
        return "Daily task limit reached. Try again tomorrow."
    try:
        steps = route(task)
    except Exception as error:
        return f"Stopped at router: {str(error)[:150]}"
    db.execute("INSERT INTO tasks VALUES (?,?,?)",
               (day, task, ",".join(steps)))
    db.commit()
    if not steps:
        return "No agent on the team fits this task."
    print("route:", " -> ".join(steps))
    context, sender, results = "No earlier work.", "router", []
    for i, name in enumerate(steps):
        last = i == len(steps) - 1
        expected = ("The final answer for the user" if last
                    else "A result the next agent can use")
        message = make_handoff(sender, name, task, context,
                               expected)
        problems = check_handoff(message)
        if problems:
            return f"Stopped before {name}: {problems}"
        try:
            result = run_agent(name, message)
        except Exception as error:
            return f"Stopped at {name}: {str(error)[:150]}"
        print("done:", name)
        results.append(f"[{name}]\n{result}")
        context, sender = result[:1500], name
    return "\n\n".join(results)

def tg(method, **params):
    request = urllib.request.Request(
        f"{TG_URL}/bot{BOT_TOKEN}/{method}",
        data=json.dumps(params).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=40) as answer:
        return json.load(answer)["result"]

def phone():
    offset = 0
    while True:
        updates = tg("getUpdates", offset=offset, timeout=30)
        for update in updates:
            offset = update["update_id"] + 1
            message = update.get("message", {})
            if message.get("from", {}).get("id") != OWNER_ID:
                continue  # only your ID gets an answer
            text = message.get("text", "")
            if text.startswith("/ask "):
                answer = run_task(text[5:])
            elif text == "/board":
                answer = board_text() or "The board is empty."
            else:
                continue
            tg("sendMessage", chat_id=OWNER_ID,
               text=answer[:4000])

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(run_task(" ".join(sys.argv[1:])))
    elif BOT_TOKEN and OWNER_ID:
        print("Team listening on your phone")
        phone()
    else:
        print('Usage: python team.py "your task"')
