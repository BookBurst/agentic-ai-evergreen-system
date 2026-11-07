import json
from check import client, MODEL

TOOLS = [{"type": "function", "function": {
    "name": "get_data", "description": "Get data on a topic",
    "parameters": {"type": "object",
                   "properties": {"topic": {"type": "string"}},
                   "required": ["topic"]}}}]

def get_data(topic):
    # Whatever the topic, the same table comes back
    return "Revenue by month: Aug 120, Sep 118, Oct 91."

def run(task, breaker=True, max_steps=8):
    messages = [
        {"role": "system", "content": "Find the cause of the "
         "drop in October revenue. State only a cause the data "
         "supports. Ask for more data with get_data until you "
         "can."},
        {"role": "user", "content": task}]
    seen, use_tools = {}, True
    for step in range(1, max_steps + 1):
        options = {"tools": TOOLS} if use_tools else {}
        msg = client.chat.completions.create(
            model=MODEL, messages=messages,
            **options).choices[0].message
        messages.append(msg)
        if not msg.tool_calls:
            return step, msg.content
        for call in msg.tool_calls:
            args = json.loads(call.function.arguments)
            result = get_data(**args)
            seen[result] = seen.get(result, 0) + 1
            messages.append({"role": "tool", "content": result,
                             "tool_call_id": call.id})
        if breaker and max(seen.values()) >= 2:
            # Nothing new came back: change the strategy
            use_tools = False
            messages.append({"role": "user", "content":
                "The same data keeps coming back. Do not ask "
                "for more. Say what the data does not show and "
                "what you would need."})
    return max_steps, "Stopped at the step limit."

if __name__ == "__main__":
    task = "Why did revenue fall in October?"
    for breaker in (False, True):
        steps, answer = run(task, breaker)
        print(f"breaker={breaker}: {steps} steps")
        print(" ", answer[:150])
