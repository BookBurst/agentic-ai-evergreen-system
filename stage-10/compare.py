import re, sys
from pathlib import Path
from prompts import load, PROMPTS
from tracing import client, MODEL

CASES = [
    "My blender arrived broken. I want my money back.",
    "Where is my order? It has been a week.",
    "Can I change the delivery address?",
    "The charger stopped working after two months.",
    "I was charged twice for the same order.",
]

def problems(reply):
    # Checks in plain code: the rules the prompt asks for
    found = []
    sentences = re.split(r"(?<=[.!?])\s+", reply.strip())
    if len(sentences) > 2:
        found.append("more than two sentences")
    if len(reply.split()) > 40:
        found.append("over 40 words")
    if re.search(r"\d", reply):
        found.append("a number or date")
    return found

def score(system):
    passed = 0
    for case in CASES:
        reply = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": system},
                      {"role": "user", "content": case}])
        text = reply.choices[0].message.content
        issues = problems(text)
        passed += not issues
        print("  ", "ok  " if not issues else "FAIL", issues)
    return passed

if __name__ == "__main__":
    live, live_text = load("support")
    candidate = sys.argv[1]
    _, new_text = load("support", candidate)
    print("live version", live)
    before = score(live_text)
    print("candidate version", candidate)
    after = score(new_text)
    print(f"live {before} of {len(CASES)}, "
          f"candidate {after} of {len(CASES)}")
    if after == len(CASES) and after >= before:
        pointer = PROMPTS / "support.current"
        pointer.write_text(candidate, "utf-8")
        print("candidate is now live")
