import json, os, sqlite3, time, urllib.request
from datetime import datetime, date
from html.parser import HTMLParser
from pathlib import Path
from openai import OpenAI

def load_env(path=".env"):
    # Copy each KEY=value line of .env into the environment
    for line in Path(path).read_text().splitlines():
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
RESEARCH_HOUR, BRIEF_HOUR = 2, 7
MAX_PAGES, MAX_TRIES, MAX_CHARS = 10, 3, 8000

db = sqlite3.connect("state.db")
db.execute("""CREATE TABLE IF NOT EXISTS pages (
    day TEXT, url TEXT, status TEXT, tries INTEGER,
    summary TEXT, PRIMARY KEY (day, url))""")
db.execute("""CREATE TABLE IF NOT EXISTS meta (
    key TEXT PRIMARY KEY, value TEXT)""")

def get_meta(key):
    row = db.execute("SELECT value FROM meta WHERE key=?",
                     (key,)).fetchone()
    return row[0] if row else None

def set_meta(key, value):
    db.execute("INSERT OR REPLACE INTO meta VALUES (?, ?)",
               (key, str(value)))
    db.commit()

class TextOnly(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts, self.skip = [], 0
    def handle_starttag(self, tag, attrs):
        self.skip += tag in ("script", "style")
    def handle_endtag(self, tag):
        self.skip -= tag in ("script", "style")
    def handle_data(self, data):
        if not self.skip and data.strip():
            self.parts.append(data.strip())

def fetch(url):
    with urllib.request.urlopen(url, timeout=20) as page:
        html = page.read(500_000).decode("utf-8", "replace")
    parser = TextOnly()
    parser.feed(html)
    return " ".join(parser.parts)[:MAX_CHARS]

RULES = """Summarize the page text in at most three sentences,
using only what the text says. If it has no useful content,
reply exactly: NO CONTENT"""

def summarize(text):
    reply = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": RULES},
                  {"role": "user", "content": text}])
    return reply.choices[0].message.content.strip()

def research(day):
    lines = Path("watchlist.txt").read_text().splitlines()
    urls = [x.strip() for x in lines
            if x.strip().startswith(("http://", "https://"))]
    urls = urls[:MAX_PAGES]
    for url in urls:
        row = db.execute(
            "SELECT status, tries FROM pages "
            "WHERE day=? AND url=?", (day, url)).fetchone()
        if row and (row[0] == "done" or row[1] >= MAX_TRIES):
            continue  # checkpoint: finished or given up
        tries = (row[1] if row else 0) + 1
        try:
            status, note = "done", summarize(fetch(url))
        except Exception as error:
            status, note = "failed", str(error)[:150]
        db.execute("INSERT OR REPLACE INTO pages "
                   "VALUES (?,?,?,?,?)",
                   (day, url, status, tries, note))
        db.commit()  # saved after every page
        print(f"{status}: {url}")

def tg(method, **params):
    # One call to the Telegram Bot API, always outgoing
    request = urllib.request.Request(
        f"{TG_URL}/bot{BOT_TOKEN}/{method}",
        data=json.dumps(params).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=40) as answer:
        return json.load(answer)["result"]

def send(text):
    if BOT_TOKEN and OWNER_ID:
        tg("sendMessage", chat_id=OWNER_ID, text=text[:4000])
    else:
        print(text)  # no bot configured: show it on screen

def make_brief(day):
    rows = db.execute("SELECT url, status, summary FROM pages "
                      "WHERE day=?", (day,)).fetchall()
    lines = [f"Morning brief, {day}"]
    for url, status, note in rows:
        if status == "failed":
            lines.append(f"\nCould not read {url}: {note[:80]}")
        elif note == "NO CONTENT":
            lines.append(f"\nNothing useful at {url}")
        else:
            lines.append(f"\n{url}\n{note}")
    return "\n".join(lines)

def due(job, hour):
    # True once per day, after the hour, even after a restart
    return (datetime.now().hour >= hour
            and get_meta(job) != str(date.today()))

def phone_commands():
    # Only the owner can command the agent, and only with /now
    if not (BOT_TOKEN and OWNER_ID):
        return False
    start = int(get_meta("offset") or 0)
    updates = tg("getUpdates", offset=start, timeout=0)
    wanted = False
    for update in updates:
        set_meta("offset", update["update_id"] + 1)
        message = update.get("message", {})
        if message.get("from", {}).get("id") != OWNER_ID:
            continue  # strangers get no answer at all
        wanted = wanted or message.get("text") == "/now"
    return wanted

if __name__ == "__main__":
    print(f"Agent running: research at {RESEARCH_HOUR}:00, "
          f"brief at {BRIEF_HOUR}:00")
    while True:
        day = str(date.today())
        if due("research", RESEARCH_HOUR):
            research(day)
            set_meta("research", day)
        ready = get_meta("research") == day
        if due("brief", BRIEF_HOUR) and ready:
            send(make_brief(day))
            set_meta("brief", day)
        if phone_commands():
            research(day)
            send(make_brief(day))
        time.sleep(30)
