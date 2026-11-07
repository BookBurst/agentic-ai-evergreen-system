import json
from check import client, MODEL

STOCK = {"desk lamp": 0, "notebook": 12}

def check_stock(item):
    # The only tool: how many units are on the shelf
    units = STOCK.get(item.lower(), 0)
    return {"item": item, "in_stock": units}

TOOLS = [{"type": "function", "function": {
    "name": "check_stock",
    "description": "Count the units of an item in stock",
    "parameters": {"type": "object",
                   "properties": {"item": {"type": "string"}},
                   "required": ["item"]}}}]

def audit(reply, calls):
    # Level 1 checks the result, level 2 checks what was done
    problems = []
    item = reply["item"].lower()
    should = STOCK.get(item, 0) > 0
    if reply["confirmed"] != should:
        problems.append(f"confirmed={reply['confirmed']}, but "
                        f"stock says {should}")
    looked = [c for c in calls if c["name"] == "check_stock"
              and c["args"].get("item", "").lower() == item]
    if not looked:
        problems.append("check_stock was never called "
                        f"for {item}")
    return problems

def run(request):
    system = ("Before confirming an order you must call "
              "check_stock for the item. Confirm only if it is "
              "in stock. When done, reply with JSON only: "
              '{"item": "...", "confirmed": true or false}.')
    messages = [{"role": "system", "content": system},
                {"role": "user", "content": request}]
    calls = []   # what the agent really did, kept by our code
    for step in range(4):
        msg = client.chat.completions.create(
            model=MODEL, messages=messages,
            tools=TOOLS).choices[0].message
        messages.append(msg)
        if not msg.tool_calls:
            return json.loads(msg.content), calls
        for call in msg.tool_calls:
            name = call.function.name
            args = json.loads(call.function.arguments)
            calls.append({"name": name, "args": args})
            # one tool only, so the name is not looked up here
            result = json.dumps(check_stock(**args))
            messages.append({"role": "tool", "content": result,
                             "tool_call_id": call.id})
    return {"item": "?", "confirmed": False}, calls

if __name__ == "__main__":
    made_up = [
        # (reply, calls the code recorded)
        ({"item": "desk lamp", "confirmed": True}, []),
        ({"item": "notebook", "confirmed": True}, []),
        ({"item": "notebook", "confirmed": True},
         [{"name": "check_stock",
           "args": {"item": "notebook"}}]),
    ]
    for reply, calls in made_up:
        print(reply)
        for problem in audit(reply, calls) or ["no problems"]:
            print("  -", problem)
