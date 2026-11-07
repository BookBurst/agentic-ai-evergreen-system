import json

with open("agent_log.jsonl", encoding="utf-8") as f:
    for line in f:
        e = json.loads(line)
        print(e["step"], e["tool"], e["args"], e["result"][:60])
