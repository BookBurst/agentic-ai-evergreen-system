import json
import re
from escalate import answer, cost

CASES = [  # (text, the quantity a person reads)
    ("Please send 12 blue pens.", 12),
    ("We need 1,200 envelopes by Monday.", 1200),
    ("Order 40 notebooks for the class.", 40),
    ("Order 7348: ship 25 mugs.", 25),
    ("Add 6 staplers to the list.", 6),
    ("Reserve 9 folders, please.", 9),
    ("We need 4,800 stickers for the fair.", 4800),
    ("Deliver 64 chairs on Friday.", 64),
    ("We are out of 3,075 cables.", 3075),
    ("Pack 15 towels per box.", 15),
]

def small(text):
    # A stand-in for a small model: takes the first number it
    # sees and stops reading at a comma
    first = re.search(r"\d+", text).group()
    return json.dumps({"quantity": int(first)})

def large(text):
    # A stand-in for a large model: always reads it right
    return json.dumps({"quantity": dict(CASES)[text]})

MODELS = [("small", small), ("large", large)]
spent = right = 0
for text, truth in CASES:
    size, reply = answer(text, MODELS)
    if size is None:
        print("a person takes this one:", text)
        continue
    quantity = json.loads(reply)["quantity"]
    verdict = "ok" if quantity == truth else "WRONG"
    right += quantity == truth
    spent += cost("small")
    if size == "large":
        spent += cost("large")
    print(f"{size:<5} {quantity:>6}  {verdict}")
total = len(CASES)
print(f"right {right} of {total}, cost {spent:.5f} dollars")
print(f"large for all: {total * cost('large'):.5f} dollars")
