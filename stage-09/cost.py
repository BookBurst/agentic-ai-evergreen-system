import json
from collections import defaultdict

# Example prices in dollars per 1 million tokens, read from the
# provider's price page in November 2026. Replace them with the
# prices of the model you use.
PRICE_IN = 0.40
PRICE_OUT = 1.60

def cost_of(tokens_in, tokens_out):
    # Dollars for one call: input and output are priced apart
    total = tokens_in * PRICE_IN + tokens_out * PRICE_OUT
    return total / 1_000_000

if __name__ == "__main__":
    rows = [json.loads(line) for line in
            open("trace.jsonl", encoding="utf-8")]
    per_agent = defaultdict(float)
    for r in rows:
        if r["kind"] == "model":
            per_agent[r["agent"]] += cost_of(r["tokens_in"],
                                             r["tokens_out"])
    for name, dollars in per_agent.items():
        print(f"{name:<12} ${dollars:.5f}")
    print(f"{'this run':<12} ${sum(per_agent.values()):.5f}")
