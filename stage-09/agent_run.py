import json
from tracing import call, record

def run_agent(name, system, task, tools=None, functions=None,
              max_steps=6):
    messages = [{"role": "system", "content": system},
                {"role": "user", "content": task}]
    for step in range(max_steps):
        options = {"tools": tools} if tools else {}
        msg = call(name, messages, **options)
        messages.append(msg)
        if not msg.tool_calls:
            return msg.content
        for tc in msg.tool_calls:
            args = json.loads(tc.function.arguments)
            result = functions[tc.function.name](**args)
            record(name, "tool", tool=tc.function.name,
                   args=args, result_chars=len(result))
            messages.append({"role": "tool", "content": result,
                             "tool_call_id": tc.id})
    return "Stopped at the step limit."
