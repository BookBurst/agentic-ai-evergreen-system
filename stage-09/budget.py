import json, time
from pathlib import Path
from cost import cost_of
from tracing import client, MODEL, record

LEDGER = Path("spend.json")  # dollars spent, one number per day
RUN_CAP = 0.05               # dollars one run may spend
DAILY_CAP = 0.50             # dollars all runs may spend a day

class BudgetExceeded(Exception):
    pass

def spent_today():
    if not LEDGER.exists():
        return 0.0
    days = json.loads(LEDGER.read_text("utf-8"))
    return days.get(time.strftime("%Y-%m-%d"), 0.0)

def add_spend(amount):
    days = {}
    if LEDGER.exists():
        days = json.loads(LEDGER.read_text("utf-8"))
    today = time.strftime("%Y-%m-%d")
    days[today] = days.get(today, 0.0) + amount
    LEDGER.write_text(json.dumps(days), "utf-8")

def capped_call(agent, messages, run, **options):
    # Check the caps first, so a refused call costs nothing
    if run["spent"] >= RUN_CAP:
        raise BudgetExceeded("run cap reached")
    if spent_today() >= DAILY_CAP:
        raise BudgetExceeded("daily cap reached")
    reply = client.chat.completions.create(
        model=MODEL, messages=messages,
        max_completion_tokens=300, **options)
    usage = reply.usage
    amount = cost_of(usage.prompt_tokens,
                     usage.completion_tokens)
    run["spent"] += amount
    add_spend(amount)
    record(agent, "model", tokens_in=usage.prompt_tokens,
           tokens_out=usage.completion_tokens, seconds=0)
    return reply.choices[0].message

if __name__ == "__main__":
    DAILY_CAP = 0.0004  # tiny on purpose, to see the stop
    run = {"spent": 0.0}
    messages = [{"role": "user",
                 "content": "Write two sentences about rain."}]
    try:
        for n in range(1, 100):
            capped_call("demo", messages, run)
            print(f"call {n} done, spent ${spent_today():.5f}")
    except BudgetExceeded as stop:
        print("Stopped:", stop)
