import csv, json, os, re
from pathlib import Path
from openai import OpenAI

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

def ask(system, user):
    # One model call that must answer in JSON
    reply = client.chat.completions.create(
        model=MODEL,
        response_format={"type": "json_object"},
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": user}])
    return json.loads(reply.choices[0].message.content)

def read_rows(path="expenses.csv"):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def figures(rows):
    # The code adds the numbers, so the model does not have to
    by_category = {}
    for r in rows:
        name, amount = r["category"], float(r["amount"])
        so_far = by_category.get(name, 0)
        by_category[name] = round(so_far + amount, 2)
    total = round(sum(by_category.values()), 2)
    return {"total": total, "by_category": by_category}

def write_report(rows, problems=None):
    system = ("Write a short expense report from the rows. "
              'Reply as JSON: {"total": number, "currency": '
              '"USD", "largest_category": "name", "summary": '
              '"two sentences"}. Use the figures exactly '
              'as given.')
    if problems:
        system += ("\nYour last report had these problems. Fix "
                   "them:\n" + "\n".join(problems))
    data = {"rows": rows, "figures": figures(rows)}
    return ask(system, json.dumps(data))

def check_report(report, rows):
    # Every criterion is a plain test the code can run
    problems = []
    truth = figures(rows)
    total, by_category = truth["total"], truth["by_category"]
    if abs(float(report.get("total", 0)) - total) > 0.01:
        problems.append(f"total is {report.get('total')}, "
                        f"the rows add up to {total}")
    top = max(by_category, key=by_category.get)
    if report.get("largest_category") != top:
        problems.append(f"largest category is {top}")
    known = [total] + [float(r["amount"]) for r in rows]
    known += list(by_category.values())
    # An amount looks like 1,263.44 or 280.3
    amount = r"\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+\.\d+"
    for n in re.findall(amount, report.get("summary", "")):
        value = float(n.replace(",", ""))
        if not any(abs(value - k) < 0.01 for k in known):
            problems.append(f"the summary has {n}, "
                            "which is not in the data")
    return problems

def deliver(rows):
    report = write_report(rows)
    problems = check_report(report, rows)
    if problems:  # one more try, with the problems listed
        report = write_report(rows, problems)
        problems = check_report(report, rows)
    status = "CHECKED" if not problems else "NEEDS A PERSON"
    return {"status": status, "problems": problems,
            "report": report}

if __name__ == "__main__":
    print(json.dumps(deliver(read_rows()), indent=2))
