import json, os, re, sqlite3
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
DOCS = Path("docs")  # the only folder it reads
MAX_STEPS = 6        # model calls per question
MAX_FIXES = 2        # corrections allowed per answer

db = sqlite3.connect(":memory:")
db.execute("CREATE VIRTUAL TABLE chunks "
           "USING fts5(id UNINDEXED, text, "
           "tokenize='porter')")  # porter: refund = refunds

def build_index():
    # One chunk per paragraph, labeled file#number
    for path in sorted(DOCS.glob("*.txt")):
        parts = path.read_text(encoding="utf-8").split("\n\n")
        for n, part in enumerate(parts, 1):
            if part.strip():
                db.execute("INSERT INTO chunks VALUES (?, ?)",
                           (f"{path.name}#{n}",
                            part.strip()[:1500]))

RETRIEVED = {}  # chunk id -> text the model has seen
SEARCHES = []   # every query the model ran

def search_documents(query):
    SEARCHES.append(query)
    words = [w for w in re.findall(r"\w+", query.lower())
             if len(w) > 2]
    if not words:
        return {"error": "Give a few keywords."}
    match = " OR ".join(f'"{w}"' for w in words)
    rows = db.execute(
        "SELECT id, text FROM chunks WHERE chunks MATCH ? "
        "ORDER BY bm25(chunks) LIMIT 4", (match,)).fetchall()
    for chunk_id, text in rows:
        RETRIEVED[chunk_id] = text
    return [{"id": i, "text": t} for i, t in rows]

def call_search(call):
    try:
        args = json.loads(call.function.arguments or "{}")
        return search_documents(**args)
    except Exception as err:  # bad arguments
        return {"error": f"{type(err).__name__}: {err}"}

SCHEMAS = [{"type": "function", "function": {
    "name": "search_documents",
    "description": "Search the documents by keywords. Returns "
                   "up to 4 passages, each with an id.",
    "parameters": {
        "type": "object",
        "properties": {"query": {"type": "string"}},
        "required": ["query"]}}}]
RULES = """You answer questions using only the passages returned
by search_documents. Search before you answer. If the passages
don't help, search again with other words, for example
synonyms or other forms of the word, before giving up.
Reply with JSON only, in this shape:
{"answer": "...", "sources": ["file.txt#2"], "found": true}
Every fact in the answer must come from a passage you list in
sources. If the passages do not contain the answer, reply:
{"answer": "I could not find this in the documents.",
 "sources": [], "found": false}
found is true only if a passage states the answer. If the
answer is missing, or you must say that the documents do not
specify it, found must be false. Never use knowledge from
outside the passages."""

def check_answer(text):
    # None if the reply is valid, else a message for the model
    try:
        data = json.loads(text)
    except ValueError:
        return "Reply with valid JSON only, with no other text."
    if (not isinstance(data, dict)
            or not isinstance(data.get("answer"), str)
            or not isinstance(data.get("sources"), list)
            or not isinstance(data.get("found"), bool)):
        return "Use exactly the keys answer, sources and found."
    if not SEARCHES:
        return "Search the documents before you answer."
    unknown = [s for s in data["sources"] if s not in RETRIEVED]
    if unknown:
        return f"These ids never came from a search: {unknown}."
    if data["found"] and not data["sources"]:
        return "found=true needs at least one source."
    if not data["found"] and data["sources"]:
        return "found=false needs an empty sources list."
    return None

def run(question):
    RETRIEVED.clear()
    SEARCHES.clear()
    messages = [{"role": "system", "content": RULES},
                {"role": "user", "content": question}]
    fixes = 0
    for step in range(MAX_STEPS):
        msg = client.chat.completions.create(
            model=MODEL, messages=messages, tools=SCHEMAS,
        ).choices[0].message
        messages.append(msg)
        if msg.tool_calls:
            for call in msg.tool_calls:
                print("  searching:", call.function.arguments)
                messages.append({
                    "role": "tool", "tool_call_id": call.id,
                    "content": json.dumps(call_search(call))})
            continue
        problem = check_answer(msg.content or "")
        if problem is None:
            return json.loads(msg.content)
        fixes += 1
        if fixes > MAX_FIXES:
            break
        messages.append({"role": "user", "content": problem})
    return {"answer": "No valid answer. Ask a person to check.",
            "sources": [], "found": False}

if __name__ == "__main__":
    build_index()
    while True:
        question = input("\nQuestion (empty to quit): ").strip()
        if not question:
            break
        result = run(question)
        answer = result["answer"]
        if not result["found"]:  # the code decides
            answer = "I could not find this in the documents."
        print("\n" + answer)
        for source in result["sources"]:
            print(f"  [{source}] {RETRIEVED[source][:70]}...")
