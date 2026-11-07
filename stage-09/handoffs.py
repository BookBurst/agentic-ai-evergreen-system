import json
from agent_run import run_agent
from cost import cost_of
from team_demo import (TOOLS, lookup, RESEARCHER, WRITER, REVIEWER)
from tracing import TRACE

TASK = "Explain how refunds and shipping work for a new customer."
SOLO = ("You answer from the company handbook. Read it with the "
        "lookup tool, starting with the index, then write one "
        "short, friendly paragraph. Never state a fact that is "
        "not in the handbook.")

def totals():
    rows = [json.loads(line) for line in
            open(TRACE, encoding="utf-8")]
    model = [r for r in rows if r["kind"] == "model"]
    tin = sum(r["tokens_in"] for r in model)
    tout = sum(r["tokens_out"] for r in model)
    return len(model), tin, tout

def report(label):
    calls, tin, tout = totals()
    print(f"{label:<10} {calls} calls  {tin} in  {tout} out",
          f" ${cost_of(tin, tout):.5f}")

TRACE.unlink(missing_ok=True)
run_agent("solo", SOLO, TASK, TOOLS, {"lookup": lookup})
report("one agent")

TRACE.unlink(missing_ok=True)
notes = run_agent("researcher", RESEARCHER, TASK, TOOLS,
                  {"lookup": lookup})
draft = run_agent("writer", WRITER, f"{TASK}\nNotes:\n{notes}")
run_agent("reviewer", REVIEWER, f"Notes:\n{notes}\nDraft:\n{draft}")
report("three agents")
