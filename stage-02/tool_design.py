import json
import os
import re
from pathlib import Path
from openai import OpenAI

for line in Path(".env").read_text().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())
client = OpenAI(api_key=os.environ["API_KEY"],
                base_url=os.environ.get("BASE_URL") or None)

# A tool described the quick way
VAGUE = {"type": "function", "function": {
    "name": "reminder",
    "description": "Reminders.",
    "parameters": {"type": "object", "properties": {
        "text": {"type": "string"},
        "when": {"type": "string"},
        "repeat": {"type": "string"}}}}}

# The same tool, described for the model
CLEAR = {"type": "function", "function": {
    "name": "add_reminder",
    "description": (
        "Save one new reminder for the user. Use it only "
        "when the user asks to be reminded of something. "
        "It cannot read or list saved reminders."),
    "parameters": {"type": "object", "properties": {
        "text": {"type": "string",
                 "description": "What to remember, short"},
        "date": {"type": "string",
                 "description": "Day as YYYY-MM-DD"},
        "repeat": {"type": "string",
                   "enum": ["none", "daily", "weekly"],
                   "description": "How often it comes "
                                  "back after the date"}},
        "required": ["text", "date", "repeat"]}}}

TODAY = "Today is Wednesday, November 4, 2026."
CASES = [  # request, expected (None = no tool call)
    ("Remind me on Friday to call the dentist.",
     ("2026-11-06", "none")),
    ("Starting tomorrow, remind me every day to take "
     "my vitamins.", ("2026-11-05", "daily")),
    ("From November 9, remind me every week to water "
     "the plants.", ("2026-11-09", "weekly")),
    ("What reminders do I have for tomorrow?", None),
    ("In two weeks remind me to pay the electric bill.",
     ("2026-11-18", "none")),
]
DATE = re.compile(r"\d{4}-\d{2}-\d{2}$")
REPEATS = {"none", "daily", "weekly"}

def usable(call, expected):
    """True if the program can save this reminder as is."""
    if expected is None:
        return call is None
    if call is None:
        return False
    args = json.loads(call.function.arguments or "{}")
    date = args.get("date") or args.get("when") or ""
    repeat = args.get("repeat") or "none"
    return (bool(DATE.match(date)) and repeat in REPEATS
            and (date, repeat) == expected)

RUNS = 3
for tool in (VAGUE, CLEAR):
    good, log = 0, []
    for text, expected in CASES:
        for _ in range(RUNS):
            reply = client.chat.completions.create(
                model=os.environ["MODEL_NAME"],
                messages=[{"role": "system", "content": TODAY},
                          {"role": "user", "content": text}],
                tools=[tool])
            calls = reply.choices[0].message.tool_calls
            call = calls[0] if calls else None
            ok = usable(call, expected)
            good += ok
            args = call.function.arguments if call else "-"
            log.append((ok, text[:30], args))
    name = tool["function"]["name"]
    print(f"{name}: {good} of {len(CASES) * RUNS} usable")
    for ok, text, args in log:
        print("  ", "OK " if ok else "BAD", text, args)
