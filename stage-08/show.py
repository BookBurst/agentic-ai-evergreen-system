import json
from collections import defaultdict

rows = [json.loads(line) for line in
        open("trace.jsonl", encoding="utf-8")]

print("step agent       what")
totals = defaultdict(lambda: [0, 0, 0])
for i, r in enumerate(rows, 1):
    if r["kind"] == "model":
        bar = "#" * (r["tokens_in"] // 100)
        line = f"{i:>3}  {r['agent']:<10} model"
        line += f" in {r['tokens_in']:>4}"
        line += f" out {r['tokens_out']:>3}"
        print(line, f"{r['seconds']}s", bar)
        t = totals[r["agent"]]
        t[0] += 1
        t[1] += r["tokens_in"]
        t[2] += r["tokens_out"]
    else:
        what = f"{r['tool']} {r['args'].get('topic')!r}"
        print(f"{i:>3}  {r['agent']:<10} tool  {what}",
              f"-> {r['result_chars']} chars")

print("\nagent        calls  tokens in  tokens out")
for name, (calls, tin, tout) in totals.items():
    print(f"{name:<12} {calls:>5}  {tin:>9}  {tout:>10}")
