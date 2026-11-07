import csv, json, os
from pathlib import Path
from openai import OpenAI, BadRequestError

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

with open("expenses.csv", newline="", encoding="utf-8") as f:
    ROWS = json.dumps(list(csv.DictReader(f)))

def once(temperature, fixed_fields):
    system = "Write a short expense report from the rows."
    options = {}
    if fixed_fields:
        system += (' Reply as JSON: {"total": number, '
                   '"largest_category": "name"}')
        options["response_format"] = {"type": "json_object"}
    reply = client.chat.completions.create(
        model=MODEL, temperature=temperature, **options,
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": ROWS}])
    text = reply.choices[0].message.content
    if fixed_fields:
        data = json.loads(text)
        return (data["total"], data["largest_category"])
    return text

if __name__ == "__main__":
    settings = [(1, False), (0, False), (0, True)]
    for temperature, fixed in settings:
        kind = "fixed fields" if fixed else "free text"
        try:
            results = [once(temperature, fixed)
                       for _ in range(5)]
        except BadRequestError:
            # Some models accept only their default temperature
            print(f"temperature {temperature}: "
                  "refused by this model")
            continue
        print(f"temperature {temperature}, {kind}: "
              f"{len(set(results))} different results "
              "in 5 runs")
