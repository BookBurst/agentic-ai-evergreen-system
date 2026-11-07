import json
from tracing import client, MODEL
from team_demo import RESEARCHER, TOOLS, DOCS

TASK = "Explain how refunds work for a new customer."

def tokens_in(messages, tools=None):
    # A tiny reply, because only what went in matters here
    options = {}
    if tools:
        options = {"tools": tools, "tool_choice": "none"}
    reply = client.chat.completions.create(
        model=MODEL, messages=messages,
        max_completion_tokens=5, **options)
    return reply.usage.prompt_tokens

user = {"role": "user", "content": TASK}
system = {"role": "system", "content": RESEARCHER}
call = {"role": "assistant", "content": None, "tool_calls": [{
    "id": "c1", "type": "function", "function": {
        "name": "lookup",
        "arguments": json.dumps({"topic": "refunds"})}}]}
result = {"role": "tool", "tool_call_id": "c1",
          "content": DOCS["refunds"]}

a = tokens_in([user])
b = tokens_in([system, user])
c = tokens_in([system, user], TOOLS)
d = tokens_in([system, user, call, result], TOOLS)
print(f"the question alone      {a:>5}")
print(f"+ system instructions   {b - a:>5}")
print(f"+ tool descriptions     {c - b:>5}")
print(f"+ one tool call and its result {d - c:>5}")
print(f"total sent              {d:>5}")
