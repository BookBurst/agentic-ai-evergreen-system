import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from openai import OpenAI

for line in Path(".env").read_text().splitlines():
    if "=" in line and not line.startswith("#"):
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())

client = OpenAI(api_key=os.environ["API_KEY"],
                base_url=os.environ.get("BASE_URL") or None)
MODEL = os.environ["MODEL_NAME"]
used = {"calls": 0, "tokens": 0}

def call(system, user):
    reply = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": user}])
    used["calls"] += 1
    used["tokens"] += reply.usage.total_tokens
    return reply.choices[0].message.content.strip()

def mixture(question, drafts=3):
    # Several independent drafts, then one call merges them
    with ThreadPoolExecutor(drafts) as pool:
        found = list(pool.map(
            lambda _: call("Answer in under 80 words.",
                           question), range(drafts)))
    numbered = "\n\n".join(f"Draft {i+1}:\n{d}"
                           for i, d in enumerate(found))
    return call("You are given drafts of an answer. Write one "
                "answer under 80 words that keeps what the "
                "drafts agree on and flags what they disagree "
                "on.", f"Question: {question}\n\n{numbered}")

if __name__ == "__main__":
    question = ("Should an agent that runs every night "
                "keep its notes in a text file or "
                "in a small database?")
    print(call("Answer in under 80 words.", question))
    print("single:", used)
    used.update(calls=0, tokens=0)
    print(mixture(question))
    print("mixture:", used)
