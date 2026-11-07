import json, os
from datetime import date
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
PRIORITIES = {"low", "normal", "high"}
INSTRUCTIONS = """Read the email and reply with JSON only:
{"customer": "name", "amount": 480.0,
 "due_date": "YYYY-MM-DD", "priority": "low, normal or high"}
Use null for anything the email does not state."""

def check_fields(data):
    # Returns a list of problems; an empty list means valid
    if not isinstance(data, dict):
        return ["the reply must be a JSON object"]
    problems = []
    if not isinstance(data.get("customer"), str):
        problems.append("customer must be a string")
    amount = data.get("amount")
    if not isinstance(amount, (int, float)) or amount <= 0:
        problems.append("amount must be a positive number")
    due = data.get("due_date")  # null is allowed: not stated
    try:
        if due is not None:
            date.fromisoformat(due)
    except (ValueError, TypeError):
        problems.append("due_date must look like 2027-03-12")
    if data.get("priority") not in PRIORITIES:
        problems.append("priority must be one of: "
                        + ", ".join(sorted(PRIORITIES)))
    return problems

def extract(email, max_tries=3):
    messages = [{"role": "system", "content": INSTRUCTIONS},
                {"role": "user", "content": email}]
    for attempt in range(1, max_tries + 1):
        reply = client.chat.completions.create(
            model=MODEL, messages=messages,
        ).choices[0].message.content
        try:
            problems = check_fields(json.loads(reply))
        except ValueError:
            problems = ["the reply was not valid JSON"]
        print(f"try {attempt}:", problems or "valid")
        if not problems:
            return json.loads(reply)
        messages.append({"role": "assistant", "content": reply})
        messages.append({"role": "user", "content":
            "Fix this, JSON only: " + "; ".join(problems)})
    return None  # give up: a person reads this email

if __name__ == "__main__":
    email = ("Hi, it's Dana Reyes. Please pay my 480 dollar "
             "hosting invoice by March 12, 2027. It's urgent.")
    print(extract(email))
