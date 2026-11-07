import json, math, os, re, sqlite3
from pathlib import Path
from openai import OpenAI
from chunk_compare import TEXT

def load_env(path=".env"):
    for line in Path(path).read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())

load_env()
client = OpenAI(api_key=os.environ["API_KEY"],
                base_url=os.environ.get("BASE_URL") or None)
MODEL = os.environ["MODEL_NAME"]
EMBED = "text-embedding-3-small"

def sentence_pieces(text):
    # One piece per sentence, each with its section title on top
    pieces, section = [], ""
    for part in text.split("\n\n"):
        part = part.strip()
        if "\n" not in part and not part.endswith("."):
            section = part
        else:
            for s in re.split(r"(?<=[.!?]) ", part):
                pieces.append(f"{section}: {s}")
    return pieces

PIECES = sentence_pieces(TEXT)
db = sqlite3.connect(":memory:")
db.execute("CREATE VIRTUAL TABLE p USING fts5(text, "
           "tokenize='porter')")
for piece in PIECES:
    db.execute("INSERT INTO p VALUES (?)", (piece,))

STOP = set("""the and for you your can how what who when
does did are was with about from onto any there that this have
has not too out our their them they but""".split())

def by_words(question, k=20):
    words = [w for w in re.findall(r"\w+", question.lower())
             if len(w) > 2 and w not in STOP]
    match = " OR ".join(f'"{w}"' for w in words)
    rows = db.execute("SELECT rowid FROM p WHERE p MATCH ? "
                      "ORDER BY bm25(p) LIMIT ?", (match, k))
    return [r[0] - 1 for r in rows]  # positions in PIECES

def embed(texts):
    out = client.embeddings.create(model=EMBED, input=texts)
    return [d.embedding for d in out.data]

VECTORS = embed(PIECES)

def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (math.sqrt(sum(x * x for x in a))
                  * math.sqrt(sum(y * y for y in b)))

def by_meaning(question, k=20):
    q = embed([question])[0]
    scores = [cosine(q, v) for v in VECTORS]
    order = sorted(range(len(PIECES)),
                   key=lambda i: -scores[i])
    return order[:k]

def hybrid(question, k=20):
    # Fusion by rank: near the top of either list wins
    score = {}
    for ranking in (by_words(question), by_meaning(question)):
        for rank, i in enumerate(ranking, 1):
            score[i] = score.get(i, 0) + 1 / (60 + rank)
    return sorted(score, key=lambda i: -score[i])[:k]

USED = {"in": 0, "out": 0}

def rerank(question, candidates, keep=3):
    # Second pass: the model reads all candidates
    listing = "\n".join(f"[{n}] {PIECES[i]}"
                        for n, i in enumerate(candidates))
    prompt = (f"Question: {question}\n\n"
              f"Passages:\n{listing}\n\n"
              f"Pick the {keep} passages that best answer the "
              "question, best first. Reply with a JSON list "
              "of their numbers only, like [4, 0, 7].")
    reply = client.chat.completions.create(
        model=MODEL, max_completion_tokens=400,
        messages=[{"role": "user", "content": prompt}])
    USED["in"] += reply.usage.prompt_tokens
    USED["out"] += reply.usage.completion_tokens
    text = reply.choices[0].message.content
    start, end = text.index("["), text.rindex("]") + 1
    numbers = json.loads(text[start:end])
    return [candidates[n] for n in numbers
            if n < len(candidates)]

# (question, start of the sentence that answers it)
TESTS = [
    ("How long can I hold onto a drill?",
     "Power tools are lent for three days"),
    ("Is there a way to extend my borrowing period?",
     "Renewals are allowed once"),
    ("What if I break a saw by being careless?",
     "If a tool is returned damaged through misuse"),
    ("Can a teenager use the circular saw?",
     "Members under eighteen cannot borrow power tools"),
    ("What if I can't make my pickup time?",
     "A reserved tool is held for the member"),
    ("Do I need goggles of my own?",
     "Protective equipment such as goggles and gloves"),
    ("What does it cost for two parents and two kids?",
     "A household of up to four people pays $45"),
    ("Can I leave a ladder at the door when you are closed?",
     "Power tools and large items must be handed over"),
    ("Who sets a repair bill and can I dispute it?",
     "Repair costs are set by the shop volunteer"),
    ("Can I borrow something to cut a branch on my roof?",
     "The library does not lend tools for use on roofs"),
    ("late fee per day",
     "A late fee of $2 per day applies"),
    ("tile saw reservation two days ahead",
     "must be reserved at least two days ahead"),
    ("angle grinder signed card",
     "also require a signed safety card"),
    ("wet vacuum loan length",
     "Large items such as the tile saw, the wet vacuum"),
    ("ninety days large-item privileges",
     "loses large-item privileges for ninety days"),
]

def hit(ranking, answer, k):
    return any(answer in PIECES[i] for i in ranking[:k])

if __name__ == "__main__":
    methods = {"words": by_words, "meaning": by_meaning,
               "hybrid": hybrid}
    top1 = {n: 0 for n in [*methods, "hybrid + rerank"]}
    top3 = dict(top1)
    for question, answer in TESTS:
        rankings = {n: f(question) for n, f in methods.items()}
        rankings["hybrid + rerank"] = rerank(
            question, rankings["hybrid"])
        for name, ranking in rankings.items():
            top1[name] += hit(ranking, answer, 1)
            top3[name] += hit(ranking, answer, 3)
    print(f"{'method':18} first  top 3   (of {len(TESTS)})")
    for name in top1:
        print(f"{name:18} {top1[name]:5} {top3[name]:6}")
    print("rerank tokens:", USED)
