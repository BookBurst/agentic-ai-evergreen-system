import json, time

def log(step, tool, args, result):
    entry = {"time": time.strftime("%H:%M:%S"),
             "step": step, "tool": tool, "args": args,
             "result": str(result)[:300]}
    with open("agent_log.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
