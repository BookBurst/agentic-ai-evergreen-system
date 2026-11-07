import re, sqlite3
from pathlib import Path

TEXT = Path("toollib/handbook.txt").read_text(encoding="utf-8")

def fixed_chunks(text, size=400):
    # Cut every `size` characters, wherever that lands
    return [text[i:i + size] for i in range(0, len(text), size)]

def smart_chunks(text):
    # One chunk per paragraph, with the section title on top and
    # the last sentence of the previous paragraph as overlap
    chunks, section, prev = [], "", ""
    for part in text.split("\n\n"):
        part = part.strip()
        if not part:
            continue
        if "\n" not in part and not part.endswith("."):
            section, prev = part, ""   # a heading line
            continue
        body = (prev + " " + part).strip()
        chunks.append(f"{section}\n{body}")
        prev = re.split(r"(?<=[.!?]) ", part)[-1]
    return chunks

def build(chunks):
    db = sqlite3.connect(":memory:")
    db.execute("CREATE VIRTUAL TABLE c USING fts5(text, "
               "tokenize='porter')")
    for chunk in chunks:
        db.execute("INSERT INTO c VALUES (?)", (chunk,))
    return db

def search(db, question, k=3):
    words = [w for w in re.findall(r"\w+", question.lower())
             if len(w) > 2]
    match = " OR ".join(f'"{w}"' for w in words)
    rows = db.execute("SELECT text FROM c WHERE c MATCH ? "
                      "ORDER BY bm25(c) LIMIT ?", (match, k))
    return [r[0] for r in rows]

# (question, the sentence that answers it)
TESTS = [
    ("How many days can I keep a power tool?",
     "Power tools are lent for three days"),
    ("Can I renew the tile saw?",
     "cannot be renewed under any circumstances"),
    ("What happens if I keep a large item past the due date?",
     "loses large-item privileges for ninety days"),
    ("What is the most a late fee can reach?",
     "up to a maximum of $20 per tool"),
    ("Can my 16-year-old borrow the router?",
     "Members under eighteen cannot borrow power tools"),
    ("How long do I have to replace a lost tool myself?",
     "within fourteen days of reporting it lost"),
    ("Can I drop off a drill after hours?",
     "only hand tools and garden tools can be returned"),
    ("What does a household of four pay each year?",
     "A household of up to four people pays $45"),
    ("How long does the safety briefing last?",
     "The briefing is valid for two years"),
    ("Do volunteers ever get free membership?",
     "pay no fee the following year"),
]

def score(chunks):
    db, hits = build(chunks), []
    for question, answer in TESTS:
        found = any(answer in c.replace("\n", " ")
                    for c in search(db, question))
        hits.append(found)
    return hits

if __name__ == "__main__":
    methods = (("fixed 400 characters", fixed_chunks(TEXT)),
               ("by paragraph, with title and overlap",
                smart_chunks(TEXT)))
    for name, chunks in methods:
        hits = score(chunks)
        sizes = [len(c) for c in chunks]
        print(f"{name}: {len(chunks)} chunks, "
              f"{min(sizes)}-{max(sizes)} characters, "
              f"{sum(hits)} of {len(TESTS)} found")
        for (q, _), ok in zip(TESTS, hits):
            print("   ", "found " if ok else "MISSED", q)
